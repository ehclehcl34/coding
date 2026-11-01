package kr.kjmn.clashmc;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Random;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import org.bukkit.Bukkit;
import org.bukkit.SoundCategory;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.entity.Player;

/**
 * 배경음악: 로비 / 전투 / 연장전 반복 + 승리·패배 짧은 음악.
 * 소리 파일은 UI 리소스팩 (assets/clashmc/sounds/bgm/*.ogg, sounds.json 의 clashmc:bgm.*) 에 들어 있음.
 * 같은 분위기의 곡이 여러 개면 (lobby, lobby2, lobby3 ...) 한 곡이 끝날 때마다 다른 곡으로 바뀜.
 * 마인크래프트는 소리 길이를 알려주지 않으므로 config 의 길이(초)마다 다음 곡을 재생.
 */
final class Bgm {
    private final Clash core;
    private final Random rng = new Random();
    boolean enabled = true;
    boolean lobbyOn = true;
    boolean battleOn = true;
    boolean endOn = true;
    float volume = 0.6F;
    SoundCategory category = SoundCategory.RECORDS;
    /** 곡 이름 → 길이(초) */
    final Map<String, Double> lengths = new LinkedHashMap<>();
    /** 분위기 → 곡 목록 */
    final Map<String, List<String>> variants = new HashMap<>();
    /** 배경음악을 끈 플레이어 (plugins/ClashMC/bgm_off.txt 에 저장) */
    final Set<UUID> muted = ConcurrentHashMap.newKeySet();
    private final Map<UUID, String> playing = new HashMap<>();
    private final Map<UUID, String> playingMood = new HashMap<>();
    private final Map<UUID, Long> startedAt = new HashMap<>();
    private final Map<UUID, Long> holdUntil = new HashMap<>();
    private final Map<GameManager, Boolean> endSeen = new HashMap<>();
    private boolean mutedLoaded;

    Bgm(Clash core) {
        this.core = core;
        this.lengths.put("lobby", 76.8);
        this.lengths.put("lobby2", 70.0);
        this.lengths.put("lobby3", 72.0);
        this.lengths.put("battle", 64.0);
        this.lengths.put("battle2", 60.0);
        this.lengths.put("battle3", 60.0);
        this.lengths.put("overtime", 51.2);
        this.lengths.put("overtime2", 48.0);
        this.lengths.put("victory", 5.6);
        this.lengths.put("defeat", 4.7);
        this.rebuildVariants();
    }

    private static String moodOf(String track) {
        int i = track.length();
        while (i > 0 && Character.isDigit(track.charAt(i - 1))) {
            i--;
        }

        return track.substring(0, i);
    }

    /** 길이가 0 보다 큰 곡만 사용 (0 이면 그 곡은 끔) */
    private void rebuildVariants() {
        this.variants.clear();
        for (Map.Entry<String, Double> e : this.lengths.entrySet()) {
            if (e.getValue() > 0.0) {
                this.variants.computeIfAbsent(moodOf(e.getKey()), k -> new ArrayList<>()).add(e.getKey());
            }
        }
    }

    void load(ConfigurationSection c) {
        this.loadMuted();
        if (c == null) {
            return;
        }

        this.enabled = c.getBoolean("enabled", true);
        this.lobbyOn = c.getBoolean("lobby", true);
        this.battleOn = c.getBoolean("battle", true);
        this.endOn = c.getBoolean("victory-defeat", true);
        this.volume = (float)Math.max(0.0, Math.min(1.0, c.getDouble("volume", 0.6)));
        try {
            this.category = SoundCategory.valueOf(c.getString("category", "RECORDS").toUpperCase());
        } catch (IllegalArgumentException e) {
            this.category = SoundCategory.RECORDS;
        }

        Map<String, Double> l = new LinkedHashMap<>();
        for (String k : this.lengths.keySet()) {
            l.put(k, c.getDouble("length." + k, this.lengths.get(k)));
        }

        // config 에 직접 추가한 곡 (예: length.lobby4: 70)
        ConfigurationSection ls = c.getConfigurationSection("length");
        if (ls != null) {
            for (String k : ls.getKeys(false)) {
                l.put(k, ls.getDouble(k, 0.0));
            }
        }

        this.lengths.putAll(l);
        this.rebuildVariants();
        if (!this.enabled) {
            this.stopAll();
        }
    }

