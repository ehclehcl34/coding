package kr.kjmn.clashmc;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.logging.Logger;
import org.bukkit.Bukkit;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;

final class Profiles {
    private final File dir;
    private final Logger log;
    private final Map<UUID, Profile> all = new ConcurrentHashMap<>();
    private List<Profile> top = new ArrayList<>();

    Profiles(File var1, Logger var2) {
        this.dir = new File(var1, "playerdata");
        this.log = var2;
    }

    void loadAll() {
        this.all.clear();
        this.dir.mkdirs();
        File[] var1 = this.dir.listFiles((var0, var1x) -> var1x.endsWith(".yml"));
        if (var1 != null) {
            for (File var5 : var1) {
                try {
                    UUID var6 = UUID.fromString(var5.getName().substring(0, var5.getName().length() - 4));
                    Profile var7 = new Profile(var6);
                    var7.load(YamlConfiguration.loadConfiguration(var5));
                    this.all.put(var6, var7);
                } catch (IllegalArgumentException var9) {
                }
            }
        }

        File var10 = new File(this.dir.getParentFile(), "decks.yml");
        if (var10.exists()) {
            YamlConfiguration var11 = YamlConfiguration.loadConfiguration(var10);

            for (String var13 : var11.getKeys(false)) {
                try {
                    Profile var14 = this.get(UUID.fromString(var13));
                    if (var14.decks.get(0).isEmpty()) {
                        var14.decks.get(0).addAll(var11.getStringList(var13));
                        var14.dirty = true;
                    }
                } catch (IllegalArgumentException var8) {
                }
            }

            if (!var10.renameTo(new File(this.dir.getParentFile(), "decks.yml.migrated"))) {
                var10.delete();
            }
        }

        this.rebuildTop();
        this.log.info("플레이어 데이터 " + this.all.size() + "명 로드");
    }

    Profile get(UUID var1) {
        return this.all.computeIfAbsent(var1, var0 -> {
            Profile var1x = new Profile(var0);
            var1x.dirty = true;
            return var1x;
        });
    }

    Profile get(Player var1) {
        Profile var2 = this.get(var1.getUniqueId());
        if (!var1.getName().equals(var2.name)) {
            var2.name = var1.getName();
            var2.dirty = true;
        }

        return var2;
    }

    void save(Profile var1) {
        try {
            this.dir.mkdirs();
            var1.save().save(new File(this.dir, var1.id + ".yml"));
            var1.dirty = false;
        } catch (IOException var3) {
            this.log.warning("플레이어 데이터 저장 실패 " + var1.id + ": " + var3.getMessage());
        }
    }

    void saveDirty() {
        for (Profile var2 : this.all.values()) {
            if (var2.dirty) {
                this.save(var2);
            }
        }
    }

    void rebuildTop() {
        ArrayList var1 = new ArrayList<>(this.all.values());
        var1.removeIf(var0 -> var0.games() == 0 && var0.trophies == 0);
        var1.sort(Comparator.<Profile>comparingInt(var0 -> -var0.trophies).thenComparing(var0 -> var0.name));
        this.top = var1;
    }

    List<Profile> top(int var1) {
        return this.top.subList(0, Math.min(var1, this.top.size()));
    }

    int rankOf(UUID var1) {
        for (int var2 = 0; var2 < this.top.size(); var2++) {
            if (this.top.get(var2).id.equals(var1)) {
                return var2 + 1;
            }
        }

        return -1;
    }

    static boolean online(UUID var0) {
        return Bukkit.getPlayer(var0) != null;
    }
}
