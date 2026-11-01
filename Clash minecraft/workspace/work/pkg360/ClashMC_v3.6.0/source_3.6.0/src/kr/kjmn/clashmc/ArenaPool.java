package kr.kjmn.clashmc;

import java.io.File;
import java.io.FileInputStream;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.World;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.FileConfiguration;

final class ArenaPool {
    private final ClashPlugin plugin;
    private final Logger log;
    final Map<String, ArenaPool.Slot> slots = new LinkedHashMap<>();

    ArenaPool(ClashPlugin var1) {
        this.plugin = var1;
        this.log = var1.getLogger();
    }

    void load() {
        LinkedHashMap var1 = new LinkedHashMap();

        for (ArenaPool.Slot var3 : this.slots.values()) {
            if (var3.match != null) {
                var1.put(var3.name, var3.match);
            }
        }

        this.slots.clear();
        FileConfiguration var14 = this.plugin.getConfig();
        ConfigurationSection var15 = var14.getConfigurationSection("arenas");
        if (var15 != null) {
            for (String var5 : var15.getKeys(false)) {
                World var6 = Bukkit.getWorld(var15.getString(var5 + ".world", "world"));
                if (var6 == null) {
                    this.log.warning("경기장 " + var5 + " 월드 없음");
                } else {
                    ArenaPool.Slot var7 = new ArenaPool.Slot(
                        var5, new Arena(var6, var15.getInt(var5 + ".x"), var15.getInt(var5 + ".y"), var15.getInt(var5 + ".z"))
                    );
                    var7.match = (GameManager)var1.get(var5);
                    this.slots.put(var5, var7);
                }
            }
        }

        if (this.slots.isEmpty() && var14.isSet("arena.x")) {
            World var16 = Bukkit.getWorld(var14.getString("arena.world", "world"));
            if (var16 != null) {
                this.slots.put("main", new ArenaPool.Slot("main", new Arena(var16, var14.getInt("arena.x"), var14.getInt("arena.y"), var14.getInt("arena.z"))));
            }
        }

        ArenaPool.Slot var17 = this.slots.get("main");
        int var18 = var14.getInt("arena-grid.count", 5);
        int var19 = var14.getInt("arena-grid.step", 90);
        if (var17 != null && var18 > 1) {
            Arena var20 = var17.arena;

            for (int var8 = 2; var8 <= var18; var8++) {
                String var9 = "arena" + var8;
                if (!this.slots.containsKey(var9)) {
                    int var10 = var20.px + var19 * (var8 - 1);
                    boolean var11 = false;

                    for (ArenaPool.Slot var13 : this.slots.values()) {
                        if (var13.arena.world == var20.world && var13.arena.px == var10 && var13.arena.py == var20.py && var13.arena.pz == var20.pz) {
                            var11 = true;
                        }
                    }

                    if (!var11) {
                        ArenaPool.Slot var21 = new ArenaPool.Slot(var9, new Arena(var20.world, var10, var20.py, var20.pz));
                        var21.match = (GameManager)var1.get(var9);
                        this.slots.put(var9, var21);
                    }
                }
            }
        }

        this.log.info("경기장 " + this.slots.size() + "개");
    }

    ArenaPool.Slot acquire() {
        for (ArenaPool.Slot var2 : this.slots.values()) {
            if (var2.free()) {
                return var2;
            }
        }

        return null;
    }

    int freeCount() {
        int var1 = 0;

        for (ArenaPool.Slot var3 : this.slots.values()) {
            if (var3.free()) {
                var1++;
            }
        }

        return var1;
    }

    void add(String var1, Location var2) {
        String var3 = "arenas." + var1;
        this.plugin.getConfig().set(var3 + ".world", var2.getWorld().getName());
        this.plugin.getConfig().set(var3 + ".x", var2.getBlockX());
        this.plugin.getConfig().set(var3 + ".y", var2.getBlockY());
        this.plugin.getConfig().set(var3 + ".z", var2.getBlockZ());
        this.plugin.saveConfig();
        this.load();
    }

