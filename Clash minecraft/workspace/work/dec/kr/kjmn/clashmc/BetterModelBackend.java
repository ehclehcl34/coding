package kr.kjmn.clashmc;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Predicate;
import java.util.logging.Logger;
import org.bukkit.Color;
import org.bukkit.entity.Entity;
import org.bukkit.entity.LivingEntity;

final class BetterModelBackend {
    private final Logger log;
    private final Class<?> api;
    private final Class<?> adapter;
    private final Class<?> actionCls;
    private final Class<?> modifierCls;
    private final Object playOnce;
    private final Object playDefault;
    private final Map<UUID, Object> trackers = new HashMap<>();
    private boolean warned;
    private final Set<String> missingWarned = new HashSet<>();
    /** 다시 만들 때 쓰는 적용 정보 {Entity, 모델 이름, 숨길 본 조건, 팀 색} */
    private final Map<UUID, Object[]> applyArgs = new HashMap<>();
    /** 모델이 만들어진 시각 (ms) */
    private final Map<UUID, Long> born = new HashMap<>();
    /** 연속으로 이상하다고 판단된 횟수 */
    private final Map<UUID, Integer> strikes = new HashMap<>();
    private int rebuilt;
    /** 테두리 발광 색 (모델을 다시 만들 때도 유지) */
    private final Map<UUID, Integer> glowRgb = new HashMap<>();
    /** 원본 스킨 보기용 기본 모델 트래커 (스킨 모델과 같은 엔티티에 겹쳐 둠) */
    private final Map<UUID, Object> alts = new HashMap<>();
    private final Map<UUID, Object[]> altArgs = new HashMap<>();
    private final Map<UUID, Integer> altStrikes = new HashMap<>();
    /** deploy 재생 중인 엔티티 → 재생 번호 (끝나면 지움) */
    private final Map<UUID, Long> deploying = new HashMap<>();
    /** deploy 중에 들어온 애니메이션 (끝나면 순서대로 실행, 같은 키는 마지막 것만) */
    private final Map<UUID, java.util.LinkedHashMap<String, Runnable>> waiting = new HashMap<>();
    private long deploySeq;
    /** 이 플레이어가 원본 스킨으로 보는지 */
    Predicate<UUID> wantsOriginal = id -> false;

    BetterModelBackend(Logger var1) throws Exception {
        this.log = var1;
        this.api = Class.forName("kr.toxicity.model.api.BetterModel");
        this.adapter = Class.forName("kr.toxicity.model.api.bukkit.platform.BukkitAdapter");
        this.actionCls = Class.forName("kr.toxicity.model.api.tracker.TrackerUpdateAction");
        this.modifierCls = Class.forName("kr.toxicity.model.api.animation.AnimationModifier");
        this.playOnce = this.modifierCls.getField("DEFAULT_WITH_PLAY_ONCE").get(null);

        Object var2;
        try {
            var2 = this.modifierCls.getField("DEFAULT").get(null);
        } catch (Throwable var4) {
            var2 = this.playOnce;
        }

        this.playDefault = var2;
    }

    boolean apply(Entity var1, String var2, Predicate<String> var3, Color var4) {
        Object t = this.build(var1, var2, var3, var4);
        if (t == null) {
            return false;
        }
        this.trackers.put(var1.getUniqueId(), t);
        this.applyArgs.put(var1.getUniqueId(), new Object[]{var1, var2, var3, var4});
        this.born.put(var1.getUniqueId(), System.currentTimeMillis());
        if (this.alts.containsKey(var1.getUniqueId())) {
            this.viewAll(var1.getUniqueId());
        }
        return true;
    }

    /** 원본 스킨 보기용 기본 모델 겹치기 (스킨 모델이 먼저 적용된 엔티티에만) */
    boolean applyAlt(Entity e, String model, Predicate<String> pred, Color c) {
        this.dropAlt(e);
        if (!this.trackers.containsKey(e.getUniqueId())) {
            return false;
        }
        Object t = this.build(e, model, pred, c);
        if (t == null) {
            return false;
        }
        this.alts.put(e.getUniqueId(), t);
        this.altArgs.put(e.getUniqueId(), new Object[]{e, model, pred, c});
        this.viewAll(e.getUniqueId());
        return true;
    }

