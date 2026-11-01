#!/usr/bin/env python3
"""ClashMC (클래시 마크) original background music generator.

Everything is synthesised from scratch with numpy/scipy (no samples):
Karplus-Strong lute/harp, additive band-limited detuned saws for brass and
strings (with a per-harmonic "filter" envelope), additive flute/clarinet,
synthetic drums, convolution reverb with a decaying-noise IR, chorus,
a look-ahead master limiter and BS.1770-style loudness normalisation.

Loops are rendered with a long tail which is folded back onto the start, so
the loop point is seamless. Run:  python3 compose.py  [track ...]
"""
import os, sys, json, wave, subprocess, time
from fractions import Fraction
from itertools import combinations
import numpy as np
from scipy.signal import lfilter, fftconvolve, butter, sosfilt
from scipy.ndimage import minimum_filter1d, uniform_filter1d

SR = 44100
HERE = os.path.dirname(os.path.abspath(__file__))
SND_DIR = os.path.join(HERE, 'assets', 'clashmc', 'sounds', 'bgm')
FFMPEG = '/usr/bin/ffmpeg'

# --------------------------------------------------------------------------
# pitch / harmony helpers
# --------------------------------------------------------------------------
NB = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def pc_of(name):
    v = NB[name[0]]
    for ch in name[1:]:
        v += 1 if ch == '#' else -1 if ch == 'b' else 0
    return v % 12


def midi(n):
    i = 1
    while i < len(n) and n[i] in '#b':
        i += 1
    acc = n[1:i].count('#') - n[1:i].count('b')
    return 12 * (int(n[i:]) + 1) + NB[n[0]] + acc


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


QUAL = {'': (0, 4, 7), 'm': (0, 3, 7), '7': (0, 4, 7, 10), 'm7': (0, 3, 7, 10),
        'maj7': (0, 4, 7, 11), 'sus4': (0, 5, 7), 'sus2': (0, 2, 7), 'dim': (0, 3, 6)}


def chord(sym):
    bass = None
    if '/' in sym:
        sym, b = sym.split('/')
        bass = pc_of(b)
    i = 1
    while i < len(sym) and sym[i] in '#b':
        i += 1
    root = pc_of(sym[:i])
    ivs = QUAL[sym[i:]]
    return dict(sym=sym, root=root, ivs=ivs, pcs=[(root + x) % 12 for x in ivs],
                bass=root if bass is None else bass)


def timeline(bars, bpb=4):
    """bars: list of strings, each one or more chord symbols splitting the bar."""
    out = []
    for i, b in enumerate(bars):
        syms = b.split()
        d = bpb / len(syms)
        for j, s in enumerate(syms):
            out.append((i * bpb + j * d, d, chord(s)))
    return out


def chord_at(tl, beat):
    for b, d, c in tl:
        if b <= beat + 1e-6 < b + d:
            return c
    return tl[-1][2]


def in_range(pc, lo, hi):
    """lowest midi note with pitch class pc that is >= lo (wraps below hi)."""
    m = lo + ((pc - lo) % 12)
    return m if m <= hi else m - 12


def voicings(ch, lo, hi, n):
    cands = [m for m in range(lo, hi + 1) if m % 12 in ch['pcs']]
    req = set(ch['pcs']) if (len(ch['pcs']) > 3 and n >= 4) else set(ch['pcs'][:3])
    res = []
    for c in combinations(cands, n):
        if not req <= {m % 12 for m in c}:
            continue
        g = np.diff(c)
        if g.min() < 2 or g.max() > 12:
            continue
        res.append(c)
    return res


def voice_lead(chords, lo, hi, n):
    prev, out = None, []
    mid = (lo + hi) / 2
    for ch in chords:
        vs = voicings(ch, lo, hi, n)
        if prev is None:
            best = min(vs, key=lambda v: abs(np.mean(v) - mid))
        else:
            best = min(vs, key=lambda v: sum(abs(a - b) for a, b in zip(v, prev))
                       + 0.35 * abs(np.mean(v) - mid))
        out.append(best)
        prev = best
    return out


def mel(text, start=0.0):
    """'F#5:1.5 E5:1/2 r:1' -> [(beat, dur, midi|None)], end beat"""
    ev, b = [], start
    for tok in text.split():
        p, d = tok.split(':')
        d = float(Fraction(d))
        ev.append((b, d, None if p == 'r' else midi(p)))
        b += d
    return ev, b


def diatonic_shift(m, scale_pcs, steps):
    """move a note by diatonic steps (negative = down) within scale."""
    notes = [x for x in range(m - 24, m + 25) if x % 12 in scale_pcs]
    if m in notes:
        i = notes.index(m)
    else:  # chromatic note -> nearest scale tone below
        i = max(j for j, x in enumerate(notes) if x < m)
    return notes[i + steps]


# --------------------------------------------------------------------------
# DSP helpers
# --------------------------------------------------------------------------
_SOS = {}


def sos(kind, f, order=2):
    key = (kind, f if np.isscalar(f) else tuple(f), order)
    if key not in _SOS:
        _SOS[key] = butter(order, f, btype=kind, fs=SR, output='sos')
    return _SOS[key]


def filt(x, kind, f, order=2):
    return sosfilt(sos(kind, f, order), x, axis=-1)


def env_adsr(n, a, d, s, r, hold, curve=1.0):
    """ADSR. hold = seconds at which release starts. r = time to ~-60 dB."""
    t = np.arange(n) / SR
    att = np.clip(t / max(a, 1e-4), 0, 1)
    att = 1 - (1 - att) ** 2
    dec = s + (1 - s) * np.exp(-np.maximum(t - a, 0) / max(d, 1e-4))
    e = att * dec
    rel = np.exp(-np.maximum(t - hold, 0) * 6.9 / max(r, 1e-3))
    e = e * rel
    k = min(n, 64)
    e[-k:] *= np.linspace(1, 0, k)
    return e ** curve


def pan_gains(p):
    th = (p + 1) * np.pi / 4
    return np.cos(th) * np.sqrt(2), np.sin(th) * np.sqrt(2)


NOISE = np.random.default_rng(99).standard_normal(SR * 8)


def noise(n, seed):
    r = np.random.default_rng(seed)
    if n > len(NOISE):
        return r.standard_normal(n)
    o = r.integers(0, len(NOISE) - n)
    return NOISE[o:o + n].copy()


# --------------------------------------------------------------------------
# instruments (all return mono or (2,n) float arrays, peak roughly <= 1)
# --------------------------------------------------------------------------
_KS = {}


def ks_string(f, n, bright=0.5, t60=2.0, pos=0.15, seed=0):
    """Karplus-Strong with two-point loss filter and allpass fractional tuning."""
    key = (round(f, 3), n, bright, t60, pos, seed % 3)
    if key in _KS:
        return _KS[key]
    P = SR / f
    D = P - 0.5
    N = int(np.floor(D))
    fr = D - N
    if fr < 0.2:
        N -= 1
        fr += 1
    c = (1 - fr) / (1 + fr)
    g = 10 ** (-3.0 / (t60 * f))
    r = np.random.default_rng(1000 + seed % 3)
    exc = r.uniform(-1, 1, N)
    a1 = np.exp(-2 * np.pi * (250 + bright * 7000) / SR)
    exc = lfilter([1 - a1], [1, -a1], np.concatenate([exc, exc]))[N:]
    k = max(1, int(pos * N))
    e2 = exc.copy()
    e2[k:] -= exc[:-k]
    e2 -= e2.mean()
    x = np.zeros(n)
    x[:N] = e2
    a = np.zeros(N + 3)
    a[0], a[1] = 1, c
    a[N] -= g * 0.5 * c
    a[N + 1] -= g * 0.5 * (1 + c)
    a[N + 2] -= g * 0.5
    y = lfilter([1, c], a, x)
    y /= (np.abs(y).max() + 1e-9)
    _KS[key] = y
    return y


def lute(m, dur, vel=1.0, seed=0):
    f = hz(m)
    rel = 0.35
    n = int((dur + rel) * SR)
    y = ks_string(f, n, bright=0.35 + 0.25 * vel, t60=1.8, pos=0.13, seed=seed)
    return y * env_adsr(n, 0.002, 10, 1, rel, dur) * vel


def harp(m, dur, vel=1.0, seed=0):
    f = hz(m)
    rel = 0.6
    n = int((dur + rel) * SR)
    y = ks_string(f, n, bright=0.55 + 0.3 * vel, t60=3.2, pos=0.28, seed=seed)
    t = np.arange(n) / SR
    y = y + 0.35 * np.sin(2 * np.pi * f * t) * np.exp(-t / 1.2) * np.minimum(t / 0.004, 1)
    return y * env_adsr(n, 0.001, 10, 1, rel, dur) * vel / 1.3


def pluck_bass(m, dur, vel=1.0, seed=0):
    """warm upright / pizzicato bass, additive with per-harmonic decay."""
    f = hz(m)
    rel = 0.15
    n = int((dur + rel) * SR)
    t = np.arange(n) / SR
    r = np.random.default_rng(seed)
    y = np.zeros(n)
    for k in range(1, 12):
        if k * f > 5000:
            break
        amp = (1.0 / k ** 1.3) * (1.0 if k == 1 else 0.8)
        y += amp * np.sin(2 * np.pi * k * f * t * (1 + 0.0004 * k) + r.uniform(0, 6.28)) \
            * np.exp(-t * (1.2 + 1.6 * k))
    thump = filt(noise(n, seed), 'lowpass', 900) * np.exp(-t / 0.012) * 0.25
    y = (y + thump) * env_adsr(n, 0.004, 10, 1, rel, dur)
    return y / 1.6 * vel


def flute(m, dur, vel=1.0, seed=0):
    f = hz(m)
    rel = 0.14
    n = int((dur + rel) * SR)
    t = np.arange(n) / SR
    r = np.random.default_rng(seed)
    vib = 0.0045 * np.clip((t - 0.2) / 0.3, 0, 1) * np.sin(2 * np.pi * 5.1 * t + r.uniform(0, 6.28))
    ph = 2 * np.pi * np.cumsum(f * (1 + vib)) / SR
    tone = np.sin(ph) + 0.20 * np.sin(2 * ph + 0.4) + 0.07 * np.sin(3 * ph + 1.0) + 0.025 * np.sin(4 * ph)
    br = filt(noise(n, seed), 'bandpass', (min(900, f), min(9000, 6 * f)))
    breath = br * (0.035 + 0.22 * np.exp(-t / 0.04))
    env = env_adsr(n, 0.055, 0.25, 0.86, rel, dur)
    swell = 1 + 0.10 * np.clip((t - 0.15) / max(dur, 0.2), 0, 1)
    return (tone + breath) * env * swell * vel / 1.25


def clarinet(m, dur, vel=1.0, seed=0):
    f = hz(m)
    rel = 0.12
    n = int((dur + rel) * SR)
    t = np.arange(n) / SR
    r = np.random.default_rng(seed)
    vib = 0.0025 * np.clip((t - 0.3) / 0.4, 0, 1) * np.sin(2 * np.pi * 4.7 * t + r.uniform(0, 6.28))
    ph = 2 * np.pi * np.cumsum(f * (1 + vib)) / SR
    y = (np.sin(ph) + 0.33 * np.sin(3 * ph) + 0.16 * np.sin(5 * ph) + 0.07 * np.sin(7 * ph)
         + 0.05 * np.sin(2 * ph) + 0.03 * np.sin(9 * ph))
    y += filt(noise(n, seed + 7), 'bandpass', (1200, 5000)) * 0.02
    return y * env_adsr(n, 0.05, 0.3, 0.9, rel, dur) * vel / 1.4


def saw_add(f, n, voices=3, det=8.0, fc=None, order=2, vib=0.0, vib_rate=5.5,
            vib_delay=0.25, scoop=0.0, spread=0.0, kmax=64, seed=0, drift=0.0):
    """Band-limited detuned saws by additive synthesis.
    fc: None, scalar Hz, or array (time-varying low-pass applied per harmonic)."""
    r = np.random.default_rng(seed)
    t = np.arange(n) / SR
    out = np.zeros((2, n))
    dets = np.linspace(-det, det, voices) if voices > 1 else np.zeros(1)
    pans = np.linspace(-spread, spread, voices) if voices > 1 else np.zeros(1)
    for i, d in enumerate(dets):
        fv = f * 2 ** ((d + r.normal(0, 1.2)) / 1200)
        mod = np.ones(n)
        if vib:
            mod += vib * np.clip((t - vib_delay) / 0.3, 0, 1) * \
                np.sin(2 * np.pi * vib_rate * (1 + 0.06 * r.normal()) * t + r.uniform(0, 6.28))
        if drift:
            mod += drift * np.sin(2 * np.pi * r.uniform(0.15, 0.4) * t + r.uniform(0, 6.28))
        if scoop:
            mod *= 2 ** (-scoop / 1200 * np.exp(-t / 0.045))
        ph = 2 * np.pi * np.cumsum(fv * mod) / SR + r.uniform(0, 6.28)
        s_prev = np.zeros(n)
        s_cur = np.sin(ph)
        c2 = 2 * np.cos(ph)
        v = np.zeros(n)
        K = int(min(kmax, 0.42 * SR / (fv * (1 + abs(vib) + 0.01))))
        for k in range(1, K + 1):
            if fc is None:
                h = 1.0
                hm = 1.0
            else:
                h = 1.0 / np.sqrt(1 + ((k * fv) / fc) ** (2 * order))
                hm = h if np.isscalar(h) else h.max()
            if hm / k < 1.5e-3:
                break
            v += (h / k) * s_cur
            s_prev, s_cur = s_cur, c2 * s_cur - s_prev
        gl, gr = pan_gains(pans[i])
        out[0] += v * gl
        out[1] += v * gr
    return out / (voices * 1.3)