    boolean remove(String var1) {
        ArenaPool.Slot var2 = this.slots.get(var1);
        if (var2 != null && var2.free()) {
            this.plugin.getConfig().set("arenas." + var1, null);
            this.plugin.saveConfig();
            this.load();
            return true;
        } else {
            return false;
        }
    }

    static String paste(File var0, World var1, int var2, int var3, int var4) {
        if (Bukkit.getPluginManager().getPlugin("FastAsyncWorldEdit") == null && Bukkit.getPluginManager().getPlugin("WorldEdit") == null) {
            return "FAWE/WorldEdit 가 설치돼 있지 않습니다";
        } else if (!var0.exists()) {
            return "파일 없음: " + var0.getName();
        } else {
            try {
                Object var34;
                try (FileInputStream var5 = new FileInputStream(var0)) {
                    Class var32 = Class.forName("com.sk89q.worldedit.extent.clipboard.io.ClipboardFormats");
                    Object var7 = var32.getMethod("findByFile", File.class).invoke(null, var0);
                    if (var7 == null) {
                        return "알 수 없는 schem 형식";
                    }

                    Object var8 = invoke(var7, "getReader", var5);
                    Object var9 = invoke(var8, "read");
                    Object var10 = Class.forName("com.sk89q.worldedit.bukkit.BukkitAdapter").getMethod("adapt", World.class).invoke(null, var1);
                    Object var11 = Class.forName("com.sk89q.worldedit.WorldEdit").getMethod("getInstance").invoke(null);
                    Object var12 = invoke(var11, "newEditSession", var10);

                    try {
                        Class var13 = Class.forName("com.sk89q.worldedit.extent.clipboard.Clipboard");
                        Object var14 = Class.forName("com.sk89q.worldedit.session.ClipboardHolder").getConstructor(var13).newInstance(var9);
                        Object var15 = invoke(var14, "createPaste", var12);
                        Object var16 = Class.forName("com.sk89q.worldedit.math.BlockVector3")
                            .getMethod("at", int.class, int.class, int.class)
                            .invoke(null, var2, var3, var4);
                        var15 = invoke(var15, "to", var16);
                        var15 = invoke(var15, "ignoreAirBlocks", false);
                        Object var17 = invoke(var15, "build");
                        Class var18 = Class.forName("com.sk89q.worldedit.function.operation.Operations");

                        for (Method var22 : var18.getMethods()) {
                            if (var22.getName().equals("complete") && var22.getParameterCount() == 1) {
                                var22.invoke(null, var17);
                                break;
                            }
                        }
                    } finally {
                        invoke(var12, "close");
                    }

                    var34 = null;
                }

                return (String)var34;
            } catch (Throwable var31) {
                Throwable var6 = var31.getCause() != null ? var31.getCause() : var31;
                return "붙여넣기 실패: " + var6;
            }
        }
    }

    private static Object invoke(Object var0, String var1, Object... var2) throws Exception {
        label38:
        for (Method var6 : var0.getClass().getMethods()) {
            if (var6.getName().equals(var1) && var6.getParameterCount() == var2.length) {
                Class[] var7 = var6.getParameterTypes();

                for (int var8 = 0; var8 < var2.length; var8++) {
                    Class var9 = var7[var8].isPrimitive() ? box(var7[var8]) : var7[var8];
                    if (var2[var8] != null && !var9.isInstance(var2[var8])) {
                        continue label38;
                    }
                }

                var6.setAccessible(true);
                return var6.invoke(var0, var2);
            }
        }

        throw new NoSuchMethodException(var0.getClass().getName() + "#" + var1);
    }

    private static Class<?> box(Class<?> var0) {
        if (var0 == boolean.class) {
            return Boolean.class;
        } else if (var0 == int.class) {
            return Integer.class;
        } else if (var0 == double.class) {
            return Double.class;
        } else if (var0 == long.class) {
            return Long.class;
        } else {
            return var0 == float.class ? Float.class : var0;
        }
    }

    List<String> names() {
        return new ArrayList<>(this.slots.keySet());
    }

    static final class Slot {
        final String name;
        final Arena arena;
        GameManager match;

        Slot(String var1, Arena var2) {
            this.name = var1;
            this.arena = var2;
        }

        boolean free() {
            return this.match == null;
        }
    }
}
