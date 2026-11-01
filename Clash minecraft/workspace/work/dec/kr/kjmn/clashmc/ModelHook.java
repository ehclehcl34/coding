package kr.kjmn.clashmc;

import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.Map.Entry;
import java.util.function.Predicate;
import java.util.logging.Logger;
import org.bukkit.Bukkit;
import org.bukkit.Color;
import org.bukkit.entity.Entity;
import org.bukkit.plugin.Plugin;

public final class ModelHook {
    private final Logger log;
    private boolean enabled;
    private Class<?> api;
    private final Map<UUID, Object[]> applied = new HashMap<>();
    private boolean warned;
    private BetterModelBackend bm;
    private Color pendingTint;
    /** 스킨 모델 이름 → 원래(기본) 모델 이름. GameManager.skinModel 이 채움 */
    public final Map<String, String> originals = new java.util.concurrent.ConcurrentHashMap<>();
    private String pendingOrig;

    public ModelHook(Logger var1, boolean var2, String var3) {
        this.log = var1;
        String var4 = var3 == null ? "auto" : var3.toLowerCase();
        boolean var5 = Bukkit.getPluginManager().getPlugin("BetterModel") != null;
        boolean var6 = Bukkit.getPluginManager().getPlugin("ModelEngine") != null;
        if (var2 && var5 && (var4.equals("bettermodel") || var4.equals("auto"))) {
            try {
                this.bm = new BetterModelBackend(var1);
                this.enabled = true;
                var1.info("BetterModel 연동 활성화");
                return;
            } catch (Throwable var9) {
                var1.warning("BetterModel API 를 찾지 못함: " + var9);
                this.bm = null;
            }
        }

        if (var2 && var6 && !var4.equals("bettermodel")) {
            try {
                this.api = Class.forName("com.ticxo.modelengine.api.ModelEngineAPI");
                this.enabled = true;
                var1.info("ModelEngine 연동 활성화");
            } catch (Throwable var8) {
                this.enabled = false;
                var1.warning("ModelEngine API 를 찾지 못함: " + var8);
            }
        } else {
            this.enabled = false;
            var1.info("ModelEngine 미사용 - 바닐라 외형으로 동작");
        }
    }

    public boolean enabled() {
        return this.enabled;
    }

    static String teamKey(Color var0) {
        if (var0 == null) {
            return "blue";
        } else {
            int var1 = var0.asRGB();
            return (var1 >> 16 & 0xFF) > (var1 & 0xFF) ? "red" : "blue";
        }
    }

    public boolean apply(Entity var1, String var2, boolean var3) {
        if (this.enabled && var1 != null && var2 != null && !var2.isEmpty()) {
            String orig = this.pendingOrig != null ? this.pendingOrig : this.originalOf(var2);
            if (orig != null && orig.contains("{team}")) {
                orig = orig.replace("{team}", "blue");
            }
            if (var2.contains("{team}")) {
                var2 = var2.replace("{team}", "blue");
            }
            if (orig != null && orig.equals(var2)) {
                orig = null;
            }

            ArrayList<String> var4 = new ArrayList<>();
            int var5 = var2.indexOf(35);
            if (var5 > 0) {
                for (String var9 : var2.substring(var5 + 1).split(",")) {
                    if (!var9.isBlank()) {
                        var4.add(var9.trim().toLowerCase());
                    }
                }

                var2 = var2.substring(0, var5);
            }

            String var15 = null;
            int var16 = var2.indexOf(58);
            if (var16 > 0) {
                var15 = var2.substring(var16 + 1).toLowerCase();
                var2 = var2.substring(0, var16);
            }

            String var17 = var15;
            Predicate<String> var18 = var2x -> hidden(var2x, var17, var4);
            if (this.bm != null) {
                boolean var19 = this.bm.apply(var1, var2, var18, this.pendingTint);
                if (var19) {
                    this.bm.dropAlt(var1);
                    if (orig != null) {
                        this.applyOriginal(var1, orig);
                    }
                    this.settleSpawn(var1);
                }

                return var19;
            } else {
                try {
                    Method var10 = this.staticMethod("createModeledEntity", var1.getClass());
                    Method var11 = this.staticMethod("createActiveModel", String.class);
                    if (var10 != null && var11 != null) {
                        Object var12 = var11.invoke(null, var2);
                        if (var12 == null) {
                            return false;
                        } else {
                            Object var13 = var10.invoke(null, var1);
                            if (var13 == null) {
                                return false;
                            } else {
                                call(var13, "addModel", var12, true);
                                if (var3) {
                                    call(var13, "setBaseEntityVisible", false);
                                }

                                this.applied.put(var1.getUniqueId(), new Object[]{var13, var12});
                                if (var15 != null || !var4.isEmpty()) {
                                    this.showVariant(var12, var18);
                                }

                                this.settleSpawn(var1);
                                return true;
                            }
                        }
                    } else {
                        throw new IllegalStateException("createModeledEntity/createActiveModel 없음");
                    }
                } catch (Throwable var14) {
                    this.warn("모델 적용 실패 (" + var2 + "): " + var14);
                    return false;
                }
            }
        } else {
            return false;
        }
    }

