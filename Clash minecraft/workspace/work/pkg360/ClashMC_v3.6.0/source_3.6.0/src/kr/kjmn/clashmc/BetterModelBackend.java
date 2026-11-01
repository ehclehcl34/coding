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
                        return false;
                    } else {
                        this.trackers.put(var1.getUniqueId(), var16);
                        this.applyArgs.put(var1.getUniqueId(), new Object[]{var1, var2, var3, var4});
                        this.born.put(var1.getUniqueId(), System.currentTimeMillis());
                        this.update(var16, this.toggle(false), var3);
                        if (var4 != null) {
                            int var17 = var4.asRGB();
                            this.update(var16, this.staticAction("tint", int.class, var17), var0 -> var0.contains("tc_"));
                            int soft = var17 == TeamColor.BLUE.color.asRGB() ? 0x4EC0C8 : 0xF06048;   // soft team colour for ts_ bones
                            this.update(var16, this.staticAction("tint", int.class, soft), var0 -> var0.contains("ts_"));
                        }

                        return true;
                    }
                }
            } else {
                return false;
            }
        } catch (Throwable var14) {
            this.warn("BetterModel 모델 적용 실패 (" + var2 + "): " + var14);
            return false;
        }
    }

    boolean exists(String var1) {
        try {
            return this.api.getMethod("model", String.class).invoke(null, var1) instanceof Optional var3 && var3.isPresent();
        } catch (Throwable var4) {
            return false;
        }
    }

    boolean anim(Entity var1, String var2) {
        Object var3 = var1 == null ? null : this.trackers.get(var1.getUniqueId());
        if (var3 == null) {
            return false;
        } else {
            try {
                Method var4 = var3.getClass().getMethod("animate", String.class, this.modifierCls);
                if (var2.equals("deploy") || var2.equals("spawn")) {
                    // 트래커가 아직 플레이어에게 안 보였으면 기본 idle 이 나중에 들어와 소환 모션을 덮음
                    // → 트래커 다음 틱(기본 애니메이션 등록 뒤)에 재생
                    Object t = var3;
                    long asked = System.currentTimeMillis();
                    try {
                        var3.getClass().getMethod("task", Runnable.class).invoke(var3, (Runnable)() -> {
                            try {
                                if (System.currentTimeMillis() - asked < 2500L) {
                                    var4.invoke(t, var2, this.playOnce);
                                }
                            } catch (Throwable ignored) {
                            }
                        });
                        return true;
                    } catch (NoSuchMethodException ignored) {
                    }
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
        Object var3 = var1 == null ? null : this.trackers.get(var1.getUniqueId());
        if (var3 == null) {
            return false;
        } else {
            try {
                var3.getClass().getMethod("animate", String.class, this.modifierCls).invoke(var3, var2, this.playDefault);
                return true;
            } catch (Throwable var5) {
                this.warn("BetterModel 애니메이션 실패 (" + var2 + "): " + var5);
                return false;
            }
        }
    }

    void stop(Entity var1, String var2) {
        Object var3 = var1 == null ? null : this.trackers.get(var1.getUniqueId());
        if (var3 != null) {
            try {
                var3.getClass().getMethod("stopAnimation", String.class).invoke(var3, var2);
            } catch (Throwable var5) {
            }
        }
    }

    void hide(Entity e, Predicate<String> pred) {
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
            this.applyArgs.remove(var1.getUniqueId());
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

        this.trackers.clear();
        this.applyArgs.clear();
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
