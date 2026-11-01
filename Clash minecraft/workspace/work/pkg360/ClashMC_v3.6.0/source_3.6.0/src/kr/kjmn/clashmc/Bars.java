package kr.kjmn.clashmc;

import java.util.HashMap;
import java.util.Map;
import org.bukkit.Color;
import org.bukkit.Location;
import org.bukkit.entity.TextDisplay;
import org.bukkit.entity.Display.Billboard;
import org.bukkit.entity.Display.Brightness;
import org.bukkit.util.Transformation;
import org.joml.Quaternionf;
import org.joml.Vector3f;

final class Bars {
    private final GameManager gm;
    private final Map<Combatant, TextDisplay> bars = new HashMap<>();
    private final Map<Combatant, String> lastText = new HashMap<>();

    Bars(GameManager var1) {
        this.gm = var1;
    }

    private double heightOf(Combatant var1) {
        if (var1.kind == Combatant.Kind.KING_TOWER) {
            return 8.6;
        } else if (var1.kind == Combatant.Kind.PRINCESS_TOWER) {
            return 7.0;
        } else if (var1.kind == Combatant.Kind.BARREL) {
            return 2.4;
        } else {
            double var2 = var1.card == null ? 2.0 : var1.card.barHeight;
            return var2 + (var1.isPlayer() ? 0.75 : 0.35);
        }
    }

    private TextDisplay create(Combatant var1, Location var2) {
        TextDisplay var3 = (TextDisplay)var2.getWorld().spawn(var2, TextDisplay.class);
        var3.addScoreboardTag("clashmc");
        var3.setBillboard(Billboard.CENTER);
        var3.setBackgroundColor(Color.fromARGB(0, 0, 0, 0));
        var3.setShadowed(true);
        var3.setSeeThrough(false);
        var3.setLineWidth(400);
        var3.setPersistent(false);
        var3.setTeleportDuration(2);
        var3.setViewRange(var1.isTower() ? 4.0F : 1.2F);
        float var4 = var1.kind == Combatant.Kind.KING_TOWER
            ? this.gm.core.kingBarScale
            : (var1.isTower() ? this.gm.core.princessBarScale : (var1.kind == Combatant.Kind.BUILDING ? 1.0F : 0.8F));
        var3.setTransformation(new Transformation(new Vector3f(), new Quaternionf(), new Vector3f(var4, var4, var4), new Quaternionf()));
        var3.setBrightness(new Brightness(15, 15));
        this.gm.battle.fx.track(var3);
        return var3;
    }