    public boolean exists(String var1) {
        if (!this.enabled || this.bm == null || var1 == null || var1.isEmpty()) {
            return true;
        } else if (!var1.contains("{team}")) {
            String var2 = var1;
            int var3 = var1.indexOf(35);
            if (var3 > 0) {
                var2 = var1.substring(0, var3);
            }

            int var4 = var2.indexOf(58);
            if (var4 > 0) {
                var2 = var2.substring(0, var4);
            }

            return this.bm.exists(var2);
        } else {
            return this.exists(var1.replace("{team}", "blue")) && this.exists(var1.replace("{team}", "red"));
        }
    }

    static boolean hidden(String var0, String var1, List<String> var2) {
        if (var0.equals("hitbox")) {
            return true;
        } else if (var1 != null && var0.contains("__") && !var0.contains(var1 + "__")) {
            return true;
        } else {
            for (String var4 : var2) {
                if (var0.equals(var4) || var0.startsWith(var4 + "_") || var0.endsWith("__" + var4) || var0.endsWith("_" + var4) && var0.startsWith("h_")) {
                    return true;
                }
            }

            return false;
        }
    }

    private void showVariant(Object var1, Predicate<String> var2) {
        String var3 = "";

        try {
            if (!(call(var1, "getBones") instanceof Map var5)) {
                return;
            }

            for (Entry<?, ?> var7 : ((Map<?, ?>)var5).entrySet()) {
                String var8 = String.valueOf(var7.getKey()).toLowerCase();
                if (var2.test(var8)) {
                    Object var9 = var7.getValue();
                    Method var10 = null;

                    for (Method var14 : var9.getClass().getMethods()) {
                        if (var14.getName().equals("setVisible") && var14.getParameterCount() == 1 && var14.getParameterTypes()[0] == boolean.class) {
                            var10 = var14;
                            break;
                        }
                    }

                    if (var10 == null) {
                        this.warn("ModelBone#setVisible 을 찾지 못함 - 묶음 모델이 겹쳐 보일 수 있음");
                        return;
                    }

                    var10.setAccessible(true);
                    var10.invoke(var9, false);
                }
            }
        } catch (Throwable var15) {
            this.warn("변형 표시 실패 (" + var3 + "): " + var15);
        }
    }

    /** 스킨 모델이면 원래 모델 이름 (뒤에 붙은 #숨김본 은 그대로 이어 붙임), 아니면 null */
    String originalOf(String m) {
        if (m == null || this.originals.isEmpty()) {
            return null;
        }
        String o = this.originals.get(m);
        if (o != null) {
            return o;
        }
        int h = m.indexOf('#');
        if (h > 0) {
            o = this.originals.get(m.substring(0, h));
            if (o != null) {
                return o + (o.indexOf('#') > 0 ? "," : "#") + m.substring(h + 1);
            }
        }
        return null;
    }

    /** 원본 스킨으로 보는 사람용 기본 모델 겹치기 */
    private void applyOriginal(Entity e, String m) {
        ArrayList<String> hide = new ArrayList<>();
        int h = m.indexOf('#');
        if (h > 0) {
            for (String b : m.substring(h + 1).split(",")) {
                if (!b.isBlank()) {
                    hide.add(b.trim().toLowerCase());
                }
            }
            m = m.substring(0, h);
        }
        String variant = null;
        int c = m.indexOf(':');
        if (c > 0) {
            variant = m.substring(c + 1).toLowerCase();
            m = m.substring(0, c);
        }
        String v = variant;
        this.bm.applyAlt(e, m, b -> hidden(b, v, hide), this.pendingTint);
    }

    /** 원본 스킨 보기 여부 판단 (Clash 가 프로필 기준으로 넣어 줌) */
    public void wantsOriginal(Predicate<UUID> p) {
        if (this.bm != null) {
            this.bm.wantsOriginal = p;
        }
    }