def brass(m, dur, vel=1.0, seed=0, stab=False, dark=0.0, voices=3):
    f = hz(m)
    rel = 0.16 if stab else 0.22
    n = int((dur + rel) * SR)
    t = np.arange(n) / SR
    fe = (1 - np.exp(-t / 0.025)) * (0.55 + 0.45 * np.exp(-t / (0.15 if stab else 0.4)))
    fe *= np.exp(-np.maximum(t - dur, 0) / 0.08)
    fc = f * (1.3 + (8.5 - 5 * dark) * vel * fe) + 150
    y = saw_add(f, n, voices=voices, det=7, fc=fc, order=2, vib=0 if stab else 0.0045,
                vib_delay=0.3, scoop=25 if not stab else 12, spread=0.25, seed=seed, kmax=40)
    if stab:
        env = env_adsr(n, 0.012, 0.18, 0.55, rel, dur)
    else:
        env = env_adsr(n, 0.035, 0.4, 0.8, rel, dur)
    return y * env * vel


def strings(m, dur, vel=1.0, seed=0, attack=0.35, rel=0.6, voices=5, fc=2600, spread=0.8):
    f = hz(m)
    n = int((dur + rel) * SR)
    y = saw_add(f, n, voices=voices, det=11, fc=fc + 2 * f, order=2, vib=0.0022, vib_rate=5.2,
                vib_delay=0.15, spread=spread, seed=seed, drift=0.0008)
    return y * env_adsr(n, attack, 0.6, 0.9, rel, dur) * vel


def spiccato(m, dur, vel=1.0, seed=0):
    f = hz(m)
    rel = 0.07
    n = int((dur + rel) * SR)
    t = np.arange(n) / SR
    fc = f * (3 + 3 * vel * np.exp(-t / 0.05)) + 900
    y = saw_add(f, n, voices=3, det=9, fc=fc, order=2, spread=0.5, seed=seed, kmax=36)
    return y * env_adsr(n, 0.006, 0.07, 0.45, rel, dur) * vel


def low_bass(m, dur, vel=1.0, seed=0):
    """driving orchestral low strings + sub."""
    f = hz(m)
    rel = 0.06
    n = int((dur + rel) * SR)
    t = np.arange(n) / SR
    fc = f * (2.5 + 4 * vel * np.exp(-t / 0.06)) + 200
    y = saw_add(f, n, voices=2, det=6, fc=fc, order=2, seed=seed, kmax=30).mean(axis=0)
    y += 0.3 * np.sin(2 * np.pi * f * t)
    return y * env_adsr(n, 0.005, 0.12, 0.6, rel, dur) * vel


# ---- percussion ----
def taiko(vel=1.0, seed=0, pitch=1.0):
    n = int(1.3 * SR)
    t = np.arange(n) / SR
    f = (60 + 75 * np.exp(-t / 0.035)) * pitch
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.32 + 0.1 * vel))
    f2 = (165 + 60 * np.exp(-t / 0.02)) * pitch
    body2 = 0.35 * np.sin(2 * np.pi * np.cumsum(f2) / SR) * np.exp(-t / 0.07)
    nz = noise(n, seed)
    thud = filt(nz, 'lowpass', 1100) * np.exp(-t / 0.035) * 0.9
    click = filt(nz, 'highpass', 2500) * np.exp(-t / 0.004) * 0.25 * vel
    y = body + body2 + thud + click
    y = np.tanh(1.3 * y) / np.tanh(1.3)
    return y * vel


def timpani(m, vel=1.0, seed=0, length=2.2):
    f = hz(m)
    n = int(length * SR)
    t = np.arange(n) / SR
    ratios = [1, 1.504, 1.742, 2.0, 2.245, 2.494, 2.8]
    amps = [1, .55, .3, .35, .18, .12, .06]
    decs = [1.5, .9, .7, .6, .45, .35, .25]
    r = np.random.default_rng(seed)
    gl = 1 + 0.015 * np.exp(-t / 0.06)
    y = np.zeros(n)
    for ra, a, d in zip(ratios, amps, decs):
        y += a * np.sin(2 * np.pi * np.cumsum(f * ra * gl) / SR + r.uniform(0, 6.28)) * np.exp(-t / d)
    y += filt(noise(n, seed), 'lowpass', 700) * np.exp(-t / 0.02) * 0.8
    y *= np.minimum(t / 0.002, 1)
    return y / 2.0 * vel


def snare(vel=1.0, seed=0):
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    tone = 0.55 * np.sin(2 * np.pi * np.cumsum(195 * (1 + 0.15 * np.exp(-t / 0.01))) / SR) * np.exp(-t / 0.05)
    tone += 0.25 * np.sin(2 * np.pi * 335 * t) * np.exp(-t / 0.035)
    nz = filt(noise(n, seed), 'bandpass', (1400, 9500)) * np.exp(-t / (0.10 + 0.07 * vel)) * 1.4
    y = (tone + nz) * np.minimum(t / 0.0008, 1)
    return y * vel / 1.3


def hat(vel=1.0, seed=0, open_=False):
    n = int((0.35 if open_ else 0.12) * SR)
    t = np.arange(n) / SR
    y = filt(noise(n, seed), 'highpass', 7000) * np.exp(-t / (0.12 if open_ else 0.028))
    return y * vel


def shaker(vel=1.0, seed=0):
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    y = filt(noise(n, seed), 'bandpass', (4500, 12000))
    e = np.minimum(t / 0.018, 1) * np.exp(-np.maximum(t - 0.018, 0) / 0.035)
    return y * e * vel


def crash(vel=1.0, seed=0):
    n = int(3.2 * SR)
    t = np.arange(n) / SR
    nz = noise(n, seed)
    y = filt(nz, 'highpass', 3200) * (0.7 * np.exp(-t / 1.1) + 0.3 * np.exp(-t / 0.15))
    r = np.random.default_rng(seed)
    for _ in range(14):
        fr = r.uniform(3000, 9000)
        y += 0.05 * np.sin(2 * np.pi * fr * t + r.uniform(0, 6.28)) * np.exp(-t / r.uniform(0.4, 1.4))
    y *= np.minimum(t / 0.003, 1)
    return y * vel / 1.5


def doum(vel=1.0, seed=0):
    n = int(0.6 * SR)
    t = np.arange(n) / SR
    f = 92 + 55 * np.exp(-t / 0.022)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.28)
    y += 0.25 * np.sin(2 * np.pi * np.cumsum(f * 2.3) / SR) * np.exp(-t / 0.06)
    y += filt(noise(n, seed), 'lowpass', 1500) * np.exp(-t / 0.01) * 0.4
    return y * vel


def tek(vel=1.0, seed=0):
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for ra, a, d in [(1, 1, .07), (1.59, .5, .05), (2.31, .3, .03)]:
        y += a * np.sin(2 * np.pi * 480 * ra * t) * np.exp(-t / d)
    y += filt(noise(n, seed), 'bandpass', (1800, 6000)) * np.exp(-t / 0.03) * 1.2
    return y * vel / 1.6


def woodblock(vel=1.0, seed=0, f=1650):
    n = int(0.15 * SR)
    t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.025) + 0.4 * np.sin(2 * np.pi * f * 2.7 * t) * np.exp(-t / 0.01)
    y += filt(noise(n, seed), 'bandpass', (1500, 5000)) * np.exp(-t / 0.004) * 0.5
    return y * vel