    void dropAlt(Entity e) {
        if (e == null) {
            return;
        }
        this.altArgs.remove(e.getUniqueId());
        this.altStrikes.remove(e.getUniqueId());
        Object a = this.alts.remove(e.getUniqueId());
        if (a != null) {
            try {
                a.getClass().getMethod("close").invoke(a);
            } catch (Throwable ignored) {
            }
            // 원본으로 보던 사람에게 숨겨 둔 스킨 모델 다시 보이기
            Object t = this.trackers.get(e.getUniqueId());
            if (t != null) {
                for (org.bukkit.entity.Player p : org.bukkit.Bukkit.getOnlinePlayers()) {
                    if (!p.equals(e)) {
                        this.vis(t, true, this.pp(p));
                    }
                }
            }
        }
    }

    /** 플레이어 한 명 기준으로 모든 겹친 모델 다시 정리 (설정 바꿨을 때 / 접속했을 때) */
    void refreshViewer(org.bukkit.entity.Player p) {
        Object pp = this.pp(p);
        if (pp == null) {
            return;
        }
        for (UUID id : new java.util.ArrayList<>(this.alts.keySet())) {
            this.view(id, p, pp);
        }
    }

    private void viewAll(UUID id) {
        for (org.bukkit.entity.Player p : org.bukkit.Bukkit.getOnlinePlayers()) {
            Object pp = this.pp(p);
            if (pp != null) {
                this.view(id, p, pp);
            }
        }
    }

    private void view(UUID id, org.bukkit.entity.Player p, Object pp) {
        Object t = this.trackers.get(id);
        Object a = this.alts.get(id);
        if (t == null || a == null || p.getUniqueId().equals(id)) {
            return;   // 자기 자신 모델은 selfView 가 처리
        }
        boolean orig = this.wantsOriginal.test(p.getUniqueId());
        this.vis(t, !orig, pp);
        this.vis(a, orig, pp);
    }

    private Object pp(Entity e) {
        try {
            for (Method m : this.adapter.getMethods()) {
                if (m.getName().equals("adapt") && Modifier.isStatic(m.getModifiers()) && m.getParameterCount() == 1
                    && m.getParameterTypes()[0].isInstance(e) && m.getReturnType().getSimpleName().equals("PlatformPlayer")) {
                    return m.invoke(null, e);
                }
            }
            return this.adapter.getMethod("adapt", Entity.class).invoke(null, e);
        } catch (Throwable ex) {
            return null;
        }
    }

    private void vis(Object t, boolean show, Object pp) {
        if (pp == null) {
            return;
        }
        String n = show ? "show" : "hide";
        try {
            for (Method m : t.getClass().getMethods()) {
                if (m.getName().equals(n) && m.getParameterCount() == 1 && m.getParameterTypes()[0].isInstance(pp)) {
                    m.invoke(t, pp);
                    return;
                }
            }
        } catch (Throwable ex) {
            this.warn("BetterModel 원본 스킨 표시 실패: " + ex);
        }
    }

    /** 이 엔티티에 붙은 트래커 전부 (스킨 + 겹친 기본 모델) */
    private java.util.List<Object> all(Entity e) {
        java.util.List<Object> l = new java.util.ArrayList<>(2);
        if (e == null) {
            return l;
        }
        Object t = this.trackers.get(e.getUniqueId());
        if (t != null) {
            l.add(t);
        }
        Object a = this.alts.get(e.getUniqueId());
        if (a != null) {
            l.add(a);
        }
        return l;
    }

    /** 플레이어는 눈높이 때문에 scale 을 키우므로, 모델은 1배로 고정해서 AI 유닛과 같은 크기로 */
    private void fixScale(Object t) {
        try {
            Class<?> sc = Class.forName("kr.toxicity.model.api.tracker.ModelScaler");
            Object one = sc.getMethod("value", float.class).invoke(null, 1.0F);
            t.getClass().getMethod("scaler", sc).invoke(t, one);
        } catch (Throwable ex) {
            this.warn("BetterModel 모델 크기 고정 실패: " + ex);
        }
    }