    private File mutedFile() {
        return new File(this.core.plugin.getDataFolder(), "bgm_off.txt");
    }

    private void loadMuted() {
        if (this.mutedLoaded) {
            return;
        }

        this.mutedLoaded = true;
        try {
            File f = this.mutedFile();
            if (f.exists()) {
                for (String line : Files.readAllLines(f.toPath(), StandardCharsets.UTF_8)) {
                    try {
                        if (!line.isBlank()) {
                            this.muted.add(UUID.fromString(line.trim()));
                        }
                    } catch (IllegalArgumentException ignored) {
                    }
                }
            }
        } catch (Exception e) {
            this.core.plugin.getLogger().warning("bgm_off.txt 읽기 실패: " + e);
        }
    }

    private void saveMuted() {
        try {
            List<String> lines = new ArrayList<>();
            for (UUID u : this.muted) {
                lines.add(u.toString());
            }

            File f = this.mutedFile();
            f.getParentFile().mkdirs();
            Files.write(f.toPath(), lines, StandardCharsets.UTF_8);
        } catch (Exception e) {
            this.core.plugin.getLogger().warning("bgm_off.txt 저장 실패: " + e);
        }
    }

    private static String key(String track) {
        return "clashmc:bgm." + track;
    }

    /** 이 플레이어가 지금 들어야 하는 분위기 (없으면 null) */
    private String want(Player p) {
        GameManager m = this.core.matchOf(p);
        if (m != null) {
            switch (m.phase) {
                case PLAYING:
                    return this.battleOn ? (m.overtime ? "overtime" : "battle") : null;
                case DECK:
                case ENDING:
                    // 매칭 잡히고 시작 기다리는 동안 / 끝난 뒤에는 조용히
                    return null;
                default:
                    return this.lobbyOn ? "lobby" : null;
            }
        }

        return this.lobbyOn ? "lobby" : null;
    }

    /** 분위기에 맞는 곡 하나 (방금 튼 곡은 피함) */
    private String pick(String mood, String last) {
        List<String> v = this.variants.get(mood);
        if (v == null || v.isEmpty()) {
            return mood;
        }

        if (v.size() == 1) {
            return v.get(0);
        }

        String t;
        do {
            t = v.get(this.rng.nextInt(v.size()));
        } while (t.equals(last));

        return t;
    }

    /** 10틱마다 */
    void tick() {
        if (!this.enabled) {
            return;
        }

        this.checkEnds();
        long now = System.currentTimeMillis();
        for (Player p : Bukkit.getOnlinePlayers()) {
            UUID id = p.getUniqueId();
            Long hold = this.holdUntil.get(id);
            if (hold != null) {
                if (now < hold) {
                    continue;
                }

                this.holdUntil.remove(id);
                this.playing.remove(id);
                this.playingMood.remove(id);
            }

            String want = this.muted.contains(id) ? null : this.want(p);
            String mood = this.playingMood.get(id);
            String cur = this.playing.get(id);
            if (!Objects.equals(mood, want)) {
                if (cur != null) {
                    this.stop(p, cur);
                }

                if (want != null) {
                    this.start(p, want, this.pick(want, null), now);
                } else {
                    this.playing.remove(id);
                    this.playingMood.remove(id);
                }
            } else if (want != null && cur != null) {
                double len = this.lengths.getOrDefault(cur, 0.0);
                Long st = this.startedAt.get(id);
                if (len > 0.0 && st != null && now - st >= (long)(len * 1000.0) - 60L) {
                    this.stop(p, cur);
                    this.start(p, want, this.pick(want, cur), now);
                }
            }
        }

        this.playing.keySet().removeIf(u -> Bukkit.getPlayer(u) == null);
        this.playingMood.keySet().removeIf(u -> Bukkit.getPlayer(u) == null);
        this.startedAt.keySet().removeIf(u -> Bukkit.getPlayer(u) == null);
        this.holdUntil.keySet().removeIf(u -> Bukkit.getPlayer(u) == null);
    }