def glock(m, dur=1.5, vel=1.0, seed=0):
    f = hz(m)
    n = int(max(dur, 1.6) * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for ra, a, d in [(1, 1, 1.6), (2.756, .35, .5), (5.404, .12, .18), (8.933, .05, .07)]:
        if f * ra < 18000:
            y += a * np.sin(2 * np.pi * f * ra * t) * np.exp(-t / d)
    y *= np.minimum(t / 0.001, 1)
    return y * vel / 1.3


def riser(n, seed=0):
    t = np.arange(n) / SR
    x = noise(n, seed)
    T = n / SR
    # sweep: blend of increasingly bright bands
    lo = filt(x, 'bandpass', (300, 1500))
    hi = filt(x, 'bandpass', (2000, 9000))
    p = t / T
    y = lo * (1 - p) + hi * p
    y = y * p ** 2.2
    k = int(0.03 * SR)
    y[-k:] *= np.linspace(1, 0, k)
    return y


# --------------------------------------------------------------------------
# reverb / chorus / mixing
# --------------------------------------------------------------------------
def make_ir(rt60=2.0, predelay=0.018, bright=0.5, seed=7):
    L = int(rt60 * 1.15 * SR)
    t = np.arange(L) / SR
    irs = []
    for ch in range(2):
        r = np.random.default_rng(seed + ch * 31)
        nz = r.standard_normal(L)
        lo = filt(nz, 'lowpass', 2800)
        hi = nz - lo
        ir = lo * np.exp(-6.9 * t / rt60) + bright * hi * np.exp(-6.9 * t / (rt60 * 0.4))
        ir *= 1 - np.exp(-t / 0.015)
        for k in range(10):  # sparse early reflections
            d = int(r.uniform(0.004, 0.07) * SR)
            ir[d] += r.choice([-1, 1]) * 0.55 * (0.82 ** k) * np.sqrt(np.mean(ir[:4000] ** 2)) * 6
        ir = np.concatenate([np.zeros(int(predelay * SR)), ir])
        irs.append(ir / np.sqrt(np.sum(ir ** 2)))
    return irs


def chorus(x, base_ms=13.0, depth_ms=2.2, rates=(0.29, 0.41), mix=0.45):
    n = x.shape[1]
    t = np.arange(n) / SR
    out = np.empty_like(x)
    for ch in range(2):
        d = (base_ms + depth_ms * np.sin(2 * np.pi * rates[ch] * t + ch * 1.7)) * SR / 1000
        idx = np.arange(n) - d
        i0 = np.floor(idx).astype(np.int64)
        fr = idx - i0
        i0c = np.clip(i0, 0, n - 2)
        y = x[1 - ch][i0c] * (1 - fr) + x[1 - ch][i0c + 1] * fr  # cross-fed for width
        y[i0 < 0] = 0
        out[ch] = x[ch] * (1 - 0.3 * mix) + y * mix
    return out


def active_rms(x):
    m = x.mean(axis=0) if x.ndim == 2 else x
    w = 2048
    k = len(m) // w
    e = (m[:k * w].reshape(k, w) ** 2).mean(axis=1)
    if e.max() <= 0:
        return 0.0
    e = e[e > e.max() * 1e-4]
    return float(np.sqrt(e.mean()))


class Song:
    def __init__(self, name, bpm, bars, loop=True, tail_s=4.0, bpb=4, seed=1):
        self.name, self.bpm, self.bars, self.loop, self.bpb = name, bpm, bars, loop, bpb
        self.spb = 60.0 / bpm * SR
        self.L = int(round(bars * bpb * self.spb))
        self.N = self.L + int(tail_s * SR)
        self.tr, self.cfg = {}, {}
        self.rng = np.random.default_rng(seed)
        self.seed = seed * 1000

    def track(self, name, level=-20, send=0.2, pan=0.0, chorus=False, hp=None, lp=None, eq=None):
        self.tr[name] = np.zeros((2, self.N))
        self.cfg[name] = dict(level=level, send=send, chorus=chorus, hp=hp, lp=lp, eq=eq)

    def sec(self, beats):
        return beats * self.spb / SR

    def nseed(self):
        self.seed += 1
        return self.seed

    def add(self, name, sig, beat, pan=0.0, gain=1.0, jitter_ms=0.0):
        st = int(round(beat * self.spb))
        if jitter_ms:
            st += int(self.rng.uniform(0, jitter_ms) * SR / 1000)
        if st >= self.N:
            return
        buf = self.tr[name]
        if sig.ndim == 1:
            gl, gr = pan_gains(pan)
            sig = np.vstack([sig * gl, sig * gr])
        else:
            sig = sig * np.array([[1 - max(0, pan)], [1 + min(0, pan)]])
        n = min(sig.shape[1], self.N - st)
        buf[:, st:st + n] += sig[:, :n] * gain

    def notes(self, name, events, fn, pan=0.0, gain=1.0, legato=1.0, transpose=0,
              vel=1.0, jitter_ms=4.0, offset=0.0, **kw):
        for b, d, m in events:
            if m is None:
                continue
            v = vel * self.rng.uniform(0.92, 1.0)
            sig = fn(m + transpose, self.sec(d) * legato, v, seed=self.nseed(), **kw)
            self.add(name, sig, b + offset, pan, gain, jitter_ms)

    def mix(self, rt60=2.0, wet=0.35, bright=0.5, report=True):
        dry = np.zeros((2, self.N))
        snd = np.zeros((2, self.N))
        for name, x in self.tr.items():
            c = self.cfg[name]
            if c['hp']:
                x = filt(x, 'highpass', c['hp'])
            if c['lp']:
                x = filt(x, 'lowpass', c['lp'])
            if c['eq']:  # (centre, gain_lin, (lo,hi)) resonant body boost
                lo, hi, g = c['eq']
                x = x + g * filt(x, 'bandpass', (lo, hi))
            if c['chorus']:
                x = chorus(x)
            r = active_rms(x)
            if r == 0:
                continue
            g = 10 ** (c['level'] / 20) / r
            x = x * g
            if report:
                print(f'    {name:12s} level {c["level"]:6.1f} dB  peak {20*np.log10(np.abs(x).max()+1e-12):6.1f} dBFS')
            dry += x
            snd += x * c['send']
        ir = make_ir(rt60, bright=bright, seed=sum(map(ord, self.name)))
        wetsig = np.vstack([fftconvolve(snd[0], ir[0])[:self.N], fftconvolve(snd[1], ir[1])[:self.N]])
        wetsig = filt(wetsig, 'highpass', 180)
        out = dry + wet * wetsig
        if self.loop:  # fold the tail back over the start -> seamless loop
            y = out[:, :self.L].copy()
            rem = out[:, self.L:]
            while rem.shape[1]:
                k = min(self.L, rem.shape[1])
                y[:, :k] += rem[:, :k]
                rem = rem[:, k:]
            return y
        return out


# --------------------------------------------------------------------------
# mastering
# --------------------------------------------------------------------------
def k_weight(x):
    G, Q, fc = 3.999843853973347, 0.7071752369554196, 1681.974450955533
    K = np.tan(np.pi * fc / SR)
    Vh = 10 ** (G / 20)
    Vb = Vh ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    b1 = [(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0]
    a1 = [1, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    fc2, Q2 = 38.13547087602444, 0.5003270373238773
    K = np.tan(np.pi * fc2 / SR)
    d = 1 + K / Q2 + K * K
    a2 = [1, 2 * (K * K - 1) / d, (1 - K / Q2 + K * K) / d]
    return lfilter([1, -2, 1], a2, lfilter(b1, a1, x, axis=-1), axis=-1)


def lufs(x):
    y = k_weight(x)
    w, h = int(0.4 * SR), int(0.1 * SR)
    if y.shape[1] < w:
        w = h = y.shape[1]
    starts = range(0, y.shape[1] - w + 1, h)
    z = np.array([np.sum(np.mean(y[:, s:s + w] ** 2, axis=1)) for s in starts])
    l = -0.691 + 10 * np.log10(z + 1e-15)
    z = z[l > -70]
    rel = -0.691 + 10 * np.log10(z.mean()) - 10
    l = -0.691 + 10 * np.log10(z + 1e-15)
    return -0.691 + 10 * np.log10(z[l > rel].mean())


def limiter(x, ceiling_db=-1.0, look_ms=4.0, release_ms=180.0):
    c = 10 ** (ceiling_db / 20)
    peak = np.abs(x).max(axis=0)
    gt = np.minimum(1.0, c / np.maximum(peak, 1e-9))
    la = max(1, int(look_ms * SR / 1000))
    gm = minimum_filter1d(gt, size=2 * la + 1, mode='nearest')
    ga = uniform_filter1d(gm, size=la, mode='nearest')
    B = 64
    nb = len(ga) // B + 1
    pad = np.concatenate([ga, np.ones(nb * B - len(ga))])
    blk = pad.reshape(nb, B).min(axis=1)
    rel = 1 - np.exp(-B / (release_ms * SR / 1000))
    g = np.empty(nb)
    cur = 1.0
    for i in range(nb):
        cur = min(blk[i], cur + (1 - cur) * rel)
        g[i] = cur
    centers = np.arange(nb) * B + B / 2
    gi = np.interp(np.arange(len(ga)), centers, g)
    gfin = np.minimum(gi, ga)
    gfin = np.minimum(gfin, gt)  # safety: never exceed ceiling
    return x * gfin, float(20 * np.log10(gfin.min()))


def master(x, loop, target=-16.0, ceiling=-1.4):
    P = SR * 2
    if loop:
        x = np.concatenate([x[:, -P:], x, x[:, :P]], axis=1)
    x = filt(x, 'highpass', 28)
    # gentle high-frequency smoothing
    x = 0.85 * x + 0.15 * filt(x, 'lowpass', 9000)
    core = (slice(None), slice(P, -P)) if loop else (slice(None), slice(None))
    g = 10 ** ((target - lufs(x[core])) / 20)
    for _ in range(3):
        y, gr = limiter(x * g, ceiling)
        err = target - lufs(y[core])
        if abs(err) < 0.1:
            break
        g *= 10 ** (err / 20)
    y = y[core]
    pk = np.abs(y).max()
    # peak-normalise to the ceiling (-1.4 dBFS before Vorbis, which overshoots by ~0.5 dB), but never
    # push the loudness more than 0.6 dB above the target
    y *= min(10 ** (ceiling / 20) / pk, 10 ** (0.6 / 20))
    return y, gr


def write_wav(path, x):
    r = np.random.default_rng(5)
    d = (r.uniform(-0.5, 0.5, x.shape) + r.uniform(-0.5, 0.5, x.shape))
    pcm = np.clip(np.round(x * 32767 + d), -32768, 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.T.tobytes())


def read_wav(path):
    with wave.open(path, 'rb') as w:
        n, ch = w.getnframes(), w.getnchannels()
        a = np.frombuffer(w.readframes(n), dtype='<i2').astype(np.float64) / 32768
    return a.reshape(-1, ch).T


# --------------------------------------------------------------------------
# TRACK 1: LOBBY  (D major, 100 BPM, 32 bars = 76.80 s)
# --------------------------------------------------------------------------
def build_lobby():
    S = Song('lobby', 100, 32, loop=True, tail_s=5.0, seed=11)
    bars = ['D', 'Bm', 'G', 'A', 'D', 'Bm', 'Em7 A7', 'D',
            'G', 'D/F#', 'Em', 'A', 'Bm', 'C', 'G', 'A7',
            'D', 'Bm', 'G', 'A', 'D', 'Bm', 'Em7 A7', 'D',
            'Em', 'F#m', 'G', 'A', 'Bm', 'G', 'Em7', 'Asus4 A']
    TL = timeline(bars)
    DMAJ = [2, 4, 6, 7, 9, 11, 1]
    S.track('flute', level=-15, send=0.30, pan=0.05)
    S.track('clar', level=-20.5, send=0.30)
    S.track('harp', level=-17, send=0.35)
    S.track('lute', level=-18.5, send=0.22, eq=(140, 420, 0.6))
    S.track('pad', level=-23, send=0.40, chorus=True, lp=5000)
    S.track('bass', level=-18.5, send=0.10, hp=35)
    S.track('doum', level=-21, send=0.12)
    S.track('tek', level=-25, send=0.18)
    S.track('shaker', level=-32, send=0.15)
    swing = 0.07

    A = ('F#5:1.5 E5:1/2 D5:1 A4:1  B4:1 D5:1/2 E5:1/2 F#5:2  G5:1.5 F#5:1/2 E5:1 D5:1  '
         'E5:2 C#5:1 A4:1  F#5:1.5 E5:1/2 D5:1 F#5:1  A5:1.5 G5:1/2 F#5:1 D5:1  '
         'E5:1 G5:1 C#5:1.5 E5:1/2  D5:3 r:1')
    B = ('B4:1 D5:1 G5:2  F#5:1 E5:1/2 D5:1/2 A4:2  B4:1 E5:1 G5:1.5 F#5:1/2  '
         'E5:2 r:1/2 A4:1/2 C#5:1/2 E5:1/2  F#5:1.5 D5:1/2 B4:2  C5:1 E5:1 G5:1.5 E5:1/2  '
         'D5:1.5 B4:1/2 G4:1 B4:1  A4:1 C#5:1 E5:1 G5:1')
    C = ('G5:1/2 F#5:1/2 E5:1/2 B4:1/2 E5:1 G5:1  A5:1/2 G5:1/2 F#5:1/2 C#5:1/2 F#5:1 A5:1  '
         'B5:1 A5:1/2 G5:1/2 D5:1 G5:1  A5:1 G5:1/2 F#5:1/2 E5:2  '
         'D5:1/2 E5:1/2 F#5:1/2 D5:1/2 B4:2  G5:1/2 F#5:1/2 E5:1/2 D5:1/2 B4:2  '
         'E5:1 G5:1 B5:1 A5:1  E5:2 C#5:1 r:1')
    evA, _ = mel(A, 0)
    evB, _ = mel(B, 32)
    evA2, _ = mel(A, 64)
    evC, _ = mel(C, 96)
    pick, _ = mel('r:3 D5:1/2 E5:1/2', 124)

    def sw(ev):  # light swing on off-beat eighths
        return [(b + (swing if abs((b * 2) % 2 - 1) < 1e-6 else 0), d, m) for b, d, m in ev]

    S.notes('flute', sw(evA + evB + evA2 + pick), flute, legato=1.02, pan=0.05)
    harm = [(b, d, diatonic_shift(m, DMAJ, -2) if m else None) for b, d, m in evA2]
    S.notes('clar', sw(harm), clarinet, legato=1.0, pan=-0.3, vel=0.9)
    clar_c, _ = mel('G4:4 A4:4 B4:4 C#5:4 D5:4 B4:4 B4:4 D5:2 C#5:2', 96)
    S.notes('clar', clar_c, clarinet, legato=0.97, pan=-0.3, vel=0.8)
    S.notes('harp', sw(evC), harp, legato=1.6, pan=0.35)

    # harp sparkle arpeggios in A' + glissando into A'
    for bar in range(16, 24):
        ch = chord_at(TL, bar * 4)
        tones = sorted(in_range(pc, 74, 85) for pc in ch['pcs'][:3])
        for j, m in enumerate(tones + [tones[0] + 12]):
            S.add('harp', harp(m, 1.2, 0.45 + 0.08 * j, seed=S.nseed()), bar * 4 + j * 0.25, 0.4)
    for j in range(12):
        m = diatonic_shift(midi('A4'), DMAJ, j)
        S.add('harp', harp(m, 0.6, 0.35 + 0.04 * j, seed=S.nseed()), 15 * 4 + 2.5 + j * (1.5 / 12), 0.35)

    # lute arpeggios
    pats = {0: [0, 1, 2, 3, 4, 3, 2, 1], 1: [0, 2, 1, 3, 2, 4, 3, 2],
            2: [0, 1, 2, 3, 4, 3, 2, 1], 3: [0, 2, 4, 2, 3, 2, 1, 2]}
    for bar in range(32):
        pat = pats[bar // 8]
        for j in range(8):
            beat = bar * 4 + j * 0.5
            ch = chord_at(TL, beat)
            r = in_range(ch['root'], 45, 56)
            iv = ch['ivs']
            tones = [in_range(ch['bass'], 45, 56) if j == 0 else r, r + iv[2], r + 12, r + 12 + iv[1],
                     r + 12 + (iv[3] if len(iv) > 3 else iv[2])]
            v = 0.95 if j == 0 else 0.8 if j == 4 else S.rng.uniform(0.55, 0.7)
            if bar < 2 and j % 2:
                continue
            S.add('lute', lute(tones[pat[j]], S.sec(1.1), v, seed=S.nseed()),
                  beat + (swing if j % 2 else 0), -0.35, jitter_ms=5)

    # strings pad (voice-led)
    chords = [c for _, _, c in TL]
    V3 = voice_lead(chords, 55, 71, 3)
    V4 = voice_lead(chords, 52, 72, 4)
    for i, (b, d, c) in enumerate(TL):
        sec = int(b // 32)
        voic = V3[i] if sec == 0 else V4[i]
        g = 0.75 if sec == 0 else 1.0
        for m in voic:
            S.add('pad', strings(m, S.sec(d) + 0.05, g, seed=S.nseed(), attack=0.45, rel=0.9, fc=1800), b, 0)

    # bass
    for i, (b, d, c) in enumerate(TL):
        bar = int(b // 4)
        r = in_range(c['bass'], 38, 49)
        if d >= 4:
            S.add('bass', pluck_bass(r, S.sec(1.4), 0.95, seed=S.nseed()), b, 0)
            if bar >= 2:
                fifth = in_range((c['root'] + 7) % 12, 38, 50)
                S.add('bass', pluck_bass(fifth, S.sec(0.9), 0.75, seed=S.nseed()), b + 2, 0)
                S.add('bass', pluck_bass(r, S.sec(0.45), 0.6, seed=S.nseed()), b + 3 + swing * 0, 0)
                S.add('bass', pluck_bass(r + 12 if r < 44 else r, S.sec(0.4), 0.5, seed=S.nseed()), b + 3.5 + swing, 0)
        else:
            S.add('bass', pluck_bass(r, S.sec(d * 0.9), 0.9, seed=S.nseed()), b, 0)

    # hand drum & shaker
    for bar in range(32):
        b0 = bar * 4
        light = bar < 4 or 28 <= bar < 31
        S.add('doum', doum(1.0, S.nseed()), b0, 0)
        if not light:
            S.add('doum', doum(0.55, S.nseed()), b0 + 2.5 + swing, 0)
        for bt, v in [(1, .75), (3, .8), (1.5, .3), (3.5, .4), (2, .3)]:
            if light and v < 0.5:
                continue
            S.add('tek', tek(v * S.rng.uniform(.9, 1.05), S.nseed()), b0 + bt + (swing if bt % 1 else 0), 0.2,
                  jitter_ms=4)
        if bar % 8 == 7:
            for k in range(4):
                S.add('tek', tek(0.35 + 0.15 * k, S.nseed()), b0 + 3 + k * 0.25, 0.2)
        if bar >= 8:
            for j in range(8):
                S.add('shaker', shaker(0.5 if j % 2 else 0.32, S.nseed()), b0 + j * 0.5 + (swing if j % 2 else 0),
                      0.5, jitter_ms=5)
    return S, dict(rt60=2.3, wet=0.38, bright=0.45)


# --------------------------------------------------------------------------
# TRACK 2: BATTLE  (F major, 135 BPM, 36 bars = 64.00 s)
# --------------------------------------------------------------------------
def build_battle():
    S = Song('battle', 135, 36, loop=True, tail_s=4.0, seed=22)
    bars = ['F', 'Eb', 'Bb', 'C',
            'F', 'C/E', 'Dm', 'Bb', 'F/A', 'Bb', 'Gm7', 'C',
            'F', 'C/E', 'Dm', 'Bb', 'Gm', 'Bb C', 'F', 'F',
            'Dm', 'Bb', 'F', 'C', 'Dm', 'Bb', 'Gm', 'Csus4 C',
            'Bb', 'C', 'Am', 'Dm', 'Bb', 'C', 'Db', 'C']
    TL = timeline(bars)
    sect = lambda bar: 'I' if bar < 4 else 'A' if bar < 12 else 'A2' if bar < 20 else 'B' if bar < 28 else 'R'
    S.track('lead', level=-14, send=0.25)
    S.track('leaddbl', level=-21, send=0.3, chorus=True)
    S.track('ostin', level=-20, send=0.18)
    S.track('stab', level=-17.5, send=0.22)
    S.track('bpad', level=-22, send=0.3)
    S.track('lowbr', level=-21, send=0.15)
    S.track('pad', level=-23.5, send=0.4, chorus=True, lp=7000)
    S.track('bass', level=-18, send=0.06, hp=40)
    S.track('taiko', level=-17, send=0.18, hp=45)
    S.track('snare', level=-23.5, send=0.2)
    S.track('hats', level=-30, send=0.1)
    S.track('crash', level=-25, send=0.15)
    S.track('timp', level=-19, send=0.25)

    A = ('C5:3/4 F5:1/4 F5:1 G5:1/2 A5:1/2 C6:1  G5:1.5 F5:1/2 E5:1 C5:1  '
         'D5:3/4 F5:1/4 A5:1 G5:1/2 F5:1/2 E5:1/2 D5:1/2  F5:3 r:1/2 C5:1/2  '
         'C5:3/4 F5:1/4 F5:1 G5:1/2 A5:1/2 Bb5:1  D6:1.5 C6:1/2 Bb5:1 F5:1  '
         'Bb5:1.5 A5:1/2 G5:1 F5:1  E5:1 G5:1 C6:2')
    A2 = ('C5:3/4 F5:1/4 F5:1 G5:1/2 A5:1/2 C6:1  G5:1.5 F5:1/2 E5:1 C5:1  '
          'D5:3/4 F5:1/4 A5:1 G5:1/2 F5:1/2 E5:1/2 D5:1/2  F5:3 r:1/2 C5:1/2  '
          'Bb5:3/4 A5:1/4 G5:1 D5:1 G5:1  F5:1 D5:1 E5:1 G5:1  C6:1.5 A5:1/2 F5:2  '
          'r:2 F5:1/2 G5:1/2 A5:1/2 C6:1/2')
    B = ('D6:1.5 C6:1/2 A5:2  Bb5:1 A5:1/2 G5:1/2 F5:2  A5:1.5 G5:1/2 F5:1 C5:1  E5:2 G5:2  '
         'F5:1.5 E5:1/2 D5:1 A5:1  D6:2 Bb5:1 F5:1  G5:1 A5:1 Bb5:1 D6:1  C6:3 r:1')
    R1 = ('F4:3/4 Bb4:1/4 Bb4:1 C5:1/2 D5:1/2 F5:1  E5:1.5 D5:1/2 C5:1 G4:1  '
          'A4:3/4 C5:1/4 E5:1 D5:1/2 C5:1/2 A4:1  D5:3 r:1')
    R2 = ('F5:3/4 Bb5:1/4 Bb5:1 A5:1/2 G5:1/2 F5:1  G5:1.5 F5:1/2 E5:1 C5:1  '
          'Db5:1 F5:1 Ab5:1 F5:1  E5:1 G5:1 C6:2')
    evA, _ = mel(A, 16)
    evA2, _ = mel(A2, 48)
    evB, _ = mel(B, 80)
    evR1, _ = mel(R1, 112)
    evR2, _ = mel(R2, 128)
    S.notes('lead', evA + evA2 + evB + evR2, brass, legato=0.96, vel=1.0, voices=2)
    S.notes('lead', evR1, brass, legato=0.96, vel=0.9, dark=0.6, voices=3)
    S.notes('leaddbl', evA2 + evB, strings, transpose=-12, legato=1.0, vel=1.0, attack=0.05, rel=0.25, fc=3500)
    S.notes('leaddbl', evR1 + evR2, strings, transpose=0, legato=1.0, vel=0.8, attack=0.06, rel=0.25, fc=3000)
    S.notes('leaddbl', evA, glock, transpose=12, vel=0.35, jitter_ms=0)

    chords = [c for _, _, c in TL]
    V4 = voice_lead(chords, 53, 70, 4)
    VH = voice_lead(chords, 64, 81, 3)
    for i, (b, d, c) in enumerate(TL):
        bar = int(b // 4)
        s = sect(bar)
        lowr = in_range(c['bass'], 41, 52)
        if s in ('I', 'B', 'R'):
            hits = [(0, 0.55, 1.0), (1.5, 0.55, 0.8), (3, 0.8, 0.9)]
            for hb, hd, hv in hits:
                if hb >= d:
                    continue
                for j, m in enumerate(V4[i]):
                    S.add('stab', brass(m, S.sec(min(hd, d - hb)), hv, seed=S.nseed(), stab=True),
                          b + hb, -0.45 + 0.3 * j, jitter_ms=3)
                S.add('lowbr', brass(lowr, S.sec(min(hd, d - hb)), hv, seed=S.nseed(), stab=True, voices=2),
                      b + hb, 0)
        else:
            for j, m in enumerate(V4[i]):
                S.add('bpad', brass(m, S.sec(d - 0.1), 0.55, seed=S.nseed()), b, -0.45 + 0.3 * j)
            S.add('stab', np.vstack([brass(m, S.sec(0.5), 0.9, seed=S.nseed(), stab=True)[0] for m in V4[i]]).sum(0),
                  b, 0)
        if s in ('A2', 'B', 'R'):
            for m in VH[i]:
                S.add('pad', strings(m, S.sec(d) + 0.05, 0.8, seed=S.nseed(), attack=0.25, rel=0.7), b, 0)

    # string ostinato + bass 8ths
    for bar in range(36):
        for j in range(16):
            beat = bar * 4 + j * 0.25
            c = chord_at(TL, beat)
            r = in_range(c['root'], 50, 61)
            tones = [r, r + c['ivs'][2], r + 12, r + 12 + c['ivs'][1]]
            pat = [0, 2, 1, 2, 0, 2, 1, 3, 0, 2, 1, 2, 0, 3, 1, 2]
            v = 0.95 if j % 4 == 0 else 0.6 + 0.1 * (j % 2 == 0)
            S.add('ostin', spiccato(tones[pat[j]], S.sec(0.22), v, seed=S.nseed()), beat, -0.3, jitter_ms=3)
        for j in range(8):
            beat = bar * 4 + j * 0.5
            c = chord_at(TL, beat)
            r = in_range(c['bass'], 36, 47)
            m = r + 12 if j in (2, 5) else r
            v = 1.0 if j in (0, 3, 6) else 0.7
            S.add('bass', low_bass(m, S.sec(0.42), v, seed=S.nseed()), beat, 0)

    # percussion
    T_A = [(0, 1), (1.5, .7), (3, .75)]
    T_D = [(0, 1), (1.5, .8), (2, .55), (3, .9), (3.5, .6)]
    T_F = [(0, 1), (1.5, .8), (2, .6), (3, .8), (3.25, .6), (3.5, .75), (3.75, .9)]
    for bar in range(36):
        b0 = bar * 4
        s = sect(bar)
        pat = T_F if bar % 4 == 3 else (T_A if s in ('A', 'A2') else T_D)
        for bt, v in pat:
            S.add('taiko', taiko(v, S.nseed(), pitch=1.0 if v > .7 else 1.15), b0 + bt, 0, jitter_ms=2)
        if s in ('A', 'A2', 'B'):
            for bt, v in [(1, .85), (3, .9), (2.75, .2), (3.75, .25), (1.75, .15)]:
                S.add('snare', snare(v * S.rng.uniform(.9, 1.0), S.nseed()), b0 + bt, 0.1, jitter_ms=3)
            for j in range(8):
                S.add('hats', hat(0.6 if j % 2 else 0.35, S.nseed()), b0 + j * 0.5, 0.35, jitter_ms=3)
        if s == 'R':
            march = [(0, .55), (0.5, .3), (1, .9), (1.75, .4), (2, .5), (2.5, .3), (3, .9), (3.5, .45)]
            if bar >= 34:
                march = [(k * 0.25, 0.3 + 0.7 * ((bar - 34) * 16 + k) / 31) for k in range(16)]
            for bt, v in march:
                S.add('snare', snare(v, S.nseed()), b0 + bt, 0.1, jitter_ms=2)
            for j in range(16):
                S.add('hats', hat(0.45 if j % 4 == 2 else 0.25, S.nseed()), b0 + j * 0.25, 0.35, jitter_ms=2)
        if bar == 3:
            for k in range(16):
                S.add('snare', snare(0.15 + 0.85 * k / 15, S.nseed()), b0 + k * 0.25, 0.1)
        if bar in (0, 4, 12, 20, 28, 32):
            S.add('crash', crash(1.0, S.nseed()), b0, -0.35 if bar % 8 else 0.35)
        c = chord_at(TL, b0)
        tm = in_range(c['root'], 38, 50)
        if s in ('I', 'B') or bar % 4 == 0:
            S.add('timp', timpani(tm, 0.9, S.nseed()), b0, -0.2)
        if s == 'B':
            S.add('timp', timpani(tm, 0.6, S.nseed()), b0 + 2, -0.2)
        if bar in (3, 35, 19):  # timpani rolls into the next section / the loop start
            nm = in_range(chord_at(TL, (b0 + 4) % (36 * 4))['root'], 38, 50)
            for k in range(24):
                S.add('timp', timpani(nm, 0.15 + 0.6 * k / 23, S.nseed(), length=0.8),
                      b0 + 2 + k / 12, -0.2)
    return S, dict(rt60=2.0, wet=0.3, bright=0.5)


# --------------------------------------------------------------------------
# TRACK 3: OVERTIME  (D minor, 150 BPM, 32 bars = 51.20 s)
# --------------------------------------------------------------------------
def build_overtime():
    S = Song('overtime', 150, 32, loop=True, tail_s=4.0, seed=33)
    bars = ['Dm', 'Bb', 'Gm', 'A',
            'Dm', 'Bb', 'Gm', 'A', 'Dm', 'F', 'Gm', 'A',
            'Dm', 'C', 'Bb', 'A', 'Dm', 'C', 'Bb A', 'Dm',
            'Gm', 'Dm', 'Bb', 'A', 'Gm', 'Dm', 'Eb', 'A',
            'Dm', 'Bb', 'Gm', 'A']
    TL = timeline(bars)
    sect = lambda bar: 'I' if bar < 4 else 'A' if bar < 12 else 'A2' if bar < 20 else 'B' if bar < 28 else 'R'
    S.track('lead', level=-14.5, send=0.25)
    S.track('leaddbl', level=-21, send=0.3, chorus=True)
    S.track('ostin', level=-19.5, send=0.16)
    S.track('stab', level=-17.5, send=0.2)
    S.track('lowbr', level=-21, send=0.12)
    S.track('pad', level=-24, send=0.4, chorus=True, lp=7000)
    S.track('drone', level=-25, send=0.3)
    S.track('bass', level=-18, send=0.05, hp=40)
    S.track('taiko', level=-16.5, send=0.16, hp=45)
    S.track('snare', level=-23.5, send=0.18)
    S.track('hats', level=-29, send=0.08)
    S.track('tick', level=-29, send=0.12)
    S.track('crash', level=-25, send=0.15)
    S.track('timp', level=-21, send=0.22)
    S.track('riser', level=-28, send=0.3)

    A = ('A4:3/4 D5:1/4 D5:1 E5:1/2 F5:1/2 A5:1  Bb5:1.5 A5:1/2 F5:1 D5:1  '
         'G5:3/4 Bb5:1/4 D6:1 C6:1/2 Bb5:1/2 A5:1/2 G5:1/2  A5:2 C#5:1 E5:1  '
         'A4:3/4 D5:1/4 D5:1 E5:1/2 F5:1/2 A5:1  C6:1.5 A5:1/2 F5:1 C5:1  '
         'D5:1 G5:1 Bb5:1 D6:1  C#6:2 A5:1 E5:1')
    A2 = ('F5:3/4 E5:1/4 D5:1 A5:2  G5:3/4 F5:1/4 E5:1 C6:2  Bb5:3/4 A5:1/4 G5:1/2 F5:1/2 D5:1 Bb5:1  '
          'A5:1 G5:1/2 F5:1/2 E5:2  F5:3/4 E5:1/4 D5:1 A5:2  G5:3/4 F5:1/4 E5:1 C6:2  '
          'D6:1 Bb5:1 C#6:1 E6:1  D6:3 r:1')
    B = ('Bb5:2 A5:1 G5:1  A5:2 F5:1 D5:1  D6:1.5 C6:1/2 Bb5:1 F5:1  E5:1 A5:1 C#6:2  '
         'D6:2 Bb5:1 G5:1  F5:1 A5:1 D6:2  Eb6:1.5 D6:1/2 Bb5:1 G5:1  A5:3 r:1')
    evA, _ = mel(A, 16)
    evA2, _ = mel(A2, 48)
    evB, _ = mel(B, 80)
    S.notes('lead', evA + evA2 + evB, brass, legato=0.95, vel=1.0, voices=2)
    S.notes('leaddbl', evA + evA2 + evB, strings, transpose=-12, legato=1.0, attack=0.04, rel=0.2, fc=3500)
    S.notes('leaddbl', evA2, glock, transpose=12, vel=0.3, jitter_ms=0)

    chords = [c for _, _, c in TL]
    V4 = voice_lead(chords, 55, 72, 4)
    VH = voice_lead(chords, 67, 84, 3)
    for i, (b, d, c) in enumerate(TL):
        bar = int(b // 4)
        s = sect(bar)
        lowr = in_range(c['bass'], 38, 49)
        hits = [(0, .45, 1.0), (0.75, .3, .7), (1.5, .45, .85), (2.5, .3, .7), (3, .7, .9)] \
            if s in ('I', 'B', 'R') else [(0, .9, 1.0), (2.5, .4, .7)]
        for hb, hd, hv in hits:
            if hb >= d:
                continue
            for j, m in enumerate(V4[i]):
                S.add('stab', brass(m, S.sec(min(hd, d - hb)), hv, seed=S.nseed(), stab=True),
                      b + hb, -0.45 + 0.3 * j, jitter_ms=3)
            S.add('lowbr', brass(lowr, S.sec(min(hd, d - hb)), hv, seed=S.nseed(), stab=True, voices=2), b + hb, 0)
        if s != 'I':
            for m in VH[i]:
                S.add('pad', strings(m, S.sec(d) + 0.05, 0.8, seed=S.nseed(), attack=0.2, rel=0.6), b, 0)
    # low drone on D in intro / end
    for b0 in (0, 112):
        for m in (midi('D2'), midi('A2')):
            S.add('drone', strings(m, S.sec(16) - 0.3, 1.0, seed=S.nseed(), attack=1.5, rel=0.8, fc=900, voices=4),
                  b0, 0)

    for bar in range(32):
        s = sect(bar)
        for j in range(16):
            beat = bar * 4 + j * 0.25
            c = chord_at(TL, beat)
            r = in_range(c['root'], 57, 68)
            tones = [r, r + c['ivs'][1], r + c['ivs'][2], r + 12]
            pat = [3, 2, 1, 2, 0, 2, 1, 2, 3, 2, 1, 2, 0, 1, 2, 1]
            v = 0.95 if j % 4 == 0 else 0.62
            S.add('ostin', spiccato(tones[pat[j]], S.sec(0.2), v, seed=S.nseed()), beat, -0.3, jitter_ms=2)
        for j in range(8):
            beat = bar * 4 + j * 0.5
            c = chord_at(TL, beat)
            r = in_range(c['bass'], 36, 47)
            m = r + 12 if j % 2 else r
            S.add('bass', low_bass(m, S.sec(0.42), 1.0 if j % 2 == 0 else 0.75, seed=S.nseed()), beat, 0)

    for bar in range(32):
        b0 = bar * 4
        s = sect(bar)
        for j in range(8):
            v = 1.0 if j in (0, 3, 6) else 0.5
            if s == 'I' and j not in (0, 3, 6):
                continue
            S.add('taiko', taiko(v, S.nseed(), pitch=1.0 if v > .7 else 1.2), b0 + j * 0.5, 0, jitter_ms=2)
        if bar % 2 == 1:
            for k in range(4):
                S.add('taiko', taiko(0.5 + 0.12 * k, S.nseed(), pitch=1.3 - 0.08 * k), b0 + 3 + k * 0.25,
                      -0.2 + 0.13 * k)
        if s != 'I':
            for bt, v in [(1, .9), (3, .95), (1.75, .2), (2.5, .2), (3.75, .3)]:
                S.add('snare', snare(v, S.nseed()), b0 + bt, 0.1, jitter_ms=2)
            if bar % 4 == 3:
                for k in range(8):
                    S.add('snare', snare(0.3 + 0.08 * k, S.nseed()), b0 + 2 + k * 0.25, 0.1)
            for j in range(16):
                S.add('hats', hat(0.55 if j % 2 else 0.3, S.nseed(), open_=(j == 14)), b0 + j * 0.25, 0.35,
                      jitter_ms=2)
        if s in ('I', 'R'):
            for j in range(8):
                S.add('tick', woodblock(0.8 if j % 2 == 0 else 0.5, S.nseed(), f=1650 if j % 2 == 0 else 1250),
                      b0 + j * 0.5, 0.45)
            if bar >= 30:
                for k in range(16):
                    S.add('snare', snare(0.2 + 0.8 * ((bar - 30) * 16 + k) / 31, S.nseed()), b0 + k * 0.25, 0.1)
        if bar % 4 == 0:
            S.add('crash', crash(1.0, S.nseed()), b0, -0.35 if bar % 8 else 0.35)
        c = chord_at(TL, b0)
        S.add('timp', timpani(in_range(c['root'], 38, 50), 0.9, S.nseed()), b0, -0.2)
        if bar in (3, 31, 19, 27):
            for k in range(24):
                S.add('timp', timpani(midi('A2'), 0.15 + 0.6 * k / 23, S.nseed(), length=0.7),
                      b0 + 2 + k / 12, -0.2)
    S.add('riser', riser(int(S.sec(8) * SR), seed=4), 30 * 4, 0)
    return S, dict(rt60=1.9, wet=0.3, bright=0.5)


# --------------------------------------------------------------------------
# TRACK 4: VICTORY  (C major fanfare, 120 BPM)
# --------------------------------------------------------------------------
def build_victory():
    S = Song('victory', 120, 2, loop=False, tail_s=2.0, seed=44)
    S.track('lead', level=-13, send=0.3)
    S.track('harm', level=-18, send=0.3)
    S.track('stab', level=-17, send=0.3)
    S.track('pad', level=-21, send=0.45, chorus=True)
    S.track('bass', level=-19, send=0.1)
    S.track('timp', level=-18, send=0.3)
    S.track('snare', level=-21, send=0.25)
    S.track('crash', level=-23, send=0.2)
    S.track('glock', level=-22, send=0.4)
    t3 = '1/3'
    lead, _ = mel(f'G4:{t3} G4:{t3} G4:{t3} C5:1 E5:{t3} E5:{t3} E5:{t3} G5:1 Eb5:1/2 F5:1/2 G5:3', 0)
    S.notes('lead', [(b, d * (0.7 if d < 0.5 else 1), m) for b, d, m in lead], brass, voices=3, jitter_ms=0)
    harm, _ = mel(f'r:1 E4:1 C5:{t3} C5:{t3} C5:{t3} D5:1 C5:1/2 D5:1/2 E5:3', 0)
    S.notes('harm', [(b, d * (0.7 if d < 0.5 else 1), m) for b, d, m in harm], brass, voices=2, jitter_ms=0, vel=0.8)
    prog = [(1, 1, 'C'), (2, 1, 'Am'), (3, 1, 'G'), (4, 0.5, 'Ab'), (4.5, 0.5, 'Bb'), (5, 3, 'C')]
    chs = [chord(c) for _, _, c in prog]
    V = voice_lead(chs, 48, 64, 4)
    for (b, d, _), v, c in zip(prog, V, chs):
        for j, m in enumerate(v):
            S.add('stab', brass(m, S.sec(d * 0.85), 0.9, seed=S.nseed(), stab=d < 2), b, -0.4 + 0.27 * j)
            S.add('pad', strings(m + 12, S.sec(d), 0.8, seed=S.nseed(), attack=0.05, rel=1.2), b, 0)
        bm = in_range(c['root'], 36, 47)
        S.add('bass', low_bass(bm, S.sec(d * 0.9), 1.0, seed=S.nseed()), b, 0)
        S.add('bass', low_bass(bm - 12 if bm - 12 >= 28 else bm, S.sec(d * 0.9), 0.6, seed=S.nseed()), b, 0)
    for k in range(3):
        S.add('snare', snare(0.5 + 0.2 * k, S.nseed()), k / 3, 0.1)
    for k in range(3):
        S.add('snare', snare(0.6, S.nseed()), 2 + k / 3, 0.1)
    S.add('snare', snare(0.9, S.nseed()), 1, 0.1)
    S.add('snare', snare(0.8, S.nseed()), 4, 0.1)
    S.add('snare', snare(0.8, S.nseed()), 4.5, 0.1)
    S.add('timp', timpani(midi('G2'), 0.8, S.nseed()), 0, -0.2)
    S.add('timp', timpani(midi('C2') + 12, 1.0, S.nseed()), 1, -0.2)
    S.add('timp', timpani(midi('G2'), 0.8, S.nseed()), 3, -0.2)
    S.add('timp', timpani(midi('C2') + 12, 1.0, S.nseed(), length=3), 5, -0.2)
    S.add('crash', crash(1.0, S.nseed()), 1, -0.3)
    S.add('crash', crash(1.0, S.nseed()), 5, 0.3)
    for j, n in enumerate(['C6', 'E6', 'G6', 'C7', 'G6', 'C7']):
        S.add('glock', glock(midi(n), 2.0, 0.9 - 0.08 * j, seed=S.nseed()), 5 + j * 0.25, 0.3)
    S.N = int(S.sec(8) * SR + 1.6 * SR)
    for k in S.tr:
        S.tr[k] = S.tr[k][:, :S.N]
    return S, dict(rt60=2.2, wet=0.35, bright=0.5)


# --------------------------------------------------------------------------
# TRACK 5: DEFEAT  (C minor, 96 BPM, descending)
# --------------------------------------------------------------------------
def build_defeat():
    S = Song('defeat', 96, 2, loop=False, tail_s=2.0, seed=55)
    S.track('lead', level=-15, send=0.4)
    S.track('flute', level=-21, send=0.45)
    S.track('pad', level=-19, send=0.5, chorus=True, lp=4000)
    S.track('bass', level=-20, send=0.2)
    S.track('harp', level=-21, send=0.45)
    S.track('timp', level=-22, send=0.3)
    lead, _ = mel('Eb5:1 D5:1 C5:1.1 B4:1.2 C5:1.7', 0)
    S.notes('lead', lead, brass, legato=0.98, vel=0.6, dark=0.9, voices=3, jitter_ms=0)
    S.notes('flute', lead, flute, transpose=12, legato=0.98, vel=0.7, jitter_ms=0)
    prog = [(0, 1, 'Cm', 'C3'), (1, 1, 'Gm/Bb', 'Bb2'), (2, 1.1, 'Ab', 'Ab2'), (3.1, 1.2, 'G', 'G2'),
            (4.3, 1.7, 'Cm', 'C2')]
    chs = [chord(c) for _, _, c, _ in prog]
    V = voice_lead(chs, 55, 69, 3)
    for (b, d, _, bn), v in zip(prog, V):
        for m in v:
            S.add('pad', strings(m, S.sec(d) + 0.1, 0.8, seed=S.nseed(), attack=0.15, rel=1.0, fc=1500), b, 0)
        S.add('bass', strings(midi(bn), S.sec(d) + 0.05, 1.0, seed=S.nseed(), attack=0.08, rel=0.8, fc=600, voices=3),
              b, 0)
    for j, n in enumerate(['G5', 'Eb5', 'C5', 'G4', 'Eb4', 'C4']):
        S.add('harp', harp(midi(n), 1.5, 0.75 - 0.06 * j, seed=S.nseed()), 4.3 + j * 0.16, 0.35)
    for k in range(14):
        S.add('timp', timpani(midi('C2') + 12, 0.1 + 0.25 * (1 - abs(k - 9) / 9), S.nseed(), length=0.8),
              3.1 + k / 8, -0.2)
    S.add('timp', timpani(midi('C2') + 12, 0.7, S.nseed(), length=2.5), 4.3, -0.2)
    S.N = int(S.sec(6) * SR + 0.95 * SR)
    for k in S.tr:
        S.tr[k] = S.tr[k][:, :S.N]
    return S, dict(rt60=2.4, wet=0.42, bright=0.4)


# --------------------------------------------------------------------------
# VARIATIONS: extra instruments + shared arranging helpers
# --------------------------------------------------------------------------
def recorder(m, dur, vel=1.0, seed=0):
    f = hz(m)
    rel = 0.08
    n = int((dur + rel) * SR)
    t = np.arange(n) / SR
    r = np.random.default_rng(seed)
    vib = 0.0022 * np.clip((t - 0.25) / 0.3, 0, 1) * np.sin(2 * np.pi * 5.6 * t + r.uniform(0, 6.28))
    ph = 2 * np.pi * np.cumsum(f * (1 + vib)) / SR
    tone = np.sin(ph) + 0.12 * np.sin(2 * ph + 0.5) + 0.09 * np.sin(3 * ph + 1.1) + 0.03 * np.sin(5 * ph)
    br = filt(noise(n, seed), 'bandpass', (1000, 8000))
    tone = tone + br * (0.025 + 0.35 * np.exp(-t / 0.02))
    return tone * env_adsr(n, 0.03, 0.15, 0.85, rel, dur) * vel / 1.2


def pizz(m, dur, vel=1.0, seed=0):
    f = hz(m)
    d = min(dur, 0.6)
    n = int((d + 0.25) * SR)
    y = ks_string(f, n, bright=round(0.25 + 0.25 * vel, 2), t60=0.7, pos=0.18, seed=seed)
    return y * env_adsr(n, 0.002, 10, 1, 0.25, d) * vel


def fiddle(m, dur, vel=1.0, seed=0):
    f = hz(m)
    rel = 0.1
    n = int((dur + rel) * SR)
    t = np.arange(n) / SR
    fc = f * (3 + 3 * (1 - np.exp(-t / 0.04))) + 1800
    y = saw_add(f, n, voices=2, det=4, fc=fc, order=2, vib=0.006, vib_rate=6.2, vib_delay=0.12,
                spread=0.15, seed=seed, kmax=48)
    bow = filt(noise(n, seed), 'bandpass', (2000, 7000)) * (0.04 + 0.12 * np.exp(-t / 0.03))
    return (y + bow) * env_adsr(n, 0.025, 0.15, 0.85, rel, dur) * vel


def tambourine(vel=1.0, seed=0):
    n = int(0.3 * SR)
    t = np.arange(n) / SR
    y = filt(noise(n, seed), 'bandpass', (5000, 14000)) * np.exp(-t / 0.09) * (1 + 0.5 * np.sin(2 * np.pi * 28 * t))
    r = np.random.default_rng(seed)
    for _ in range(6):
        y += 0.08 * np.sin(2 * np.pi * r.uniform(6000, 10000) * t) * np.exp(-t / 0.12)
    return y * np.minimum(t / 0.001, 1) * vel


def chord_tones(c, lo):
    r = in_range(c['root'], lo, lo + 11)
    iv = c['ivs']
    return [r, r + iv[1], r + iv[2], r + 12, r + 12 + iv[1], r + 12 + iv[2], r + 24]


def ostinato(S, TL, bars, track, lo, pat, step, fn, pan=-0.3, dur=None, ok=lambda bar: True, acc=(0.95, 0.62)):
    per = int(round(S.bpb / step))
    for bar in range(bars):
        if not ok(bar):
            continue
        for j in range(per):
            beat = bar * S.bpb + j * step
            t = chord_tones(chord_at(TL, beat), lo)
            unit = 3 if S.bpb == 6 else 1
            v = acc[0] if abs((j * step) % unit) < 1e-6 else acc[1]
            S.add(track, fn(t[pat[j % len(pat)]], S.sec(dur or step * 0.9), v, seed=S.nseed()), beat, pan,
                  jitter_ms=2)


def bassline(S, TL, bars, track, lo, steps, fn, ok=lambda bar: True):
    """steps: (beat, kind, dur_beats, vel); kind r=bass note, o=octave up, 5=fifth, 3=third, 7=b7."""
    for bar in range(bars):
        if not ok(bar):
            continue
        for bt, kind, d, v in steps:
            beat = bar * S.bpb + bt
            c = chord_at(TL, beat)
            r = in_range(c['bass'], lo, lo + 11)
            m = {'r': r, 'o': r + 12, '5': in_range((c['root'] + c['ivs'][2]) % 12, lo, lo + 12),
                 '3': in_range((c['root'] + c['ivs'][1]) % 12, lo, lo + 12), '7': r + 10}[kind]
            S.add(track, fn(m, S.sec(d), v, seed=S.nseed()), beat, 0, jitter_ms=2)


def stabs(S, TL, V, hits, ok, track='stab', low='lowbr', low_lo=41):
    for i, (b, d, c) in enumerate(TL):
        bar = int(b // S.bpb)
        if not ok(bar):
            continue
        for hb, hd, hv in hits:
            if hb >= d - 1e-6:
                continue
            L = S.sec(min(hd, d - hb))
            for j, m in enumerate(V[i]):
                S.add(track, brass(m, L, hv, seed=S.nseed(), stab=True), b + hb, -0.45 + 0.3 * j, jitter_ms=3)
            if low:
                S.add(low, brass(in_range(c['bass'], low_lo, low_lo + 11), L, hv, seed=S.nseed(), stab=True,
                                 voices=2), b + hb, 0)


def padchords(S, TL, V, track, ok, vel=0.8, attack=0.25, rel=0.7, fc=2600, fn=None):
    for i, (b, d, c) in enumerate(TL):
        if ok(int(b // S.bpb)):
            for m in V[i]:
                S.add(track, strings(m, S.sec(d) + 0.05, vel, seed=S.nseed(), attack=attack, rel=rel, fc=fc), b, 0)


def drum(S, track, fn, hits, bar0, pan=0.0, jitter_ms=2, **kw):
    for bt, v in hits:
        S.add(track, fn(v, S.nseed(), **kw), bar0 + bt, pan, jitter_ms=jitter_ms)


def roll(S, track, m, b0, beats, n, v0=0.15, v1=0.75):
    for k in range(n):
        S.add(track, timpani(m, v0 + (v1 - v0) * k / (n - 1), S.nseed(), length=0.8), b0 + k * beats / n, -0.2)


# --------------------------------------------------------------------------
# LOBBY 2: waltz (G major, 3/4, 144 BPM, 56 bars = 70.00 s)
# --------------------------------------------------------------------------
def build_lobby2():
    S = Song('lobby2', 144, 56, loop=True, tail_s=5.0, bpb=3, seed=66)
    A = ['G', 'G', 'C', 'G', 'Em', 'Am', 'D7', 'D7', 'G', 'G', 'C', 'Cm', 'G/D', 'Am7', 'D7', 'G']
    B = ['Em', 'Em', 'Am', 'Am', 'D', 'D', 'G', 'G', 'C', 'C', 'G/B', 'Em', 'Am', 'D', 'G', 'D7']
    Cd = ['C', 'G/B', 'Am', 'D', 'Em', 'C', 'Am7', 'D7']
    TL = timeline(A + B + A + Cd, bpb=3)
    GMAJ = [7, 9, 11, 0, 2, 4, 6]
    S.track('rec', level=-15, send=0.32)
    S.track('clar', level=-21, send=0.32)
    S.track('harp', level=-17.5, send=0.35)
    S.track('harpc', level=-20, send=0.3)
    S.track('pad', level=-24, send=0.4, chorus=True, lp=5000)
    S.track('bass', level=-19, send=0.12, hp=35)
    S.track('doum', level=-23, send=0.15)
    S.track('tek', level=-27, send=0.18)
    S.track('shaker', level=-33, send=0.15)
    mA = ('B4:2 D5:1  G5:2 F#5:1  E5:2 G5:1  D5:3  B4:2 E5:1  E5:2 C5:1  A4:1 D5:1 F#5:1  A5:2 C5:1  '
          'B4:2 D5:1  G5:2 B5:1  A5:1 G5:1 E5:1  Eb5:2 C5:1  D5:2 G5:1  G5:1 E5:1 C5:1  A5:2 F#5:1  G5:2 r:1')
    mB = ('E5:1 F#5:1/2 G5:1/2 B5:1  G5:2 E5:1  C6:1 B5:1/2 A5:1/2 E5:1  A5:2 r:1  '
          'F#5:1 G5:1/2 A5:1/2 D6:1  A5:2 F#5:1  B5:1 A5:1/2 G5:1/2 D5:1  G5:2 B4:1  '
          'C5:1 E5:1 G5:1  A5:1 G5:1 E5:1  D5:2 G5:1  G5:1 B5:1 E5:1  C6:2 A5:1  F#5:2 D5:1  '
          'G5:1 B5:1 D6:1  C6:2 A5:1')
    mC = ('E5:1 G5:1 C6:1  B5:2 G5:1  A5:1 E5:1 C5:1  D5:2 F#5:1  E5:1 G5:1 B5:1  C6:2 G5:1  '
          'A5:1 G5:1 E5:1  F#5:2 r:1')
    evA, _ = mel(mA, 0)
    evB, _ = mel(mB, 48)
    evA2, _ = mel(mA, 96)
    evC, _ = mel(mC, 144)
    pick, _ = mel('r:2 D5:1', 165)
    S.notes('rec', evA + evB + evA2 + pick, recorder, legato=1.0, pan=0.1)
    S.notes('clar', [(b, d, diatonic_shift(m, GMAJ, -2) if m else None) for b, d, m in evA2], clarinet,
            pan=-0.3, vel=0.85)
    S.notes('harp', evC, harp, legato=1.5, pan=0.3)
    chords = [c for _, _, c in TL]
    V3 = voice_lead(chords, 55, 69, 3)
    VP = voice_lead(chords, 52, 71, 4)
    for i, (b, d, c) in enumerate(TL):
        bar = int(b // 3)
        for bt in (1, 2):  # oom-PAH-PAH
            for m in V3[i]:
                S.add('harpc', harp(m, S.sec(0.8), 0.5 if bt == 1 else 0.42, seed=S.nseed()), b + bt, -0.3,
                      jitter_ms=6)
        if 32 <= bar < 48 and bar % 2 == 0:  # sparkle arpeggios in A'
            for j, m in enumerate(sorted(in_range(pc, 74, 85) for pc in c['pcs'][:3])):
                S.add('harp', harp(m, 1.0, 0.4 + 0.08 * j, seed=S.nseed()), b + j * 0.5, 0.4)
    padchords(S, TL, VP, 'pad', lambda bar: bar >= 16, vel=0.8, attack=0.5, rel=0.9, fc=1800)
    bassline(S, TL, 56, 'bass', 40, [(0, 'r', 2.4, 0.95)], pluck_bass, ok=lambda bar: bar % 2 == 0)
    bassline(S, TL, 56, 'bass', 40, [(0, '5', 2.4, 0.85)], pluck_bass, ok=lambda bar: bar % 2 == 1)
    for bar in range(56):
        b0 = bar * 3
        drum(S, 'doum', doum, [(0, 0.9)], b0)
        if bar >= 8:
            drum(S, 'tek', tek, [(1, 0.55), (2, 0.45)], b0, 0.2, jitter_ms=4)
        if 16 <= bar < 48:
            drum(S, 'shaker', shaker, [(j * 0.5, 0.45 if j % 2 else 0.3) for j in range(6)], b0, 0.5, jitter_ms=4)
    return S, dict(rt60=2.4, wet=0.38, bright=0.45)


# --------------------------------------------------------------------------
# LOBBY 3: bouncy marketplace (A major, 120 BPM, 36 bars = 72.00 s)
# --------------------------------------------------------------------------
def build_lobby3():
    S = Song('lobby3', 120, 36, loop=True, tail_s=4.5, seed=77)
    I = ['A', 'D', 'A', 'E7']
    A = ['A', 'D', 'A', 'E', 'A', 'D', 'E7', 'A']
    B = ['F#m', 'D', 'A', 'E', 'F#m', 'D', 'B7', 'E7']
    C = ['D', 'E', 'C#m', 'F#m', 'Bm', 'E', 'A', 'E7']
    TL = timeline(I + A + B + A + C)
    AMAJ = [9, 11, 1, 2, 4, 6, 8]
    sect = lambda bar: 'I' if bar < 4 else 'A' if bar < 12 else 'B' if bar < 20 else 'A2' if bar < 28 else 'C'
    S.track('pizzlead', level=-17, send=0.25)
    S.track('wind', level=-17, send=0.3)
    S.track('clar', level=-21, send=0.3)
    S.track('glock', level=-23, send=0.35)
    S.track('pizzch', level=-21.5, send=0.2)
    S.track('pad', level=-25, send=0.4, chorus=True, lp=5000)
    S.track('bass', level=-18, send=0.1, hp=35)
    S.track('doum', level=-22, send=0.12)
    S.track('tamb', level=-27, send=0.15)
    S.track('shaker', level=-32, send=0.12)
    S.track('wood', level=-30, send=0.15)
    mA = ('E5:1/2 A5:1/2 C#6:1/2 A5:1/2 E5:1 r:1  F#5:1/2 A5:1/2 D6:1/2 A5:1/2 F#5:1 r:1  '
          'E5:1/2 C#5:1/2 E5:1/2 A5:1/2 B5:1/2 C#6:1/2 B5:1/2 A5:1/2  G#5:1 E5:1 B4:1 r:1  '
          'E5:1/2 A5:1/2 C#6:1/2 A5:1/2 E5:1 r:1  F#5:1/2 A5:1/2 D6:1/2 C#6:1/2 B5:1/2 A5:1/2 F#5:1/2 r:1/2  '
          'E5:1/2 G#5:1/2 B5:1/2 D6:1/2 C#6:1/2 B5:1/2 G#5:1/2 B5:1/2  A5:1 E5:1/2 C#5:1/2 A4:1 r:1')
    mB = ('C#5:1.5 D5:1/2 E5:1 F#5:1  A5:2 F#5:1 D5:1  E5:1.5 F#5:1/2 E5:1 C#5:1  B4:3 r:1  '
          'C#5:1.5 D5:1/2 E5:1 A5:1  F#5:1 A5:1 D6:2  C#6:1 B5:1 A5:1 F#5:1  G#5:2 E5:1 D5:1')
    mC = ('F#5:1/2 E5:1/2 D5:1/2 E5:1/2 F#5:1 A5:1  G#5:1/2 F#5:1/2 E5:1/2 F#5:1/2 G#5:1 B5:1  '
          'C#6:1/2 B5:1/2 G#5:1/2 E5:1/2 C#5:1 E5:1  F#5:2 C#5:1 A4:1  '
          'D5:1/2 F#5:1/2 B5:1/2 F#5:1/2 D5:1 B4:1  E5:1/2 G#5:1/2 B5:1/2 G#5:1/2 E5:1 D5:1  '
          'C#5:1/2 E5:1/2 A5:1/2 C#6:1/2 B5:1/2 A5:1/2 G#5:1/2 A5:1/2  B5:1 G#5:1 E5:1 D5:1')
    evA, _ = mel(mA, 16)
    evB, _ = mel(mB, 48)
    evA2, _ = mel(mA, 80)
    evC, _ = mel(mC, 112)
    S.notes('pizzlead', evA + evA2 + evC, pizz, pan=0.15, vel=1.0)
    S.notes('wind', evB, clarinet, legato=1.0, pan=0.1)
    S.notes('wind', evA2, flute, legato=0.6, pan=-0.1, vel=0.8)
    S.notes('clar', [(b, d, diatonic_shift(m, AMAJ, -2) if m else None) for b, d, m in evB], flute,
            transpose=12, pan=-0.35, vel=0.6, legato=0.95)
    S.notes('glock', evA2 + evC, glock, transpose=12, vel=0.5, jitter_ms=0, pan=0.3)
    chords = [c for _, _, c in TL]
    V3 = voice_lead(chords, 57, 69, 3)
    VP = voice_lead(chords, 54, 71, 4)
    for i, (b, d, c) in enumerate(TL):
        bar = int(b // 4)
        offs = [1, 3] + ([1.5, 3.5] if sect(bar) in ('A2', 'C') else [])
        for bt in offs:
            for m in V3[i]:
                S.add('pizzch', pizz(m, S.sec(0.3), 0.75 if bt % 1 == 0 else 0.5, seed=S.nseed()), b + bt, -0.35,
                      jitter_ms=5)
    padchords(S, TL, VP, 'pad', lambda bar: sect(bar) in ('B', 'C'), vel=0.7, attack=0.4, rel=0.8, fc=1800)
    bassline(S, TL, 36, 'bass', 40, [(0, 'r', 0.9, 1.0), (2, '5', 0.9, 0.85)], pluck_bass)
    bassline(S, TL, 36, 'bass', 40, [(3.5, 'o', 0.4, 0.55)], pluck_bass, ok=lambda bar: sect(bar) in ('A2', 'C'))
    for bar in range(36):
        b0 = bar * 4
        s = sect(bar)
        drum(S, 'doum', doum, [(0, 0.9), (2, 0.7)], b0)
        if s != 'I':
            drum(S, 'tamb', tambourine, [(1, 0.8), (3, 0.85)], b0, 0.35)
        else:
            drum(S, 'wood', woodblock, [(j + 0.5, 0.6) for j in range(4)], b0, -0.4, f=1150)
        if s in ('A2', 'C', 'B'):
            drum(S, 'shaker', shaker, [(j * 0.5, 0.5 if j % 2 else 0.3) for j in range(8)], b0, 0.5, jitter_ms=4)
        if s in ('A', 'C'):
            drum(S, 'wood', woodblock, [(0.5, 0.5), (2.5, 0.5)], b0, -0.4, f=1150)
        if bar % 8 == 3:
            drum(S, 'tamb', tambourine, [(3 + k * 0.25, 0.4 + 0.15 * k) for k in range(4)], b0, 0.35)
    return S, dict(rt60=2.0, wet=0.32, bright=0.5)


# --------------------------------------------------------------------------
# BATTLE 2: minor war march (G minor, 140 BPM, 35 bars = 60.00 s)
# --------------------------------------------------------------------------
def build_battle2():
    S = Song('battle2', 140, 35, loop=True, tail_s=4.0, seed=88)
    I = ['Gm', 'Gm', 'D']
    A = ['Gm', 'Eb', 'Cm', 'D', 'Gm', 'Bb', 'Cm D', 'Gm']
    B = ['Eb', 'Bb', 'F', 'Gm', 'Eb', 'Bb', 'Cm', 'D']
    C = ['Cm', 'Gm', 'Cm', 'D', 'Eb', 'Cm', 'D', 'D']
    TL = timeline(I + A + B + A + C)
    sect = lambda bar: 'I' if bar < 3 else 'A' if bar < 11 else 'B' if bar < 19 else 'A2' if bar < 27 else 'C'
    S.track('lead', level=-14, send=0.25)
    S.track('horns', level=-18, send=0.3)
    S.track('leaddbl', level=-21, send=0.3, chorus=True)
    S.track('ostin', level=-21, send=0.15)
    S.track('stab', level=-18, send=0.22)
    S.track('bpad', level=-22, send=0.3)
    S.track('lowbr', level=-21, send=0.15)
    S.track('pad', level=-24, send=0.4, chorus=True, lp=7000)
    S.track('bass', level=-17.5, send=0.06, hp=40)
    S.track('taiko', level=-16, send=0.18, hp=40)
    S.track('snare', level=-23, send=0.2)
    S.track('crash', level=-25, send=0.15)
    S.track('timp', level=-20, send=0.25)
    mA = ('G4:3/4 G4:1/4 D5:1 Bb4:3/4 A4:1/4 G4:1  Bb4:3/4 C5:1/4 Eb5:1.5 D5:1/2 Bb4:1  '
          'C5:3/4 C5:1/4 G5:1 Eb5:3/4 D5:1/4 C5:1  D5:2 A4:1 F#4:1  G4:3/4 G4:1/4 D5:1 G5:1 Bb5:1  '
          'F5:3/4 Eb5:1/4 D5:1 Bb4:2  Eb5:1 C5:1 D5:1 F#5:1  G5:3 r:1')
    mB = ('Bb5:2 G5:1 Eb5:1  F5:2 D5:1 Bb4:1  C5:3/4 F5:1/4 A5:1 C6:2  Bb5:1.5 A5:1/2 G5:2  '
          'G5:3/4 Bb5:1/4 Eb6:1 D6:1 Bb5:1  F5:2 Bb5:2  C6:1 Bb5:1 G5:1 Eb5:1  D5:1 F#5:1 A5:1 D6:1')
    mC = ('C5:3/4 Eb5:1/4 G5:2 r:1  D5:3/4 G5:1/4 Bb5:2 r:1  C6:1 Bb5:1 G5:1 Eb5:1  F#5:2 D5:2  '
          'G5:3/4 Eb5:1/4 Bb5:2 r:1  C6:3/4 G5:1/4 Eb6:2 r:1  D6:1 C6:1 A5:1 F#5:1  D5:2 r:2')
    evA, _ = mel(mA, 12)
    evB, _ = mel(mB, 44)
    evA2, _ = mel(mA, 76)
    evC, _ = mel(mC, 108)
    call, _ = mel('D4:3/4 G4:1/4 G4:1 Bb4:1 D5:1  D5:3/4 C5:1/4 Bb4:1 A4:1 G4:1  F#4:2 A4:1 D5:1', 0)
    S.notes('horns', call + evA, brass, transpose=0, legato=0.95, vel=0.95, dark=0.5, voices=3)
    S.notes('horns', evA2, brass, transpose=-12, legato=0.95, vel=0.9, dark=0.5, voices=3)
    S.notes('lead', evB + evC, brass, legato=0.95, vel=1.0, voices=2, dark=0.2)
    S.notes('lead', evA2, brass, legato=0.95, vel=1.0, voices=2)
    S.notes('leaddbl', evB + evA2 + evC, strings, transpose=-12, legato=1.0, attack=0.05, rel=0.25, fc=3200)
    chords = [c for _, _, c in TL]
    V4 = voice_lead(chords, 53, 70, 4)
    VH = voice_lead(chords, 64, 81, 3)
    stabs(S, TL, V4, [(0, 0.5, 1.0), (0.75, 0.2, 0.7), (1, 0.5, 0.9), (2.5, 0.4, 0.8), (3, 0.6, 0.9)],
          lambda bar: sect(bar) in ('I', 'C'), low_lo=38)
    stabs(S, TL, V4, [(0, 0.6, 1.0), (2, 0.4, 0.75)], lambda bar: sect(bar) == 'B', low_lo=38)
    for i, (b, d, c) in enumerate(TL):
        if sect(int(b // 4)) in ('A', 'A2'):
            for j, m in enumerate(V4[i]):
                S.add('bpad', brass(m, S.sec(d - 0.1), 0.5, seed=S.nseed()), b, -0.45 + 0.3 * j)
    padchords(S, TL, VH, 'pad', lambda bar: sect(bar) in ('B', 'A2', 'C'), vel=0.8)
    ostinato(S, TL, 35, 'ostin', 50, [0, 0, 1, 0, 2, 0, 1, 0, 0, 0, 1, 0, 2, 1, 2, 3], 0.25, spiccato,
             ok=lambda bar: sect(bar) != 'I')
    march_bass = [(0, 'r', 0.6, 1.0), (0.75, 'r', 0.22, 0.6), (1, 'r', 0.45, 0.8), (2, 'r', 0.6, 1.0),
                  (2.75, 'r', 0.22, 0.6), (3, 'o', 0.45, 0.8)]
    bassline(S, TL, 35, 'bass', 36, march_bass, low_bass)
    for bar in range(35):
        b0 = bar * 4
        s = sect(bar)
        drum(S, 'taiko', taiko, [(0, 1.0), (2, 1.0)], b0, pitch=0.85)
        drum(S, 'taiko', taiko, [(1, 0.6), (3, 0.65)] + ([(3.5, 0.5), (3.75, 0.6)] if bar % 4 == 2 else []),
             b0, pitch=1.15)
        if s != 'I':
            drum(S, 'snare', snare, [(0, .9), (0.5, .35), (0.75, .55), (1, .8), (1.5, .35), (2, .9), (2.5, .35),
                                     (2.75, .55), (3, .8), (3.25, .35), (3.5, .45), (3.75, .55)], b0, 0.1)
        else:
            drum(S, 'snare', snare, [(k * 0.25, 0.15 + 0.6 * ((bar * 16 + k) / 47)) for k in range(16)], b0, 0.1)
        if bar in (0, 3, 11, 19, 27):
            S.add('crash', crash(1.0, S.nseed()), b0, 0.3 if bar % 2 else -0.3)
        c = chord_at(TL, b0)
        S.add('timp', timpani(in_range(c['root'], 38, 50), 0.85, S.nseed()), b0, -0.2)
        if bar in (2, 34, 18):
            roll(S, 'timp', in_range(chord_at(TL, (b0 + 4) % 140)['root'], 38, 50), b0 + 2, 2, 24)
    return S, dict(rt60=2.1, wet=0.3, bright=0.45)


# --------------------------------------------------------------------------
# BATTLE 3: adventurous jig (G major, 6/8, dotted-quarter 96 = 288 eighths, 48 bars = 60.00 s)
# --------------------------------------------------------------------------
def build_battle3():
    S = Song('battle3', 288, 48, loop=True, tail_s=4.0, bpb=6, seed=99)
    I = ['G', 'C', 'G', 'D']
    A = ['G', 'C', 'G', 'D', 'G', 'C', 'D', 'G']
    B = ['Em', 'C', 'G', 'D', 'Em', 'C', 'Am D', 'G']
    C = ['C', 'D', 'Bm', 'Em', 'C', 'D', 'G/B C', 'D']
    T = ['Em', 'C', 'D', 'D']
    TL = timeline(I + A + A + B + B + C + T, bpb=6)
    GMAJ = [7, 9, 11, 0, 2, 4, 6]
    sect = lambda bar: ('I' if bar < 4 else 'A' if bar < 12 else 'A2' if bar < 20 else 'B' if bar < 28
                        else 'B2' if bar < 36 else 'C' if bar < 44 else 'T')
    S.track('fiddle', level=-14.5, send=0.25, eq=(500, 3000, 0.4))
    S.track('flute', level=-19, send=0.3)
    S.track('harm', level=-21, send=0.3)
    S.track('lead', level=-15, send=0.25)
    S.track('ostin', level=-20.5, send=0.18)
    S.track('stab', level=-18, send=0.22)
    S.track('bpad', level=-22.5, send=0.3)
    S.track('lowbr', level=-21.5, send=0.15)
    S.track('bass', level=-18, send=0.06, hp=40)
    S.track('bodhran', level=-19, send=0.12, hp=45)
    S.track('tek', level=-25, send=0.15)
    S.track('taiko', level=-18, send=0.18, hp=45)
    S.track('snare', level=-23.5, send=0.2)
    S.track('shaker', level=-30, send=0.1)
    S.track('crash', level=-25, send=0.15)
    S.track('timp', level=-21, send=0.25)
    mA = ('G5:2 B5:1 D6:2 B5:1  C6:2 B5:1 A5:1 G5:1 E5:1  D5:2 G5:1 B5:2 G5:1  A5:1 B5:1 A5:1 F#5:1 E5:1 D5:1  '
          'G5:2 B5:1 D6:2 B5:1  E6:2 D6:1 C6:1 B5:1 A5:1  B5:1 A5:1 G5:1 F#5:1 G5:1 A5:1  G5:3 G4:1 B4:1 D5:1')
    mB = ('E5:2 G5:1 B5:2 G5:1  C6:2 B5:1 A5:1 G5:1 E5:1  D5:1 G5:1 B5:1 D6:2 B5:1  A5:3 F#5:2 D5:1  '
          'E5:2 G5:1 B5:2 E6:1  E6:1 D6:1 C6:1 G5:2 E5:1  A5:1 C6:1 A5:1 F#5:1 A5:1 F#5:1  G5:3 r:3')
    mC = ('G5:2 E5:1 C6:3  A5:2 F#5:1 D6:3  B5:2 A5:1 F#5:2 D5:1  E5:6  '
          'G5:2 A5:1 B5:2 C6:1  D6:3 A5:3  B5:3 C6:3  D6:3 r:3')
    evA, _ = mel(mA, 24)
    evA2, _ = mel(mA, 72)
    evB, _ = mel(mB, 120)
    evB2, _ = mel(mB, 168)
    evC, _ = mel(mC, 216)
    S.notes('fiddle', evA + evA2 + evB + evC, fiddle, legato=0.92, pan=0.1)
    S.notes('flute', evA2, flute, legato=0.85, pan=-0.15, vel=0.85)
    S.notes('harm', [(b, d, diatonic_shift(m, GMAJ, -2) if m else None) for b, d, m in evA2 + evB2], clarinet,
            pan=-0.35, legato=0.9, vel=0.8)
    S.notes('lead', evB2, brass, legato=0.92, voices=2)
    S.notes('lead', evC, brass, transpose=-12, legato=0.95, voices=3, dark=0.3)
    chords = [c for _, _, c in TL]
    V4 = voice_lead(chords, 53, 70, 4)
    stabs(S, TL, V4, [(0, 1.5, 1.0), (3, 1.5, 0.8)], lambda bar: sect(bar) in ('I', 'B2', 'C', 'T'))
    for i, (b, d, c) in enumerate(TL):
        if sect(int(b // 6)) in ('A2', 'B'):
            for j, m in enumerate(V4[i]):
                S.add('bpad', brass(m, S.sec(d) - 0.05, 0.5, seed=S.nseed()), b, -0.45 + 0.3 * j)
    ostinato(S, TL, 48, 'ostin', 55, [0, 1, 2, 3, 2, 1], 1, spiccato, dur=0.8)
    bassline(S, TL, 48, 'bass', 36, [(0, 'r', 2.6, 1.0), (3, '5', 2.6, 0.8)], low_bass)
    for bar in range(48):
        b0 = bar * 6
        s = sect(bar)
        drum(S, 'bodhran', doum, [(0, 1.0), (3, 0.8)] + ([(5, 0.5)] if bar % 2 else []), b0)
        drum(S, 'tek', tek, [(1, .45), (2, .55), (4, .45), (5, .55)], b0, 0.2)
        if s in ('B2', 'C', 'I', 'T'):
            drum(S, 'taiko', taiko, [(0, 1.0), (3, 0.75)] + ([(4, .6), (5, .8)] if bar % 4 == 3 else []), b0)
        if s not in ('I', 'A'):
            drum(S, 'snare', snare, [(3, 0.85)] + ([(5, 0.3)] if bar % 2 else []), b0, 0.1)
            drum(S, 'shaker', shaker, [(j, 0.5 if j % 3 else 0.3) for j in range(6)], b0, 0.5)
        if bar % 4 == 3 and s != 'I':
            drum(S, 'snare', snare, [(3 + k * 0.5, 0.3 + 0.1 * k) for k in range(6)], b0, 0.1)
        if bar in (0, 4, 12, 20, 28, 36, 44):
            S.add('crash', crash(1.0, S.nseed()), b0, 0.3 if bar % 8 else -0.3)
        if s in ('C', 'B2', 'I', 'T'):
            S.add('timp', timpani(in_range(chord_at(TL, b0)['root'], 38, 50), 0.8, S.nseed()), b0, -0.2)
        if bar in (3, 47, 35):
            roll(S, 'timp', in_range(chord_at(TL, (b0 + 6) % 288)['root'], 38, 50), b0 + 2, 4, 20)
    return S, dict(rt60=2.0, wet=0.3, bright=0.5)


# --------------------------------------------------------------------------
# OVERTIME 2: (C minor, 160 BPM, 32 bars = 48.00 s)
# --------------------------------------------------------------------------
def build_overtime2():
    S = Song('overtime2', 160, 32, loop=True, tail_s=4.0, seed=111)
    I = ['Cm', 'Cm', 'Ab', 'G']
    A = ['Cm', 'Ab', 'Fm', 'G', 'Cm', 'Ab', 'Db', 'G']
    B = ['Ab', 'Eb', 'Fm', 'Cm', 'Ab', 'Bb', 'Fm', 'G']
    C = ['Cm', 'Bb', 'Ab', 'G', 'Cm', 'Bb', 'Ab Bb', 'G']
    E = ['Cm', 'Ab', 'Db', 'G']
    TL = timeline(I + A + B + C + E)
    sect = lambda bar: 'I' if bar < 4 else 'A' if bar < 12 else 'B' if bar < 20 else 'C' if bar < 28 else 'E'
    S.track('lead', level=-14.5, send=0.25)
    S.track('leaddbl', level=-21, send=0.3, chorus=True)
    S.track('glock', level=-25, send=0.3)
    S.track('ostin', level=-19.5, send=0.16)
    S.track('stab', level=-17.5, send=0.2)
    S.track('lowbr', level=-21, send=0.12)
    S.track('pad', level=-24, send=0.4, chorus=True, lp=7000)
    S.track('drone', level=-25, send=0.3)
    S.track('bass', level=-18, send=0.05, hp=40)
    S.track('taiko', level=-16.5, send=0.16, hp=45)
    S.track('snare', level=-23.5, send=0.18)
    S.track('hats', level=-29, send=0.08)
    S.track('tick', level=-29, send=0.12)
    S.track('crash', level=-25, send=0.15)
    S.track('timp', level=-21, send=0.22)
    S.track('riser', level=-28, send=0.3)
    mA = ('C5:1/2 D5:1/2 Eb5:1/2 G5:1/2 C6:1 G5:1  Ab5:1.5 G5:1/2 Eb5:1 C5:1  '
          'F5:1/2 G5:1/2 Ab5:1/2 C6:1/2 Ab5:1 F5:1  G5:1.5 F5:1/2 D5:1 B4:1  '
          'C5:1/2 D5:1/2 Eb5:1/2 G5:1/2 C6:1 Eb6:1  C6:1.5 Bb5:1/2 Ab5:1 Eb5:1  '
          'Db6:1 C6:1/2 Bb5:1/2 Ab5:1 F5:1  G5:2 B5:1 D6:1')
    mB = ('C6:2 Eb6:2  Bb5:2 G5:2  Ab5:2 F5:1 C6:1  G5:2 Eb5:1 C5:1  '
          'C6:2 Eb6:2  D6:2 Bb5:1 F5:1  Ab5:1 G5:1 F5:1 Ab5:1  G5:2 B5:1 D6:1')
    mC = ('C6:1/2 G5:1/2 Eb5:1/2 G5:1/2 C6:1 r:1  Bb5:1/2 F5:1/2 D5:1/2 F5:1/2 Bb5:1 r:1  '
          'Ab5:1/2 Eb5:1/2 C5:1/2 Eb5:1/2 Ab5:1 C6:1  B5:2 G5:2  '
          'C6:1/2 G5:1/2 Eb5:1/2 G5:1/2 C6:1 r:1  Bb5:1/2 F5:1/2 D5:1/2 F5:1/2 Bb5:1 r:1  '
          'Ab5:1/2 C6:1/2 Eb6:1 D6:1/2 Bb5:1/2 F5:1  G5:2 B5:1 D6:1')
    evA, _ = mel(mA, 16)
    evB, _ = mel(mB, 48)
    evC, _ = mel(mC, 80)
    S.notes('lead', evA + evB + evC, brass, legato=0.95, voices=2)
    S.notes('leaddbl', evA + evB + evC, strings, transpose=-12, legato=1.0, attack=0.04, rel=0.2, fc=3500)
    S.notes('glock', evB, glock, transpose=12, vel=0.4, jitter_ms=0, pan=0.3)
    chords = [c for _, _, c in TL]
    V4 = voice_lead(chords, 55, 72, 4)
    VH = voice_lead(chords, 67, 84, 3)
    stabs(S, TL, V4, [(0, .45, 1.0), (0.75, .3, .7), (1.5, .45, .85), (2.5, .3, .7), (3, .7, .9)],
          lambda bar: sect(bar) in ('I', 'C', 'E'), low_lo=38)
    stabs(S, TL, V4, [(0, .9, 1.0), (2.5, .4, .7)], lambda bar: sect(bar) in ('A', 'B'), low_lo=38)
    padchords(S, TL, VH, 'pad', lambda bar: sect(bar) in ('B', 'C'), vel=0.8, attack=0.2, rel=0.6)
    for b0 in (0, 112):
        for m in (midi('C2'), midi('G2')):
            S.add('drone', strings(m, S.sec(16) - 0.3, 1.0, seed=S.nseed(), attack=1.2, rel=0.8, fc=900, voices=4),
                  b0, 0)
    ostinato(S, TL, 32, 'ostin', 60, [0, 1, 2, 1, 3, 2, 1, 2, 0, 1, 2, 1, 3, 2, 4, 2], 0.25, spiccato, dur=0.2)
    bassline(S, TL, 32, 'bass', 36, [(j * 0.5, 'o' if j in (2, 5) else 'r', 0.42, 1.0 if j % 2 == 0 else 0.75)
                                     for j in range(8)], low_bass)
    for bar in range(32):
        b0 = bar * 4
        s = sect(bar)
        drum(S, 'taiko', taiko, [(k, 1.0 if k % 2 == 0 else 0.7) for k in range(4)], b0)
        if bar % 2 == 1:
            for k in range(4):
                S.add('taiko', taiko(0.5 + 0.12 * k, S.nseed(), pitch=1.35 - 0.1 * k), b0 + 3 + k * 0.25,
                      0.25 - 0.15 * k)
        if s != 'I':
            drum(S, 'snare', snare, [(1, .9), (3, .95), (1.75, .2), (2.5, .25), (3.75, .3)], b0, 0.1)
            if bar % 4 == 3:
                drum(S, 'snare', snare, [(2 + k * 0.25, 0.3 + 0.08 * k) for k in range(8)], b0, 0.1)
            drum(S, 'hats', hat, [(j * 0.25, 0.55 if j % 2 else 0.3) for j in range(16)], b0, 0.35)
        if s in ('I', 'E'):
            drum(S, 'tick', woodblock, [(j * 0.5, 0.8 if j % 2 == 0 else 0.5) for j in range(8)], b0, -0.45)
            if bar >= 30:
                drum(S, 'snare', snare, [(k * 0.25, 0.2 + 0.8 * ((bar - 30) * 16 + k) / 31) for k in range(16)], b0, 0.1)
        if bar % 4 == 0:
            S.add('crash', crash(1.0, S.nseed()), b0, -0.35 if bar % 8 else 0.35)
        S.add('timp', timpani(in_range(chord_at(TL, b0)['root'], 38, 50), 0.9, S.nseed()), b0, -0.2)
        if bar in (3, 11, 19, 27, 31):
            roll(S, 'timp', midi('G2'), b0 + 2, 2, 24)
    S.add('riser', riser(int(S.sec(8) * SR), seed=8), 30 * 4, 0)
    return S, dict(rt60=1.9, wet=0.3, bright=0.5)


# --------------------------------------------------------------------------
# render / encode / verify
# --------------------------------------------------------------------------
BUILDERS = dict(lobby=build_lobby, battle=build_battle, overtime=build_overtime,
                victory=build_victory, defeat=build_defeat,
                lobby2=build_lobby2, lobby3=build_lobby3, battle2=build_battle2, battle3=build_battle3,
                overtime2=build_overtime2)
ACCENTS = {'battle': (4, 12, 20, 28, 32), 'overtime': (4, 8, 12, 16, 20, 24, 28),
           'battle2': (3, 11, 19, 27), 'battle3': (4, 12, 20, 28, 36, 44), 'overtime2': (4, 8, 12, 16, 20, 24, 28)}
META = {'lobby': (100, 'D major'), 'battle': (135, 'F major'), 'overtime': (150, 'D minor'),
        'victory': (120, 'C major'), 'defeat': (96, 'C minor'), 'lobby2': (144, 'G major, 3/4'),
        'lobby3': (120, 'A major'), 'battle2': (140, 'G minor'), 'battle3': (288, 'G major, 6/8 (dotted-quarter 96)'),
        'overtime2': (160, 'C minor')}


def spectrogram_png(x, path, title):
    from PIL import Image, ImageDraw
    m = x.mean(axis=0)
    W, cols, rows = 4096, 960, 300
    hop = max(1, (len(m) - W) // cols)
    win = np.hanning(W)
    fr = np.fft.rfftfreq(W, 1 / SR)
    ftarget = np.geomspace(30, 18000, rows)
    bins = np.searchsorted(fr, ftarget)
    img = np.zeros((rows, cols))
    for c in range(cols):
        s = c * hop
        seg = m[s:s + W]
        if len(seg) < W:
            seg = np.pad(seg, (0, W - len(seg)))
        mag = np.abs(np.fft.rfft(seg * win))
        img[:, c] = 20 * np.log10(mag[bins] + 1e-9)
    img -= img.max()
    v = np.clip((img + 72) / 72, 0, 1)[::-1] ** 1.6
    stops = np.array([[0, 0, 0], [40, 10, 90], [170, 30, 110], [245, 120, 40], [255, 240, 160]]) / 255
    pos = v * (len(stops) - 1)
    i0 = np.minimum(pos.astype(int), len(stops) - 2)
    fr = (pos - i0)[..., None]
    rgb = stops[i0] * (1 - fr) + stops[i0 + 1] * fr
    im = Image.fromarray((rgb * 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for f in (100, 1000, 10000):
        y = rows - 1 - int(np.searchsorted(ftarget, f))
        d.line([(0, y), (12, y)], fill=(255, 255, 255))
        d.text((14, y - 6), f'{f}Hz', fill=(255, 255, 255))
    d.text((cols - 260, 4), title, fill=(255, 255, 255))
    im.save(path)


def verify(name, ogg, loop, bpm, accent_bars=(), bpb=4):
    tmp = os.path.join(HERE, f'_chk_{name}.wav')
    subprocess.run([FFMPEG, '-v', 'error', '-y', '-i', ogg, '-c:a', 'pcm_s16le', tmp], check=True)
    x = read_wav(tmp)
    os.remove(tmp)
    n = x.shape[1]
    peak = 20 * np.log10(np.abs(x).max())
    rms = 20 * np.log10(np.sqrt(np.mean(x ** 2)))
    L = lufs(x)
    info = dict(samples=n, seconds=n / SR, peak_dbfs=round(peak, 2), rms_dbfs=round(rms, 2), lufs=round(L, 2),
                kbytes=round(os.path.getsize(ogg) / 1024, 1))
    if loop:
        # Click check at the loop seam. (1) sample step across the wrap vs the 99th percentile of
        # all sample steps; (2) HF energy (2nd difference) in +-3 ms around the wrap compared with the
        # same measure at every other bar line (bar lines also carry musical onsets, so this is the
        # fair reference); 0 dB or less means the seam is no "clickier" than an ordinary downbeat.
        m = x.mean(axis=0)
        bar = bpb * 60.0 / bpm * SR
        w = int(0.003 * SR)
        circ = np.concatenate([m[-4096:], m, m[:4096]])
        d2 = np.diff(circ, 2)

        def hf(pos):
            c = pos + 4096 - 1
            return np.sqrt(np.mean(d2[c - w:c + w] ** 2))
        seam = hf(0)
        others = [hf(int(round(k * bar))) for k in range(1, int(round(n / bar)))]
        info['seam_hf_vs_barlines_db'] = round(20 * np.log10(seam / np.median(others)), 2)
        acc = [hf(int(round(k * bar))) for k in accent_bars if k]
        if acc:  # downbeats with the same accent (crash/taiko/brass hit) as the loop start
            info['seam_hf_vs_accent_bars_db'] = round(20 * np.log10(seam / np.median(acc)), 2)
        info['seam_step'] = round(float(np.abs(x[:, 0] - x[:, -1]).max()), 5)
        info['step_p99'] = round(float(np.percentile(np.abs(np.diff(x, axis=1)), 99)), 5)
        info['bars'] = round(n / SR / (bpb * 60 / bpm), 4)
    spectrogram_png(x, os.path.join(HERE, f'spec_{name}.png'), f'{name}  {n / SR:.2f}s')
    return info


def render(name):
    t0 = time.time()
    S, mx = BUILDERS[name]()
    print(f'[{name}] notes placed in {time.time() - t0:.1f}s')
    y = S.mix(**mx)
    if not S.loop:  # stinger: gentle fade of the reverb tail
        k = int(0.5 * SR)
        y[:, -k:] *= np.linspace(1, 0, k) ** 2
        y[:, :32] *= np.linspace(0, 1, 32)
    y, gr = master(y, S.loop, target=-16.0 if S.loop else -14.0)
    print(f'[{name}] mastered, max limiter GR {gr:.2f} dB, len {y.shape[1] / SR:.3f}s ({time.time() - t0:.1f}s)')
    os.makedirs(SND_DIR, exist_ok=True)
    wav = os.path.join(HERE, f'{name}.wav')
    ogg = os.path.join(SND_DIR, f'{name}.ogg')
    write_wav(wav, y)
    subprocess.run([FFMPEG, '-v', 'error', '-y', '-i', wav, '-c:a', 'libvorbis', '-q:a', '4', '-ac', '2',
                    '-ar', '44100', ogg], check=True)
    os.remove(wav)
    info = verify(name, ogg, S.loop, S.bpm, ACCENTS.get(name, ()), S.bpb)
    info['expected_samples'] = y.shape[1]
    print(f'[{name}] {json.dumps(info)}')
    return info


def write_sounds_json():
    ev = {f'bgm.{n}': {'sounds': [{'name': f'clashmc:bgm/{n}', 'stream': True}]} for n in BUILDERS}
    with open(os.path.join(HERE, 'assets', 'clashmc', 'sounds.json'), 'w') as f:
        json.dump(ev, f, indent=2)


if __name__ == '__main__':
    names = sys.argv[1:] or list(BUILDERS)
    res = {n: render(n) for n in names}
    write_sounds_json()
    print(json.dumps(res, indent=1))