    private boolean hitboxWarned;

    /** 모델의 BetterModel 히트박스 전부 제거 */
    private void dropHitboxes(Object t) {
        try {
            java.lang.reflect.Field f = null;
            for (Class<?> c = t.getClass(); c != null && f == null; c = c.getSuperclass()) {
                try {
                    f = c.getDeclaredField("pipeline");
                } catch (NoSuchFieldException ignored) {
                }
            }
            if (f == null) {
                return;
            }
            f.setAccessible(true);
            Object p = f.get(t);
            if (p == null) {
                return;
            }
            Object st = p.getClass().getMethod("hitboxes").invoke(p);
            Method rm = Class.forName("kr.toxicity.model.api.nms.HitBox").getMethod("removeHitBox");
            for (Object hb : ((java.util.stream.Stream<?>)st).toList()) {
                if (hb != null) {
                    rm.invoke(hb);
                }
            }
        } catch (Throwable ex) {
            if (!this.hitboxWarned) {
                this.hitboxWarned = true;
                this.warn("BetterModel 히트박스 제거 실패: " + ex);
            }
        }
    }

    private Object build(Entity var1, String var2, Predicate<String> var3, Color var4) {
        try {
            if (this.api.getMethod("model", String.class).invoke(null, var2) instanceof Optional var6 && !var6.isEmpty()) {
                if (var1 instanceof LivingEntity var7) {
                    var7.setInvisible(false);
                }

                Object var15 = var6.get();
                Object var8 = this.adapter.getMethod("adapt", Entity.class).invoke(null, var1);
                Method var9 = null;

                for (Method var13 : var15.getClass().getMethods()) {
                    if (var13.getName().equals("create") && var13.getParameterCount() == 1 && var13.getParameterTypes()[0].isInstance(var8)) {
                        var9 = var13;
                        break;
                    }
                }

                if (var9 == null) {
                    throw new NoSuchMethodException("ModelRenderer#create(PlatformEntity)");
                } else {
                    Object var16 = var9.invoke(var15, var8);
                    if (var16 == null) {
                        return null;
                    } else {
                        this.update(var16, this.toggle(false), var3);
                        if (var4 != null) {
                            int var17 = var4.asRGB();
                            this.update(var16, this.staticAction("tint", int.class, var17), var0 -> var0.contains("tc_"));
                            int soft = var17 == TeamColor.BLUE.color.asRGB() ? 0x4EC0C8 : 0xF06048;   // soft team colour for ts_ bones
                            this.update(var16, this.staticAction("tint", int.class, soft), var0 -> var0.contains("ts_"));
                        }

                        Integer g = this.glowRgb.get(var1.getUniqueId());
                        if (g != null) {
                            this.applyGlow(var16, g);
                        }

                        if (var1 instanceof org.bukkit.entity.Player) {
                            this.fixScale(var16);
                        }

                        if (var1 instanceof org.bukkit.entity.ArmorStand
                            || var1.getScoreboardTags() != null && var1.getScoreboardTags().contains("clashmc_nohit")) {
                            // 아머스탠드에 붙는 모델 (투사체·효과·타워·건물 장식): BetterModel 히트박스가 있으면
                            // 플레이어 공격이 거기에 막힘 → 지움 (늦게 생기는 것까지 한 번 더). 클릭 판정은 따로 Interaction 으로 함
                            Object hbT = var16;
                            this.dropHitboxes(hbT);
                            this.later(2L, () -> this.dropHitboxes(hbT));
                        }

                        return var16;
                    }
                }
            } else {
                return null;
            }
        } catch (Throwable var14) {
            this.warn("BetterModel 모델 적용 실패 (" + var2 + "): " + var14);
            return null;
        }
    }

