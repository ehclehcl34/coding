package kr.kjmn.clashmc;

import java.util.ArrayList;
import java.util.Collections;
import org.bukkit.Location;

final class Bot {
    private final GameManager gm;
    final TeamColor team;
    Bot.Level level;
    double interval;
    boolean infinite;
    private long next;
    private boolean pushLeft;

    Bot(GameManager var1, TeamColor var2, Bot.Level var3) {
        this.gm = var1;
        this.team = var2;
        this.level = var3;
        this.interval = var3.interval;
        this.next = var1.tick + 60L;
        this.pushLeft = var1.rng.nextBoolean();
    }

    void now() {
        this.next = 0L;
    }

    void tick() {
        GameTeam var1 = this.gm.teams.get(this.team);
        if (var1 != null) {
            if (this.infinite) {
                var1.elixir = this.gm.maxElixir;
            }

            if (this.gm.tick >= this.next) {
                Combatant var2 = this.threat();
                double var3 = this.interval * (0.7 + this.gm.rng.nextDouble() * 0.6);
                if (var2 != null && this.level.smart > 0.0) {
                    var3 *= 0.5;
                }

                this.next = this.gm.tick + (long)(var3 * 20.0);
                if (this.level != Bot.Level.HARD || var2 != null || !(var1.elixir < 8.0) || this.gm.doubleElixir()) {
                    this.play(var1, var2);
                }
            }
        }
    }

    private Combatant threat() {
        Combatant var1 = null;
        double var2 = Double.MAX_VALUE;

        for (Combatant var5 : this.gm.battle.all) {
            if (var5.alive() && var5.team != this.team && !var5.isTower() && var5.kind != Combatant.Kind.BUILDING) {
                Location var6 = var5.loc();
                if (var6 != null) {
                    TeamColor var7 = this.gm.arena.sideOf(this.gm.arena.tileZ(var6.getZ()));
                    if (var7 == this.team) {
                        double var8 = this.gm.arena.kingCenter(this.team).distance(var6);
                        if (var8 < var2) {
                            var2 = var8;
                            var1 = var5;
                        }
                    }
                }
            }
        }

        return var1;
    }

    private void play(GameTeam var1, Combatant var2) {
        ArrayList var3 = new ArrayList();

        for (int var4 = 0; var4 < 4; var4++) {
            CardDef var5 = this.gm.cards.get(var1.hand[var4]);
            if (var5 != null && var1.elixir + 1.0E-9 >= this.gm.costOf(var1, var5) && (!var5.id.equals("mirror") || var1.lastPlayed != null)) {
                var3.add(var4);
            }
        }

        if (!var3.isEmpty()) {
            Collections.shuffle(var3, this.gm.rng);
            if (this.level.smart > 0.0) {
                var3.sort((var3x, var4x) -> Double.compare(this.score(var1, var4x, var2), this.score(var1, var3x, var2)));
            }

            for (int var10 : var3) {
                CardDef var6 = this.gm.cards.get(var1.hand[var10]);
                if (!(this.level.smart > 0.0) || !(this.score(var1, var10, var2) < -5.0)) {
                    int[] var7 = this.pickTile(var6.id.equals("mirror") ? this.gm.cards.get(var1.lastPlayed) : var6, var2);
                    if (var7 != null) {
                        var1.elixir = var1.elixir - this.gm.costOf(var1, var6);
                        String var8 = var1.pending.poll();
                        var1.pending.add(var6.id);
                        var1.hand[var10] = var8;
                        this.gm.battle.deploy(var1, var6, var7[0], var7[1], this.gm.arena.tileCenter(var7[0], var7[1]));
                        this.gm.botPlayed(var1, var6, var7);
                        return;
                    }
                }
            }
        }
    }

    private double score(GameTeam var1, int var2, Combatant var3) {
        CardDef var4 = this.gm.cards.get(var1.hand[var2]);
        if (var4 == null) {
            return -99.0;
        } else {
            double var5 = this.gm.rng.nextDouble() * 3.0;
            if (var4.isSpell()) {
                int var7 = this.clusterAt(this.bestSpellSpot(var4), var4.radius > 0.0 ? var4.radius : 2.5);
                var5 += var7 >= 3 ? 12.0 : (var7 >= 2 ? 6.0 * this.level.smart : -8.0);
            } else if (var3 != null) {
                if (var4.type == CardDef.Type.BUILDING) {
                    var5 += 7.0;
                }

                if (var4.targets != CardDef.Targets.BUILDINGS) {
                    var5 += 5.0;
                }

                if (var3.air && var4.targets == CardDef.Targets.GROUND) {
                    var5 -= 10.0;
                }
            } else {
                if (var4.targets == CardDef.Targets.BUILDINGS) {
                    var5 += 4.0 + 4.0 * this.level.smart;
                }

                if (var4.type == CardDef.Type.BUILDING) {
                    var5 -= 6.0;
                }
            }

            return var5;
        }
    }