    /** 이 플레이어 기준으로 겹친 모델 다시 정리 */
    public void refreshViewer(org.bukkit.entity.Player p) {
        if (this.bm != null && p != null) {
            this.bm.refreshViewer(p);
        }
    }

    /** 모델의 본 하나 보이기/숨기기 (BetterModel 만) */
    public void part(Entity e, String bone, boolean show) {
        if (this.bm != null && e != null) {
            this.bm.part(e, bone, show);
        }
    }

    /** 플레이어 자신에게도 자기 모델 보이기 (BetterModel 만) */
    public void selfView(Entity e, boolean show) {
        if (this.bm != null && e != null) {
            this.bm.selfView(e, show);
        }
    }

    /** 모델 전체 숨기기/보이기 (BetterModel 만) */
    public void visible(Entity e, boolean show) {
        if (this.bm != null && e != null) {
            this.bm.visible(e, show);
        }
    }

    /** 모델 테두리를 팀 색으로 빛나게 (BetterModel 만) */
    public void glow(Entity e, Color c) {
        if (this.bm != null && e != null) {
            this.bm.glow(e, c);
        }
    }

    public boolean apply(Entity var1, String var2, boolean var3, Color var4) {
        String orig = var2 == null ? null : this.originalOf(var2);
        if (orig != null && orig.contains("{team}")) {
            orig = orig.replace("{team}", teamKey(var4));
        }
        if (var2 != null && var2.contains("{team}")) {
            var2 = var2.replace("{team}", teamKey(var4));
        }

        if (this.bm != null) {
            this.pendingTint = var4;
            this.pendingOrig = orig;

            boolean var9;
            try {
                var9 = this.apply(var1, var2, var3);
            } finally {
                this.pendingTint = null;
                this.pendingOrig = null;
            }

            return var9;
        } else {
            boolean var5 = this.apply(var1, var2, var3);
            if (var5 && var4 != null) {
                this.tint(var1, var4);
            }

            return var5;
        }
    }

    public void tint(Entity var1, Color var2) {
        if (this.bm == null) {
            Object[] var3 = this.applied.get(var1.getUniqueId());
            if (this.enabled && var3 != null) {
                try {
                    if (!(call(var3[1], "getBones") instanceof Map var5)) {
                        return;
                    }

                    for (Entry<?, ?> var7 : ((Map<?, ?>)var5).entrySet()) {
                        if (String.valueOf(var7.getKey()).toLowerCase().contains("tc_")) {
                            Object var8 = var7.getValue();
                            Method var9 = find(var8.getClass(), "setDefaultTint", 1);
                            if (var9 == null) {
                                var9 = find(var8.getClass(), "setTint", 1);
                            }

                            if (var9 != null) {
                                var9.setAccessible(true);
                                var9.invoke(var8, var2);
                            }
                        }
                    }
                } catch (Throwable var10) {
                    this.warn("팀 색 틴트 실패: " + var10);
                }
            }
        }
    }

    public boolean anim(Entity var1, String var2) {
        if (!this.enabled || var1 == null) {
            return false;
        } else if (this.bm != null) {
            return this.bm.anim(var1, var2);
        } else {
            Object[] var3 = this.applied.get(var1.getUniqueId());
            if (var3 == null) {
                return false;
            } else {
                try {
                    Object var4 = call(var3[1], "getAnimationHandler");
                    if (var4 == null) {
                        return false;
                    }

                    Method var5 = find(var4.getClass(), "playAnimation", 5);
                    if (var5 != null) {
                        var5.setAccessible(true);
                        var5.invoke(var4, var2, 0.1, 0.1, 1.0, true);
                        return true;
                    }
                } catch (Throwable var6) {
                    this.warn("애니메이션 실패 (" + var2 + "): " + var6);
                }

                return false;
            }
        }
    }

    public void scale(Entity var1, double var2) {
        if (this.enabled && var1 != null && this.bm == null) {
            Object[] var4 = this.applied.get(var1.getUniqueId());
            if (var4 != null) {
                try {
                    Method var5 = find(var4[1].getClass(), "setScale", 1);
                    if (var5 != null) {
                        var5.setAccessible(true);
                        var5.invoke(var4[1], var2);
                    }
                } catch (Throwable var6) {
                    this.warn("모델 배율 실패: " + var6);
                }
            }
        }
    }

    private org.bukkit.scheduler.BukkitTask watchdogTask;

