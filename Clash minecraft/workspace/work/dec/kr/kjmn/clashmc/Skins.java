package kr.kjmn.clashmc;

import java.io.File;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;

final class Skins {
    final Map<String, Skins.Skin> all = new LinkedHashMap<>();
    private final Logger log;

    Skins(Logger var1) {
        this.log = var1;
    }

    void load(File var1) {
        this.all.clear();
        if (var1.exists()) {
            YamlConfiguration var2 = YamlConfiguration.loadConfiguration(var1);
            ConfigurationSection var3 = var2.getConfigurationSection("skins");
            if (var3 != null) {
                for (String var5 : var3.getKeys(false)) {
                    ConfigurationSection var6 = var3.getConfigurationSection(var5);
                    if (var6 != null) {
                        this.all
                            .put(
                                var5,
                                new Skins.Skin(
                                    var5,
                                    var6.getString("target", ""),
                                    var6.getString("name", var5),
                                    var6.getString("theme", ""),
                                    var6.getString("model", ""),
                                    var6.getString("barrel-model", ""),
                                    var6.getString("rarity", "common"),
                                    var6.getString("unlock", "default"),
                                    var6.getString("desc", "")
                                )
                            );
                    }
                }

                this.log.info("스킨 " + this.all.size() + "개");
            }
        }
    }

    List<Skins.Skin> forTarget(String var1) {
        ArrayList var2 = new ArrayList();

        for (Skins.Skin var4 : this.all.values()) {
            if (var4.target.equals(var1)) {
                var2.add(var4);
            }
        }

        return var2;
    }

    boolean owns(Profile var1, Skins.Skin var2) {
        if (var1.skins.contains(var2.id)) {
            return true;
        } else {
            String var3 = var2.unlock == null ? "default" : var2.unlock;
            if (var3.equals("default")) {
                return true;
            } else if (var3.equals("admin")) {
                return false;
            } else {
                int var4 = var3.indexOf(58);
                if (var4 < 0) {
                    return false;
                } else {
                    int var5;
                    try {
                        var5 = Integer.parseInt(var3.substring(var4 + 1).trim());
                    } catch (NumberFormatException var8) {
                        return false;
                    }

                    String var6 = var3.substring(0, var4);
                    switch (var6) {
                        case "trophies":
                            return var1.best >= var5;
                        case "wins":
                            return var1.wins >= var5;
                        case "ranked-wins":
                            return var1.rankedWins >= var5;
                        case "games":
                            return var1.games() >= var5;
                        case "king":
                            return var1.kingGames >= var5;
                        default:
                            return false;
                    }
                }
            }
        }
    }

    String unlockText(Skins.Skin var1) {
        String var2 = var1.unlock == null ? "default" : var1.unlock;
        if (var2.equals("default")) {
            return "§a기본 지급";
        } else if (var2.equals("admin")) {
            return "§c이벤트 / 관리자 지급";
        } else {
            int var3 = var2.indexOf(58);
            String var4 = var3 < 0 ? "" : var2.substring(var3 + 1);
            String var5 = var3 < 0 ? var2 : var2.substring(0, var3);
            switch (var5) {
                case "trophies":
                    return "§e최고 트로피 " + var4 + " 달성";
                case "wins":
                    return "§e승리 " + var4 + "회";
                case "ranked-wins":
                    return "§e랭크전 승리 " + var4 + "회";
                case "games":
                    return "§e경기 " + var4 + "판";
                case "king":
                    return "§e킹으로 " + var4 + "판";
                default:
                    return "§7" + var2;
            }
        }
    }

    Skins.Skin selected(Profile var1, String var2) {
        if (var1 == null) {
            return null;
        } else {
            String var3 = var1.selected.get(var2);
            if (var3 == null) {
                return null;
            } else {
                Skins.Skin var4 = this.all.get(var3);
                return var4 != null && var4.target.equals(var2) && this.owns(var1, var4) ? var4 : null;
            }
        }
    }

    record Skin(String id, String target, String name, String theme, String model, String barrelModel, String rarity, String unlock, String desc) {
        String rarityColor() {
            String var1 = this.rarity;
            switch (var1) {
                case "rare":
                    return "§6";
                case "epic":
                    return "§d";
                case "legendary":
                    return "§b";
                default:
                    return "§7";
            }
        }
    }
}
