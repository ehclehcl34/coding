import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()

def rep(a, b):
    global s
    n = s.count(a)
    assert n == 1, (n, a[:120])
    s = s.replace(a, b)

# ---------- 1. 설정 필드 + 생성자 ----------
rep("""    final Fx fx;
    final Bars bars;

    Battle(GameManager var1) {
        this.gm = var1;
        this.fx = new Fx(var1);
        this.bars = new Bars(var1);
    }
""", """    final Fx fx;
    final Bars bars;
    // 겹침 방지 (game.collision.*)
    private final boolean collideOn;
    private final double collideStrength;
    private final double collideMaxPush;
    private final double collidePlayerPush;
    // 프린스 돌진: 이 틱 수 이상 멈춰 있으면 돌진/누적 거리 초기화 (game.charge-reset-ticks)
    private final long chargeResetTicks;

    Battle(GameManager var1) {
        this.gm = var1;
        this.fx = new Fx(var1);
        this.bars = new Bars(var1);
        org.bukkit.configuration.file.FileConfiguration cfg = var1.plugin.getConfig();
        this.collideOn = cfg.getBoolean("game.collision.enabled", true);
        this.collideStrength = Math.max(0.05, Math.min(1.0, cfg.getDouble("game.collision.strength", 0.5)));
        this.collideMaxPush = Math.max(0.05, cfg.getDouble("game.collision.max-push", 0.35));
        this.collidePlayerPush = Math.max(0.0, cfg.getDouble("game.collision.player-push", 0.5));
        this.chargeResetTicks = Math.max(1L, (long)cfg.getDouble("game.charge-reset-ticks", 6.0));
    }
""")

# ---------- 2. 배치: 건물이 타워/다른 건물과 겹치면 막기 ----------
rep("""                for (Combatant var8 : this.all) {
                    if (var8.isTower() && var8.alive() && var5.tileInRect(var3, var4, var8.towerTx, var8.towerTz, var8.towerTiles)) {
                        return "타워 위에는 배치할 수 없습니다";
                    }
                }

                if (var2.anywhere) {""", """                for (Combatant var8 : this.all) {
                    if (var8.isTower() && var8.alive() && var5.tileInRect(var3, var4, var8.towerTx, var8.towerTz, var8.towerTiles)) {
                        return "타워 위에는 배치할 수 없습니다";
                    }
                }

                if (var2.type == CardDef.Type.BUILDING) {
                    String overlap = this.buildingOverlap(var2, var5.tileCenter(var3, var4));
                    if (overlap != null) {
                        return overlap;
                    }
                }

                if (var2.anywhere) {""")

# ---------- 3. 틱 끝에 겹침 방지 ----------
rep("""        this.all.removeIf(var0 -> var0.dead && !var0.isTower());
        if (this.gm.hpDisplays) {""", """        if (this.gm.phase == GameManager.Phase.PLAYING) {
            this.separate();
        }

        this.all.removeIf(var0 -> var0.dead && !var0.isTower());
        if (this.gm.hpDisplays) {""")

# ---------- 4. AI: 멈추면 돌진 초기화 ----------
rep("""                    if (var4 != null) {
                        this.step(var1, var2, this.route(var1, var2, var4));
                    }
                }
            }
        } else {
            var1.dead = true;
        }
    }
""", """                    if (var4 != null) {
                        this.step(var1, var2, this.route(var1, var2, var4));
                    }
                }
            }

            this.chargeIdleCheck(var1);
        } else {
            var1.dead = true;
        }
    }
""")