    private Location bestSpellSpot(CardDef var1) {
        Location var2 = null;
        int var3 = 0;
        double var4 = var1.radius > 0.0 ? var1.radius : 2.5;

        for (Combatant var7 : this.gm.battle.all) {
            if (var7.alive() && var7.team != this.team) {
                Location var8 = var7.loc();
                if (var8 != null) {
                    int var9 = this.clusterAt(var8, var4);
                    if (var9 > var3) {
                        var3 = var9;
                        var2 = var8;
                    }
                }
            }
        }

        return var2;
    }

    private int clusterAt(Location var1, double var2) {
        if (var1 == null) {
            return 0;
        } else {
            int var4 = 0;

            for (Combatant var6 : this.gm.battle.all) {
                if (var6.alive() && var6.team != this.team) {
                    Location var7 = var6.loc();
                    if (var7 != null) {
                        double var8 = var7.getX() - var1.getX();
                        double var10 = var7.getZ() - var1.getZ();
                        if (var8 * var8 + var10 * var10 <= var2 * var2) {
                            var4 += var6.isTower() ? 2 : 1;
                        }
                    }
                }
            }

            return var4;
        }
    }

    private int[] splitTile(CardDef var1, int var2, int var3) {
        byte var4 = 9;

        for (int var5 = 0; var5 < 4; var5++) {
            int var6 = var2 + var3 * var5;
            if (var6 < 0 || var6 >= 32) {
                break;
            }

            int var7 = this.gm.rng.nextBoolean() ? var4 - 1 : var4;

            for (int var11 : new int[]{var7, var7 == var4 ? var4 - 1 : var4}) {
                if (this.gm.battle.placementError(this.team, var1, var11, var6) == null) {
                    return new int[]{var11, var6};
                }
            }
        }

        return null;
    }

    private boolean threatBothLanes() {
        boolean var1 = false;
        boolean var2 = false;
        double var3 = this.gm.arena.centerX();

        for (Combatant var6 : this.gm.battle.all) {
            if (var6.alive() && var6.team != this.team && !var6.isTower() && var6.kind != Combatant.Kind.BUILDING) {
                Location var7 = var6.loc();
                if (var7 != null && this.gm.arena.sideOf(this.gm.arena.tileZ(var7.getZ())) == this.team) {
                    if (var7.getX() < var3) {
                        var1 = true;
                    } else {
                        var2 = true;
                    }
                }
            }
        }

        return var1 && var2;
    }

