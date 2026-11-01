package kr.kjmn.clashmc;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import net.md_5.bungee.api.chat.BaseComponent;
import net.md_5.bungee.api.chat.ClickEvent;
import net.md_5.bungee.api.chat.TextComponent;
import net.md_5.bungee.api.chat.ClickEvent.Action;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.OfflinePlayer;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.inventory.meta.SkullMeta;
import org.bukkit.persistence.PersistentDataType;

final class Ui {
    static final char BG_MAIN = '\ue100';
    static final char BG_DECK = '\ue101';
    static final char BG_SKINS = '\ue102';
    static final char BG_SKIN_PICK = '\ue103';
    static final char BG_PROFILE = '\ue104';
    static final char BG_LEADER = '\ue105';
    static final char BG_ROOM = '\ue106';
    static final char BG_AI = '\ue107';
    static final char BG_ROOMS = '\ue108';
    static final char BG_ROOM_NEW = '\ue109';

    private Ui() {
    }

    static String title(char var0, String var1) {
        return !Glyphs.pack ? "§8" + var1 : "§f" + Glyphs.space(-8) + var0 + Glyphs.space(-169) + "§f" + var1;
    }

    static ItemStack icon(String var0, Material var1, String var2, String... var3) {
        return icon(var0, var1, var2, Arrays.asList(var3));
    }

    static ItemStack icon(String var0, Material var1, String var2, List<String> var3) {
        ItemStack var4 = new ItemStack(Glyphs.pack ? Material.PAPER : var1);
        ItemMeta var5 = var4.getItemMeta();
        if (var5 != null) {
            var5.setDisplayName(var2);
            var5.setLore(new ArrayList(var3));
            if (Glyphs.pack) {
                try {
                    var5.setItemModel(new NamespacedKey("clashmc", "ui_" + var0));
                } catch (Throwable var7) {
                }
            }

            var4.setItemMeta(var5);
        }

        return var4;
    }

    static ItemStack blank(String var0, List<String> var1, Material var2) {
        return icon("blank", var2, var0, var1);
    }

    static ItemStack glow(ItemStack var0, boolean var1) {
        ItemMeta var2 = var0.getItemMeta();
        if (var2 != null) {
            try {
                var2.setEnchantmentGlintOverride(var1);
            } catch (Throwable var4) {
            }

            var0.setItemMeta(var2);
        }

        return var0;
    }

    static ItemStack head(UUID var0, String var1, List<String> var2) {
        ItemStack var3 = new ItemStack(Material.PLAYER_HEAD);
        ItemMeta var4 = var3.getItemMeta();
        if (var4 instanceof SkullMeta var5) {
            try {
                OfflinePlayer var6 = Bukkit.getOfflinePlayer(var0);
                var5.setOwningPlayer(var6);
            } catch (Throwable var7) {
            }
        }

        if (var4 != null) {
            var4.setDisplayName(var1);
            var4.setLore(new ArrayList(var2));
            var3.setItemMeta(var4);
        }

        return var3;
    }

    static ItemStack tag(ItemStack var0, NamespacedKey var1, String var2) {
        ItemMeta var3 = var0.getItemMeta();
        if (var3 != null) {
            var3.getPersistentDataContainer().set(var1, PersistentDataType.STRING, var2);
            var0.setItemMeta(var3);
        }

        return var0;
    }

    static String tagOf(ItemStack var0, NamespacedKey var1) {
        if (var0 != null && var0.hasItemMeta()) {
            ItemMeta var2 = var0.getItemMeta();
            return var2 == null ? null : (String)var2.getPersistentDataContainer().get(var1, PersistentDataType.STRING);
        } else {
            return null;
        }
    }

    static ItemStack withModel(ItemStack var0, String var1) {
        if (!Glyphs.pack) {
            return var0;
        } else {
            ItemMeta var2 = var0.getItemMeta();
            if (var2 != null) {
                try {
                    var2.setItemModel(new NamespacedKey("clashmc", var1));
                } catch (Throwable var4) {
                }

                var0.setItemMeta(var2);
            }

            return var0;
        }
    }

    static void clickable(Player var0, String var1, String var2, String var3) {
        TextComponent var4 = new TextComponent(TextComponent.fromLegacyText(var1));
        TextComponent var5 = new TextComponent(TextComponent.fromLegacyText(var2));
        var5.setClickEvent(new ClickEvent(Action.RUN_COMMAND, var3));
        var0.spigot().sendMessage(new BaseComponent[]{var4, var5});
    }

    static void suggest(Player var0, String var1, String var2) {
        TextComponent var3 = new TextComponent(TextComponent.fromLegacyText(var1));
        var3.setClickEvent(new ClickEvent(Action.SUGGEST_COMMAND, var2));
        var0.spigot().sendMessage(new BaseComponent[]{var3});
    }

    static String bar(double var0, int var2, String var3, String var4) {
        int var5 = (int)Math.round(Math.max(0.0, Math.min(1.0, var0)) * var2);
        StringBuilder var6 = new StringBuilder(var3);

        for (int var7 = 0; var7 < var2; var7++) {
            if (var7 == var5) {
                var6.append(var4);
            }

            var6.append('|');
        }

        return var6.toString();
    }
}