    /** 플레이어 자신에게 자기 모델 보이기/숨기기 (BetterModel 은 원래 본인에게는 안 보냄) */
    void selfView(Entity e, boolean show) {
        if (!(e instanceof org.bukkit.entity.Player)) {
            return;
        }
        Object t = this.trackers.get(e.getUniqueId());
        if (t == null) {
            return;
        }
        Object alt = this.alts.get(e.getUniqueId());
        if (alt != null) {
            Object me = this.pp(e);
            boolean orig = this.wantsOriginal.test(e.getUniqueId());
            this.vis(t, show && !orig, me);
            this.vis(alt, show && orig, me);
            if (show) {
                try {
                    Object reg = t.getClass().getMethod("registry").invoke(t);
                    for (Method m : reg.getClass().getMethods()) {
                        if (m.getName().equals("spawnIfNotSpawned") && m.getParameterCount() == 1 && m.getParameterTypes()[0].isInstance(me)) {
                            m.invoke(reg, me);
                            break;
                        }
                    }
                } catch (Throwable ex) {
                    this.warn("BetterModel 자기 모델 표시 실패: " + ex);
                }
            }
            return;
        }
        try {
            Object pp = null;
            for (Method m : this.adapter.getMethods()) {
                if (m.getName().equals("adapt") && Modifier.isStatic(m.getModifiers()) && m.getParameterCount() == 1
                    && m.getParameterTypes()[0].isInstance(e) && m.getReturnType().getSimpleName().equals("PlatformPlayer")) {
                    pp = m.invoke(null, e);
                    break;
                }
            }
            if (pp == null) {
                pp = this.adapter.getMethod("adapt", Entity.class).invoke(null, e);
            }
            String vis = show ? "show" : "hide";
            for (Method m : t.getClass().getMethods()) {
                if (m.getName().equals(vis) && m.getParameterCount() == 1 && m.getParameterTypes()[0].isInstance(pp)) {
                    m.invoke(t, pp);
                    break;
                }
            }
            if (!show) {
                return;
            }
            Object reg = t.getClass().getMethod("registry").invoke(t);
            for (Method m : reg.getClass().getMethods()) {
                if (m.getName().equals("spawnIfNotSpawned") && m.getParameterCount() == 1 && m.getParameterTypes()[0].isInstance(pp)) {
                    m.invoke(reg, pp);
                    return;
                }
            }
        } catch (Throwable ex) {
            this.warn("BetterModel 자기 모델 표시 실패: " + ex);
        }
    }

    /** 본 보이기/숨기기 (이름이 정확히 같은 본) */
    void part(Entity e, String bone, boolean show) {
        for (Object t : this.all(e)) {
            try {
                this.update(t, this.toggle(show), s -> s.equals(bone));
            } catch (Throwable ex) {
                this.warn("BetterModel 본 표시 실패: " + ex);
            }
        }
    }

    /** 모델 전체 숨기기/보이기 (원래 숨겨 둔 본·hitbox 는 계속 숨김) */
    @SuppressWarnings("unchecked")
    void visible(Entity e, boolean show) {
        if (e == null) {
            return;
        }
        for (int i = 0; i < 2; i++) {
            Object t = (i == 0 ? this.trackers : this.alts).get(e.getUniqueId());
            if (t == null) {
                continue;
            }
            Object[] a = (i == 0 ? this.applyArgs : this.altArgs).get(e.getUniqueId());
            Predicate<String> hidden = a != null && a[2] instanceof Predicate<?> p ? (Predicate<String>)p : s -> false;
            try {
                this.update(t, this.toggle(show), s -> !show || (!hidden.test(s) && !s.equals("hitbox")));
            } catch (Throwable ex) {
                this.warn("BetterModel 모델 숨기기 실패: " + ex);
            }
        }
    }

    void glow(Entity e, Color c) {
        if (!this.trackers.containsKey(e.getUniqueId())) {
            return;
        }
        int rgb = c.asRGB();
        this.glowRgb.put(e.getUniqueId(), rgb);
        for (Object t : this.all(e)) {
            try {
                this.applyGlow(t, rgb);
            } catch (Throwable ex) {
                this.warn("BetterModel 발광 실패: " + ex);
            }
        }
    }

