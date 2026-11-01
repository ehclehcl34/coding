package kr.kjmn.clashmc;

final class Glyphs {
    static boolean pack = true;
    static final char DROP = '\ue000';
    static final char CELL_EMPTY = '\ue001';
    static final char CELL_FULL = '\ue002';
    static final char CELL_Q1 = '\ue003';
    static final char CELL_Q2 = '\ue004';
    static final char CELL_Q3 = '\ue005';
    static final char CELL_ALERT = '\ue006';
    static final char CELL_ALERT_FULL = '\ue007';
    static final char CELL_NEED_FULL = '\ue008';
    static final char CELL_NEED_EMPTY = '\ue009';
    static final char COLON = '\ue01a';
    static final char X2 = '\ue01b';
    static final char CLOCK = '\ue01c';
    static final char CROWN_BLUE = '\ue020';
    static final char CROWN_RED = '\ue021';
    static final char CROWN_EMPTY = '\ue022';
    static final char CROWN_GOLD = '\ue023';
    static final char BAR_CAP = '\ue030';
    static final char BAR_FULL = '\ue031';
    static final char BAR_EMPTY = '\ue032';
    static final char TBAR_CAP = '\ue034';
    static final char TBAR_FULL = '\ue035';
    static final char TBAR_EMPTY = '\ue036';
    static final char IC_CROWN = '\ue040';
    static final char IC_SHIELD = '\ue041';
    static final char IC_SWORD = '\ue042';
    static final char IC_HEART = '\ue043';

    private Glyphs() {
    }

    static String space(int var0) {
        if (pack && var0 != 0) {
            StringBuilder var1 = new StringBuilder();
            boolean var2 = var0 < 0;
            int var3 = Math.abs(var0);

            for (int var4 = 7; var4 >= 0; var4--) {
                for (int var5 = 1 << var4; var3 >= var5; var3 -= var5) {
                    var1.append((char)((var2 ? '\uf801' : '\uf821') + var4));
                }
            }

            return var1.toString();
        } else {
            return "";
        }
    }

    static String bigNumber(int var0) {
        if (!pack) {
            return String.valueOf(var0);
        } else {
            StringBuilder var1 = new StringBuilder();

            for (char var5 : String.valueOf(var0).toCharArray()) {
                var1.append((char)(57360 + (var5 - '0')));
            }

            return var1.toString();
        }
    }

    static String elixirBar(double var0, int var2, int var3, boolean var4, boolean var5) {
        int var6 = (int)Math.floor(var0 + 1.0E-9);
        double var7 = var0 - var6;
        if (!pack) {
            StringBuilder var13 = new StringBuilder("§d엘릭서 ");

            for (int var14 = 1; var14 <= var2; var14++) {
                if (var14 <= var6) {
                    var13.append(var4 && var3 > 0 && var14 <= var3 ? "§c■" : (var3 > 0 && var14 <= var3 ? "§e■" : "§d■"));
                } else {
                    var13.append(var4 && var14 <= var3 ? "§4□" : (var3 > 0 && var14 <= var3 ? "§6□" : "§8■"));
                }
            }

            var13.append(" §f").append(String.format("%.1f", var0));
            if (var3 > 0) {
                var13.append(var4 ? " §c(필요 " + var3 + ")" : " §7/ " + var3);
            }

            if (var5) {
                var13.append(" §d×2");
            }

            return var13.toString();
        } else {
            StringBuilder var9 = new StringBuilder("§f");
            var9.append('\ue000').append(space(1));

            for (int var10 = 1; var10 <= var2; var10++) {
                boolean var12 = var3 > 0 && var10 <= var3;
                int var11;
                if (var10 <= var6) {
                    var11 = var12 ? (var4 ? '\ue007' : '\ue008') : '\ue002';
                } else if (var12) {
                    var11 = var4 ? '\ue006' : '\ue009';
                } else if (var10 == var6 + 1 && var7 >= 0.75) {
                    var11 = 57349;
                } else if (var10 == var6 + 1 && var7 >= 0.5) {
                    var11 = 57348;
                } else if (var10 == var6 + 1 && var7 >= 0.25) {
                    var11 = 57347;
                } else {
                    var11 = 57345;
                }

                var9.append((char)var11);
            }

            var9.append(space(3)).append(var4 ? "§c" : "§d").append(bigNumber(var6));
            if (var5) {
                var9.append(space(3)).append("§f").append('\ue01b');
            }

            return var9.toString();
        }
    }

    static String scoreLine(int var0, int var1, int var2, boolean var3, boolean var4) {
        int var5 = Math.max(0, var2) / 60;
        int var6 = Math.max(0, var2) % 60;
        if (!pack) {
            return (var3 ? "§c연장 " : "§f")
                + var5
                + ":"
                + String.format("%02d", var6)
                + "   §9파랑 "
                + var0
                + " §f: §c"
                + var1
                + " 빨강"
                + (var4 ? "   §d×2 엘릭서" : "");
        } else {
            StringBuilder var7 = new StringBuilder("§f");

            for (int var8 = 0; var8 < 3; var8++) {
                var7.append((char)(var8 < var0 ? '\ue020' : '\ue022'));
            }

            var7.append(space(10)).append("§f").append('\ue01c').append(space(2));
            var7.append(var3 ? "§c" : (var2 <= 10 ? "§6" : "§f"));
            var7.append(bigNumber(var5)).append('\ue01a').append(bigNumber(var6 / 10)).append(bigNumber(var6 % 10));
            var7.append(space(10)).append("§f");

            for (int var9 = 0; var9 < 3; var9++) {
                var7.append((char)(var9 < var1 ? '\ue021' : '\ue022'));
            }

            if (var4) {
                var7.append(space(6)).append('\ue01b');
            }

            return var7.toString();
        }
    }

    static String hpBar(double var0, boolean var2, String var3) {
        int var4 = var2 ? 20 : 10;
        int var5 = (int)Math.ceil(Math.max(0.0, Math.min(1.0, var0)) * var4 - 1.0E-9);
        if (var0 > 0.0 && var5 == 0) {
            var5 = 1;
        }

        if (!pack) {
            StringBuilder var11 = new StringBuilder(var3);

            for (int var12 = 0; var12 < var4; var12++) {
                if (var12 == var5) {
                    var11.append("§8");
                }

                var11.append('▌');
            }

            return var11.toString();
        } else {
            int var6 = var2 ? '\ue034' : '\ue030';
            int var7 = var2 ? '\ue035' : '\ue031';
            int var8 = var2 ? '\ue036' : '\ue032';
            StringBuilder var9 = new StringBuilder("§f").append((char)var6).append(space(-1)).append(var3);

            for (int var10 = 0; var10 < var5; var10++) {
                var9.append((char)var7);
            }

            var9.append("§f");

            for (int var13 = var5; var13 < var4; var13++) {
                var9.append((char)var8);
            }

            var9.append(space(-1)).append((char)var6);
            return var9.toString();
        }
    }

    static String icon(char var0, String var1) {
        return pack ? "§f" + var0 : var1;
    }
}