    String textOf(Combatant var1) {
        double var2 = var1.maxHp <= 0.0 ? 0.0 : Math.max(0.0, var1.hp) / var1.maxHp;
        int var4 = (int)Math.ceil(Math.max(0.0, var1.hp));
        String var5 = var1.team.cc;
        if (var1.isTower()) {
            boolean var10 = var1.kind == Combatant.Kind.KING_TOWER;
            String var11 = var10
                ? Glyphs.icon('\ue040', "§6♔") + " " + var5 + "§l킹 타워" + (var1.active ? "" : " §8§o(잠듦)")
                : Glyphs.icon('\ue041', "§7◆") + " " + var5 + "프린세스";
            String var12 = Glyphs.pack ? (var2 > 0.5 ? "§f" : (var2 > 0.25 ? "§e" : "§c")) + Glyphs.bigNumber(var4) : "§f§l" + var4;
            return var11 + "\n" + Glyphs.hpBar(var2, true, var5) + "\n" + var12 + " §7/ " + (int)var1.maxHp;
        } else {
            String var6 = "";
            if (var1.isPlayer()) {
                var6 = "§f" + GameManager.nameOf(var1.playerId) + " §7" + var1.card.name + "\n";
            } else if (var1.kind == Combatant.Kind.BUILDING) {
                var6 = var5 + var1.card.name + "\n";
            } else if (var1.kind == Combatant.Kind.BARREL) {
                var6 = var5 + "해골통\n";
            }

            String var7 = (this.gm.unitHpNumbers ? " §f" + var4 : "") + (var1.shield > 0.0 ? " §b◆" + (int)Math.ceil(var1.shield) : "");
            String var8 = this.gm.tick < var1.stunUntil ? " §b❄" : "";
            if (this.gm.tick < var1.deployUntil) {
                int var9 = (int)Math.ceil((var1.deployUntil - this.gm.tick) / 20.0 * 10.0);
                return var6 + "§b⏳ " + Glyphs.hpBar(var2, false, "§b") + " §b" + var9 / 10 + "." + var9 % 10 + "s";
            } else {
                if (var1.card != null && var1.card.stunResetsCharge) {
                    // 스파키: 충전 남은 시간
                    long left = var1.nextAttack - this.gm.tick;
                    String ch;
                    if (left <= 0L) {
                        ch = "§e§l⚡ 충전 완료!";
                    } else {
                        int t = (int)Math.ceil(left / 20.0 * 10.0);
                        int total = Math.max(1, var1.card.hitTicks());
                        int bars = (int)Math.max(0L, Math.min(10L, 10L - left * 10L / total));
                        ch = "§b⚡ §3" + "▮".repeat(bars) + "§8" + "▮".repeat(10 - bars) + " §b" + t / 10 + "." + t % 10 + "s";
                    }

                    return var6 + ch + "\n" + Glyphs.hpBar(var2, false, var5) + var7 + var8;
                }

                return var6 + Glyphs.hpBar(var2, false, var5) + var7 + var8;
            }
        }
    }

    void tick() {
        for (Combatant var2 : this.gm.battle.all) {
            if (var2.alive() && (!var2.hidden || var2.kind != Combatant.Kind.BUILDING || var2.card.id.equals("tesla"))) {
                Location var3 = var2.loc();
                if (var3 != null) {
                    Location var4 = var3.clone().add(0.0, this.heightOf(var2), 0.0);
                    if (var2.hidden) {
                        var4.add(0.0, -1.6, 0.0);
                    }

                    TextDisplay var5 = this.bars.get(var2);
                    if (var5 == null || !var5.isValid()) {
                        var5 = this.create(var2, var4);
                        this.bars.put(var2, var5);
                        this.lastText.remove(var2);
                    } else if (!var2.isStructure()) {
                        // 움직였을 때만 위치 보냄 (가만히 있는 유닛 체력바 패킷 절약)
                        Location cur = var5.getLocation();
                        double ddx = cur.getX() - var4.getX();
                        double ddy = cur.getY() - var4.getY();
                        double ddz = cur.getZ() - var4.getZ();
                        if (ddx * ddx + ddy * ddy + ddz * ddz > 0.0025) {
                            var5.teleport(var4);
                        }
                    }

                    String var6 = this.textOf(var2);
                    if (!var6.equals(this.lastText.get(var2))) {
                        var5.setText(var6);
                        this.lastText.put(var2, var6);
                    }
                }
            } else {
                this.remove(var2);
            }
        }

        this.bars.keySet().removeIf(var1 -> {
            if (var1.alive()) {
                return false;
            } else {
                TextDisplay var2x = this.bars.get(var1);
                if (var2x != null) {
                    this.gm.battle.fx.untrack(var2x);
                    var2x.remove();
                }

                this.lastText.remove(var1);
                return true;
            }
        });
    }

    void remove(Combatant var1) {
        TextDisplay var2 = this.bars.remove(var1);
        this.lastText.remove(var1);
        if (var2 != null) {
            this.gm.battle.fx.untrack(var2);
            var2.remove();
        }
    }

    void clear() {
        for (TextDisplay var2 : this.bars.values()) {
            var2.remove();
        }

        this.bars.clear();
        this.lastText.clear();
    }
}