    private void applyGlow(Object t, int rgb) throws Exception {
        this.update(t, this.staticAction("glow", boolean.class, true), s -> true);
        this.update(t, this.staticAction("glowColor", int.class, rgb), s -> true);
    }

    boolean exists(String var1) {
        try {
            return this.api.getMethod("model", String.class).invoke(null, var1) instanceof Optional var3 && var3.isPresent();
        } catch (Throwable var4) {
            return false;
        }
    }

    boolean anim(Entity var1, String var2) {
        if (var1 == null) {
            return false;
        }
        UUID id = var1.getUniqueId();
        boolean dep = var2.equals("deploy") || var2.equals("spawn");
        if (dep) {
            if (!this.trackers.containsKey(id)) {
                return false;
            }
            long tok = ++this.deploySeq;
            this.deploying.put(id, tok);
            this.waiting.remove(id);
            // 안전장치: 콜백이 안 오면 8초 뒤 강제로 대기열 실행
            this.later(160L, () -> this.endDeploy(id, tok));
            boolean ok = false;
            for (Object t : this.all(var1)) {
                ok |= this.animOne(t, var2, t == this.trackers.get(id) ? id : null, tok);
            }
            if (!ok) {
                this.endDeploy(id, tok);
            }
            return ok;
        }
        if (this.deploying.containsKey(id)) {
            if (var2.equals("death")) {
                // 죽으면 바로 (deploy 무시)
                this.deploying.remove(id);
                this.waiting.remove(id);
            } else if (var2.equals("hit")) {
                return true;   // 피격 모션은 deploy 를 끊으므로 생략
            } else {
                this.queue(id, "anim:" + var2, () -> this.anim(var1, var2));
                return true;
            }
        }
        boolean ok = false;
        for (Object t : this.all(var1)) {
            ok |= this.animOne(t, var2, null, 0L);
        }
        return ok;
    }

    private void queue(UUID id, String key, Runnable r) {
        java.util.LinkedHashMap<String, Runnable> q = this.waiting.computeIfAbsent(id, k -> new java.util.LinkedHashMap<>());
        q.remove(key);
        if (key.startsWith("hold:")) {
            // 상태 애니메이션은 마지막 것 하나만
            q.keySet().removeIf(k -> k.startsWith("hold:"));
        }
        q.put(key, r);
    }

    /** deploy 끝 → 기다리던 애니메이션 실행 (메인 스레드에서) */
    private void endDeploy(UUID id, long tok) {
        Runnable run = () -> {
            Long cur = this.deploying.get(id);
            if (cur == null || cur != tok) {
                return;
            }
            this.deploying.remove(id);
            java.util.LinkedHashMap<String, Runnable> q = this.waiting.remove(id);
            if (q != null) {
                for (Runnable r : q.values()) {
                    try {
                        r.run();
                    } catch (Throwable ex) {
                        this.warn("대기 애니메이션 실패: " + ex);
                    }
                }
            }
        };
        if (org.bukkit.Bukkit.isPrimaryThread()) {
            run.run();
        } else {
            this.later(0L, run);
        }
    }

    private void later(long ticks, Runnable r) {
        org.bukkit.plugin.Plugin pl = org.bukkit.Bukkit.getPluginManager().getPlugin("ClashMC");
        if (pl != null && pl.isEnabled()) {
            if (ticks <= 0L) {
                org.bukkit.Bukkit.getScheduler().runTask(pl, r);
            } else {
                org.bukkit.Bukkit.getScheduler().runTaskLater(pl, r, ticks);
            }
        }
    }

