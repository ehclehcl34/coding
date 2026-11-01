package kr.kjmn.clashmc;

import java.util.List;

final class Ranks {
    static final List<Ranks.Tier> TIERS = List.of(
        new Ranks.Tier("브론즈", 0, "§6", '\ue050', "[B]"),
        new Ranks.Tier("실버", 300, "§7", '\ue051', "[S]"),
        new Ranks.Tier("골드", 700, "§e", '\ue052', "[G]"),
        new Ranks.Tier("플래티넘", 1200, "§b", '\ue053', "[P]"),
        new Ranks.Tier("다이아몬드", 1800, "§9", '\ue054', "[D]"),
        new Ranks.Tier("마스터", 2500, "§d", '\ue055', "[M]"),
        new Ranks.Tier("그랜드마스터", 3300, "§c", '\ue056', "[GM]"),
        new Ranks.Tier("챔피언", 4200, "§6§l", '\ue057', "[C]")
    );

    private Ranks() {
    }

    static Ranks.Tier tier(int var0) {
        Ranks.Tier var1 = TIERS.get(0);

        for (Ranks.Tier var3 : TIERS) {
            if (var0 >= var3.min) {
                var1 = var3;
            }
        }

        return var1;
    }

    static Ranks.Tier next(int var0) {
        for (Ranks.Tier var2 : TIERS) {
            if (var0 < var2.min) {
                return var2;
            }
        }

        return null;
    }

    static String division(int var0) {
        Ranks.Tier var1 = tier(var0);
        Ranks.Tier var2 = next(var0);
        if (var2 == null) {
            return "";
        } else {
            int var3 = var2.min - var1.min;
            int var4 = var0 - var1.min;
            int var5 = 3 - Math.min(2, var4 * 3 / Math.max(1, var3));
            return var5 == 3 ? " III" : (var5 == 2 ? " II" : " I");
        }
    }

    static String badge(int var0) {
        Ranks.Tier var1 = tier(var0);
        return Glyphs.pack ? "§f" + var1.badge : var1.color + var1.fallback;
    }

    static String label(int var0) {
        Ranks.Tier var1 = tier(var0);
        return badge(var0) + " " + var1.color + var1.name + division(var0);
    }

    static int gain(double var0, double var2, int var4) {
        double var5 = 30.0 + (var2 - var0) / 20.0;
        if (var4 >= 3) {
            var5 += Math.min(6, var4 - 2) * 1.5;
        }

        return (int)Math.round(Math.max(12.0, Math.min(48.0, var5)));
    }

    static int loss(double var0, double var2, int var4) {
        double var5 = 30.0 - (var2 - var0) / 20.0;
        if (var4 < 300) {
            var5 *= 0.5;
        }

        return (int)Math.round(Math.max(var4 < 300 ? 5.0 : 10.0, Math.min(45.0, var5)));
    }

    record Tier(String name, int min, String color, char badge, String fallback) {
    }
}