# ---------- 5. 사거리: 건물/타워는 사각형 가장자리까지 거리 ----------
rep("""    private boolean inRange(Combatant var1, Location var2, Combatant var3, double var4) {
        Location var6 = var3.loc();
        return var2 != null && var6 != null ? flat(var2, var6) - var3.radius <= var4 + 0.6 : false;
    }
""", """    private boolean inRange(Combatant var1, Location var2, Combatant var3, double var4) {
        Location var6 = var3.loc();
        if (var2 != null && var6 != null) {
            double[] box = this.structBox(var3);
            if (box != null) {
                // 겹침 방지가 유닛을 사각형 밖으로 밀어내므로, 사거리도 사각형 가장자리 기준 (모서리에서 막혀 못 때리는 것 방지)
                double ex = Math.max(box[0] - var2.getX(), Math.max(0.0, var2.getX() - box[2]));
                double ez = Math.max(box[1] - var2.getZ(), Math.max(0.0, var2.getZ() - box[3]));
                if (Math.sqrt(ex * ex + ez * ez) <= var4 + 0.6) {
                    return true;
                }
            }

            return flat(var2, var6) - var3.radius <= var4 + 0.6;
        } else {
            return false;
        }
    }
""")

# ---------- 6. step: 이동 방향 기록 ----------
rep("""            var9.setY(var10);
            var9.setDirection(var6);
            var9.setPitch(0.0F);
            var1.mob.teleport(var9);""", """            var9.setY(var10);
            var9.setDirection(var6);
            var9.setPitch(0.0F);
            var1.mob.teleport(var9);
            var1.moveDx = var6.getX();
            var1.moveDz = var6.getZ();
            var1.moveTick = this.now();""")

# 돌진 시작 연출 (AI)
rep("""            } else if (var1.chargeDist >= var1.card.chargeDistance) {
                var1.charging = true;
                this.A().world.playSound(var2, "entity.horse.angry", 0.9F, 1.0F);
            }""", """            } else if (var1.chargeDist >= var1.card.chargeDistance) {
                var1.charging = true;
                this.chargeStartFx(var2);
                var4 *= 2.0;
            }""")

# ---------- 7. 넉백되면 돌진 초기화 ----------
rep("""                var6.normalize().multiply(var3);
                if (var1.isPlayer()) {
                    Player var7 = var1.player();""", """                var6.normalize().multiply(var3);
                this.resetCharge(var1);
                if (var1.isPlayer()) {
                    Player var7 = var1.player();""")

# ---------- 8. 플레이어 프린스 ----------
rep("""                if (!var1.charging && var1.chargeDist >= var1.card.chargeDistance) {
                    var1.charging = true;
                    var2.playSound(var5, "entity.horse.angry", 0.9F, 1.0F);
                    var2.sendActionBar("§6§l돌진!");
                }

                if (var1.charging) {
                    var4 *= 2.0F;
                }""", """                if (!var1.charging && var1.chargeDist >= var1.card.chargeDistance) {
                    var1.charging = true;
                    this.chargeStartFx(var5);
                }

                if (var1.charging) {
                    var4 *= 2.0F;
                    this.A().world.spawnParticle(Particle.CLOUD, var5.clone().add(0.0, 0.2, 0.0), 2, 0.3, 0.05, 0.3, 0.01);
                    this.A().world.spawnParticle(Particle.CRIT, var5.clone().add(0.0, 1.2, 0.0), 2, 0.3, 0.3, 0.3, 0.05);
                    if (this.now() % 10L == 0L) {
                        var2.sendActionBar("§6§l⚡ 돌진! §e다음 공격 " + (int)var1.card.chargeDamage);
                    }
                } else if (this.now() % 5L == 0L) {
                    int bars = (int)Math.min(10.0, Math.floor(var1.chargeDist / Math.max(0.1, var1.card.chargeDistance) * 10.0));
                    var2.sendActionBar("§7돌진 준비 §e" + "▮".repeat(bars) + "§8" + "▮".repeat(10 - bars));
                }""")

rep("""            var1.lastPos = var11;
            this.setWalking(var1, var2, this.now() - var1.lastMoveTick <= 3L);""", """            var1.lastPos = var11;
            this.chargeIdleCheck(var1);
            this.setWalking(var1, var2, this.now() - var1.lastMoveTick <= 3L);""")