    /**
     * (예전엔 1.5초 뒤 "spawn" 을 강제로 멈췄는데, 다른 애니메이션이 없을 때 멈추면 그 프레임에서 굳어버림 → 제거)
     * 대신 10틱마다 모델 상태를 검사해서 멈춘 모델을 다시 만듦.
     */
    private void settleSpawn(Entity var1) {
        if (this.bm == null) {
            return;
        }

        if (this.watchdogTask != null && !this.watchdogTask.isCancelled()) {
            return;
        }

        Plugin var2 = Bukkit.getPluginManager().getPlugin("ClashMC");
        if (var2 != null && var2.isEnabled()) {
            this.watchdogTask = Bukkit.getScheduler().runTaskTimer(var2, () -> {
                if (this.bm == null || this.bm.isEmpty()) {
                    if (this.watchdogTask != null) {
                        this.watchdogTask.cancel();
                        this.watchdogTask = null;
                    }
                    return;
                }

                try {
                    this.bm.watchdog();
                } catch (Throwable var3) {
                    this.warn("모델 감시 실패: " + var3);
                }
            }, 10L, 10L);
        }
    }

    public int rebuiltModels() {
        return this.bm == null ? 0 : this.bm.rebuiltCount();
    }

    public boolean animState(Entity var1, String var2, String var3) {
        if (this.enabled && var1 != null) {
            if (var3 != null) {
                this.stop(var1, var3);
            }

            return this.bm != null ? this.bm.animHold(var1, var2) : this.anim(var1, var2);
        } else {
            return false;
        }
    }

    public void stop(Entity var1, String var2) {
        if (this.enabled && var1 != null) {
            if (this.bm != null) {
                this.bm.stop(var1, var2);
            } else {
                Object[] var3 = this.applied.get(var1.getUniqueId());
                if (var3 != null) {
                    try {
                        Object var4 = call(var3[1], "getAnimationHandler");
                        Method var5 = var4 == null ? null : find(var4.getClass(), "stopAnimation", 1);
                        if (var5 != null) {
                            var5.setAccessible(true);
                            var5.invoke(var4, var2);
                        }
                    } catch (Throwable var6) {
                    }
                }
            }
        }
    }

    /** 본 하나(와 그 이름으로 시작하는 본)를 숨김. 예: 다크 프린스 실드가 깨지면 "shield" */
    public void hideBone(Entity var1, String var2) {
        if (this.enabled && var1 != null && var2 != null && this.bm != null) {
            String n = var2.toLowerCase();
            this.bm.hide(var1, b -> b.equals(n) || b.startsWith(n + "_") || b.endsWith("_" + n));
        }
    }

    public void remove(Entity var1) {
        if (var1 != null) {
            if (this.bm != null) {
                this.bm.remove(var1);
            } else {
                Object[] var2 = this.applied.remove(var1.getUniqueId());
                if (this.enabled && var2 != null) {
                    try {
                        Method var3 = find(var2[0].getClass(), "destroy", 0);
                        if (var3 != null) {
                            var3.setAccessible(true);
                            var3.invoke(var2[0]);
                            return;
                        }

                        Method var4 = this.staticMethod("removeModeledEntity", UUID.class);
                        if (var4 != null) {
                            var4.invoke(null, var1.getUniqueId());
                        }
                    } catch (Throwable var5) {
                        this.warn("모델 제거 실패: " + var5);
                    }
                }
            }
        }
    }

    public void clearAll() {
        if (this.watchdogTask != null) {
            this.watchdogTask.cancel();
            this.watchdogTask = null;
        }
        this.applied.clear();
        if (this.bm != null) {
            this.bm.clear();
        }
    }

    private Method staticMethod(String var1, Class<?> var2) {
        for (Method var6 : this.api.getMethods()) {
            if (var6.getName().equals(var1)
                && var6.getParameterCount() == 1
                && Modifier.isStatic(var6.getModifiers())
                && var6.getParameterTypes()[0].isAssignableFrom(var2)) {
                return var6;
            }
        }

        return null;
    }

    private static Method find(Class<?> var0, String var1, int var2) {
        for (Method var6 : var0.getMethods()) {
            if (var6.getName().equals(var1) && var6.getParameterCount() == var2) {
                return var6;
            }
        }

        return null;
    }

    private static Object call(Object var0, String var1, Object... var2) throws Exception {
        Method var3 = find(var0.getClass(), var1, var2.length);
        if (var3 == null) {
            throw new NoSuchMethodException(var0.getClass().getName() + "#" + var1);
        } else {
            var3.setAccessible(true);
            return var3.invoke(var0, var2);
        }
    }

    private void warn(String var1) {
        if (!this.warned) {
            this.warned = true;
            this.log.warning(var1 + " (이후 같은 경고는 생략)");
        }
    }
}