    private int[] pickTile(CardDef var1, Combatant var2) {
        Arena var3 = this.gm.arena;
        boolean var4 = this.team == TeamColor.RED;
        if (!var1.isSpell() || !var1.id.equals("rage") && !var1.id.equals("clone")) {
            if (var1.isSpell()) {
                Location var15 = this.bestSpellSpot(var1);
                if (var15 == null) {
                    Combatant var21 = this.gm.battle.towerOf(this.team.other(), this.gm.rng.nextBoolean() ? "left" : "right");
                    if (var21 == null || !var21.alive()) {
                        var21 = this.gm.battle.towerOf(this.team.other(), "king");
                    }

                    var15 = var21 == null ? null : var21.fixed;
                }

                if (var15 == null) {
                    return null;
                } else {
                    int var22 = var3.tileX(var15.getX());
                    int var26 = var3.tileZ(var15.getZ());
                    if (this.gm.battle.placementError(this.team, var1, var22, var26) != null) {
                        if (!var1.ownSide) {
                            return null;
                        }

                        var26 = var4 ? 18 : 13;
                        if (this.gm.battle.placementError(this.team, var1, var22, var26) != null) {
                            return null;
                        }
                    }

                    return new int[]{var22, var26};
                }
            } else {
                boolean var14 = this.gm.splitEnabled
                    && var1.type == CardDef.Type.SQUAD
                    && var1.count >= 2
                    && !var1.anywhere
                    && !var1.id.equals("goblin_barrel");
                if (var14 && this.level.smart > 0.0 && this.threatBothLanes()) {
                    int[] var16 = this.splitTile(var1, var4 ? 23 : 8, var4 ? 1 : -1);
                    if (var16 != null) {
                        return var16;
                    }
                }

                if (var2 != null && this.level.smart > 0.0) {
                    Location var17 = var2.loc();
                    int var23 = var3.tileX(var17.getX());
                    int var27 = var3.tileZ(var17.getZ());
                    if (var1.type == CardDef.Type.BUILDING) {
                        var23 = 8 + this.gm.rng.nextInt(2);
                        var27 = var4 ? 21 : 10;
                    } else {
                        var27 += var4 ? 2 : -2;
                    }

                    for (int var31 = 0; var31 < 8; var31++) {
                        int var33 = Math.max(0, Math.min(17, var23 + this.gm.rng.nextInt(3) - 1));
                        int var34 = Math.max(0, Math.min(31, var27 + this.gm.rng.nextInt(3) - 1));
                        if (this.gm.battle.placementError(this.team, var1, var33, var34) == null) {
                            return new int[]{var33, var34};
                        }
                    }
                }

                if (var14 && var2 == null && this.gm.rng.nextDouble() < 0.3 + 0.4 * this.level.smart) {
                    int[] var18 = this.gm.rng.nextDouble() < 0.6
                        ? this.splitTile(var1, var4 ? 31 : 0, var4 ? -1 : 1)
                        : this.splitTile(var1, var4 ? 25 : 6, var4 ? 1 : -1);
                    if (var18 != null) {
                        return var18;
                    }
                }

                if (var1.id.equals("goblin_barrel") && this.level.smart > 0.0 && this.gm.rng.nextDouble() < 0.4 + 0.5 * this.level.smart) {
                    Combatant var19 = this.gm.battle.towerOf(this.team.other(), this.gm.rng.nextBoolean() ? "left" : "right");
                    if (var19 == null || !var19.alive()) {
                        var19 = this.gm.battle.towerOf(this.team.other(), "king");
                    }

                    if (var19 != null && var19.alive()) {
                        int var24 = var19.towerTx + var19.towerTiles / 2;
                        int var29 = var19.towerTz + var19.towerTiles / 2;
                        if (this.gm.battle.placementError(this.team, var1, var24, var29) == null) {
                            return new int[]{var24, var29};
                        }
                    }
                }

                boolean var20 = this.level == Bot.Level.HARD ? this.pushLeft : this.gm.rng.nextBoolean();

                for (int var25 = 0; var25 < 30; var25++) {
                    int var30 = var20 ? this.gm.rng.nextInt(9) : 9 + this.gm.rng.nextInt(9);
                    int var32;
                    if (var1.anywhere) {
                        var32 = var4 ? 2 + this.gm.rng.nextInt(12) : 17 + this.gm.rng.nextInt(12);
                    } else if (var1.type == CardDef.Type.BUILDING) {
                        var32 = var4 ? 20 + this.gm.rng.nextInt(4) : 8 + this.gm.rng.nextInt(4);
                    } else if (var1.targets == CardDef.Targets.BUILDINGS && this.level.smart > 0.0) {
                        var32 = var4 ? 17 + this.gm.rng.nextInt(2) : 13 + this.gm.rng.nextInt(2);
                    } else {
                        var32 = var4 ? 17 + this.gm.rng.nextInt(11) : 4 + this.gm.rng.nextInt(11);
                    }

                    if (this.gm.battle.placementError(this.team, var1, var30, var32) == null) {
                        return new int[]{var30, var32};
                    }
                }

                return null;
            }
        } else {
            Location var5 = null;
            int var6 = 0;

            for (Combatant var8 : this.gm.battle.all) {
                if (var8.alive() && var8.team == this.team && !var8.isStructure()) {
                    Location var9 = var8.loc();
                    if (var9 != null) {
                        int var10 = 0;

                        for (Combatant var12 : this.gm.battle.all) {
                            if (var12.alive() && var12.team == this.team && !var12.isStructure()) {
                                Location var13 = var12.loc();
                                if (var13 != null && Math.hypot(var13.getX() - var9.getX(), var13.getZ() - var9.getZ()) <= var1.radius) {
                                    var10++;
                                }
                            }
                        }

                        if (var10 > var6) {
                            var6 = var10;
                            var5 = var9;
                        }
                    }
                }
            }

            return var5 != null && var6 >= 2 ? new int[]{var3.tileX(var5.getX()), var3.tileZ(var5.getZ())} : null;
        }
    }

    static enum Level {
        EASY("쉬움", 6.0, 0.0),
        NORMAL("보통", 3.5, 0.5),
        HARD("어려움", 2.0, 1.0);

        final String ko;
        final double interval;
        final double smart;

        private Level(String nullxx, double nullxxx, double nullxxxx) {
            this.ko = nullxx;
            this.interval = nullxxx;
            this.smart = nullxxxx;
        }
    }
}