# ---------- 9. 새 메서드들 (flat 앞에) ----------
rep("""    private static double flat(Location var0, Location var1) {""", """    // ===================== 프린스 돌진 =====================

    private void resetCharge(Combatant c) {
        if (c.card != null && c.card.charge && (c.charging || c.chargeDist > 0.0)) {
            boolean was = c.charging;
            c.charging = false;
            c.chargeDist = 0.0;
            if (was) {
                Player p = c.player();
                if (p != null) {
                    p.sendActionBar("§7돌진 풀림");
                }
            }
        }
    }

    /** 원작처럼 계속 움직여야 돌진이 유지됨: 일정 시간 멈춰 있으면 초기화 */
    private void chargeIdleCheck(Combatant c) {
        if (c.card != null && c.card.charge && (c.charging || c.chargeDist > 0.0) && this.now() - c.lastMoveTick > this.chargeResetTicks) {
            this.resetCharge(c);
        }
    }

    private void chargeStartFx(Location l) {
        World w = this.A().world;
        w.playSound(l, "entity.horse.angry", 1.0F, 1.0F);
        w.playSound(l, "entity.horse.gallop", 1.0F, 1.2F);
        w.spawnParticle(Particle.CLOUD, l.clone().add(0.0, 0.3, 0.0), 12, 0.5, 0.1, 0.5, 0.05);
        w.spawnParticle(Particle.CRIT, l.clone().add(0.0, 1.4, 0.0), 10, 0.4, 0.4, 0.4, 0.2);
    }

    // ===================== 겹침 방지 =====================

    /** 타워/건물이 차지하는 사각형 {x0, z0, x1, z1}. 구조물이 아니면 null */
    private double[] structBox(Combatant s) {
        if (s.isTower() && s.towerTiles > 0) {
            Arena a = this.A();
            return new double[]{a.minX + s.towerTx * 3, a.minZ + s.towerTz * 3, a.minX + (s.towerTx + s.towerTiles) * 3, a.minZ + (s.towerTz + s.towerTiles) * 3};
        } else if (s.kind == Combatant.Kind.BUILDING && s.fixed != null) {
            double h = s.radius;
            return new double[]{s.fixed.getX() - h, s.fixed.getZ() - h, s.fixed.getX() + h, s.fixed.getZ() + h};
        } else {
            return null;
        }
    }

    /** 건물을 놓을 자리가 타워나 다른 건물과 겹치면 이유, 아니면 null */
    private String buildingOverlap(CardDef card, Location center) {
        double h = card.size / 2.0;
        double x0 = center.getX() - h + 0.05, x1 = center.getX() + h - 0.05;
        double z0 = center.getZ() - h + 0.05, z1 = center.getZ() + h - 0.05;
        for (Combatant c : this.all) {
            if (!c.alive()) {
                continue;
            }

            double[] b = this.structBox(c);
            if (b != null && x0 < b[2] && x1 > b[0] && z0 < b[3] && z1 > b[1]) {
                return c.isTower() ? "타워와 겹쳐서 배치할 수 없습니다" : "다른 건물과 겹쳐서 배치할 수 없습니다";
            }
        }

        return null;
    }

    private static double bodyRadius(Combatant c) {
        return c.radius > 0.05 ? c.radius : 0.5;
    }

    /** 무거운(큰) 유닛이 가벼운 유닛을 밀어냄 */
    private static double bodyMass(Combatant c) {
        if (c.card == null) {
            return 1.0;
        }

        double w = Math.max(0.3, c.card.hitboxW);
        double hgt = Math.max(0.5, c.card.hitboxH);
        return w * w * hgt;
    }

    /** 강(다리 밖)에 있는지: 강 점프 중인 유닛은 겹침 계산에서 뺌 */
    private boolean inRiverOffBridge(double x, double z) {
        Arena a = this.A();
        if (z <= a.riverMinZ() || z >= a.riverMaxZ()) {
            return false;
        }

        double half = a.bridgeHalf();
        return Math.abs(x - a.bridgeX(true)) > half && Math.abs(x - a.bridgeX(false)) > half;
    }

    /**
     * 매 틱: 유닛끼리(지상끼리 / 공중끼리) 겹치면 서로 밀어내고,
     * 지상 유닛은 타워·건물 사각형 안으로 못 들어가게 밀어냄.
     * AI 는 텔레포트로, 플레이어 유닛은 속도로 밀림.
     */
    private void separate() {
        if (!this.collideOn) {
            return;
        }

        Arena a = this.A();
        List<Combatant> body = new ArrayList<>();
        List<Location> pos = new ArrayList<>();
        for (Combatant c : this.all) {
            if (!c.alive() || c.hidden || c.dead) {
                continue;
            }

            if (c.kind != Combatant.Kind.TROOP && c.kind != Combatant.Kind.BARREL) {
                continue;
            }

            if (!c.isPlayer() && (c.mob == null || !c.mob.isValid())) {
                continue;
            }

            Location l = c.loc();
            if (l == null || l.getWorld() != a.world || !a.inField(l)) {
                continue;
            }

            if (!c.air && this.inRiverOffBridge(l.getX(), l.getZ())) {
                continue;
            }

            body.add(c);
            pos.add(l);
        }

        int n = body.size();
        if (n == 0) {
            return;
        }

        double[] dx = new double[n];
        double[] dz = new double[n];

        // 1) 유닛 vs 유닛
        for (int i = 0; i < n; i++) {
            Combatant ci = body.get(i);
            Location li = pos.get(i);
            double ri = bodyRadius(ci);
            for (int j = i + 1; j < n; j++) {
                Combatant cj = body.get(j);
                if (ci.air != cj.air) {
                    continue;
                }

                Location lj = pos.get(j);
                double min = ri + bodyRadius(cj);
                double ex = lj.getX() - li.getX();
                double ez = lj.getZ() - li.getZ();
                double d2 = ex * ex + ez * ez;
                if (d2 >= min * min) {
                    continue;
                }

                double d = Math.sqrt(d2);
                if (d < 1.0E-4) {
                    double ang = ((ci.id * 7919L + cj.id * 104729L) % 360L) * Math.PI / 180.0;
                    ex = Math.cos(ang);
                    ez = Math.sin(ang);
                    d = 0.0;
                } else {
                    ex /= d;
                    ez /= d;
                }

                double push = (min - d) * this.collideStrength;
                double mi = bodyMass(ci);
                double mj = bodyMass(cj);
                double si = mj / (mi + mj);
                double sj = mi / (mi + mj);
                dx[i] -= ex * push * si;
                dz[i] -= ez * push * si;
                dx[j] += ex * push * sj;
                dz[j] += ez * push * sj;
            }
        }

        // 유닛끼리 미는 양은 한 틱에 너무 크지 않게
        for (int i = 0; i < n; i++) {
            double len = Math.sqrt(dx[i] * dx[i] + dz[i] * dz[i]);
            if (len > this.collideMaxPush) {
                dx[i] *= this.collideMaxPush / len;
                dz[i] *= this.collideMaxPush / len;
            }
        }

        // 2) 지상 유닛 vs 타워/건물 (구조물은 안 움직임, 한 번에 완전히 밀어냄)
        List<double[]> boxes = new ArrayList<>();
        for (Combatant s : this.all) {
            if (s.alive()) {
                double[] b = this.structBox(s);
                if (b != null) {
                    boxes.add(b);
                }
            }
        }

        for (int i = 0; i < n; i++) {
            Combatant c = body.get(i);
            if (c.air) {
                continue;
            }

            double r = bodyRadius(c);
            for (double[] b : boxes) {
                double px = pos.get(i).getX() + dx[i];
                double pz = pos.get(i).getZ() + dz[i];
                if (px < b[0] - r || px > b[2] + r || pz < b[1] - r || pz > b[3] + r) {
                    continue;
                }

                double qx = Math.max(b[0], Math.min(b[2], px));
                double qz = Math.max(b[1], Math.min(b[3], pz));
                double nx;
                double nz;
                double depth;
                if (qx == px && qz == pz) {
                    // 중심이 사각형 안: 가장 가까운 변으로
                    double l = px - b[0], rr = b[2] - px, t = pz - b[1], bt = b[3] - pz;
                    double m = Math.min(Math.min(l, rr), Math.min(t, bt));
                    if (m == l) {
                        nx = -1.0; nz = 0.0;
                    } else if (m == rr) {
                        nx = 1.0; nz = 0.0;
                    } else if (m == t) {
                        nx = 0.0; nz = -1.0;
                    } else {
                        nx = 0.0; nz = 1.0;
                    }

                    depth = m + r;
                } else {
                    double ex = px - qx;
                    double ez = pz - qz;
                    double d = Math.sqrt(ex * ex + ez * ez);
                    if (d >= r) {
                        continue;
                    }

                    nx = ex / d;
                    nz = ez / d;
                    depth = r - d;
                }

                dx[i] += nx * depth;
                dz[i] += nz * depth;

                // AI 가 정면으로 들이받고 있으면 옆으로 미끄러지게 (건물 앞에서 멈춰버리는 것 방지)
                if (!c.isPlayer() && c.moveTick == this.now()) {
                    double mv = Math.sqrt(c.moveDx * c.moveDx + c.moveDz * c.moveDz);
                    if (mv > 1.0E-4 && (c.moveDx * nx + c.moveDz * nz) / mv < -0.3) {
                        double tx = -nz;
                        double tz = nx;
                        double side = c.moveDx * tx + c.moveDz * tz;
                        if (Math.abs(side) < 1.0E-3) {
                            side = (c.id & 1) == 0 ? 1.0 : -1.0;
                        }

                        double sgn = Math.signum(side);
                        dx[i] += tx * sgn * mv * 0.8;
                        dz[i] += tz * sgn * mv * 0.8;
                    }
                }
            }
        }

        // 3) 적용
        double fx0 = a.minX + 0.4;
        double fx1 = a.minX + 54 - 0.4;
        double fz0 = a.minZ + 0.4;
        double fz1 = a.minZ + 96 - 0.4;
        for (int i = 0; i < n; i++) {
            double mx = dx[i];
            double mz = dz[i];
            if (mx * mx + mz * mz < 1.0E-5) {
                continue;
            }

            Combatant c = body.get(i);
            Location from = pos.get(i);
            double tx = Math.max(fx0, Math.min(fx1, from.getX() + mx));
            double tz = Math.max(fz0, Math.min(fz1, from.getZ() + mz));
            if (!c.air && this.inRiverOffBridge(tx, tz)) {
                // 다리 밖 강으로 밀려나지 않게: 가까운 다리 폭 안으로
                double half = a.bridgeHalf() - 0.5;
                double bx = Math.abs(tx - a.bridgeX(true)) < Math.abs(tx - a.bridgeX(false)) ? a.bridgeX(true) : a.bridgeX(false);
                tx = Math.max(bx - half, Math.min(bx + half, tx));
                if (this.inRiverOffBridge(tx, tz)) {
                    continue;
                }
            }

            mx = tx - from.getX();
            mz = tz - from.getZ();
            if (c.isPlayer()) {
                Player p = c.player();
                if (p != null && this.collidePlayerPush > 0.0) {
                    Vector v = p.getVelocity();
                    double k = this.collidePlayerPush;
                    p.setVelocity(new Vector(v.getX() + mx * k, v.getY(), v.getZ() + mz * k));
                }
            } else {
                Location to = from.clone();
                to.setX(tx);
                to.setZ(tz);
                c.mob.teleport(to);
            }
        }
    }

    private static double flat(Location var0, Location var1) {""")

open(p, 'w', encoding='utf-8').write(s)
print('patched')