    private boolean animOne(Object var3, String var2, UUID cbId, long tok) {
        if (var3 == null) {
            return false;
        } else {
            try {
                Method var4 = var3.getClass().getMethod("animate", String.class, this.modifierCls);
                if (var2.equals("deploy") || var2.equals("spawn")) {
                    // 트래커가 아직 플레이어에게 안 보였으면 기본 idle 이 나중에 들어와 소환 모션을 덮음
                    // → 트래커 다음 틱(기본 애니메이션 등록 뒤)에 재생
                    // 끝나면(콜백) 기다리던 애니메이션 실행
                    Object t = var3;
                    long asked = System.currentTimeMillis();
                    Method withEnd = var3.getClass().getMethod("animate", String.class, this.modifierCls, Runnable.class);
                    Runnable done = cbId == null ? () -> {} : () -> this.endDeploy(cbId, tok);
                    Runnable play = () -> {
                        try {
                            boolean ok = System.currentTimeMillis() - asked < 2500L
                                && Boolean.TRUE.equals(withEnd.invoke(t, var2, this.playOnce, done));
                            if (!ok) {
                                done.run();   // deploy 없는 모델 → 바로 다음 애니메이션
                            }
                        } catch (Throwable ignored) {
                            done.run();
                        }
                    };
                    try {
                        var3.getClass().getMethod("task", Runnable.class).invoke(var3, play);
                    } catch (NoSuchMethodException ignored) {
                        play.run();
                    }
                    return true;
                }
                var4.invoke(var3, var2, this.playOnce);
                return true;
            } catch (Throwable var5) {
                this.warn("BetterModel 애니메이션 실패 (" + var2 + "): " + var5);
                return false;
            }
        }
    }

    boolean animHold(Entity var1, String var2) {
        if (var1 != null && this.deploying.containsKey(var1.getUniqueId())) {
            this.queue(var1.getUniqueId(), "hold:" + var2, () -> this.animHold(var1, var2));
            return true;
        }
        boolean ok = false;
        for (Object var3 : this.all(var1)) {
            try {
                var3.getClass().getMethod("animate", String.class, this.modifierCls).invoke(var3, var2, this.playDefault);
                ok = true;
            } catch (Throwable var5) {
                this.warn("BetterModel 애니메이션 실패 (" + var2 + "): " + var5);
            }
        }
        return ok;
    }

    void stop(Entity var1, String var2) {
        if (var1 != null && !var2.equals("deploy") && !var2.equals("spawn") && this.deploying.containsKey(var1.getUniqueId())) {
            java.util.LinkedHashMap<String, Runnable> q = this.waiting.get(var1.getUniqueId());
            if (q != null && q.remove("hold:" + var2) != null) {
                return;   // 아직 시작도 안 한 상태 애니메이션 → 취소만
            }
            this.queue(var1.getUniqueId(), "stop:" + var2, () -> this.stop(var1, var2));
            return;
        }
        for (Object var3 : this.all(var1)) {
            try {
                var3.getClass().getMethod("stopAnimation", String.class).invoke(var3, var2);
            } catch (Throwable var5) {
            }
        }
    }

    void hide(Entity e, Predicate<String> pred) {
        Object alt = e == null ? null : this.alts.get(e.getUniqueId());
        if (alt != null) {
            try {
                this.update(alt, this.toggle(false), pred);
                Object[] a = this.altArgs.get(e.getUniqueId());
                if (a != null && a[2] instanceof Predicate<?> old) {
                    @SuppressWarnings("unchecked")
                    Predicate<String> o = (Predicate<String>)old;
                    a[2] = o.or(pred);
                }
            } catch (Throwable ex) {
                this.warn("BetterModel 본 숨기기 실패: " + ex);
            }
        }
        Object t = e == null ? null : this.trackers.get(e.getUniqueId());
        if (t != null) {
            try {
                this.update(t, this.toggle(false), pred);
                Object[] a = this.applyArgs.get(e.getUniqueId());
                if (a != null && a[2] instanceof Predicate<?> old) {
                    // 모델을 다시 만들 때도 숨긴 채로
                    @SuppressWarnings("unchecked")
                    Predicate<String> o = (Predicate<String>)old;
                    a[2] = o.or(pred);
                }
            } catch (Throwable ex) {
                this.warn("BetterModel 본 숨기기 실패: " + ex);
            }
        }
    }