    /** 경기가 끝나는 순간 승리/패배 음악 */
    private void checkEnds() {
        this.endSeen.keySet().removeIf(m -> !this.core.matches.contains(m));
        for (GameManager m : this.core.matches) {
            boolean ending = m.phase == GameManager.Phase.ENDING;
            Boolean was = this.endSeen.put(m, ending);
            if (ending && !Boolean.TRUE.equals(was)) {
                for (GameTeam t : m.teams.values()) {
                    for (UUID u : t.members) {
                        Player p = Bukkit.getPlayer(u);
                        if (p != null) {
                            this.stinger(p, m.winner == null ? null : m.winner == t.color);
                        }
                    }
                }
            }
        }
    }

    private void start(Player p, String mood, String track, long now) {
        p.playSound(p, key(track), this.category, this.volume, 1.0F);
        this.playing.put(p.getUniqueId(), track);
        this.playingMood.put(p.getUniqueId(), mood);
        this.startedAt.put(p.getUniqueId(), now);
    }

    private void stop(Player p, String track) {
        p.stopSound(key(track), this.category);
    }

    /** win: true 승리 / false 패배 / null 무승부(음악 없음) */
    void stinger(Player p, Boolean win) {
        UUID id = p.getUniqueId();
        String cur = this.playing.remove(id);
        this.playingMood.remove(id);
        if (cur != null) {
            this.stop(p, cur);
        }

        if (!this.enabled || !this.endOn || win == null || this.muted.contains(id)) {
            return;
        }

        String k = win ? "victory" : "defeat";
        p.playSound(p, key(k), this.category, Math.min(1.0F, this.volume + 0.2F), 1.0F);
        this.playing.put(id, k);
        this.playingMood.put(id, k);
        this.holdUntil.put(id, System.currentTimeMillis() + (long)(this.lengths.getOrDefault(k, 5.0) * 1000.0) + 2500L);
    }

    /** 리소스팩이 방금 적용됨 → 지금 곡을 처음부터 (팩 적용 전에 튼 소리는 안 들렸으므로) */
    void restart(Player p) {
        UUID id = p.getUniqueId();
        if (this.holdUntil.containsKey(id)) {
            return;
        }

        String cur = this.playing.remove(id);
        this.playingMood.remove(id);
        if (cur != null) {
            this.stop(p, cur);
        }
    }

    /** 켜고 끄기, 켜졌으면 true (저장됨) */
    boolean toggle(Player p) {
        UUID id = p.getUniqueId();
        boolean on;
        if (this.muted.remove(id)) {
            on = true;
        } else {
            this.muted.add(id);
            String cur = this.playing.remove(id);
            this.playingMood.remove(id);
            if (cur != null) {
                this.stop(p, cur);
            }

            this.holdUntil.remove(id);
            on = false;
        }

        this.saveMuted();
        p.sendMessage(on ? "§6[클래시] §f배경음악 §a켜짐" : "§6[클래시] §f배경음악 §c꺼짐 §7(메뉴의 ♫ 버튼 또는 /clash bgm 으로 다시 켜기)");
        return on;
    }

    void stopAll() {
        for (Map.Entry<UUID, String> e : this.playing.entrySet()) {
            Player p = Bukkit.getPlayer(e.getKey());
            if (p != null) {
                this.stop(p, e.getValue());
            }
        }

        this.playing.clear();
        this.playingMood.clear();
        this.startedAt.clear();
        this.holdUntil.clear();
    }

    void quit(Player p) {
        this.playing.remove(p.getUniqueId());
        this.playingMood.remove(p.getUniqueId());
        this.startedAt.remove(p.getUniqueId());
        this.holdUntil.remove(p.getUniqueId());
    }
}