    void remove(Entity var1) {
        if (var1 != null) {
            this.deploying.remove(var1.getUniqueId());
            this.waiting.remove(var1.getUniqueId());
            this.altArgs.remove(var1.getUniqueId());
            this.altStrikes.remove(var1.getUniqueId());
            Object alt = this.alts.remove(var1.getUniqueId());
            if (alt != null) {
                try {
                    alt.getClass().getMethod("close").invoke(alt);
                } catch (Throwable ignored) {
                }
            }
            this.applyArgs.remove(var1.getUniqueId());
            this.glowRgb.remove(var1.getUniqueId());
            this.born.remove(var1.getUniqueId());
            this.strikes.remove(var1.getUniqueId());
        }
        Object var2 = var1 == null ? null : this.trackers.remove(var1.getUniqueId());
        if (var2 != null) {
            try {
                var2.getClass().getMethod("close").invoke(var2);
            } catch (Throwable var4) {
                this.warn("BetterModel 제거 실패: " + var4);
            }
        }
    }

    void clear() {
        for (Object var2 : this.trackers.values()) {
            try {
                var2.getClass().getMethod("close").invoke(var2);
            } catch (Throwable var4) {
            }
        }

        for (Object a : this.alts.values()) {
            try {
                a.getClass().getMethod("close").invoke(a);
            } catch (Throwable ignored) {
            }
        }

        this.deploying.clear();
        this.waiting.clear();
        this.alts.clear();
        this.altArgs.clear();
        this.altStrikes.clear();
        this.trackers.clear();
        this.applyArgs.clear();
        this.glowRgb.clear();
        this.born.clear();
        this.strikes.clear();
    }

    boolean isEmpty() {
        return this.trackers.isEmpty();
    }

    int rebuiltCount() {
        return this.rebuilt;
    }

    private static Object call0(Object o, String name) {
        try {
            return o.getClass().getMethod(name).invoke(o);
        } catch (Throwable e) {
            return null;
        }
    }

    /**
     * 모델 멈춤 감시 (10틱마다).
     * BetterModel 트래커는 보는 플레이어가 0명이 되는 순간 애니메이션 스케줄러를 끄는데, 같은 순간 플레이어가 다시
     * 보이기 시작하면 스케줄러가 꺼진 채로 남아 첫 프레임(소환 모션 1프레임)에서 그대로 굳음.
     * → 보는 사람이 있는데 스케줄러가 꺼져 있거나, 소환 모션이 몇 초 넘게 계속되면 모델을 새로 만들어 복구.
     */
    void watchdog() {
        long nowMs = System.currentTimeMillis();
        for (Map.Entry<UUID, Object> en : new java.util.ArrayList<>(this.trackers.entrySet())) {
            UUID id = en.getKey();
            Object t = en.getValue();
            Object[] a = this.applyArgs.get(id);
            if (a == null || !(a[0] instanceof Entity e) || !e.isValid()) {
                continue;
            }

            long age = nowMs - this.born.getOrDefault(id, nowMs);
            if (age < 1500L) {
                continue;
            }

            boolean bad = false;
            boolean stuckDeploy = false;
            if (Boolean.TRUE.equals(call0(t, "isClosed"))) {
                bad = true;
            } else {
                Object pc = call0(t, "playerCount");
                Object sch = call0(t, "isScheduled");
                if (pc instanceof Integer n && n > 0 && Boolean.FALSE.equals(sch)) {
                    bad = true;
                } else if (age > 5000L && this.runningDeploy(t)) {
                    bad = true;
                    stuckDeploy = true;
                }
            }

            if (!bad) {
                this.strikes.remove(id);
                continue;
            }

            int s = this.strikes.merge(id, 1, Integer::sum);
            if (stuckDeploy && s == 1) {
                // 1차: 소환 모션만 멈춰봄 (idle 이 있으면 바로 풀림)
                this.stop(e, "deploy");
                this.stop(e, "spawn");
            } else if (s >= 2) {
                this.rebuild(id);
            }
        }

        // 겹친 기본 모델도 똑같이 감시
        for (Map.Entry<UUID, Object> en : new java.util.ArrayList<>(this.alts.entrySet())) {
            UUID id = en.getKey();
            Object t = en.getValue();
            Object[] a = this.altArgs.get(id);
            if (a == null || !(a[0] instanceof Entity e) || !e.isValid()) {
                continue;
            }
            long age = nowMs - this.born.getOrDefault(id, nowMs);
            if (age < 1500L) {
                continue;
            }
            boolean bad = Boolean.TRUE.equals(call0(t, "isClosed"));
            if (!bad) {
                Object pc = call0(t, "playerCount");
                Object sch = call0(t, "isScheduled");
                bad = pc instanceof Integer n && n > 0 && Boolean.FALSE.equals(sch) || age > 5000L && this.runningDeploy(t);
            }
            if (!bad) {
                this.altStrikes.remove(id);
                continue;
            }
            if (this.altStrikes.merge(id, 1, Integer::sum) >= 2) {
                this.altStrikes.remove(id);
                this.rebuilt++;
                @SuppressWarnings("unchecked")
                Predicate<String> pr = (Predicate<String>)a[2];
                this.applyAlt(e, (String)a[1], pr, (Color)a[3]);
            }
        }
    }

    private boolean runningDeploy(Object t) {
        Object bones = call0(t, "bones");
        if (!(bones instanceof java.util.Collection<?> c)) {
            return false;
        }

        for (Object b : c) {
            Object ra = call0(b, "runningAnimation");
            if (ra != null) {
                Object n = call0(ra, "name");
                if ("deploy".equals(n) || "spawn".equals(n)) {
                    return true;
                }
            }
        }

        return false;
    }

    @SuppressWarnings("unchecked")
    private void rebuild(UUID id) {
        Long dt = this.deploying.get(id);
        if (dt != null) {
            this.later(1L, () -> this.endDeploy(id, dt));   // 새 모델 만든 다음 틱에
        }
        Object[] a = this.applyArgs.get(id);
        Object old = this.trackers.remove(id);
        this.strikes.remove(id);
        if (old != null) {
            try {
                old.getClass().getMethod("close").invoke(old);
            } catch (Throwable ignored) {
            }
        }

        if (a != null && a[0] instanceof Entity e && e.isValid()) {
            this.rebuilt++;
            if (!this.apply(e, (String)a[1], (Predicate<String>)a[2], (Color)a[3])) {
                this.applyArgs.remove(id);
            }
        }
    }

    private Object toggle(boolean var1) throws Exception {
        return this.staticAction("togglePart", boolean.class, var1);
    }

    private Object staticAction(String var1, Class<?> var2, Object var3) throws Exception {
        Method var4 = this.actionCls.getMethod(var1, var2);
        if (!Modifier.isStatic(var4.getModifiers())) {
            throw new NoSuchMethodException(var1);
        } else {
            return var4.invoke(null, var3);
        }
    }

    private void update(Object var1, Object var2, Predicate<String> var3) throws Exception {
        Method var4 = null;

        for (Method var8 : var1.getClass().getMethods()) {
            if (var8.getName().equals("update") && var8.getParameterCount() == 2 && var8.getParameterTypes()[1] == Predicate.class) {
                var4 = var8;
                break;
            }
        }

        if (var4 == null) {
            throw new NoSuchMethodException("Tracker#update(action, Predicate)");
        } else {
            Predicate var9 = var1x -> {
                try {
                    Object var2x = var1x.getClass().getMethod("name").invoke(var1x);
                    Object var3x = var2x.getClass().getMethod("rawName").invoke(var2x);
                    return var3.test(String.valueOf(var3x).toLowerCase());
                } catch (Throwable var4x) {
                    return false;
                }
            };
            var4.invoke(var1, var2, var9);
        }
    }

    private void warn(String var1) {
        if (!this.warned) {
            this.warned = true;
            this.log.warning(var1 + " (이후 같은 경고는 생략)");
        }
    }
}
