package kr.kjmn.clashmc;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.function.Consumer;
import org.bukkit.Bukkit;
import org.bukkit.Color;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.World;
import org.bukkit.Particle.DustOptions;
import org.bukkit.attribute.Attribute;
import org.bukkit.attribute.AttributeInstance;
import org.bukkit.block.Block;
import org.bukkit.entity.Ageable;
import org.bukkit.entity.ArmorStand;
import org.bukkit.entity.BlockDisplay;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Interaction;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Player;
import org.bukkit.inventory.EntityEquipment;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.inventory.meta.LeatherArmorMeta;
import org.bukkit.scheduler.BukkitRunnable;
import org.bukkit.util.RayTraceResult;
import org.bukkit.util.Vector;
import org.joml.Vector3f;
import org.joml.Quaternionf;
import org.bukkit.util.Transformation;
import org.bukkit.entity.Display.Brightness;

public final class Battle {
    private final GameManager gm;
    final List<Combatant> all = new ArrayList<>();
    final Map<UUID, Combatant> byEntity = new HashMap<>();
    private final List<Battle.Zone> zones = new ArrayList<>();
    private final List<BukkitRunnable> running = new ArrayList<>();
    private final Set<UUID> reserved = new HashSet<>();
    final Fx fx;
    final Bars bars;
    // 겹침 방지 (game.collision.*)
    private final boolean collideOn;
    private final double collideStrength;
    private final double collideMaxPush;
    private final double collidePlayerPush;
    // 프린스 돌진: 이 틱 수 이상 멈춰 있으면 돌진/누적 거리 초기화 (game.charge-reset-ticks)
    private final long chargeResetTicks;
    // 탑뷰 (킹이 F키로 전환): 경기장 가운데 상공에서 내려다봄
    private final Set<UUID> topView = new HashSet<>();
    private final boolean topViewOn;
    private final double topViewHeight;

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
        this.topViewOn = cfg.getBoolean("game.top-view.enabled", true);
        this.topViewHeight = Math.max(8.0, cfg.getDouble("game.top-view.height", 40.0));
    }

    private Arena A() {
        return this.gm.arena;
    }

    private long now() {
        return this.gm.tick;
    }

    void buildTowers() {
        for (TeamColor var4 : TeamColor.values()) {
            this.makeTower(var4, Combatant.Kind.PRINCESS_TOWER, true);
            this.makeTower(var4, Combatant.Kind.PRINCESS_TOWER, false);
            this.makeTower(var4, Combatant.Kind.KING_TOWER, false);
        }
    }

    private void makeTower(TeamColor var1, Combatant.Kind var2, boolean var3) {
        boolean var4 = var2 == Combatant.Kind.KING_TOWER;
        Combatant var5 = new Combatant(var2, var1, null);
        var5.left = var3;
        var5.towerTx = var4 ? this.A().kingTx() : this.A().princessTx(var3);
        var5.towerTz = var4 ? this.A().kingTz(var1) : this.A().princessTz(var1);
        var5.towerTiles = var4 ? 4 : 3;
        var5.maxHp = var5.hp = var4 ? this.gm.kingHp : this.gm.princessHp;
        var5.radius = var5.towerTiles * 3 / 2.0;
        var5.active = !var4;
        var5.fixed = var4 ? this.A().kingCenter(var1) : this.A().princessCenter(var1, var3);
        var5.fixed.setYaw(this.facing(var1));
        var5.towerModel = this.gm.skinModel(var1, var4 ? "king" : "princess", var4 ? this.gm.kingModel : ptower(this.gm.princessModel), null, false);
        boolean var6 = this.gm.models.enabled() && var5.towerModel != null && !var5.towerModel.isEmpty();
        this.setTowerBlocks(var5, var6 && this.gm.barrierCollision ? Material.BARRIER : Material.STONE_BRICKS, var1.concrete, var4 ? 6 : 5);
        this.spawnTowerParts(var5);
        this.refreshName(var5);
        this.all.add(var5);
    }

    private boolean spawnTowerParts(Combatant var1) {
        boolean var2 = var1.kind == Combatant.Kind.KING_TOWER;
        int var3 = var1.towerTiles * 3;
        int var4 = var2 ? 6 : 5;
        World var5 = this.A().world;
        if (var1.hitbox == null || !var1.hitbox.isValid()) {
            if (var1.hitbox != null) {
                this.byEntity.remove(var1.hitbox.getUniqueId());
            }

            Interaction var6 = (Interaction)var5.spawn(var1.fixed.clone(), Interaction.class);
            var6.addScoreboardTag("clashmc");
            var6.setInteractionWidth(var3 + 0.2F);
            var6.setInteractionHeight((float)(var4 * (var2 ? KING_S : PRIN_S)) + 0.5F);
            var6.setPersistent(false);
            var1.hitbox = var6;
            this.byEntity.put(var6.getUniqueId(), var1);
        }

        if (var1.label == null || !var1.label.isValid()) {
            ArmorStand var8 = (ArmorStand)var5.spawn(var1.fixed.clone().add(0.0, var4 + 1.2, 0.0), ArmorStand.class);
            var8.addScoreboardTag("clashmc");
            stand(var8, true);
            var1.label = var8;
            this.refreshName(var1);
        }

        String var9 = var1.towerModel;
        if (this.gm.models.enabled() && var9 != null && !var9.isEmpty() && var1.modelTries <= 8) {
            var1.extras.removeIf(var0 -> !var0.isValid());
            if (!var1.extras.isEmpty()) {
                return true;
            } else {
                ArmorStand var7 = (ArmorStand)var5.spawn(var1.fixed.clone(), ArmorStand.class);
                var7.addScoreboardTag("clashmc");
                stand(var7, true);
                if (this.gm.models.apply(var7, var9, true, var1.team.color)) {
                    var1.extras.add(var7);
                    var1.modelTries = 0;
                    if (!var2 && "clash_princess_tower".equals(var9)) {
                        // 꼭대기 프린세스는 따로 띄워서 적 쪽으로 몸을 돌림
                        ArmorStand top = (ArmorStand)var5.spawn(var1.fixed.clone().add(0.0, PRINCESS_TOP_Y, 0.0), ArmorStand.class);
                        top.addScoreboardTag("clashmc");
                        stand(top, true);
                        if (this.gm.models.apply(top, "clash_princess_top", true, var1.team.color)) {
                            var1.extras.add(top);
                            var1.turret = top;
                        } else {
                            top.remove();
                        }
                    }
                    return true;
                } else {
                    var7.remove();
                    if (++var1.modelTries <= 8) {
                        this.fx.later(10L, () -> {
                            if (var1.alive() && var1.extras.isEmpty() && this.gm.phase != GameManager.Phase.DONE) {
                                this.spawnTowerParts(var1);
                            }
                        });
                    } else if (var1.modelTries == 9) {
                        this.setTowerBlocks(var1, Material.STONE_BRICKS, var1.team.concrete, var2 ? 6 : 5);
                        this.gm.plugin.getLogger().warning("타워 모델 적용 실패: " + var9 + " → 블록 타워로 대체");
                    }

                    return false;
                }
            }
        } else {
            return false;
        }
    }

    void watchdog() {
        for (Combatant var2 : this.all) {
            if (var2.isTower() && var2.alive()) {
                boolean var3 = var2.hitbox == null || !var2.hitbox.isValid() || var2.label == null || !var2.label.isValid();

                for (Entity var5 : var2.extras) {
                    var3 |= !var5.isValid();
                }

                if (var3) {
                    for (Entity var7 : var2.extras) {
                        if (!var7.isValid()) {
                            this.gm.models.remove(var7);
                        }
                    }

                    this.spawnTowerParts(var2);
                }
            }
        }
    }

    private void setTowerBlocks(Combatant var1, Material var2, Material var3, int var4) {
        int var5 = this.A().minX + var1.towerTx * 3;
        int var6 = this.A().minZ + var1.towerTz * 3;
        int var7 = var1.towerTiles * 3;
        int var8 = this.A().floorY;

        for (int var9 = 0; var9 < var7; var9++) {
            for (int var10 = 0; var10 < var7; var10++) {
                boolean var11 = var9 == 0 || var10 == 0 || var9 == var7 - 1 || var10 == var7 - 1;

                for (int var12 = 1; var12 <= var4 + 1; var12++) {
                    Material var13;
                    if (var12 <= var4) {
                        var13 = var12 == var4 && var2 != Material.BARRIER ? var3 : var2;
                    } else {
                        var13 = var11 && (var9 + var10) % 2 == 0 && var2 != Material.BARRIER ? Material.STONE_BRICK_WALL : Material.AIR;
                    }

                    this.A().world.getBlockAt(var5 + var9, var8 + var12, var6 + var10).setType(var13);
                }
            }
        }
    }

    private void clearTowerBlocks(Combatant var1, boolean var2) {
        int var3 = this.A().minX + var1.towerTx * 3;
        int var4 = this.A().minZ + var1.towerTz * 3;
        int var5 = var1.towerTiles * 3;
        int var6 = this.A().floorY;

        for (int var7 = 0; var7 < var5; var7++) {
            for (int var8 = 0; var8 < var5; var8++) {
                for (int var9 = 1; var9 <= 10; var9++) {
                    this.A().world.getBlockAt(var3 + var7, var6 + var9, var4 + var8).setType(Material.AIR);
                }

                if (var2 && this.gm.rng.nextDouble() < 0.35) {
                    this.A()
                        .world
                        .getBlockAt(var3 + var7, var6 + 1, var4 + var8)
                        .setType(this.gm.rng.nextBoolean() ? Material.COBBLESTONE_SLAB : Material.STONE_BRICK_SLAB);
                }
            }
        }
    }

    private static void stand(ArmorStand var0, boolean var1) {
        var0.setMarker(var1);
        var0.setInvisible(true);
        var0.setGravity(false);
        var0.setInvulnerable(true);
        var0.setBasePlate(false);
        var0.setPersistent(false);
        var0.setCustomNameVisible(true);
    }

    double lowestTowerRatio(TeamColor var1) {
        double var2 = 1.0;

        for (Combatant var5 : this.all) {
            if (var5.isTower() && var5.team == var1) {
                double var6 = var5.dead ? 0.0 : var5.hp / var5.maxHp;
                var2 = Math.min(var2, var6);
            }
        }

        return var2;
    }

    private Combatant tower(TeamColor var1, Combatant.Kind var2, boolean var3) {
        for (Combatant var5 : this.all) {
            if (var5.team == var1 && var5.kind == var2 && (var2 == Combatant.Kind.KING_TOWER || var5.left == var3)) {
                return var5;
            }
        }

        return null;
    }

    /** 타워/건물과 겹쳐서 못 놓는 칸이면 가장 가까운 놓을 수 있는 칸 {x, z}, 아니면 null (원래 칸이 괜찮아도 null) */
    int[] snapTile(TeamColor team, CardDef card, int tx, int tz) {
        if (card == null) {
            return null;
        }
        String err = this.placementError(team, card, tx, tz);
        if (err == null || !err.contains("겹쳐서") && !err.contains("타워 위") && !err.contains("걸려서")) {
            return null;
        }
        int[] best = null;
        double bestD = 1.0E9;
        for (int r = 1; r <= 4 && best == null; r++) {
            for (int dx = -r; dx <= r; dx++) {
                for (int dz = -r; dz <= r; dz++) {
                    if (Math.max(Math.abs(dx), Math.abs(dz)) != r) {
                        continue;
                    }
                    int x = tx + dx, z = tz + dz;
                    if (this.placementError(team, card, x, z) != null) {
                        continue;
                    }
                    double d = dx * dx + dz * dz;
                    if (d < bestD) {
                        bestD = d;
                        best = new int[]{x, z};
                    }
                }
            }
        }
        return best;
    }

    String placementError(TeamColor var1, CardDef var2, int var3, int var4) {
        Arena var5 = this.A();
        if (!var5.inField(var3, var4)) {
            return "경기장 밖입니다";
        } else if (var2.isSpell()) {
            return var2.ownSide && var5.sideOf(var4) != var1 ? var2.name + "은(는) 자기 진영에만 쓸 수 있습니다" : null;
        } else if (var5.isRiverRow(var4)) {
            return "강에는 배치할 수 없습니다";
        } else {
            boolean var6 = var2.id.equals("goblin_barrel");
            if (var6) {
                return null;
            } else {
                for (Combatant var8 : this.all) {
                    if (var8.isTower() && var8.alive() && var5.tileInRect(var3, var4, var8.towerTx, var8.towerTz, var8.towerTiles)) {
                        return "타워 위에는 배치할 수 없습니다";
                    }
                }

                if (var2.type == CardDef.Type.BUILDING) {
                    // 큰 건물: 차지하는 칸이 경기장 밖 / 강 / 상대 진영에 걸리면 안 됨
                    Location bc = var5.tileCenter(var3, var4);
                    double bh = var2.size / 2.0 - 0.1;
                    TeamColor bside = var5.sideOf(var4);
                    for (int sx = -1; sx <= 1; sx += 2) {
                        for (int sz = -1; sz <= 1; sz += 2) {
                            int ctx = var5.tileX(bc.getX() + sx * bh), ctz = var5.tileZ(bc.getZ() + sz * bh);
                            if (!var5.inField(ctx, ctz)) {
                                return "경기장 끝에 걸려서 배치할 수 없습니다";
                            }
                            if (var5.isRiverRow(ctz)) {
                                return "강에 걸려서 배치할 수 없습니다";
                            }
                            if (!var2.anywhere && bside == var1 && var5.sideOf(ctz) != var1) {
                                return "진영 밖에 걸려서 배치할 수 없습니다";
                            }
                        }
                    }
                    String overlap = this.buildingOverlap(var2, bc);
                    if (overlap != null) {
                        return overlap;
                    }
                }

                if (var2.anywhere) {
                    return null;
                } else {
                    TeamColor var10 = var5.sideOf(var4);
                    if (var10 == var1) {
                        return null;
                    } else {
                        boolean var11 = var3 < 9;
                        Combatant var9 = this.tower(var1.other(), Combatant.Kind.PRINCESS_TOWER, var11);
                        if (var9 != null && var9.dead) {
                            if (var1 == TeamColor.BLUE && var4 <= 23) {
                                return null;
                            }

                            if (var1 == TeamColor.RED && var4 >= 8) {
                                return null;
                            }
                        }

                        return "자기 진영에만 배치할 수 있습니다";
                    }
                }
            }
        }
    }

    void previewPlacement(Player var1, GameTeam var2) {
        String var3 = this.gm.cardIdOf(var1.getInventory().getItemInMainHand());
        if (var3 != null) {
            CardDef var4 = this.gm.cards.get(var3);
            if (var4 != null && var4.id.equals("mirror")) {
                var4 = var2.lastPlayed == null ? null : this.gm.cards.get(var2.lastPlayed);
            }

            if (var4 != null) {
                Block var5 = var1.getTargetBlockExact(160);
                if (var5 != null) {
                    int var6 = this.A().tileX(var5.getX() + 0.5);
                    int var7 = this.A().tileZ(var5.getZ() + 0.5);
                    int[] snap = this.snapTile(var2.color, var4, var6, var7);
                    if (snap != null) {
                        var6 = snap[0];
                        var7 = snap[1];
                    }
                    if (this.A().inField(var6, var7)) {
                        boolean ok = this.placementError(var2.color, var4, var6, var7) == null
                            && var2.elixir + 1.0E-9 >= this.gm.costOf(var2, this.gm.cards.get(var3));
                        Location c = this.A().tileCenter(var6, var7);
                        double x0 = this.A().minX + var6 * 3;
                        double z0 = this.A().minZ + var7 * 3;
                        int edge = ok ? 0 : 1;
                        List<double[]> segs = new ArrayList<>();
                        // 배치 범위 (회색 / 못 놓으면 빨강): 건물은 차지하는 칸, 유닛은 배치 칸 (최소 1타일)
                        double fp = var4.isSpell() ? 3.0 : Math.max(3.0, var4.isBuilding() ? var4.size : var4.footprint);
                        double fh = fp / 2.0;
                        int fillK = ok ? 7 : 3;
                        int edgeK = ok ? 6 : 1;
                        double cx = c.getX(), cz = c.getZ();
                        segs.add(new double[]{cx - fh, cz - fh, cx + fh, cz + fh, fillK});
                        segs.add(new double[]{cx - fh, cz - fh, cx + fh, cz - fh, edgeK});
                        segs.add(new double[]{cx + fh, cz - fh, cx + fh, cz + fh, edgeK});
                        segs.add(new double[]{cx + fh, cz + fh, cx - fh, cz + fh, edgeK});
                        segs.add(new double[]{cx - fh, cz + fh, cx - fh, cz - fh, edgeK});

                        // 실제 모델 범위 (초록): 건물은 겉모습 사각형, 유닛은 소환되는 자리마다 몸 크기 원
                        if (var4.isBuilding()) {
                            double mh = modelW(var4) / 2.0;
                            segs.add(new double[]{cx - mh, cz - mh, cx + mh, cz - mh, 0});
                            segs.add(new double[]{cx + mh, cz - mh, cx + mh, cz + mh, 0});
                            segs.add(new double[]{cx + mh, cz + mh, cx - mh, cz + mh, 0});
                            segs.add(new double[]{cx - mh, cz + mh, cx - mh, cz - mh, 0});
                        } else if (!var4.isSpell()) {
                            int cnt = Math.max(1, var4.count);
                            double bw = modelW(var4);
                            if (!var4.mix.isEmpty()) {
                                CardDef mc = this.gm.cards.get(var4.mix.get(0)[0]);
                                if (mc != null) {
                                    bw = modelW(mc);
                                }
                            }
                            double ring = cnt <= 1 ? 0.0 : Math.max(var4.radius > 0.0 ? var4.radius : (cnt <= 3 ? 0.9 : 1.3),
                                Math.min(6.0, 0.45 * bw / Math.sin(Math.PI / cnt)));
                            int segN = cnt > 6 ? 8 : (cnt > 3 ? 12 : 20);
                            double r = bw / 2.0;
                            for (int u = 0; u < cnt; u++) {
                                double ua = (Math.PI * 2) * u / cnt;
                                double ux = cx + Math.cos(ua) * ring, uz = cz + Math.sin(ua) * ring;
                                for (int q = 0; q < segN; q++) {
                                    double a0 = (Math.PI * 2) * q / segN;
                                    double a1 = (Math.PI * 2) * (q + 1) / segN;
                                    segs.add(new double[]{ux + Math.cos(a0) * r, uz + Math.sin(a0) * r, ux + Math.cos(a1) * r, uz + Math.sin(a1) * r, 0});
                                }
                            }
                        }

                        // 통나무 / 바바리안 통: 굴러가는 길
                        if (var4.isSpell() && var4.length > 0.0) {
                            double hw = var4.width / 2.0;
                            double z1 = c.getZ() + var2.color.dir * var4.length;
                            int k = ok ? 4 : 5;
                            segs.add(new double[]{c.getX() - hw, c.getZ(), c.getX() - hw, z1, k});
                            segs.add(new double[]{c.getX() + hw, c.getZ(), c.getX() + hw, z1, k});
                            segs.add(new double[]{c.getX() - hw, c.getZ(), c.getX() + hw, c.getZ(), k});
                            segs.add(new double[]{c.getX() - hw, z1, c.getX() + hw, z1, k});
                        }

                        // 범위 마법: 원
                        if (var4.isSpell() && var4.radius > 0.0) {
                            int n = 32;
                            int k = ok ? 4 : 5;
                            for (int i = 0; i < n; i++) {
                                double a0 = (Math.PI * 2) * i / n;
                                double a1 = (Math.PI * 2) * (i + 1) / n;
                                segs.add(new double[]{c.getX() + Math.cos(a0) * var4.radius, c.getZ() + Math.sin(a0) * var4.radius,
                                    c.getX() + Math.cos(a1) * var4.radius, c.getZ() + Math.sin(a1) * var4.radius, k});
                            }
                        }

                        this.drawOutline(var1, segs, this.A().floorY + 1.02);
                    }
                }
            }
        }
    }

    // ===================== 배치 미리보기: 빛나는 블록 디스플레이 (멀리서·탑뷰에서도 보임, 그 킹에게만) =====================

    private static final class Outline {
        final List<BlockDisplay> bars = new ArrayList<>();
        String key = "";
        long seen;
        boolean hidden = true;
    }

    private final Map<UUID, Battle.Outline> outlines = new HashMap<>();

    /** seg = {x1, z1, x2, z2, 종류}. 0 = 모델 범위(초록), 1/3 = 배치 불가 테두리/바닥(빨강), 4/5 = 마법 범위, 6/7 = 배치 범위 테두리/바닥(회색) */
    private void drawOutline(Player p, List<double[]> segs, double y) {
        Battle.Outline o = this.outlines.computeIfAbsent(p.getUniqueId(), k -> new Battle.Outline());
        o.seen = this.now();
        StringBuilder sb = new StringBuilder();
        for (double[] sg : segs) {
            for (double v : sg) {
                sb.append(Math.round(v * 100.0)).append(',');
            }
        }

        String key = sb.toString();
        if (!o.hidden && key.equals(o.key)) {
            return;
        }

        o.key = key;
        o.hidden = false;
        World w = this.A().world;
        o.bars.removeIf(d -> !d.isValid());
        while (o.bars.size() < segs.size()) {
            BlockDisplay d = (BlockDisplay)w.spawn(new Location(w, segs.get(0)[0], y, segs.get(0)[1]), BlockDisplay.class);
            d.addScoreboardTag("clashmc");
            d.setPersistent(false);
            d.setVisibleByDefault(false);
            d.setBrightness(new Brightness(15, 15));
            d.setViewRange(4.0F);
            d.setTeleportDuration(0);
            p.showEntity(this.gm.plugin, d);
            o.bars.add(d);
        }

        for (int i = 0; i < o.bars.size(); i++) {
            BlockDisplay d = o.bars.get(i);
            if (i >= segs.size()) {
                d.setTransformation(new Transformation(new Vector3f(), new Quaternionf(), new Vector3f(0.0F, 0.0F, 0.0F), new Quaternionf()));
                continue;
            }

            double[] sg = segs.get(i);
            int kind = (int)sg[4];
            boolean fill = kind == 2 || kind == 3 || kind == 7;
            Material m;
            Color glow;
            switch (kind) {
                case 0: m = Material.LIME_CONCRETE; glow = Color.fromRGB(80, 255, 80); break;
                case 1: m = Material.RED_CONCRETE; glow = Color.fromRGB(255, 60, 60); break;
                case 2: m = Material.LIME_STAINED_GLASS; glow = null; break;
                case 3: m = Material.RED_STAINED_GLASS; glow = null; break;
                case 4: m = Material.YELLOW_CONCRETE; glow = Color.fromRGB(255, 230, 80); break;
                case 6: m = Material.LIGHT_GRAY_CONCRETE; glow = Color.fromRGB(205, 205, 205); break;
                case 7: m = Material.LIGHT_GRAY_STAINED_GLASS; glow = null; break;
                default: m = Material.ORANGE_CONCRETE; glow = Color.fromRGB(255, 120, 40); break;
            }

            d.setBlock(m.createBlockData());
            d.setGlowing(glow != null);
            if (glow != null) {
                d.setGlowColorOverride(glow);
            }

            Location at = new Location(w, sg[0], y, sg[1]);
            if (fill) {
                d.teleport(at);
                d.setTransformation(new Transformation(new Vector3f(0.0F, -0.01F, 0.0F), new Quaternionf(),
                    new Vector3f((float)(sg[2] - sg[0]), 0.02F, (float)(sg[3] - sg[1])), new Quaternionf()));
            } else {
                double dx = sg[2] - sg[0];
                double dz = sg[3] - sg[1];
                double len = Math.sqrt(dx * dx + dz * dz);
                double a = Math.atan2(dz, dx);
                float wdt = 0.16F;
                float hgt = 0.06F;
                d.teleport(at);
                d.setTransformation(new Transformation(
                    new Vector3f((float)(wdt / 2.0 * Math.sin(a)), 0.0F, (float)(-wdt / 2.0 * Math.cos(a))),
                    new Quaternionf().rotateY((float)(-a)),
                    new Vector3f((float)len, hgt, wdt),
                    new Quaternionf()));
            }
        }
    }

    /** 이번 틱에 안 그려진 미리보기는 숨김 */
    private void hideStaleOutlines() {
        for (Battle.Outline o : this.outlines.values()) {
            if (!o.hidden && this.now() - o.seen > 4L) {
                o.hidden = true;
                o.key = "";
                for (BlockDisplay d : o.bars) {
                    if (d.isValid()) {
                        d.setTransformation(new Transformation(new Vector3f(), new Quaternionf(), new Vector3f(0.0F, 0.0F, 0.0F), new Quaternionf()));
                    }
                }
            }
        }
    }

    void deploy(GameTeam var1, CardDef var2, int var3, int var4, Location var5) {
        CardDef var6 = var2;
        if (var2.id.equals("mirror")) {
            var6 = var1.lastPlayed == null ? null : this.gm.cards.get(var1.lastPlayed);
            if (var6 == null) {
                return;
            }

            Location var7 = this.A().tileCenter(var3, var4).add(0.0, 1.0, 0.0);
            this.A().world.spawnParticle(Particle.END_ROD, var7, 30, 0.6, 0.6, 0.6, 0.05);
            this.A().world.spawnParticle(Particle.DUST, var7, 20, 0.6, 0.6, 0.6, 0.0, new DustOptions(Color.fromRGB(190, 230, 255), 1.4F));
            this.A().world.playSound(var7, "block.amethyst_block.resonate", 1.0F, 1.4F);
            this.A().world.playSound(var7, "block.glass.place", 1.0F, 1.6F);
        } else {
            var1.lastPlayed = var2.id;
        }

        this.deployCard(var1, var6, var3, var4, var5);
        this.gm.giveHand(var1);
    }

    /** 배치 미리보기 초록 범위: 실제 모델 가로 폭 (모델이 없으면 히트박스 폭) */
    private static double modelW(CardDef c) {
        double w = ModelHeights.width(c.model);
        return w > 0.05 ? w : c.hitboxW;
    }

    /** 카드 사용 효과음: 쓴 킹에게는 바로 귀에 또렷하게 (탑뷰처럼 멀리 떠 있어도 들림), 주변에는 크게 */
    private void playCardSound(GameTeam team, Location at) {
        if (this.gm.assault) {
            return;
        }
        World w = this.A().world;
        w.playSound(at, "entity.player.attack.sweep", 1.6F, 1.3F);
        w.playSound(at, "block.wood.place", 1.6F, 0.8F);
        Player k = team.kingPlayer();
        if (k != null && k.isOnline()) {
            k.playSound(k, "block.note_block.bell", org.bukkit.SoundCategory.MASTER, 1.0F, 1.6F);
            k.playSound(k, "entity.player.attack.sweep", org.bukkit.SoundCategory.MASTER, 1.0F, 1.2F);
            k.playSound(k, "block.wood.place", org.bukkit.SoundCategory.MASTER, 1.0F, 0.9F);
        }
    }

    private void deployCard(GameTeam var1, CardDef var2, int var3, int var4, Location var5) {
        Location var6 = this.A().tileCenter(var3, var4);
        World var7 = this.A().world;
        this.playCardSound(var1, var6);
        switch (var2.type) {
            case SPELL:
                this.castSpell(var1.color, var2, var6);
                return;
            case BUILDING:
                this.spawnBuilding(var1.color, var2, var6);
                return;
            default:
                if (var2.id.equals("goblin_barrel")) {
                    Location var16 = this.A().kingCenter(var1.color).add(0.0, 9.0, 0.0);
                    Combatant var17 = this.towerAtTile(var3, var4);
                    Location var18 = var17 == null
                        ? var6.clone().add(0.0, 0.6, 0.0)
                        : var17.fixed.clone().add(0.0, var17.kind == Combatant.Kind.KING_TOWER ? 6.0 * KING_S : 5.2 * PRIN_S, 0.0);
                    this.fx.shoot(Fx.Shot.BARREL, var16, () -> var18, var8x -> {
                        Combatant var9 = this.towerAtTile(var3, var4);
                        if (var9 == null) {
                            this.fx.impact(Fx.Shot.BARREL, var6, 0.0);
                            this.spawnTroops(var1, var2, var6, var2.deployTicks());
                        } else {
                            this.fx.impact(Fx.Shot.BARREL, var18, 0.0);
                            this.spawnTroopsAt(var1, var2, this.splitAround(var9, var16), var2.deployTicks(), var18);
                        }
                    }, var2.projectileModel, var1.color.color);
                } else if (var2.id.equals("miner")) {
                    Location var15 = this.A().kingCenter(var1.color);
                    this.fx.tunnel(var15, var6, 12.0, () -> this.spawnTroops(var1, var2, var6, 20));
                } else if (var2.id.equals("skeleton_barrel")) {
                    this.spawnBarrel(var1, var2, var6);
                } else if (!var2.mix.isEmpty()) {
                    int var8 = 0;

                    for (String[] var10 : var2.mix) {
                        CardDef var11 = this.gm.cards.get(var10[0]);
                        if (var11 != null) {
                            int var12;
                            try {
                                var12 = Integer.parseInt(var10[1]);
                            } catch (NumberFormatException var14) {
                                var12 = var11.count;
                            }

                            Location var13 = var6.clone().add(0.0, 0.0, -var1.color.dir * 1.2 * var8 + (var8 == 0 ? var1.color.dir * 0.5 : 0.0));
                            this.spawnTroops(var1, var11, var13, var2.deployTicks(), var12, null);
                            var8++;
                        }
                    }
                } else {
                    this.spawnTroops(var1, var2, var6, var2.deployTicks());
                    if (var2.spawnDamage > 0.0) {
                        if (var2.hitSlow > 0.0) {
                            // 얼음 마법사: 배치할 때 냉기 폭발 (피해 + 감속)
                            World fw = this.A().world;
                            double fr = Math.max(1.0, var2.spawnRadius);
                            fw.spawnParticle(Particle.SNOWFLAKE, var6.clone().add(0.0, 0.8, 0.0), 80, fr / 2.0, 0.5, fr / 2.0, 0.05);
                            this.fx.ring(var6, fr, Color.fromRGB(170, 230, 255));
                            fw.playSound(var6, "entity.player.hurt_freeze", 1.0F, 1.2F);
                            for (Combatant fc : this.area(var6, fr, var1.color.other(), true, true)) {
                                this.damage(fc, var2.spawnDamage, null);
                                this.slow(fc, var2.hitSlow, 20);
                            }
                        } else if (var2.jumpMax > 0.0) {
                            // 메가 나이트: 떨어지면서 쿵
                            this.megaFall(var6, var2.deployTicks());
                            this.fx.later(Math.max(1L, var2.deployTicks() - 4L), () -> {
                                this.slamAt(var1.color, var6, var2.spawnRadius, var2.spawnDamage, 1.0F);
                                this.megaLandFx(var6, var2.spawnRadius);
                            });
                        } else {
                            this.zapAt(var1.color, var6, var2.spawnRadius, var2.spawnDamage, var2.spawnDamage * 0.3, var2.stun);
                        }
                    }
                }
        }
    }

    /** 돌격전: 카드 한 장을 그 칸에 바로 소환 (엘릭서·손패 없이) */
    void assaultDeploy(GameTeam team, CardDef card, int tx, int tz, Location at) {
        this.deployCard(team, card, tx, tz, at);
    }

    /** 돌격전: 사거리 안에 적이 없으면 전장에서 가장 가까운 적에게 감 (10틱마다만 다시 찾음) */
    private Location hunt(Combatant c, Location from) {
        Combatant h = c.huntTarget;
        if (h == null || !h.alive() || h.hidden || (this.now() + c.id) % 10L == 0L) {
            h = null;
            double best = Double.MAX_VALUE;
            boolean groundOnly = c.kind == Combatant.Kind.BARREL || c.card == null || c.card.targets != CardDef.Targets.AIR_GROUND;
            for (Combatant o : this.all) {
                if (o.team != c.team && o.alive() && !o.hidden && (o.kind == Combatant.Kind.TROOP || o.kind == Combatant.Kind.BARREL) && (!groundOnly || !o.air)) {
                    Location l = o.loc();
                    if (l != null) {
                        double dx = l.getX() - from.getX();
                        double dz = l.getZ() - from.getZ();
                        double d = dx * dx + dz * dz;
                        if (d < best) {
                            best = d;
                            h = o;
                        }
                    }
                }
            }
            c.huntTarget = h;
        }
        return h == null ? null : h.loc();
    }

    Combatant towerAtTile(int var1, int var2) {
        for (Combatant var4 : this.all) {
            if (var4.isTower() && var4.alive() && this.A().tileInRect(var1, var2, var4.towerTx, var4.towerTz, var4.towerTiles)) {
                return var4;
            }
        }

        return null;
    }

    private List<Location> splitAround(Combatant var1, Location var2) {
        ArrayList var3 = new ArrayList();
        Location var4 = var1.fixed;
        double var5 = Math.atan2(var2.getZ() - var4.getZ(), var2.getX() - var4.getX());
        double var7 = var1.towerTiles * 3 / 2.0 + 0.9;

        for (double var12 : new double[]{0.0, Math.toRadians(115.0), -Math.toRadians(115.0)}) {
            double var14 = var5 + var12;
            double var16 = var4.getX() + Math.cos(var14) * var7;
            double var18 = var4.getZ() + Math.sin(var14) * var7;
            var16 = Math.max(this.A().minX + 0.5, Math.min(this.A().minX + 54 - 0.5, var16));
            var18 = Math.max(this.A().minZ + 0.5, Math.min(this.A().minZ + 96 - 0.5, var18));
            var3.add(new Location(this.A().world, var16, this.groundY(), var18));
        }

        return var3;
    }

    private void spawnTroopsAt(GameTeam var1, CardDef var2, List<Location> var3, int var4, Location var5) {
        UUID var6 = var2.aiOnly ? null : var1.pollQueue();
        Object var7 = null;

        for (int var8 = 0; var8 < var3.size(); var8++) {
            Location var9 = (Location)var3.get(var8);
            Location var10 = var9.clone();
            var10.setYaw((float)Math.toDegrees(Math.atan2(-(var9.getX() - var5.getX()), var9.getZ() - var5.getZ())));

            for (int var11 = 1; var11 <= 8; var11++) {
                double var12 = var11 / 8.0;
                Location var14 = var5.clone()
                    .add(
                        (var9.getX() - var5.getX()) * var12,
                        (var9.getY() - var5.getY()) * var12 + Math.sin(Math.PI * var12) * 1.2,
                        (var9.getZ() - var5.getZ()) * var12
                    );
                this.A().world.spawnParticle(Particle.CLOUD, var14, 1, 0.05, 0.05, 0.05, 0.0);
            }

            if (var8 == 0 && var6 != null) {
                Player var16 = Bukkit.getPlayer(var6);
                if (var16 != null) {
                    var7 = this.spawnPlayerUnit(var1, var2, var16, var10, var4);
                    continue;
                }
            }

            Combatant var17 = this.spawnAi(var1.color, var2, var10, var4);
            var17.leader = null;
        }

        this.A().world.playSound(var5, "entity.zombie.break_wooden_door", 0.8F, 1.2F);
    }

    private void spawnTroops(GameTeam var1, CardDef var2, Location var3, int var4) {
        this.spawnTroops(var1, var2, var3, var4, var2.count, null);
    }

    private void spawnTroops(GameTeam var1, CardDef var2, Location var3, int var4, int var5, UUID var6) {
        UUID var7 = var6 != null ? var6 : (var2.aiOnly ? null : var1.pollQueue());
        boolean var8 = this.canSplit(var2, var5, var3) && var6 == null;
        List var9 = var8 ? this.splitFormation(var3, var5) : this.formation(var3, var5, Math.max(var2.radius > 0.0 ? var2.radius : (var5 <= 3 ? 0.9 : 1.3),
            var5 > 1 ? Math.min(6.0, 0.55 * Math.max(var2.hitboxW, modelW(var2)) / Math.sin(Math.PI / var5)) : 0.0));
        Combatant var10 = null;

        for (int var11 = 0; var11 < var5; var11++) {
            Location var12 = (Location)var9.get(var11);
            Boolean var13 = var8 ? var12.getX() < this.A().centerX() : null;
            if (var11 == 0 && var7 != null) {
                Player var14 = Bukkit.getPlayer(var7);
                if (var14 != null) {
                    var10 = this.spawnPlayerUnit(var1, var2, var14, var12, var4);
                    var10.lane = var13;
                    continue;
                }
            }

            Combatant var15 = this.spawnAi(var1.color, var2, var12, var4);
            var15.lane = var13;
            if (var2.type == CardDef.Type.SQUAD && (var10 == null || !var8 || Objects.equals(var10.lane, var13))) {
                var15.leader = var10;
            }
        }

        if (var8) {
            this.A().world.spawnParticle(Particle.CRIT, var3.clone().add(0.0, 0.6, 0.0), 16, 1.4, 0.2, 0.3, 0.05);
        }

        this.A().world.spawnParticle(Particle.CLOUD, var3.clone().add(0.0, 0.3, 0.0), 12, 0.6, 0.1, 0.6, 0.01);
    }

    boolean canSplit(CardDef var1, int var2, Location var3) {
        return this.gm.splitEnabled && var2 >= 2 && var1.type == CardDef.Type.SQUAD && !var1.id.equals("goblin_barrel")
            ? Math.abs(var3.getX() - this.A().centerX()) <= this.gm.splitWidth
            : false;
    }

    private List<Location> splitFormation(Location var1, int var2) {
        ArrayList var3 = new ArrayList();
        int var4 = (var2 + 1) / 2;
        int var5 = var2 - var4;
        this.addColumn(var3, var1, -1, var4);
        this.addColumn(var3, var1, 1, var5);
        return var3;
    }

    private void addColumn(List<Location> var1, Location var2, int var3, int var4) {
        double var5 = this.A().centerX() + var3 * 1.1;
        int var7 = var4 > 4 ? 2 : 1;
        int var8 = (var4 + var7 - 1) / var7;

        for (int var9 = 0; var9 < var4; var9++) {
            int var10 = var9 % var7;
            int var11 = var9 / var7;
            double var12 = var5 + var3 * var10 * 0.9;
            double var14 = var2.getZ() + (var11 - (var8 - 1) / 2.0) * 0.8;
            var1.add(new Location(this.A().world, var12, var2.getY(), var14));
        }
    }

    private List<Location> formation(Location var1, int var2, double var3) {
        ArrayList var5 = new ArrayList();
        if (var2 == 1) {
            var5.add(var1.clone());
            return var5;
        } else {
            for (int var6 = 0; var6 < var2; var6++) {
                double var7 = (Math.PI * 2) * var6 / var2;
                var5.add(var1.clone().add(Math.cos(var7) * var3, 0.0, Math.sin(var7) * var3));
            }

            return var5;
        }
    }

    private double groundY() {
        return this.A().floorY + 1;
    }

    private double airY() {
        return this.A().floorY + 1 + this.gm.airHeight;
    }

    private Combatant spawnPlayerUnit(GameTeam var1, CardDef var2, Player var3, Location var4, int var5) {
        Combatant var6 = new Combatant(Combatant.Kind.TROOP, var1.color, var2);
        var6.playerId = var3.getUniqueId();
        var6.maxHp = var6.hp = var2.hp;
        var6.air = var2.air;
        var6.deployUntil = this.now() + var5;
        this.initUnit(var6);
        this.all.add(var6);
        this.byEntity.put(var3.getUniqueId(), var6);
        this.gm.activeUnits.add(var3.getUniqueId());
        Location var7 = var4.clone();
        var7.setY(var2.air ? this.airY() : this.groundY());
        var7.setYaw(var1.color == TeamColor.BLUE ? 0.0F : 180.0F);
        var7.setPitch(10.0F);
        var3.setGameMode(GameMode.ADVENTURE);
        var3.teleport(var7);
        var3.getInventory().clear();
        if (var2.weapon != Material.AIR) {
            var3.getInventory().setItem(0, named(new ItemStack(var2.weapon), "§f" + var2.name + " 무기"));
        }

        var3.getInventory().setHeldItemSlot(0);
        var3.setWalkSpeed((float)Math.min(1.0, var2.speedBlocks * this.gm.walkPerBlock));
        var3.setFlySpeed((float)Math.min(1.0, var2.speedBlocks * this.gm.flyPerBlock));
        var3.setAllowFlight(var2.air);
        var3.setFlying(var2.air);
        var3.setFoodLevel(6);
        var3.setSaturation(0.0F);
        var3.setHealth(20.0);
        var6.radius = var2.hitboxW / 2.0;
        String unitModel = this.gm.skinModel(var1.color, var2.id, var2.model, var3.getUniqueId(), false);
        boolean var8 = this.applyUnit(var3, unitModel, true, var1.color.color);
        var6.modeled = var8;
        if (var8 && var2.weapon != Material.AIR) {
            // 모델이 무기를 들고 있으니 손에 든 아이템은 치움 (투명한 몸에 아이템만 떠 보이지 않게)
            var3.getInventory().setItem(8, var3.getInventory().getItem(0));
            var3.getInventory().setItem(0, null);
        }
        this.playerUnitBody(var6, var3);
        if (var8) {
            var3.sendMessage("§7[F] 키: 내 모델 보기/숨기기 (1인칭에선 숨김 추천, F5 3인칭에선 보기)");
        }
        if (var8 && this.gm.eyeFromModel) {
            // 1인칭 시점을 모델 머리 높이로: 플레이어 눈높이(1.62 x scale)를 모델 눈높이에 맞춤
            // (BetterModel 모델은 엔티티 scale 을 안 따라가서 모델 크기는 그대로)
            double eye = ModelHeights.eye(unitModel);
            if (eye <= 0.0) {
                eye = ModelHeights.eye(var2.model);
            }
            if (eye > 0.0) {
                double s = Math.max(0.25, Math.min(Math.max(0.25, this.gm.eyeMaxScale), eye / 1.62));
                applyScale(var3, s);
            } else if (this.gm.scalePlayers) {
                applyScale(var3, var2.hitboxH / 1.8);
            }
        } else if (this.gm.scalePlayers) {
            double var9 = applyScale(var3, var2.hitboxH / 1.8);
            if (var8 && this.gm.modelFollowsScale) {
                this.gm.models.scale(var3, 1.0 / var9);
            }
        }

        if (!var8) {
            ItemStack var12 = new ItemStack(Material.LEATHER_HELMET);
            if (var12.getItemMeta() instanceof LeatherArmorMeta var11) {
                var11.setColor(var1.color.color);
                var12.setItemMeta(var11);
            }

            var3.getInventory().setHelmet(var12);
        }

        this.gm.models.anim(var3, "deploy");
        var3.sendTitle(
            var1.color.cc + var2.name + " §f소환!",
            "§7체력 " + (int)var2.hp + " · 데미지 " + (int)var2.damage + (var2.targets == CardDef.Targets.BUILDINGS ? " · 건물만 공격" : ""),
            0,
            30,
            10
        );
        var3.playSound(var7, "entity.player.levelup", 0.7F, 1.4F);
        return var6;
    }

    private static ItemStack named(ItemStack var0, String var1) {
        ItemMeta var2 = var0.getItemMeta();
        if (var2 != null) {
            var2.setDisplayName(var1);
            var0.setItemMeta(var2);
        }

        return var0;
    }

    private Combatant spawnAi(TeamColor var1, CardDef var2, Location var3, int var4) {
        Location var5 = var3.clone();
        var5.setY(var2.air ? this.airY() : this.groundY());
        var5.setYaw(var1 == TeamColor.BLUE ? 0.0F : 180.0F);
        LivingEntity var6 = (LivingEntity)this.A().world.spawnEntity(var5, var2.mob);
        var6.addScoreboardTag("clashmc");
        this.prepMob(var6);
        if (var6 instanceof Ageable var7) {
            if (var2.baby) {
                var7.setBaby();
            } else {
                var7.setAdult();
            }
        }

        EntityEquipment var16 = var6.getEquipment();
        if (var16 != null) {
            var16.clear();
            if (var2.weapon != Material.AIR) {
                var16.setItemInMainHand(new ItemStack(var2.weapon));
            }

            if (!this.gm.models.enabled() || var2.model.isEmpty()) {
                ItemStack var8 = new ItemStack(Material.LEATHER_HELMET);
                if (var8.getItemMeta() instanceof LeatherArmorMeta var10) {
                    var10.setColor(var1.color);
                    var8.setItemMeta(var10);
                }

                var16.setHelmet(var8);
            }
        }

        Combatant var17 = new Combatant(Combatant.Kind.TROOP, var1, var2);
        var17.mob = var6;
        var17.maxHp = var17.hp = var2.hp;
        var17.air = var2.air;
        var17.deployUntil = this.now() + var4;
        this.initUnit(var17);
        var17.radius = var2.hitboxW / 2.0;
        boolean var18 = this.applyUnit(var6, this.gm.skinModel(var1, var2.id, var2.model, null, false), true, var1.color);
        if (!var18 || this.gm.scaleModeledMobs) {
            double var19 = attr(var6) == null ? 1.0 : attr(var6).getBaseValue();
            double var12 = var6.getHeight() / Math.max(0.0625, var19);
            double var14 = applyScale(var6, var2.hitboxH / Math.max(0.1, var12));
            if (var18 && this.gm.modelFollowsScale) {
                this.gm.models.scale(var6, 1.0 / var14);
            }
        }

        this.gm.models.anim(var6, "deploy");
        this.all.add(var17);
        this.byEntity.put(var6.getUniqueId(), var17);
        this.refreshName(var17);
        return var17;
    }

    static AttributeInstance attr(LivingEntity var0) {
        try {
            return var0.getAttribute(Attribute.SCALE);
        } catch (Throwable var2) {
            return null;
        }
    }

    static double applyScale(LivingEntity var0, double var1) {
        double var3 = Math.max(0.25, Math.min(4.0, var1));
        AttributeInstance var5 = attr(var0);
        if (var5 == null) {
            return 1.0;
        } else {
            var5.setBaseValue(var3);
            return var3;
        }
    }

    private void prepMob(LivingEntity var1) {
        for (Entity var3 : var1.getPassengers()) {
            var3.remove();
        }

        var1.leaveVehicle();
        var1.setAI(false);
        var1.setSilent(true);
        var1.setGravity(false);
        var1.setRemoveWhenFarAway(false);
        var1.setCanPickupItems(false);
        var1.setPersistent(false);
        var1.setCustomNameVisible(true);
        var1.setCollidable(false);
    }

    private void spawnBarrel(GameTeam var1, CardDef var2, Location var3) {
        Location var4 = var3.clone();
        var4.setY(this.airY());
        ArmorStand var5 = (ArmorStand)this.A().world.spawn(var4, ArmorStand.class);
        var5.addScoreboardTag("clashmc");
        var5.setInvisible(true);
        var5.setGravity(false);
        var5.setBasePlate(false);
        var5.setSmall(false);
        var5.setPersistent(false);
        var5.setCustomNameVisible(true);
        EntityEquipment var6 = var5.getEquipment();
        if (var6 != null) {
            var6.setHelmet(new ItemStack(Material.BARREL));
        }

        Combatant var7 = new Combatant(Combatant.Kind.BARREL, var1.color, var2);
        var7.mob = var5;
        var7.air = true;
        var7.maxHp = var7.hp = var2.barrelHp;
        var7.deployUntil = this.now() + 20L;
        var7.reservedPlayer = var1.pollQueue();
        if (var7.reservedPlayer != null) {
            this.reserved.add(var7.reservedPlayer);
            Player var8 = Bukkit.getPlayer(var7.reservedPlayer);
            if (var8 != null) {
                var8.sendTitle("§e해골통 탑승", "§7통이 터지면 해골로 소환됩니다", 0, 40, 10);
            }
        }

        if (!var2.barrelModel.isEmpty()) {
            this.applyUnit(var5, this.gm.skinModel(var1.color, var2.id, var2.barrelModel, null, true), true, var1.color.color);
        }

        this.all.add(var7);
        this.byEntity.put(var5.getUniqueId(), var7);
        this.refreshName(var7);
    }

    private void popBarrel(Combatant var1) {
        if (var1.mob != null) {
            Location var2 = var1.mob.getLocation();
            var2.setY(this.groundY());
            World var3 = this.A().world;
            var3.spawnParticle(Particle.EXPLOSION, var2, 1);
            this.fx.impact(Fx.Shot.BARREL, var2, 0.0);
            var3.playSound(var2, "entity.generic.explode", 0.7F, 1.6F);

            for (Combatant var5 : this.area(var2, var1.card.barrelDeathRadius, var1.team.other(), true, true)) {
                this.damage(var5, var5.isTower() ? var1.card.barrelDeathDamage : var1.card.barrelDeathDamage, var1);
            }

            UUID var6 = var1.reservedPlayer;
            var1.reservedPlayer = null;
            if (var6 != null) {
                this.reserved.remove(var6);
            }

            GameTeam var7 = this.gm.teams.get(var1.team);
            if (var7 != null) {
                if (var6 != null && (Bukkit.getPlayer(var6) == null || !var7.members.contains(var6))) {
                    var6 = null;
                }

                if (var6 == null) {
                    this.spawnTroops(var7, var1.card, var2, 10, var1.card.count, null);
                } else {
                    this.spawnTroops(var7, var1.card, var2, 10, var1.card.count, var6);
                }
            }
        }
    }

    private float facing(TeamColor var1) {
        return var1 == TeamColor.BLUE ? 0.0F : 180.0F;
    }

    private Combatant spawnBuilding(TeamColor var1, CardDef var2, Location var3) {
        World var4 = this.A().world;
        var3 = var3.clone();
        var3.setYaw(this.facing(var1));
        Interaction var5 = (Interaction)var4.spawn(var3.clone(), Interaction.class);
        var5.addScoreboardTag("clashmc");
        var5.setInteractionWidth((float)var2.hitboxW);
        var5.setInteractionHeight((float)var2.hitboxH);
        var5.setPersistent(false);
        ArmorStand var6 = (ArmorStand)var4.spawn(var3.clone(), ArmorStand.class);
        var6.addScoreboardTag("clashmc");
        stand(var6, false);
        var6.setSmall(false);
        EntityEquipment var7 = var6.getEquipment();
        String var8 = this.gm.skinModel(var1, var2.id, var2.model, null, false);
        boolean var9 = var2.turret && this.gm.models.enabled() && !var8.isEmpty();
        boolean var10 = this.applyUnit(var6, var9 ? var8 + "#top,tc_flag" : var8, true, var1.color);
        if (var7 != null && !var10 && var2.helmet != Material.AIR) {
            var7.setHelmet(new ItemStack(var2.helmet));
        }

        Combatant var11 = new Combatant(Combatant.Kind.BUILDING, var1, var2);
        var11.modeled = var10;
        if (!var10 && this.gm.models.enabled() && !var8.isEmpty()) {
            this.retryBuildingModel(var11, var6, var8, var9, 1);
        }

        if (var9 && var10) {
            ArmorStand var12 = (ArmorStand)var4.spawn(var3.clone(), ArmorStand.class);
            var12.addScoreboardTag("clashmc");
            stand(var12, true);
            if (this.applyUnit(var12, var8 + "#base", true, var1.color)) {
                var11.extras.add(var12);
                var11.turret = var12;
            } else {
                var12.remove();
            }
        }

        var11.mob = var6;
        var11.label = var6;
        var11.hitbox = var5;
        var11.fixed = var3.clone();
        var11.radius = var2.size / 2.0;
        var11.maxHp = var11.hp = var2.hp;
        var11.deployUntil = this.now() + var2.deployTicks();
        var11.expireAt = this.now() + (long)(var2.lifetime * 20.0) + var2.deployTicks();
        this.all.add(var11);
        this.byEntity.put(var5.getUniqueId(), var11);
        this.byEntity.put(var6.getUniqueId(), var11);
        this.refreshName(var11);
        var4.playSound(var3, "block.anvil.land", 0.5F, 1.2F);
        this.gm.models.anim(var6, "deploy");
        if (var11.turret != null) {
            this.gm.models.anim(var11.turret, "deploy");
        }

        return var11;
    }

    private void retryBuildingModel(Combatant var1, ArmorStand var2, String var3, boolean var4, int var5) {
        this.fx.later(8L, () -> {
            if (var1.alive() && var2.isValid()) {
                if (this.applyUnit(var2, var4 ? var3 + "#top,tc_flag" : var3, true, var1.team.color)) {
                    var1.modeled = true;
                    EntityEquipment var6 = var2.getEquipment();
                    if (var6 != null) {
                        var6.setHelmet(null);
                    }

                    if (var4) {
                        ArmorStand var7 = (ArmorStand)this.A().world.spawn(var1.fixed.clone(), ArmorStand.class);
                        var7.addScoreboardTag("clashmc");
                        stand(var7, true);
                        if (this.applyUnit(var7, var3 + "#base", true, var1.team.color)) {
                            var1.extras.add(var7);
                            var1.turret = var7;
                        } else {
                            var7.remove();
                        }
                    }
                } else if (var5 < 8) {
                    this.retryBuildingModel(var1, var2, var3, var4, var5 + 1);
                }
            }
        });
    }

    private void castSpell(TeamColor var1, CardDef var2, Location var3) {
        World var4 = this.A().world;
        Location var5 = this.A().kingCenter(var1).add(0.0, 9.0, 0.0);
        String var6 = var2.id;
        switch (var6) {
            case "zap":
                this.zapAt(var1, var3, var2.radius, var2.damage, var2.towerDamage, var2.stun);
                break;
            case "fireball":
                this.fx.telegraph(var3, var2.radius, Color.fromRGB(255, 140, 40), (int)Math.min(60.0, 4.0 + var5.distance(var3) / 1.1));
                this.fx.shoot(Fx.Shot.BIG_FIREBALL, var5, () -> var3.clone().add(0.0, 0.5, 0.0), var4x -> {
                    this.fx.impact(Fx.Shot.BIG_FIREBALL, var3, var2.radius);
                    this.fx.spellArea(var3, var2.radius, Color.fromRGB(255, 120, 30), Material.ORANGE_STAINED_GLASS, 12);

                    for (Combatant var6x : this.area(var3, var2.radius, var1.other(), true, true)) {
                        this.damage(var6x, var6x.isTower() ? var2.towerDamage : var2.damage, null);
                        this.knockback(var6x, var3, var2.knockback, false, true);
                    }
                });
                break;
            case "poison":
                Battle.Zone var13 = new Battle.Zone();
                var13.team = var1;
                var13.card = var2;
                var13.center = var3.clone();
                var13.until = this.now() + (long)(var2.duration * 20.0);
                var13.nextTick = this.now() + 10L;
                var13.disc = this.fx.floorDisc(var3, var2.radius, Material.LIME_STAINED_GLASS, 0.02F);
                this.fx.edge(var3, var2.radius, Color.fromRGB(120, 230, 60));
                this.zones.add(var13);
                var4.playSound(var3, "entity.splash_potion.break", 1.0F, 0.7F);
                break;
            case "freeze":
                this.fx.telegraph(var3, var2.radius, Color.fromRGB(170, 230, 255), 10);
                Bukkit.getScheduler()
                    .runTaskLater(
                        this.gm.plugin,
                        () -> {
                            if (this.gm.phase == GameManager.Phase.PLAYING) {
                                var4.spawnParticle(Particle.SNOWFLAKE, var3.clone().add(0.0, 1.0, 0.0), 160, var2.radius / 2.0, 1.0, var2.radius / 2.0, 0.03);
                                var4.spawnParticle(
                                    Particle.BLOCK,
                                    var3.clone().add(0.0, 0.5, 0.0),
                                    60,
                                    var2.radius / 2.0,
                                    0.5,
                                    var2.radius / 2.0,
                                    0.0,
                                    Material.ICE.createBlockData()
                                );
                                this.fx.ring(var3, var2.radius, Color.fromRGB(170, 230, 255));
                                this.fx
                                    .spellArea(
                                        var3,
                                        var2.radius,
                                        Color.fromRGB(170, 230, 255),
                                        Material.LIGHT_BLUE_STAINED_GLASS,
                                        (int)Math.round(var2.duration * 20.0)
                                    );
                                var4.playSound(var3, "block.glass.break", 1.0F, 0.6F);
                                var4.playSound(var3, "entity.player.hurt_freeze", 1.0F, 0.8F);

                                for (Combatant var6x : this.area(var3, var2.radius, var1.other(), true, true)) {
                                    this.damage(var6x, var6x.isTower() ? var2.towerDamage : var2.damage, null);
                                    this.stun(var6x, var2.duration);
                                    Location var7 = var6x.loc();
                                    if (var7 != null && !var6x.isTower()) {
                                        double var8 = var6x.kind == Combatant.Kind.BUILDING ? var6x.card.hitboxW : var6x.radius * 2.0;
                                        double var10 = var6x.card == null ? 2.0 : var6x.card.hitboxH;
                                        this.fx.encase(var7, var8, var10, (int)Math.round(var2.duration * 20.0));
                                    }
                                }
                            }
                        },
                        10L
                    );
                break;
            case "the_log":
            case "barbarian_barrel":
                this.rollLog(var1, var2, var3);
                break;
            case "arrows":
                this.arrowVolley(var1, var2, var3, var5);
                break;
            case "lightning":
                this.lightningStrike(var1, var2, var3);
                break;
            case "rocket":
                this.fx.telegraph(var3, var2.radius, Color.fromRGB(255, 80, 40), (int)Math.min(80.0, 6.0 + var5.distance(var3) / 0.6));
                // 발사 불꽃: 순간 폭발 + 0.5초 동안 분사 불꽃·연기
                var4.spawnParticle(Particle.FLAME, var5, 60, 0.8, 0.5, 0.8, 0.12);
                var4.spawnParticle(Particle.LAVA, var5, 12, 0.7, 0.4, 0.7, 0.0);
                var4.spawnParticle(Particle.LARGE_SMOKE, var5, 30, 0.9, 0.4, 0.9, 0.06);
                var4.spawnParticle(Particle.EXPLOSION, var5, 3, 0.6, 0.3, 0.6, 0.0);
                var4.playSound(var5, "entity.blaze.shoot", 1.0F, 0.6F);
                for (int burst = 1; burst <= 5; burst++) {
                    this.fx.later(burst * 2L, () -> {
                        if (this.gm.phase == GameManager.Phase.PLAYING) {
                            this.A().world.spawnParticle(Particle.FLAME, var5, 16, 0.5, 0.3, 0.5, 0.07);
                            this.A().world.spawnParticle(Particle.CAMPFIRE_COSY_SMOKE, var5, 6, 0.6, 0.2, 0.6, 0.03);
                        }
                    });
                }

                this.fx.shoot(Fx.Shot.ROCKET, var5, () -> var3.clone().add(0.0, 0.5, 0.0), var4x -> {
                    this.fx.impact(Fx.Shot.ROCKET, var3, var2.radius);
                    this.fx.spellArea(var3, var2.radius, Color.fromRGB(255, 90, 30), Material.ORANGE_STAINED_GLASS, 12);

                    for (Combatant var6x : this.area(var3, var2.radius, var1.other(), true, true)) {
                        this.damage(var6x, var6x.isTower() ? var2.towerDamage : var2.damage, null);
                        this.knockback(var6x, var3, var2.knockback, false, true);
                    }
                }, var2.projectileModel, var1.color);
                break;
            case "rage":
            case "earthquake":
            case "tornado":
            case "graveyard":
                Battle.Zone var12 = new Battle.Zone();
                var12.team = var1;
                var12.card = var2;
                var12.center = var3.clone();
                var12.until = this.now() + (long)(var2.duration * 20.0);
                var12.nextTick = this.now() + (var2.id.equals("rage") ? 0L : (var2.id.equals("graveyard") ? Math.round(var2.deploy * 20.0) : 2L));
                if (var2.id.equals("graveyard")) {
                    var12.ticksLeft = var2.spawnCount;
                }

                Material var14 = var2.id.equals("rage")
                    ? Material.PURPLE_STAINED_GLASS
                    : (
                        var2.id.equals("earthquake")
                            ? Material.BROWN_STAINED_GLASS
                            : (var2.id.equals("graveyard") ? Material.GRAY_STAINED_GLASS : Material.LIGHT_GRAY_STAINED_GLASS)
                    );
                var12.disc = this.fx.floorDisc(var3, var2.radius, var14, 0.02F);
                if (var2.id.equals("rage")) {
                    this.fx.ring(var3, var2.radius, Color.fromRGB(190, 60, 255));
                    var4.spawnParticle(Particle.WITCH, var3.clone().add(0.0, 0.6, 0.0), 60, var2.radius / 2.0, 0.4, var2.radius / 2.0, 0.05);
                    var4.playSound(var3, "entity.evoker.prepare_attack", 1.0F, 1.2F);
                    var4.playSound(var3, "entity.ravager.roar", 0.6F, 1.6F);

                    for (Combatant var11 : this.area(var3, var2.radius, var1.other(), true, true)) {
                        this.damage(var11, var11.isTower() ? var2.towerDamage : var2.damage, null);
                    }
                } else if (var2.id.equals("earthquake")) {
                    var4.playSound(var3, "entity.warden.dig", 1.0F, 0.8F);
                    var4.playSound(var3, "block.basalt.break", 1.0F, 0.5F);
                } else if (var2.id.equals("graveyard")) {
                    var4.playSound(var3, "ambient.cave", 1.0F, 0.8F);
                    var4.playSound(var3, "entity.skeleton.ambient", 1.0F, 0.6F);
                    this.fx.ring(var3, var2.radius, Color.fromRGB(120, 255, 120));
                } else {
                    var4.playSound(var3, "entity.breeze.wind_burst", 1.0F, 0.7F);
                    var4.playSound(var3, "item.elytra.flying", 0.8F, 1.4F);
                }

                this.zones.add(var12);
                break;
            case "clone":
                this.cloneAt(var1, var2, var3);
                break;
            case "giant_snowball":
                this.fx.telegraph(var3, var2.radius, Color.fromRGB(235, 245, 255), (int)Math.min(60.0, 4.0 + var5.distance(var3) / 0.8));
                this.fx.shoot(Fx.Shot.SNOWBALL, var5, () -> var3.clone().add(0.0, 0.6, 0.0), var5x -> {
                    this.fx.impact(Fx.Shot.SNOWBALL, var3, var2.radius);
                    this.fx.spellArea(var3, var2.radius, Color.fromRGB(235, 245, 255), Material.WHITE_STAINED_GLASS, 14);

                    for (Combatant var7 : this.area(var3, var2.radius, var1.other(), true, false)) {
                        this.damage(var7, var7.isTower() ? var2.towerDamage : var2.damage, null);
                        this.knockback(var7, var3, var2.knockback, false, true);
                        this.slow(var7, var2.slow, (int)Math.round(var2.slowDuration * 20.0));
                        Location var8 = var7.loc();
                        if (var8 != null && !var7.isTower()) {
                            var4.spawnParticle(Particle.SNOWFLAKE, var8.clone().add(0.0, 1.0, 0.0), 12, 0.3, 0.5, 0.3, 0.01);
                        }
                    }
                });
                break;
            default:
                for (Combatant var9 : this.area(var3, Math.max(2.0, var2.radius), var1.other(), true, true)) {
                    this.damage(var9, var9.isTower() ? var2.towerDamage : var2.damage, null);
                }
        }
    }

    private void lightningStrike(TeamColor var1, CardDef var2, Location var3) {
        World var4 = this.A().world;
        this.fx.telegraph(var3, var2.radius, Color.fromRGB(150, 210, 255), 8);
        List<Combatant> var5 = this.area(var3, var2.radius, var1.other(), true, true);
        var5.sort((var0, var1x) -> Double.compare(var1x.hp, var0.hp));
        int var6 = Math.min(Math.max(1, var2.count), var5.size());

        for (int var7 = 0; var7 < var6; var7++) {
            Combatant var8 = (Combatant)var5.get(var7);
            Bukkit.getScheduler().runTaskLater(this.gm.plugin, () -> {
                if (this.gm.phase == GameManager.Phase.PLAYING && var8.alive()) {
                    Location var4x = this.aim(var8);
                    if (var4x != null) {
                        this.fx.lightning(var4x.clone().add(0.0, 14.0, 0.0), var4x, true);
                        this.fx.lightning(var4x.clone().add(0.4, 14.0, -0.3), var4x, false);
                        var4.spawnParticle(Particle.FLASH, var4x, 1, 0.0, 0.0, 0.0, 0.0);
                        var4.spawnParticle(Particle.ELECTRIC_SPARK, var4x, 40, 0.5, 0.8, 0.5, 0.3);
                        var4.playSound(var4x, "entity.lightning_bolt.thunder", 0.8F, 1.3F);
                        var4.playSound(var4x, "entity.lightning_bolt.impact", 1.0F, 1.0F);
                        this.damage(var8, var8.isTower() ? var2.towerDamage : var2.damage, null);
                        this.stun(var8, var2.stun);
                    }
                }
            }, 8L + var7 * 5L);
        }

        if (var5.isEmpty()) {
            var4.playSound(var3, "entity.lightning_bolt.thunder", 0.5F, 1.6F);
        }
    }

    private void tickSpecialZone(Battle.Zone var1, double var2) {
        World var4 = this.A().world;
        CardDef var5 = var1.card;
        long var6 = this.now();
        String var8 = var5.id;
        switch (var8) {
            case "rage":
                if (var6 % 3L == 0L) {
                    this.fx.edge(var1.center, var2, Color.fromRGB(190, 60, 255));

                    for (int var25 = 0; var25 < 8; var25++) {
                        double var33 = this.gm.rng.nextDouble() * Math.PI * 2.0;
                        double var39 = Math.sqrt(this.gm.rng.nextDouble()) * var2;
                        var4.spawnParticle(
                            Particle.DUST,
                            var1.center.getX() + Math.cos(var33) * var39,
                            this.groundY() + 0.2 + this.gm.rng.nextDouble() * 1.2,
                            var1.center.getZ() + Math.sin(var33) * var39,
                            1,
                            0.0,
                            0.05,
                            0.0,
                            0.0,
                            new DustOptions(Color.fromRGB(200, 70, 255), 1.4F)
                        );
                    }
                }

                for (Combatant var34 : this.area(var1.center, var2, var1.team, true, true)) {
                    if (!var34.isTower()) {
                        var34.rageUntil = var6 + 40L;
                        var34.rageBoost = var5.boost;
                    }
                }
                break;
            case "earthquake":
                if (var6 % 3L == 0L) {
                    this.fx.edge(var1.center, var2, Color.fromRGB(150, 110, 70));
                    var4.spawnParticle(
                        Particle.BLOCK, var1.center.clone().add(0.0, 0.2, 0.0), 25, var2 / 2.0, 0.1, var2 / 2.0, 0.0, Material.DIRT.createBlockData()
                    );
                    var4.spawnParticle(
                        Particle.BLOCK, var1.center.clone().add(0.0, 0.2, 0.0), 10, var2 / 2.0, 0.1, var2 / 2.0, 0.0, Material.STONE.createBlockData()
                    );
                }

                for (Combatant var31 : this.area(var1.center, var2, var1.team.other(), true, false)) {
                    this.slow(var31, var5.slow, 10);
                }

                if (var6 >= var1.nextTick) {
                    var1.nextTick = var6 + 20L;
                    var4.playSound(var1.center, "entity.generic.explode", 0.4F, 0.5F);
                    var4.playSound(var1.center, "block.gravel.break", 1.0F, 0.6F);
                    var4.spawnParticle(Particle.CAMPFIRE_COSY_SMOKE, var1.center, 8, var2 / 3.0, 0.1, var2 / 3.0, 0.01);

                    for (Combatant var32 : this.area(var1.center, var2, var1.team.other(), true, false)) {
                        double var35 = var32.isTower() ? var5.towerDamage : (var32.kind == Combatant.Kind.BUILDING ? var5.buildingDamage : var5.damage);
                        this.damage(var32, var35, null);
                    }
                }
                break;
            case "tornado":
                for (int var20 = 0; var20 < 3; var20++) {
                    double var28 = var6 * 0.5 + var20 * Math.PI * 2.0 / 3.0;

                    for (double var37 = 0.0; var37 < 3.0; var37 += 0.6) {
                        double var40 = var2 * (0.25 + var37 / 3.0 * 0.6);
                        var4.spawnParticle(
                            Particle.CLOUD,
                            var1.center.getX() + Math.cos(var28 + var37) * var40,
                            this.groundY() + var37,
                            var1.center.getZ() + Math.sin(var28 + var37) * var40,
                            1,
                            0.0,
                            0.0,
                            0.0,
                            0.0
                        );
                    }
                }

                if (var6 % 2L == 0L) {
                    var4.spawnParticle(Particle.SWEEP_ATTACK, var1.center.clone().add(0.0, 1.0, 0.0), 2, var2 / 3.0, 0.5, var2 / 3.0, 0.0);
                }

                for (Combatant var29 : this.area(var1.center, var2, var1.team.other(), true, true)) {
                    if (!var29.isStructure()) {
                        Location var12 = var29.loc();
                        if (var12 != null) {
                            Vector var38 = new Vector(var1.center.getX() - var12.getX(), 0.0, var1.center.getZ() - var12.getZ());
                            double var14 = var38.length();
                            if (!(var14 < 0.3)) {
                                double var16 = var29.maxHp > 2500.0 ? 0.5 : 1.0;
                                var38.multiply(Math.min(var14, var5.pull * var16) / var14);
                                if (var29.isPlayer()) {
                                    Player var41 = var29.player();
                                    if (var41 != null) {
                                        var41.setVelocity(var38.clone().multiply(1.2).setY(0.05));
                                    }
                                } else if (var29.mob != null) {
                                    Location var42 = var12.clone().add(var38);
                                    var42.setY(var29.air ? this.airY() : this.groundY());
                                    var29.mob.teleport(var42);
                                }
                                // 토네이도로 끌려온 적이 우리 킹 타워 사거리에 들어오면 킹 타워가 깨어남
                                Combatant kt = this.tower(var1.team, Combatant.Kind.KING_TOWER, false);
                                if (kt != null && kt.alive() && !kt.active && kt.fixed != null) {
                                    Location pl = var29.loc();
                                    if (pl != null && flat(pl, kt.fixed) - kt.radius - var29.radius <= this.gm.kingRange) {
                                        this.activateKing(kt);
                                    }
                                }
                            }
                        }
                    }
                }

                if (var6 >= var1.nextTick) {
                    var1.nextTick = var6 + 10L;
                    var4.playSound(var1.center, "entity.breeze.idle_ground", 0.8F, 0.8F);

                    for (Combatant var30 : this.area(var1.center, var2, var1.team.other(), true, true)) {
                        this.damage(var30, var30.isTower() ? var5.towerDamage : var5.damage, null);
                    }
                }
                break;
            case "graveyard":
                if (var6 % 3L == 0L) {
                    this.fx.edge(var1.center, var2, Color.fromRGB(110, 230, 110));

                    for (int var10 = 0; var10 < 6; var10++) {
                        double var11 = this.gm.rng.nextDouble() * Math.PI * 2.0;
                        double var13 = Math.sqrt(this.gm.rng.nextDouble()) * var2;
                        var4.spawnParticle(
                            Particle.DUST,
                            var1.center.getX() + Math.cos(var11) * var13,
                            this.groundY() + 0.15 + this.gm.rng.nextDouble() * 0.5,
                            var1.center.getZ() + Math.sin(var11) * var13,
                            1,
                            0.0,
                            0.02,
                            0.0,
                            0.0,
                            new DustOptions(Color.fromRGB(70, 80, 70), 1.6F)
                        );
                    }

                    var4.spawnParticle(Particle.SCULK_SOUL, var1.center.clone().add(0.0, 0.4, 0.0), 1, var2 / 2.0, 0.1, var2 / 2.0, 0.01);
                }

                CardDef var19 = var5.spawnCard.isEmpty() ? null : this.gm.cards.get(var5.spawnCard);
                if (var19 != null && var1.ticksLeft > 0 && var6 >= var1.nextTick) {
                    var1.nextTick = var6 + Math.max(1L, Math.round(var5.spawnEvery * 20.0));
                    var1.ticksLeft--;
                    double var27 = Math.min(var2 * 0.75, 6.0);
                    double var36 = this.gm.rng.nextDouble() * Math.PI * 2.0;
                    double var15 = var27 + this.gm.rng.nextDouble() * Math.max(0.1, var2 - var27);
                    Location var17 = new Location(
                        this.A().world, var1.center.getX() + Math.cos(var36) * var15, this.groundY(), var1.center.getZ() + Math.sin(var36) * var15
                    );
                    var17.setX(Math.max(this.A().minX + 0.5, Math.min(this.A().minX + 54 - 0.5, var17.getX())));
                    var17.setZ(Math.max(this.A().minZ + 0.5, Math.min(this.A().minZ + 96 - 0.5, var17.getZ())));
                    var4.spawnParticle(Particle.BLOCK, var17.clone().add(0.0, 0.3, 0.0), 18, 0.3, 0.1, 0.3, 0.0, Material.DIRT.createBlockData());
                    var4.spawnParticle(Particle.SOUL, var17.clone().add(0.0, 0.5, 0.0), 4, 0.2, 0.3, 0.2, 0.02);
                    var4.playSound(var17, "entity.skeleton.step", 0.8F, 0.8F);
                    var4.playSound(var17, "block.rooted_dirt.break", 0.8F, 0.7F);
                    Combatant var18 = this.spawnAi(var1.team, var19, var17, 6);
                    var18.leader = null;
                }

                if (var1.ticksLeft == 0 && var6 > var1.nextTick) {
                    var1.until = Math.min(var1.until, var6 + 20L);
                }
        }
    }

    private void cloneAt(TeamColor var1, CardDef var2, Location var3) {
        World var4 = this.A().world;
        this.fx.ring(var3, var2.radius, Color.fromRGB(110, 200, 255));
        this.fx.spellArea(var3, var2.radius, Color.fromRGB(110, 200, 255), Material.LIGHT_BLUE_STAINED_GLASS, 10);
        var4.playSound(var3, "block.beacon.activate", 1.0F, 1.6F);
        var4.playSound(var3, "entity.illusioner.mirror_move", 1.0F, 1.0F);

        for (Combatant var6 : this.area(var3, var2.radius, var1, true, true)) {
            if (!var6.isStructure() && !var6.clone && var6.kind == Combatant.Kind.TROOP && var6.card != null) {
                Location var7 = var6.loc();
                if (var7 != null) {
                    Location var8 = var7.clone().add(this.gm.rng.nextDouble() - 0.5, 0.0, -var1.dir * 0.8);
                    Combatant var9 = this.spawnAi(var1, var6.card, var8, 8);
                    var9.hp = var9.maxHp = 1.0;
                    var9.clone = true;
                    var9.leader = null;
                    this.refreshName(var9);
                    var4.spawnParticle(Particle.END_ROD, var8.clone().add(0.0, 1.0, 0.0), 10, 0.3, 0.5, 0.3, 0.03);
                    var4.spawnParticle(
                        Particle.DUST, var8.clone().add(0.0, 1.0, 0.0), 14, 0.3, 0.6, 0.3, 0.0, new DustOptions(Color.fromRGB(110, 200, 255), 1.2F)
                    );
                }
            }
        }
    }

    private void spawnAiGroup(TeamColor var1, CardDef var2, Location var3, int var4, int var5) {
        for (Location var8 : this.formation(var3, var4, var4 <= 2 ? 0.7 : 1.1)) {
            if (!var2.air) {
                var8 = this.dryLand(var1, var3, var8);
            }
            Combatant var9 = this.spawnAi(var1, var2, var8, var5);
            var9.leader = null;
        }
    }

    private void arrowVolley(TeamColor var1, CardDef var2, Location var3, Location var4) {
        World var5 = this.A().world;
        this.fx.telegraph(var3, var2.radius, Color.fromRGB(255, 240, 200), 14);
        int var6 = var2.waves;

        for (int var7 = 0; var7 < var6; var7++) {
            int var8 = var7;
            Bukkit.getScheduler().runTaskLater(this.gm.plugin, () -> {
                if (this.gm.phase == GameManager.Phase.PLAYING) {
                    for (int var8x = 0; var8x < 9; var8x++) {
                        double var9 = this.gm.rng.nextDouble() * Math.PI * 2.0;
                        double var11 = Math.sqrt(this.gm.rng.nextDouble()) * var2.radius;
                        Location var13 = var3.clone().add(Math.cos(var9) * var11, 0.2, Math.sin(var9) * var11);
                        Location var14 = var4.clone().add(this.gm.rng.nextDouble() * 2.0 - 1.0, 2.0, this.gm.rng.nextDouble() * 2.0 - 1.0);
                        this.fx.shoot(Fx.Shot.ARROW, var14, () -> var13, var1xx -> var5.spawnParticle(Particle.CRIT, var1xx, 3, 0.1, 0.1, 0.1, 0.1));
                    }

                    double var15 = var4.distance(var3) / Fx.Shot.ARROW.speed * 20.0;
                    Bukkit.getScheduler().runTaskLater(this.gm.plugin, () -> {
                        if (this.gm.phase == GameManager.Phase.PLAYING) {
                            this.fx.ring(var3, var2.radius, Color.fromRGB(255, 240, 200));
                            var5.spawnParticle(Particle.CRIT, var3.clone().add(0.0, 0.4, 0.0), 50, var2.radius / 2.0, 0.2, var2.radius / 2.0, 0.15);
                            var5.playSound(var3, "entity.arrow.hit", 1.0F, 0.8F + var8 * 0.15F);

                            for (Combatant var8xx : this.area(var3, var2.radius, var1.other(), true, true)) {
                                this.damage(var8xx, (var8xx.isTower() ? var2.towerDamage : var2.damage) / var6, null);
                            }
                        }
                    }, Math.max(1L, Math.round(var15)));
                }
            }, var7 * 6L);
        }
    }

    private void kamikaze(final Combatant var1, final Combatant var2) {
        final CardDef var3 = var1.card;
        World var4 = this.A().world;
        final Location var5 = var1.loc();
        if (var5 != null) {
            var1.stunUntil = this.now() + 200L;
            var1.nextAttack = this.now() + 200L;
            BukkitRunnable var6 = new BukkitRunnable() {
                int i = 0;

                public void run() {
                    if (Battle.this.gm.phase == GameManager.Phase.PLAYING && !var1.dead) {
                        this.i++;
                        Location var1x = var2.alive() && var2.loc() != null ? var2.loc() : null;
                        Location var2x = var1x != null ? var1x : var5;
                        double var3x = Math.min(1.0, this.i / 8.0);
                        Location var5x = var5.clone().add(var2x.toVector().subtract(var5.toVector()).multiply(var3x));
                        var5x.setY((var1.air ? Battle.this.airY() : Battle.this.groundY()) + Math.sin(Math.PI * var3x) * 1.6);
                        if (var1.mob != null) {
                            var1.mob.teleport(var5x);
                        }

                        Battle.this.spiritTrail(var3, var5x);
                        if (this.i >= 8) {
                            this.cancel();
                            Battle.this.running.remove(this);
                            Battle.this.spiritBurst(var1, var2, var5x);
                            Battle.this.kill(var1);
                        }
                    } else {
                        this.cancel();
                        Battle.this.running.remove(this);
                    }
                }
            };
            this.running.add(var6);
            var6.runTaskTimer(this.gm.plugin, 0L, 1L);
            var4.playSound(var5, "entity.slime.jump", 0.8F, 1.5F);
        }
    }

    private void spiritAura(Combatant var1) {
        Location var2 = var1.loc();
        if (var2 != null && this.now() >= var1.deployUntil - 10L) {
            World var3 = this.A().world;
            long var4 = this.now();
            double var6 = 0.55;
            Location var8 = var2.clone().add(0.0, var6, 0.0);
            double var9 = var4 * 0.35;
            String var13 = var1.card.id;
            DustOptions var11;
            DustOptions var12;
            switch (var13) {
                case "ice_spirit":
                    var11 = new DustOptions(Color.fromRGB(200, 240, 255), 0.9F);
                    var12 = new DustOptions(Color.fromRGB(150, 215, 255), 1.6F);
                    break;
                case "fire_spirit":
                    var11 = new DustOptions(Color.fromRGB(255, 170, 40), 0.9F);
                    var12 = new DustOptions(Color.fromRGB(255, 90, 20), 1.6F);
                    break;
                case "heal_spirit":
                    var11 = new DustOptions(Color.fromRGB(255, 240, 150), 0.9F);
                    var12 = new DustOptions(Color.fromRGB(255, 210, 60), 1.6F);
                    break;
                default:
                    var11 = new DustOptions(Color.fromRGB(200, 250, 255), 0.9F);
                    var12 = new DustOptions(Color.fromRGB(110, 200, 255), 1.6F);
            }

            for (int var24 = 0; var24 < 2; var24++) {
                double var26 = (var24 == 0 ? var9 : -var9 * 1.3) + var24 * Math.PI;
                double var16 = 0.55;
                double var18 = var6 + (var24 == 0 ? 0.15 : -0.1) + Math.sin(var4 * 0.2 + var24) * 0.12;
                var3.spawnParticle(
                    Particle.DUST,
                    var2.getX() + Math.cos(var26) * var16,
                    var2.getY() + var18,
                    var2.getZ() + Math.sin(var26) * var16,
                    1,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    var11
                );
            }

            if (var4 % 3L == 0L) {
                var3.spawnParticle(Particle.DUST, var8, 2, 0.28, 0.25, 0.28, 0.0, var12);
            }

            var13 = var1.card.id;
            switch (var13) {
                case "ice_spirit":
                    if (var4 % 2L == 0L) {
                        var3.spawnParticle(Particle.SNOWFLAKE, var8, 1, 0.3, 0.3, 0.3, 0.01);
                    }

                    if (var4 % 5L == 0L) {
                        var3.spawnParticle(Particle.END_ROD, var2.clone().add(0.0, 1.0, 0.0), 1, 0.15, 0.1, 0.15, 0.005);
                    }

                    if (var4 % 6L == 0L) {
                        DustOptions var28 = new DustOptions(Color.fromRGB(235, 250, 255), 0.7F);

                        for (int var29 = 0; var29 < 6; var29++) {
                            double var30 = (Math.PI * 2) * var29 / 6.0 + var4 * 0.05;
                            var3.spawnParticle(
                                Particle.DUST,
                                var2.getX() + Math.cos(var30) * 0.5,
                                var2.getY() + 0.05,
                                var2.getZ() + Math.sin(var30) * 0.5,
                                1,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                var28
                            );
                        }
                    }
                    break;
                case "fire_spirit":
                    if (var4 % 2L == 0L) {
                        var3.spawnParticle(Particle.FLAME, var2.clone().add(0.0, 0.95, 0.0), 2, 0.12, 0.08, 0.12, 0.012);
                    }

                    if (var4 % 2L == 1L) {
                        var3.spawnParticle(Particle.SMALL_FLAME, var8, 2, 0.3, 0.25, 0.3, 0.01);
                    }

                    if (var4 % 7L == 0L) {
                        var3.spawnParticle(Particle.LARGE_SMOKE, var2.clone().add(0.0, 1.2, 0.0), 1, 0.1, 0.05, 0.1, 0.01);
                    }

                    if (var4 % 11L == 0L) {
                        var3.spawnParticle(Particle.LAVA, var8, 1, 0.1, 0.1, 0.1, 0.0);
                    }
                    break;
                case "heal_spirit":
                    if (var4 % 3L == 0L) {
                        var3.spawnParticle(Particle.END_ROD, var2.clone().add(0.0, 1.0, 0.0), 1, 0.15, 0.1, 0.15, 0.005);
                    }

                    if (var4 % 8L == 0L) {
                        var3.spawnParticle(Particle.HAPPY_VILLAGER, var8, 2, 0.3, 0.3, 0.3, 0.0);
                    }
                    break;
                default:
                    if (var4 % 2L == 0L) {
                        var3.spawnParticle(Particle.ELECTRIC_SPARK, var8, 3, 0.35, 0.3, 0.35, 0.08);
                    }

                    if (var4 % 4L == 0L) {
                        var3.spawnParticle(Particle.END_ROD, var2.clone().add(0.0, 1.1, 0.0), 1, 0.1, 0.05, 0.1, 0.01);
                    }

                    if (var4 % 9L == 0L) {
                        double var15 = this.gm.rng.nextDouble() * Math.PI * 2.0;
                        Location var17 = var8.clone().add(Math.cos(var15) * 0.3, 0.2, Math.sin(var15) * 0.3);
                        Location var31 = var8.clone().add(Math.cos(var15 + 2.2) * 0.7, -0.3 + this.gm.rng.nextDouble() * 0.6, Math.sin(var15 + 2.2) * 0.7);
                        DustOptions var19 = new DustOptions(Color.fromRGB(240, 250, 255), 0.6F);

                        for (int var20 = 0; var20 <= 5; var20++) {
                            double var21 = var20 / 5.0;
                            Location var23 = var17.clone()
                                .add(var31.toVector().subtract(var17.toVector()).multiply(var21))
                                .add((this.gm.rng.nextDouble() - 0.5) * 0.12, (this.gm.rng.nextDouble() - 0.5) * 0.12, (this.gm.rng.nextDouble() - 0.5) * 0.12);
                            var3.spawnParticle(Particle.DUST, var23, 1, 0.0, 0.0, 0.0, 0.0, var19);
                        }
                    }

                    if (var4 % 30L == 0L) {
                        var3.playSound(var2, "block.beacon.ambient", 0.2F, 2.0F);
                    }
            }
        }
    }

    private void spiritTrail(CardDef var1, Location var2) {
        World var3 = this.A().world;
        String var4 = var1.id;
        switch (var4) {
            case "ice_spirit":
                var3.spawnParticle(Particle.SNOWFLAKE, var2, 3, 0.1, 0.1, 0.1, 0.01);
                break;
            case "fire_spirit":
                var3.spawnParticle(Particle.FLAME, var2, 4, 0.1, 0.1, 0.1, 0.01);
                break;
            case "heal_spirit":
                var3.spawnParticle(Particle.END_ROD, var2, 2, 0.1, 0.1, 0.1, 0.01);
                var3.spawnParticle(Particle.DUST, var2, 3, 0.1, 0.1, 0.1, 0.0, new DustOptions(Color.fromRGB(255, 225, 90), 1.2F));
                break;
            default:
                var3.spawnParticle(Particle.ELECTRIC_SPARK, var2, 4, 0.1, 0.1, 0.1, 0.05);
        }
    }

    private void spiritBurst(Combatant var1, Combatant var2, Location var3) {
        CardDef var4 = var1.card;
        World var5 = this.A().world;
        Location var6 = var3.clone();
        var6.setY(this.groundY());
        if (var4.chain > 0) {
            HashSet var25 = new HashSet();
            Combatant var8 = var2.alive() ? var2 : null;
            Location var26 = var3.clone();

            for (int var27 = 0; var27 < var4.chain && var8 != null; var27++) {
                var25.add(var8.id);
                Location var28 = this.aim(var8);
                if (var28 != null) {
                    this.fx.lightning(var26, var28, var27 == 0);
                }

                this.damage(var8, var4.damage, var1);
                this.stun(var8, var4.stun);
                if (var28 != null) {
                    var26 = var28;
                }

                Combatant var29 = null;
                double var30 = var4.chainRange * var4.chainRange;
                Location var31 = var8.loc();

                for (Combatant var17 : this.all) {
                    if (var17.alive() && !var25.contains(var17.id) && var17.team != var1.team && !var17.hidden && this.canTarget(var1, var17) && var31 != null) {
                        Location var18 = var17.loc();
                        if (var18 != null) {
                            double var19 = var18.getX() - var31.getX();
                            double var21 = var18.getZ() - var31.getZ();
                            double var23 = var19 * var19 + var21 * var21;
                            if (var23 <= var30) {
                                var30 = var23;
                                var29 = var17;
                            }
                        }
                    }
                }

                var8 = var29;
            }

            var5.playSound(var3, "entity.lightning_bolt.impact", 0.6F, 1.8F);
        } else {
            double var7 = Math.max(0.8, var4.splash);
            boolean var9 = var4.targets != CardDef.Targets.GROUND;
            if (var4.id.equals("ice_spirit")) {
                var5.spawnParticle(Particle.SNOWFLAKE, var6.clone().add(0.0, 0.8, 0.0), 60, var7 / 2.0, 0.5, var7 / 2.0, 0.04);
                var5.spawnParticle(Particle.BLOCK, var6.clone().add(0.0, 0.6, 0.0), 30, var7 / 2.0, 0.4, var7 / 2.0, 0.0, Material.ICE.createBlockData());
                this.fx.ring(var6, var7, Color.fromRGB(170, 230, 255));
                var5.playSound(var6, "block.glass.break", 0.9F, 1.2F);
                var5.playSound(var6, "entity.player.hurt_freeze", 0.8F, 1.2F);
            } else if (var4.heal > 0.0) {
                var5.spawnParticle(Particle.END_ROD, var6.clone().add(0.0, 0.8, 0.0), 40, var7 / 2.0, 0.5, var7 / 2.0, 0.05);
                var5.spawnParticle(Particle.DUST, var6.clone().add(0.0, 0.6, 0.0), 40, var7 / 2.0, 0.4, var7 / 2.0, 0.0, new DustOptions(Color.fromRGB(255, 220, 80), 1.6F));
                this.fx.ring(var6, var7, Color.fromRGB(255, 225, 90));
                var5.playSound(var6, "block.amethyst_block.chime", 1.0F, 1.2F);
                var5.playSound(var6, "entity.player.levelup", 0.5F, 1.8F);
                this.healBurst(var1, var6);
            } else {
                var5.spawnParticle(Particle.FLAME, var6.clone().add(0.0, 0.6, 0.0), 70, var7 / 2.0, 0.4, var7 / 2.0, 0.05);
                var5.spawnParticle(Particle.LAVA, var6, 8, var7 / 3.0, 0.2, var7 / 3.0, 0.0);
                this.fx.ring(var6, var7, Color.fromRGB(255, 130, 30));
                var5.playSound(var6, "entity.generic.burn", 1.0F, 1.0F);
                var5.playSound(var6, "entity.blaze.hurt", 0.5F, 1.4F);
            }

            for (Combatant var11 : this.area(var6, var7, var1.team.other(), true, var9)) {
                this.damage(var11, var11.isTower() && var4.towerDamage > 0.0 ? var4.towerDamage : var4.damage, var1);
                if (var4.stun > 0.0) {
                    this.stun(var11, var4.stun);
                    Location var12 = var11.loc();
                    if (var4.id.equals("ice_spirit") && var12 != null && !var11.isTower()) {
                        double var13 = var11.kind == Combatant.Kind.BUILDING ? var11.card.hitboxW : var11.radius * 2.0;
                        double var15 = var11.card == null ? 2.0 : var11.card.hitboxH;
                        this.fx.encase(var12, var13, var15, (int)Math.round(var4.stun * 20.0));
                    }
                }
            }
        }
    }

    private void zapAt(TeamColor var1, Location var2, double var3, double var5, double var7, double var9) {
        this.fx.zapStrike(var2, var3);
        this.fx.spellArea(var2, var3, Color.fromRGB(120, 200, 255), Material.YELLOW_STAINED_GLASS, 10);

        for (Combatant var12 : this.area(var2, var3, var1.other(), true, true)) {
            this.damage(var12, var12.isTower() ? (var7 > 0.0 ? var7 : var5) : var5, null);
            this.stun(var12, var9);
        }
    }

    private void rollLog(TeamColor var1, CardDef var2, Location var3) {
        HashSet var4 = new HashSet();
        double var5 = var2.width;
        double var7 = var2.length;
        double var9 = var5 / 2.0;
        int var11 = var1.dir;
        Consumer<Location> var12 = null;
        CardDef var13 = var2.spawnCard.isEmpty() ? null : this.gm.cards.get(var2.spawnCard);
        if (var13 != null) {
            var12 = var3x -> {
                GameTeam var4x = this.gm.teams.get(var1);
                if (var4x != null) {
                    Location var5x = var3x.clone();
                    var5x.setY(this.groundY());
                    // 통이 강물 위에서 멈추면 바바리안은 강 건너편 둑에서 나옴 (굴러가던 방향)
                    if (this.inRiverOffBridge(var5x.getX(), var5x.getZ())) {
                        var5x.setZ(var11 > 0 ? this.A().riverMaxZ() + 0.8 : this.A().riverMinZ() - 0.8);
                    }
                    this.A().world.playSound(var5x, "entity.zombie.break_wooden_door", 0.9F, 1.1F);
                    this.A().world.spawnParticle(Particle.CLOUD, var5x.clone().add(0.0, 0.5, 0.0), 14, 0.4, 0.3, 0.4, 0.02);
                    this.spawnTroops(var4x, var13, var5x, 12, 1, null);
                }
            };
        }

        this.fx
            .rollingLog(
                var3,
                var11,
                var5,
                var7,
                var2.model,
                var1.color,
                var7x -> this.rollHit(var1, var2, var7x, var4, var9, var11),
                var12,
                var13 != null ? Material.BARREL : Material.OAK_LOG
            );
    }

    private void rollHit(TeamColor var1, CardDef var2, Location var3, Set<Integer> var4, double var5, int var7) {
        for (Combatant var9 : new ArrayList<>(this.all)) {
            if (var9.alive() && var9.team != var1 && !var9.air && !var4.contains(var9.id) && !var9.hidden) {
                Location var10 = var9.loc();
                if (var10 != null) {
                    double var11 = Math.abs(var10.getX() - var3.getX());
                    double var13 = Math.abs(var10.getZ() - var3.getZ());
                    if (var11 <= var5 + var9.radius && var13 <= 0.8 + var9.radius) {
                        var4.add(var9.id);
                        this.damage(var9, var9.isTower() ? var2.towerDamage : var2.damage, null);
                        if (var9.kind == Combatant.Kind.TROOP) {
                            this.knockback(var9, var10.clone().add(0.0, 0.0, -var7), var2.knockback, var2.id.equals("the_log"), false);
                        }
                    }
                }
            }
        }
    }

    private void travel(final Location var1, final Location var2, final Particle var3, double var4, final Runnable var6) {
        final double var7 = var1.distance(var2);
        final int var9 = Math.max(4, (int)Math.round(var7 / var4 * 20.0));
        final World var10 = this.A().world;
        BukkitRunnable var11 = new BukkitRunnable() {
            int i = 0;

            public void run() {
                if (Battle.this.gm.phase != GameManager.Phase.PLAYING) {
                    this.cancel();
                    Battle.this.running.remove(this);
                } else {
                    this.i++;
                    double var1x = (double)this.i / var9;
                    Vector var3x = var2.toVector().subtract(var1.toVector()).multiply(var1x);
                    Location var4x = var1.clone().add(var3x).add(0.0, Math.sin(Math.PI * var1x) * Math.min(12.0, var7 / 3.0), 0.0);
                    var10.spawnParticle(var3, var4x, 4, 0.1, 0.1, 0.1, 0.01);
                    if (this.i >= var9) {
                        this.cancel();
                        Battle.this.running.remove(this);
                        var6.run();
                    }
                }
            }
        };
        this.running.add(var11);
        var11.runTaskTimer(this.gm.plugin, 0L, 1L);
    }

    private void travelGround(final Location var1, final Location var2, final Runnable var3) {
        double var4 = var1.distance(var2);
        final int var6 = 20 + (int)Math.round(var4 / 12.0 * 20.0);
        final World var7 = this.A().world;
        BukkitRunnable var8 = new BukkitRunnable() {
            int i = 0;

            public void run() {
                if (Battle.this.gm.phase != GameManager.Phase.PLAYING) {
                    this.cancel();
                    Battle.this.running.remove(this);
                } else {
                    this.i++;
                    double var1x = Math.min(1.0, (double)this.i / var6);
                    Location var3x = var1.clone().add(var2.toVector().subtract(var1.toVector()).multiply(var1x));
                    var3x.setY(Battle.this.groundY());
                    var7.spawnParticle(Particle.SMOKE, var3x, 3, 0.2, 0.05, 0.2, 0.01);
                    if (this.i >= var6) {
                        this.cancel();
                        Battle.this.running.remove(this);
                        var3.run();
                    }
                }
            }
        };
        this.running.add(var8);
        var8.runTaskTimer(this.gm.plugin, 0L, 1L);
    }

    private List<Combatant> area(Location var1, double var2, TeamColor var4, boolean var5, boolean var6) {
        ArrayList var7 = new ArrayList();

        for (Combatant var9 : this.all) {
            if (var9.alive() && var9.team == var4 && (var9.air ? var6 : var5)) {
                Location var10 = var9.loc();
                if (var10 != null && flat(var10, var1) - var9.radius <= var2) {
                    var7.add(var9);
                }
            }
        }

        return var7;
    }

    private void stun(Combatant var1, double var2) {
        if (!(var2 <= 0.0)) {
            var1.stunUntil = Math.max(var1.stunUntil, this.now() + Math.round(var2 * 20.0));
            if (!var1.isTower()) {
                var1.target = null;   // 감전·스턴되면 가장 가까운 대상으로 다시 고름
            }
            if (var1.card != null && var1.card.stunResetsCharge && !var1.isTower()) {
                // 스파키: 감전되면 충전이 처음부터
                var1.nextAttack = Math.max(var1.nextAttack, var1.stunUntil + var1.card.hitTicks());
                Location sl = var1.loc();
                if (sl != null) {
                    this.A().world.spawnParticle(Particle.SMOKE, sl.clone().add(0.0, 1.2, 0.0), 12, 0.4, 0.3, 0.4, 0.02);
                    this.A().world.playSound(sl, "block.beacon.deactivate", 0.8F, 1.6F);
                }
            }

            var1.infernoTarget = null;
            var1.charging = false;
            var1.chargeDist = 0.0;
            var1.target = var1.isStructure() ? null : var1.target;
        }
    }

    /** 보통 넉백: 중형 이하 지상 유닛만 (대형 유닛·건물·타워는 안 밀림) */
    private void knockback(Combatant var1, Location var2, double var3) {
        this.knockback(var1, var2, var3, false, false);
    }

    /**
     * 넉백 규칙
     * - 건물·타워는 절대 안 밀림
     * - 대형 유닛 (card heavy: 자이언트, 페카, 골렘 등) 은 anySize (통나무) 일 때만 밀림
     * - 공중 유닛은 airOk (파이어볼 등) 일 때만 밀림
     * - 밀리면 돌진 초기화 + 공격 모션 취소 (다시 준비) + 인페르노 단계 초기화
     */
    private void knockback(Combatant var1, Location var2, double var3, boolean anySize, boolean airOk) {
        if (var3 <= 0.0 || var1.kind != Combatant.Kind.TROOP) {
            return;
        }
        if (var1.air && !airOk) {
            return;
        }
        if (!anySize && var1.card != null && var1.card.heavy) {
            return;
        }
        {
            Location var5 = var1.loc();
            if (var5 != null) {
                Vector var6 = var5.toVector().subtract(var2.toVector()).setY(0.0);
                if (var6.lengthSquared() < 1.0E-4) {
                    var6 = new Vector(0.0, 0.0, var1.team == TeamColor.BLUE ? -1.0 : 1.0);
                }

                var6.normalize().multiply(var3);
                this.resetCharge(var1);
                // 공격 모션 취소: 다시 공격 준비부터 (최소 반 박자)
                if (var1.card != null) {
                    var1.nextAttack = Math.max(var1.nextAttack, this.now() + Math.max(4L, this.hitTicks(var1) / 2L));
                    if (!var1.card.damageStages.isEmpty()) {
                        var1.infernoSince = this.now();
                    }
                }
                if (var1.isPlayer()) {
                    Player var7 = var1.player();
                    if (var7 != null) {
                        var7.setVelocity(var6.clone().multiply(0.45).setY(0.25));
                    }
                } else if (var1.mob != null) {
                    // 한 번에 순간이동하면 같은 틱 이동에 덮여 안 보임 → 6틱 동안 밀려나게 (그동안 AI 이동 멈춤)
                    var1.knockTicks = 6;
                    var1.knockVx = var6.getX() / 6.0;
                    var1.knockVz = var6.getZ() / 6.0;
                }
            }
        }
    }

    void tick() {
        Iterator var1 = this.zones.iterator();

        while (var1.hasNext()) {
            Battle.Zone var2 = (Battle.Zone)var1.next();
            if (this.now() >= var2.until) {
                if (var2.disc != null) {
                    this.fx.fadeDisc(var2.disc);
                }

                var1.remove();
            } else {
                double var3 = var2.card.radius;
                if (!var2.card.id.equals("poison")) {
                    this.tickSpecialZone(var2, var3);
                } else {
                    if (this.now() % 4L == 0L) {
                        this.fx.edge(var2.center, var3, Color.fromRGB(120, 230, 60));

                        for (int var5 = 0; var5 < 10; var5++) {
                            double var6 = this.gm.rng.nextDouble() * Math.PI * 2.0;
                            double var8 = Math.sqrt(this.gm.rng.nextDouble()) * var3;
                            Location var10 = new Location(
                                this.A().world,
                                var2.center.getX() + Math.cos(var6) * var8,
                                this.groundY() + 0.15 + this.gm.rng.nextDouble() * 0.9,
                                var2.center.getZ() + Math.sin(var6) * var8
                            );
                            this.A()
                                .world
                                .spawnParticle(
                                    Particle.DUST,
                                    var10,
                                    1,
                                    0.0,
                                    0.05,
                                    0.0,
                                    0.0,
                                    new DustOptions(this.gm.rng.nextBoolean() ? Color.fromRGB(90, 200, 40) : Color.fromRGB(160, 240, 90), 1.3F)
                                );
                        }

                        this.A().world.spawnParticle(Particle.ITEM_SLIME, var2.center.clone().add(0.0, 0.3, 0.0), 2, var3 / 2.0, 0.1, var3 / 2.0, 0.0);
                        this.A().world.spawnParticle(Particle.WITCH, var2.center.clone().add(0.0, 0.4, 0.0), 3, var3 / 2.0, 0.2, var3 / 2.0, 0.0);
                    }

                    if (this.now() >= var2.nextTick) {
                        var2.nextTick = this.now() + 20L;

                        for (Combatant var14 : this.area(var2.center, var2.card.radius, var2.team.other(), true, true)) {
                            this.damage(var14, var14.isTower() ? var2.card.towerDamage : var2.card.damage, null);
                            this.slow(var14, this.slowOf(), 25);
                        }
                    }
                }
            }
        }

        for (Combatant var12 : new ArrayList<>(this.all)) {
            if (this.gm.phase != GameManager.Phase.PLAYING) {
                return;
            }

            if (var12.alive()) {
                switch (var12.kind) {
                    case KING_TOWER:
                    case PRINCESS_TOWER:
                        this.tickShooter(var12);
                        break;
                    case BUILDING:
                        this.tickBuilding(var12);
                        break;
                    case BARREL:
                    case TROOP:
                        if (var12.isPlayer()) {
                            this.tickPlayerUnit(var12);
                        } else {
                            this.tickAi(var12);
                        }

                        if (var12.card != null && var12.card.kamikaze && var12.alive() && this.now() % 2L == 0L) {
                            this.spiritAura(var12);
                        }

                        if (var12.kind == Combatant.Kind.TROOP && var12.alive()) {
                            this.tickTroopExtras(var12);
                        }
                }
            }
        }

        if (this.gm.phase == GameManager.Phase.PLAYING) {
            this.separate();
        }

        this.flushMoves();
        if (this.now() % 10L == 0L && !this.gm.assault) {
            this.refreshGlows();
        }
        this.sweepDeployMarks(false);
        this.hideStaleOutlines();

        this.all.removeIf(var0 -> var0.dead && !var0.isTower());
        if (this.gm.hpDisplays && this.now() % (this.gm.assault ? 4L : 2L) == 0L) {
            this.bars.tick();
        }

        if (this.now() % 20L == 0L) {
            this.watchdog();
        }
    }

    private void tickShooter(Combatant var1) {
        if (var1.kind != Combatant.Kind.KING_TOWER || var1.active) {
            if (this.now() >= var1.stunUntil) {
                double var2 = var1.kind == Combatant.Kind.KING_TOWER ? this.gm.kingRange : this.gm.princessRange;
                Combatant var4 = var1.target;
                Combatant var5 = this.nearest(var1, var1.fixed, var2, false);
                if (var4 != null && var4.alive() && var4.team != var1.team && !var4.hidden && this.inRange(var1, var1.fixed, var4, var2)) {
                    // 타워도 사거리 안의 대상을 죽을 때까지 계속 공격

                } else {
                    var4 = var5;
                }

                var1.target = var4;
                this.turnTop(var1, var4);
                if (var4 != null && this.now() >= var1.nextAttack) {
                    double var6 = var1.kind == Combatant.Kind.KING_TOWER ? this.gm.kingDmg : this.gm.princessDmg;
                    double var8 = var1.kind == Combatant.Kind.KING_TOWER ? this.gm.kingHit : this.gm.princessHit;
                    var1.nextAttack = this.now() + Math.max(1L, Math.round(var8 * 20.0));
                    boolean var10 = var1.kind == Combatant.Kind.KING_TOWER;

                    for (Entity var12 : var1.extras) {
                        this.gm.models.anim(var12, "attack");
                    }

                    Combatant var14 = var4;
                    this.fx
                        .shoot(
                            var10 ? Fx.Shot.CANNONBALL : Fx.Shot.BOLT, var1.fixed.clone().add(0.0, var10 ? 6.0 : 5.2, 0.0), () -> this.aim(var14), var6x -> {
                                this.fx.impact(var10 ? Fx.Shot.CANNONBALL : Fx.Shot.BOLT, var6x, 0.0);
                                this.damage(var14, var6, var1);
                            }
                        );
                }
            }
        }
    }

    private void tickBuilding(Combatant var1) {
        if (this.now() >= var1.expireAt) {
            this.kill(var1);
        } else {
            var1.hp = var1.hp - var1.maxHp / (var1.card.lifetime * 20.0);
            if (var1.hp <= 0.0) {
                this.kill(var1);
            } else {
                if (this.now() % 10L == 0L) {
                    this.refreshName(var1);
                }

                if (this.now() >= var1.deployUntil) {
                    if (this.now() >= var1.stunUntil) {
                        if (var1.card.elixirEvery > 0.0) {
                            // 엘릭서 정제소: 일정 시간마다 우리 팀 엘릭서
                            long every = Math.round(var1.card.elixirEvery * 20.0 / (this.now() < var1.rageUntil ? 1.0 + var1.rageBoost : 1.0));
                            if (var1.nextSpawn == 0L) {
                                var1.nextSpawn = this.now() + every;
                            }

                            if (this.now() >= var1.nextSpawn) {
                                var1.nextSpawn = this.now() + every;
                                this.giveElixir(var1.team, var1.card.elixirAmount, var1.fixed);
                                this.gm.models.anim(var1.mob, "attack");
                                this.A().world.playSound(var1.fixed, "block.bubble_column.upwards_inside", 1.0F, 1.2F);
                            }
                        }

                        if (var1.card.spawnEvery > 0.0) {
                            CardDef var2 = var1.card.spawnCard.isEmpty() ? null : this.gm.cards.get(var1.card.spawnCard);
                            if (var1.nextSpawn == 0L) {
                                var1.nextSpawn = this.now() + 20L;
                            }

                            if (var2 != null && this.now() >= var1.nextSpawn) {
                                boolean var3 = !var1.card.spawnWhenEnemy
                                    || this.nearest(var1, var1.fixed, var1.card.range, false) != null
                                    || this.anyEnemyNear(var1.team, var1.fixed, var1.card.range);
                                if (var3) {
                                    Location var4 = var1.fixed.clone().add(0.0, 0.0, var1.team.dir * (var1.card.size / 2.0 + 0.8));
                                    var4.setY(this.groundY());
                                    this.spawnAiGroup(var1.team, var2, var4, var1.card.spawnCount, 6);
                                    this.gm.models.anim(var1.mob, "attack");
                                    this.A().world.playSound(var4, "block.wooden_door.open", 0.8F, 0.9F);
                                    this.A().world.spawnParticle(Particle.POOF, var4.clone().add(0.0, 0.5, 0.0), 8, 0.4, 0.3, 0.4, 0.02);
                                }

                                double var14 = var1.card.spawnEvery * 20.0;
                                if (this.now() < var1.rageUntil) {
                                    var14 /= 1.0 + var1.rageBoost;
                                }

                                var1.nextSpawn = this.now() + (long)var14;
                            }

                            if (var1.card.damage <= 0.0) {
                                return;
                            }
                        }

                        Combatant var11 = var1.target;
                        Combatant var13 = this.nearest(var1, var1.fixed, var1.card.range, false);
                        if (var11 != null
                            && var11.alive()
                            && !var11.hidden
                            && this.canTarget(var1, var11)
                            && this.inRange(var1, var1.fixed, var11, var1.card.range)) {
                            // 건물도 사거리 안의 대상은 죽거나 나갈 때까지 계속 공격 (더 가까운 적이 와도 안 바꿈)
                        } else {
                            var11 = var13;
                        }

                        if (var11 != var1.target) {
                            var1.infernoTarget = null;
                        }

                        var1.target = var11;
                        if (var1.turret != null && var1.turret.isValid() && var11 != null) {
                            Location var15 = var11.loc();
                            if (var15 != null) {
                                Location var5 = var1.turret.getLocation();
                                Vector var6 = var15.toVector().subtract(var1.fixed.toVector()).setY(0.0);
                                if (var6.lengthSquared() > 1.0E-4) {
                                    float var7 = (float)Math.toDegrees(Math.atan2(-var6.getX(), var6.getZ()));
                                    float var8 = ((var7 - var5.getYaw()) % 360.0F + 540.0F) % 360.0F - 180.0F;
                                    float var9 = Math.max(-12.0F, Math.min(12.0F, var8));
                                    Location var10 = var1.fixed.clone();
                                    var10.setYaw(var5.getYaw() + var9);
                                    var10.setPitch(0.0F);
                                    var1.turret.teleport(var10);
                                }
                            }
                        }

                        if (var1.card.id.equals("tesla")) {
                            if (var11 != null) {
                                var1.lastSeenTarget = this.now();
                            }

                            boolean var16 = var11 == null && this.now() - var1.lastSeenTarget > 20L && this.now() - var1.lastDamaged > 60L;
                            if (var16 != var1.hidden && var1.mob != null) {
                                var1.hidden = var16;
                                Location var19 = var1.fixed.clone();
                                if (var1.modeled) {
                                    this.gm.models.animState(var1.mob, var1.hidden ? "retract" : "emerge", var1.hidden ? "emerge" : "retract");
                                } else {
                                    if (var1.hidden) {
                                        var19.add(0.0, -1.6, 0.0);
                                    }

                                    var1.mob.teleport(var19);
                                }

                                if (!var1.hidden) {
                                    var1.nextAttack = Math.max(var1.nextAttack, this.now() + 10L);
                                }

                                String var10002 = var1.hidden ? "block.piston.contract" : "block.piston.extend";
                                this.A().world.playSound(var19, var10002, 0.6F, var1.hidden ? 0.9F : 1.3F);
                                this.A()
                                    .world
                                    .spawnParticle(Particle.BLOCK, var19.clone().add(0.0, 0.2, 0.0), 14, 0.6, 0.05, 0.6, 0.0, Material.DIRT.createBlockData());
                            }
                        }

                        if (var11 != null && var1.card.damage > 0.0 && this.now() >= var1.nextAttack) {
                            var1.nextAttack = this.now() + this.hitTicks(var1);
                            double var17 = var1.card.damage;
                            if (!var1.card.damageStages.isEmpty()) {
                                if (var1.infernoTarget != var11) {
                                    var1.infernoTarget = var11;
                                    var1.infernoSince = this.now();
                                }

                                int var21 = (int)Math.min(
                                    (double)(var1.card.damageStages.size() - 1), (this.now() - var1.infernoSince) / (var1.card.stageSeconds * 20.0)
                                );
                                var17 = var1.card.damageStages.get(var21);
                                Color[] var22 = new Color[]{Color.fromRGB(255, 200, 60), Color.fromRGB(255, 120, 30), Color.fromRGB(255, 40, 20)};
                                Location var23 = this.aim(var11);
                                if (var23 != null) {
                                    this.fx
                                        .beam(
                                            var1.fixed.clone().add(0.0, 3.3, 0.0), var23, null, new DustOptions(var22[Math.min(2, var21)], 0.8F + var21 * 0.5F)
                                        );
                                    this.A().world.spawnParticle(Particle.FLAME, var23, 3 + var21 * 4, 0.2, 0.3, 0.2, 0.02);
                                }

                                if (this.now() % 10L == 0L) {
                                    this.A().world.playSound(var1.fixed, "block.fire.ambient", 0.8F, 0.6F + var21 * 0.3F);
                                }

                                this.gm.models.anim(var1.mob, "attack");
                                this.damage(var11, var17, var1);
                            } else if (var1.card.id.equals("tesla")) {
                                Location var20 = this.aim(var11);
                                if (var20 != null) {
                                    this.fx.lightning(var1.fixed.clone().add(0.0, var1.card.hitboxH * 0.85, 0.0), var20, true);
                                }

                                this.gm.models.anim(var1.mob, "attack");
                                this.damage(var11, var17, var1);
                                // 뇌전탑: 전기 공격이라 맞으면 잠깐 마비 (돌진·충전 초기화)
                                this.stun(var11, var1.card.stun);
                            } else {
                                this.gm.models.anim((Entity)(var1.turret != null ? var1.turret : var1.mob), "attack");
                                Location var24 = this.aim(var11);
                                Location var25 = var1.fixed.clone().add(0.0, 1.6, 0.0);
                                if (var24 != null) {
                                    var25.add(var24.toVector().subtract(var25.toVector()).setY(0.0).normalize().multiply(1.6));
                                }

                                final Combatant shotTarget = var11;
                                final double shotDmg = var17;
                                Fx.Shot bShot = Fx.Shot.CANNONBALL;
                                if (!var1.card.shot.isEmpty()) {
                                    try {
                                        bShot = Fx.Shot.valueOf(var1.card.shot);
                                    } catch (IllegalArgumentException ignored) {
                                    }
                                }

                                if (var1.card.shotHeight > 0.0) {
                                    var25.setY(var1.fixed.getY() + var1.card.shotHeight);
                                }

                                final Fx.Shot fShot = bShot;
                                this.fx.shoot(fShot, var25, () -> this.aim(shotTarget), var5x -> {
                                    this.fx.impact(fShot, var5x, var1.card.splash);
                                    if (this.gm.phase == GameManager.Phase.PLAYING) {
                                        this.splash(var1, shotTarget, var5x, shotDmg);
                                        this.damage(shotTarget, shotDmg, var1);
                                    }
                                });
                            }
                        }
                    }
                }
            }
        }
    }

    void setWalking(Combatant var1, Entity var2, boolean var3) {
        if (var1.walking != var3 && var2 != null) {
            var1.walking = var3;
            if (var3) {
                this.gm.models.animState(var2, "walk", null);
            } else {
                this.gm.models.stop(var2, "walk");
            }
        }
    }

    private void tickAi(Combatant var1) {
        if (var1.mob != null && var1.mob.isValid()) {
            if (this.now() < var1.dashUntil) {
                return;
            }

            // 지상 유닛이 다리 밖 강물에 들어가 있으면 (통 스폰·밀림 등) 가장 가까운 강둑/다리로 바로 빠져나옴
            if (!var1.air && (var1.card == null || !var1.card.riverJump)) {
                Location rl = var1.pendingMove != null ? var1.pendingMove : var1.mob.getLocation();
                Location out = this.riverExit(rl);
                if (out != null) {
                    var1.knockTicks = 0;
                    Vector rv = out.toVector().subtract(rl.toVector()).setY(0.0);
                    double rd = rv.length();
                    Location to = rd <= 0.45 ? out : rl.clone().add(rv.multiply(0.45 / rd));
                    to.setY(this.groundY());
                    to.setDirection(rv.lengthSquared() > 1.0E-6 ? rv : new Vector(0, 0, 1));
                    to.setPitch(0.0F);
                    var1.pendingMove = to;
                    var1.moveDx = to.getX() - rl.getX();
                    var1.moveDz = to.getZ() - rl.getZ();
                    var1.moveTick = this.now();
                    return;
                }
            }

            if (var1.knockTicks > 0) {
                var1.knockTicks--;
                Location kl = (var1.pendingMove != null ? var1.pendingMove : var1.mob.getLocation()).clone().add(var1.knockVx, 0.0, var1.knockVz);
                if (this.A().inField(kl) && (var1.air || !this.A().isRiverRow(this.A().tileZ(kl.getZ())) && !this.insideTowerBox(kl))) {
                    var1.pendingMove = kl;
                } else {
                    var1.knockTicks = 0;
                }
                return;
            }

            if (var1.walking && this.now() - var1.lastMoveTick > 3L) {
                this.setWalking(var1, var1.mob, false);
            }

            if (this.now() >= var1.deployUntil && this.now() >= var1.stunUntil) {
                Location var2 = var1.mob.getLocation();
                Combatant var3;
                if (this.gm.assault && (this.now() + var1.id) % 4L != 0L
                    && (var1.target == null || var1.target.alive() && !var1.target.hidden && this.canTarget(var1, var1.target))) {
                    var3 = var1.target;
                } else {
                    var3 = this.pickTarget(var1, var2);
                }
                var1.target = var3;
                if (this.specialMove(var1, var2, var3)) {
                    return;
                }
                if (var3 != null && this.inRange(var1, var2, var3, var1.kind == Combatant.Kind.BARREL ? 0.8 : var1.card.range)) {
                    this.face(var1, var2, var3.loc());
                    if (var1.kind == Combatant.Kind.BARREL) {
                        this.kill(var1);
                    } else {
                        if (this.now() >= var1.nextAttack) {
                            var1.nextAttack = this.now() + this.hitTicks(var1);
                            this.attack(var1, var3);
                        }
                    }
                } else {
                    Location var4;
                    if (var3 != null) {
                        var4 = var3.loc();
                    } else if (var1.leader != null && var1.leader.alive()) {
                        Location var5 = var1.leader.loc();
                        if (var5 == null || flat(var5, var2) <= this.gm.leash * 0.5) {
                            return;
                        }

                        var4 = var5;
                    } else {
                        var4 = this.laneGoal(var1, var2);
                    }

                    if (var4 != null) {
                        this.step(var1, var2, this.avoid(var1, var2, this.route(var1, var2, var4), var3));
                    }
                }
            }

            this.chargeIdleCheck(var1);
        } else {
            var1.dead = true;
        }
    }

    private Combatant pickTarget(Combatant var1, Location var2) {
        // 원작처럼 한 번 때리기 시작한 대상은 죽거나 사거리 밖으로 나갈 때까지 계속 공격 (스턴되면 타겟 초기화)
        Combatant lock = var1.target;
        if (lock != null && lock.alive() && !lock.hidden && this.canTarget(var1, lock)
            && this.inRange(var1, var2, lock, var1.kind == Combatant.Kind.BARREL ? 0.8 : var1.card.range)) {
            return lock;
        }
        boolean var3 = !this.gm.assault && (var1.kind == Combatant.Kind.BARREL || var1.card.targets == CardDef.Targets.BUILDINGS);
        Combatant var4;
        if (var3) {
            var4 = null;
            double var5 = Double.MAX_VALUE;

            for (Combatant var8 : this.all) {
                if (var8.alive() && var8.team != var1.team && var8.isStructure()) {
                    double var9 = this.edgeDist(var1, var2, var8, var8.loc());
                    if (var9 < var5) {
                        var5 = var9;
                        var4 = var8;
                    }
                }
            }
        } else {
            // 적 인식 거리 = 사거리 (히트박스 끝 ↔ 끝)
            var4 = this.nearest(var1, var2, var1.card.range, true);
            if (var4 == null && var1.leader != null && var1.leader.alive()) {
                Combatant var11 = var1.leader.lastHit;
                return var11 != null && var11.alive() && this.canTarget(var1, var11) ? var11 : null;
            }
        }

        return this.closer(var1.target, var4, var2, var1);
    }

    private Combatant closer(Combatant var1, Combatant var2, Location var3, Combatant var4) {
        if (var1 == null || !var1.alive() || var1.hidden || !this.canTarget(var4, var1)) {
            return var2;
        } else if (var2 != null && var2 != var1) {
            Location var5 = var1.loc();
            Location var6 = var2.loc();
            if (var5 == null) {
                return var2;
            } else if (var6 == null) {
                return var1;
            } else {
                double var7 = this.edgeDist(var4, var3, var1, var5);
                double var9 = this.edgeDist(var4, var3, var2, var6);
                return var9 < var7 - 0.6 ? var2 : var1;
            }
        } else {
            return var1;
        }
    }

    private boolean anyEnemyNear(TeamColor var1, Location var2, double var3) {
        for (Combatant var6 : this.all) {
            if (var6.alive() && var6.team != var1 && !var6.isTower() && !var6.hidden) {
                Location var7 = var6.loc();
                if (var7 != null && flat(var7, var2) - var6.radius <= var3) {
                    return true;
                }
            }
        }

        return false;
    }

    private Combatant nearest(Combatant var1, Location var2, double var3, boolean var5) {
        Combatant var6 = null;
        double var7 = Double.MAX_VALUE;

        for (Combatant var10 : this.all) {
            if (var10.alive() && var10.team != var1.team && !var10.hidden && this.canTarget(var1, var10)) {
                Location var11 = var10.loc();
                if (var11 != null) {
                    // 공격자 히트박스 끝 ↔ 대상 히트박스 끝 거리 (사거리·어그로 모두)
                    double var12 = this.edgeDist(var1, var2, var10, var11);
                    if (var12 <= var3 + 0.3 && var12 < var7) {
                        var7 = var12;
                        var6 = var10;
                    }
                }
            }
        }

        return var6;
    }

    boolean canTarget(Combatant var1, Combatant var2) {
        if (var2 != null && var2.alive() && var2.team != var1.team) {
            if (!var2.isTower() && this.now() < var2.deployUntil) {
                return false;
            } else if (var1.isTower()) {
                return true;
            } else if (var1.kind == Combatant.Kind.BARREL) {
                return this.gm.assault ? !var2.air : var2.isStructure();
            } else {
                CardDef.Targets var3 = var1.card.targets;
                if (var3 == CardDef.Targets.BUILDINGS) {
                    return this.gm.assault ? !var2.air : var2.isStructure();
                } else {
                    return var3 == CardDef.Targets.GROUND ? !var2.air : true;
                }
            }
        } else {
            return false;
        }
    }

    private boolean inRange(Combatant var1, Location var2, Combatant var3, double var4) {
        Location var6 = var3.loc();
        if (var2 != null && var6 != null) {
            // 사거리 = 공격자 히트박스 끝 ↔ 대상 히트박스 끝
            return this.edgeDist(var1, var2, var3, var6) <= var4 + 0.4;
        } else {
            return false;
        }
    }

    /** 히트박스 가장자리끼리 거리 (타워·건물 = 사각형, 유닛 = 원) */
    private double edgeDist(Combatant a, Location al, Combatant b, Location bl) {
        if (al == null || bl == null) {
            return Double.MAX_VALUE;
        }
        double[] ba = a != null && a.isStructure() ? this.structBox(a) : null;
        double[] bb = b.isStructure() ? this.structBox(b) : null;
        double ra = ba != null || a == null ? 0.0 : bodyRadius(a);
        double rb = bb != null ? 0.0 : bodyRadius(b);
        if (ba != null && bb != null) {
            double dx = Math.max(0.0, Math.max(ba[0] - bb[2], bb[0] - ba[2]));
            double dz = Math.max(0.0, Math.max(ba[1] - bb[3], bb[1] - ba[3]));
            return Math.sqrt(dx * dx + dz * dz);
        } else if (ba != null || bb != null) {
            double[] box = ba != null ? ba : bb;
            Location c = ba != null ? bl : al;
            double ex = Math.max(box[0] - c.getX(), Math.max(0.0, c.getX() - box[2]));
            double ez = Math.max(box[1] - c.getZ(), Math.max(0.0, c.getZ() - box[3]));
            return Math.max(0.0, Math.sqrt(ex * ex + ez * ez) - (ba != null ? rb : ra));
        } else {
            return Math.max(0.0, flat(al, bl) - ra - rb);
        }
    }

    private Location laneGoal(Combatant var1, Location var2) {
        if (this.gm.assault) {
            return this.hunt(var1, var2);
        }
        boolean var3 = var1.lane != null ? var1.lane : var2.getX() < this.A().centerX();
        TeamColor var4 = var1.team.other();
        Combatant var5 = this.tower(var4, Combatant.Kind.PRINCESS_TOWER, var3);
        if (var5 != null && var5.alive()) {
            return var5.fixed;
        } else {
            Combatant var6 = this.tower(var4, Combatant.Kind.KING_TOWER, false);
            return var6 != null && var6.alive() ? var6.fixed : null;
        }
    }

    private Location route(Combatant var1, Location var2, Location var3) {
        if (!var1.air && !var1.card.riverJump) {
            Location var4 = this.aroundKing(var1, var2, var3);
            if (var4 != null) {
                return var4;
            } else {
                double var5 = this.A().riverMinZ();
                double var7 = this.A().riverMaxZ();
                boolean var9 = var2.getZ() < var5;
                boolean var10 = var3.getZ() < var5;
                boolean var11 = var2.getZ() >= var7;
                boolean var12 = var3.getZ() >= var7;
                boolean var13 = !var9 && !var11;
                if ((!var9 || !var10) && (!var11 || !var12)) {
                    boolean var14 = var1.lane != null && var1.target == null ? var1.lane : var2.getX() < this.A().centerX();
                    double var15 = this.A().bridgeX(var14);
                    double var17 = this.A().bridgeHalf() - 0.6;
                    double var19 = Math.max(var15 - var17, Math.min(var15 + var17, var2.getX()));
                    if (var13) {
                        return new Location(this.A().world, var19, this.groundY(), var10 ? var5 - 1.0 : var7 + 1.0);
                    } else {
                        double var21 = var9 ? var5 - 0.8 : var7 + 0.8;
                        return !(Math.abs(var2.getX() - var15) > var17) && !(Math.abs(var2.getZ() - var21) > 1.2)
                            ? new Location(this.A().world, var19, this.groundY(), var9 ? var7 + 1.0 : var5 - 1.0)
                            : new Location(this.A().world, var19 == var2.getX() ? var2.getX() : var15, this.groundY(), var21);
                    }
                } else {
                    return var3;
                }
            }
        } else {
            return var3;
        }
    }

    // ===================== 3.5.0 새 카드 기능 =====================

    /** 얼음 마법사: 맞은 적 감속 */
    private void hitSlow(Combatant src, Combatant t) {
        if (src.card == null || src.card.hitSlow <= 0.0 || t == null || !t.alive()) {
            return;
        }

        this.slow(t, src.card.hitSlow, (int)Math.round(src.card.hitSlowDuration * 20.0));
        Location l = t.loc();
        if (l != null && !t.isTower()) {
            this.A().world.spawnParticle(Particle.SNOWFLAKE, l.clone().add(0.0, 1.0, 0.0), 8, 0.3, 0.4, 0.3, 0.01);
        }
    }

    /** 발키리 회전 베기 효과 */
    private void spinFx(Location c, double r) {
        World w = this.A().world;
        double rr = Math.max(1.0, r);
        for (int i = 0; i < 12; i++) {
            double a = Math.PI * 2.0 * i / 12.0;
            w.spawnParticle(Particle.SWEEP_ATTACK, c.getX() + Math.cos(a) * rr * 0.7, c.getY() + 1.0, c.getZ() + Math.sin(a) * rr * 0.7, 1, 0.0, 0.0, 0.0, 0.0);
        }

        w.playSound(c, "entity.player.attack.sweep", 1.0F, 0.7F);
    }

    /** 땅 찍기 (메가 나이트 소환 / 점프): 지상 범위 피해 + 살짝 밀침 */
    /** 메가 나이트 등장: 떨어지는 동안 위에서 내려오는 불꽃·연기 줄기 + 바닥에 착지 표시 */
    private void megaFall(Location at, int ticks) {
        World w = this.A().world;
        Location g = at.clone();
        g.setY(this.groundY());
        int n = Math.max(2, ticks - 4);
        w.playSound(g, "entity.ender_dragon.flap", 1.4F, 0.6F);
        for (int i = 0; i < n; i++) {
            final double k = 1.0 - (double)i / n;
            this.fx.later(i, () -> {
                if (this.gm.phase != GameManager.Phase.PLAYING) {
                    return;
                }
                Location p = g.clone().add(0.0, 1.0 + k * 9.0, 0.0);
                w.spawnParticle(Particle.FLAME, p, 10, 0.35, 0.5, 0.35, 0.02);
                w.spawnParticle(Particle.LARGE_SMOKE, p, 5, 0.3, 0.4, 0.3, 0.01);
                w.spawnParticle(Particle.DUST, g.clone().add(0.0, 0.15, 0.0), 12, 1.2, 0.0, 1.2, 0.0, new DustOptions(Color.fromRGB(60, 60, 70), 1.6F));
            });
        }
    }

    /** 메가 나이트 착지: 크게 튀는 폭발 + 퍼지는 충격파 고리 + 흙·돌 파편 + 묵직한 소리 */
    private void megaLandFx(Location at, double r) {
        World w = this.A().world;
        Location g = at.clone();
        g.setY(this.groundY());
        double rr = Math.max(1.5, r);
        w.spawnParticle(Particle.EXPLOSION_EMITTER, g.clone().add(0.0, 0.5, 0.0), 1, 0.0, 0.0, 0.0, 0.0);
        w.spawnParticle(Particle.EXPLOSION, g.clone().add(0.0, 0.6, 0.0), 10, rr / 2.0, 0.3, rr / 2.0, 0.0);
        w.spawnParticle(Particle.BLOCK, g.clone().add(0.0, 0.5, 0.0), 160, rr / 1.6, 0.6, rr / 1.6, 0.4, Material.STONE.createBlockData());
        w.spawnParticle(Particle.BLOCK, g.clone().add(0.0, 0.5, 0.0), 120, rr / 1.6, 0.6, rr / 1.6, 0.4, Material.DIRT.createBlockData());
        w.spawnParticle(Particle.LAVA, g.clone().add(0.0, 0.5, 0.0), 14, rr / 3.0, 0.3, rr / 3.0, 0.0);
        w.spawnParticle(Particle.FLAME, g.clone().add(0.0, 0.3, 0.0), 80, rr / 2.0, 0.2, rr / 2.0, 0.12);
        w.spawnParticle(Particle.CAMPFIRE_COSY_SMOKE, g.clone().add(0.0, 0.4, 0.0), 25, rr / 2.0, 0.2, rr / 2.0, 0.03);
        w.playSound(g, "entity.generic.explode", 2.0F, 0.5F);
        w.playSound(g, "item.mace.smash_ground_heavy", 2.0F, 0.8F);
        w.playSound(g, "entity.iron_golem.damage", 1.5F, 0.5F);
        w.playSound(g, "entity.warden.sonic_boom", 0.7F, 1.4F);
        // 충격파: 3번 퍼지는 고리
        for (int i = 0; i < 4; i++) {
            final double rad = rr * (0.5 + i * 0.4);
            this.fx.later(i * 2L, () -> {
                if (this.gm.phase != GameManager.Phase.PLAYING) {
                    return;
                }
                this.fx.ring(g, rad, Color.fromRGB(255, 170, 60));
                int pts = (int)Math.max(16, rad * 10);
                for (int q = 0; q < pts; q++) {
                    double a = Math.PI * 2 * q / pts;
                    w.spawnParticle(Particle.CLOUD, g.clone().add(Math.cos(a) * rad, 0.2, Math.sin(a) * rad), 1, 0.0, 0.05, 0.0, 0.02);
                }
            });
        }
    }

    private void slamAt(TeamColor team, Location at, double r, double dmg, float vol) {
        if (this.gm.phase != GameManager.Phase.PLAYING) {
            return;
        }

        World w = this.A().world;
        Location g = at.clone();
        g.setY(this.groundY());
        double rr = Math.max(1.0, r);
        w.spawnParticle(Particle.EXPLOSION, g.clone().add(0.0, 0.4, 0.0), 3, rr / 3.0, 0.1, rr / 3.0, 0.0);
        w.spawnParticle(Particle.BLOCK, g.clone().add(0.0, 0.3, 0.0), 60, rr / 2.0, 0.2, rr / 2.0, 0.0, Material.DIRT.createBlockData());
        w.spawnParticle(Particle.CLOUD, g.clone().add(0.0, 0.3, 0.0), 30, rr / 2.0, 0.1, rr / 2.0, 0.05);
        this.fx.ring(g, rr, Color.fromRGB(90, 90, 110));
        w.playSound(g, "entity.generic.explode", vol, 0.6F);
        w.playSound(g, "block.anvil.land", vol * 0.8F, 0.5F);
        for (Combatant c : this.area(g, rr, team.other(), true, false)) {
            this.damage(c, dmg, null);
            if (!c.isStructure()) {
                this.knockback(c, g, 1.0);
            }
        }
    }

    /** 강을 사이에 두고 있는지 (대시·점프로 강은 못 넘음) */
    private boolean acrossRiver(Location a, Location b) {
        double mid = (this.A().riverMinZ() + this.A().riverMaxZ()) / 2.0;
        boolean sa = a.getZ() < this.A().riverMinZ(), sb = b.getZ() < this.A().riverMinZ();
        boolean na = a.getZ() > this.A().riverMaxZ(), nb = b.getZ() > this.A().riverMaxZ();
        return (sa && !sb) || (na && !nb) || (a.getZ() - mid) * (b.getZ() - mid) < 0.0;
    }

    /** 도둑 대시 / 메가 나이트 점프: 사거리 사이에 대상이 있으면 날아가서 공격. 했으면 true */
    private boolean specialMove(Combatant c, Location from, Combatant t) {
        CardDef d = c.card;
        if (t == null || d == null || c.isPlayer() || c.mob == null || this.now() < c.nextSpecial || this.now() < c.stunUntil) {
            return false;
        }

        boolean dash = d.dash;
        boolean jump = !dash && d.jumpMax > 0.0;
        if (!dash && !jump || t.air || !t.alive()) {
            return false;
        }

        Location tl = t.loc();
        if (tl == null || this.acrossRiver(from, tl)) {
            return false;
        }

        double dist = flat(from, tl) - t.radius;
        double mn = dash ? d.dashMin : d.jumpMin;
        double mx = dash ? d.dashMax : d.jumpMax;
        if (dist < mn || dist > mx) {
            return false;
        }

        long dur = dash ? 8L : 18L;
        c.dashUntil = this.now() + dur;
        c.nextSpecial = this.now() + dur + (dash ? 30L : 40L);
        this.setWalking(c, c.mob, false);
        this.gm.models.anim(c.mob, dash ? "dash" : "jump");
        if (dash) {
            // 도둑 은신 질주: 대시하는 동안 모습이 사라지고 보라 연기만 남음 (무적)
            this.gm.models.visible(c.mob, false);
            this.A().world.spawnParticle(Particle.LARGE_SMOKE, from.clone().add(0.0, 0.8, 0.0), 14, 0.3, 0.5, 0.3, 0.02);
            this.A().world.playSound(from, "entity.illusioner.mirror_move", 0.8F, 1.4F);
        }
        Vector dir = tl.toVector().subtract(from.toVector()).setY(0.0);
        double len = dir.length();
        dir.multiply(1.0 / Math.max(1.0E-4, len));
        double stop = Math.max(0.0, len - (t.isStructure() ? 0.5 : t.radius + bodyRadius(c)));
        double[] box = t.isStructure() ? this.structBox(t) : null;
        if (box != null) {
            // 타워·건물: 밀려나지 않게 벽 바로 앞에서 멈춤
            double enter = rayBoxEnter(from.getX(), from.getZ(), dir.getX(), dir.getZ(), box);
            if (enter >= 0.0) {
                stop = Math.max(0.0, enter - bodyRadius(c) - 0.15);
            }
        }
        Location start = from.clone();
        Location end = from.clone().add(dir.clone().multiply(stop));
        end.setY(this.groundY());
        World w = this.A().world;
        w.playSound(from, dash ? "entity.phantom.flap" : "entity.ravager.roar", 0.8F, dash ? 1.6F : 1.2F);
        BukkitRunnable r = new BukkitRunnable() {
            int i = 0;

            public void run() {
                if (Battle.this.gm.phase != GameManager.Phase.PLAYING || !c.alive() || c.mob == null || !c.mob.isValid()) {
                    this.cancel();
                    Battle.this.running.remove(this);
                    if (dash && c.mob != null && c.mob.isValid()) {
                        Battle.this.gm.models.visible(c.mob, true);
                    }
                    return;
                }

                this.i++;
                double k = Math.min(1.0, (double)this.i / dur);
                Location p = start.clone().add(end.toVector().subtract(start.toVector()).multiply(k));
                p.setY(Battle.this.groundY() + (dash ? 0.0 : Math.sin(Math.PI * k) * 3.5));
                p.setDirection(dir);
                p.setPitch(0.0F);
                c.mob.teleport(p);
                if (dash) {
                    w.spawnParticle(Particle.DUST, p.clone().add(0.0, 0.9, 0.0), 8, 0.25, 0.5, 0.25, 0.0, new DustOptions(Color.fromRGB(170, 90, 230), 1.3F));
                    w.spawnParticle(Particle.SMOKE, p.clone().add(0.0, 0.6, 0.0), 4, 0.2, 0.3, 0.2, 0.01);
                    w.spawnParticle(Particle.CLOUD, p.clone().add(0.0, 0.1, 0.0), 1, 0.1, 0.0, 0.1, 0.01);
                } else {
                    w.spawnParticle(Particle.LARGE_SMOKE, p.clone().add(0.0, 0.5, 0.0), 2, 0.3, 0.2, 0.3, 0.01);
                }

                if (this.i >= dur) {
                    this.cancel();
                    Battle.this.running.remove(this);
                    c.nextAttack = Battle.this.now() + Battle.this.hitTicks(c);
                    if (dash) {
                        Battle.this.gm.models.visible(c.mob, true);
                        w.spawnParticle(Particle.LARGE_SMOKE, p.clone().add(0.0, 0.8, 0.0), 10, 0.3, 0.5, 0.3, 0.02);
                        if (t.alive()) {
                            Battle.this.gm.models.anim(c.mob, "attack");
                            w.playSound(p, "entity.player.attack.strong", 1.0F, 0.8F);
                            w.spawnParticle(Particle.CRIT, p.clone().add(0.0, 1.0, 0.0), 12, 0.4, 0.4, 0.4, 0.2);
                            Battle.this.damage(t, d.dashDamage > 0.0 ? d.dashDamage : d.damage, c);
                        }
                    } else {
                        Battle.this.slamAt(c.team, p, d.spawnRadius > 0.0 ? d.spawnRadius : 3.0, d.jumpDamage, 1.0F);
                    }
                }
            }
        };
        this.running.add(r);
        r.runTaskTimer(this.gm.plugin, 1L, 1L);
        return true;
    }

    /** 사냥꾼 산탄: 부채꼴로 여러 발, 가까울수록 많이 맞음 */
    private void hunterShot(Combatant src, Combatant tgt, Location from, double perPellet) {
        Location tl = this.aim(tgt);
        if (tl == null) {
            return;
        }

        CardDef d = src.card;
        World w = this.A().world;
        Vector base = tl.toVector().subtract(from.toVector()).setY(0.0);
        if (base.lengthSquared() < 1.0E-4) {
            base = new Vector(0, 0, src.team.dir);
        }

        base.normalize();
        double range = d.range + 1.0;
        java.util.Map<Combatant, Integer> hits = new java.util.HashMap<>();
        int n = d.pellets;
        for (int i = 0; i < n; i++) {
            double ang = Math.toRadians(-14.0 + 28.0 * i / Math.max(1, n - 1) + (this.gm.rng.nextDouble() - 0.5) * 3.0);
            double cs = Math.cos(ang), sn = Math.sin(ang);
            Vector v = new Vector(base.getX() * cs - base.getZ() * sn, 0.0, base.getX() * sn + base.getZ() * cs);
            Combatant hit = null;
            double hitAt = range;
            for (Combatant e : this.all) {
                if (!e.alive() || e.hidden || !this.canTarget(src, e)) {
                    continue;
                }

                Location el = e.loc();
                if (el == null) {
                    continue;
                }

                double ex = el.getX() - from.getX(), ez = el.getZ() - from.getZ();
                double along = ex * v.getX() + ez * v.getZ();
                if (along <= 0.0 || along > hitAt) {
                    continue;
                }

                double side = Math.abs(ex * v.getZ() - ez * v.getX());
                double rad = e.isTower() ? e.towerTiles * 1.5 : e.radius + 0.35;
                if (side <= rad) {
                    hit = e;
                    hitAt = along;
                }
            }

            for (double s = 0.6; s < hitAt; s += 0.9) {
                w.spawnParticle(Particle.CRIT, from.clone().add(v.clone().multiply(s)), 1, 0.02, 0.02, 0.02, 0.0);
            }

            if (hit != null) {
                hits.merge(hit, 1, Integer::sum);
            }
        }

        w.spawnParticle(Particle.EXPLOSION, from.clone().add(base.clone().multiply(0.8)), 1, 0.0, 0.0, 0.0, 0.0);
        w.spawnParticle(Particle.SMOKE, from.clone().add(base.clone().multiply(0.8)), 10, 0.15, 0.15, 0.15, 0.03);
        w.playSound(from, "entity.generic.explode", 0.7F, 1.7F);
        for (java.util.Map.Entry<Combatant, Integer> e : hits.entrySet()) {
            this.damage(e.getKey(), perPellet * e.getValue(), src);
        }
    }

    /** 일직선 관통 공격: 볼러 바위 / 도끼맨 도끼(갔다 돌아옴) / 마법 아처 화살 */
    private void lineAttack(Combatant src, Combatant tgt, Location from, double dmg) {
        CardDef d = src.card;
        Location tl = this.aim(tgt);
        if (tl == null) {
            return;
        }

        Vector dir = tl.toVector().subtract(from.toVector()).setY(0.0);
        if (dir.lengthSquared() < 1.0E-4) {
            return;
        }

        double dist = dir.length() + Math.max(1.0, d.pierceExtra);
        if (d.axe) {
            dist = Math.max(dist, d.range);
        }

        dir.normalize();
        boolean hitAir = !d.roll && d.targets != CardDef.Targets.GROUND;
        double speed = d.roll ? 0.4 : (d.axe ? 0.55 : 1.3);
        double half = d.roll ? 1.0 : (d.axe ? 1.0 : 0.6);
        World w = this.A().world;
        Location start = from.clone();
        if (d.roll) {
            start.setY(this.groundY());
        }

        ArmorStand rock = null;
        // 도끼맨: 던지는 순간(공격 모션 0.25초) 손의 도끼를 숨기고 도끼 모델을 날림 → 돌아오면 다시 손에
        org.bukkit.entity.Entity body = src.playerId != null ? src.player() : src.mob;
        if (d.axe && body != null) {
            this.gm.models.part(body, "axe", false);
        }
        if ((d.roll || d.axe) && this.gm.models.enabled() && !d.projectileModel.isEmpty()) {
            ArmorStand st = (ArmorStand)w.spawn(start.clone(), ArmorStand.class);
            st.addScoreboardTag("clashmc");
            stand(st, true);
            st.addScoreboardTag("clashmc_nohit");
            if (this.gm.models.apply(st, d.projectileModel, true, src.team.color)) {
                this.gm.models.anim(st, d.roll ? "roll" : "spin");
                this.fx.track(st);
                rock = st;
            } else {
                st.remove();
            }
        }

        ArmorStand frock = rock;
        double fdist = dist;
        BukkitRunnable r = new BukkitRunnable() {
            double s = 0.0;
            boolean back = false;
            Location pos = start.clone();
            final Set<Integer> hit = new HashSet<>();

            public void run() {
                if (Battle.this.gm.phase != GameManager.Phase.PLAYING) {
                    this.finish();
                    return;
                }

                if (!this.back) {
                    this.s += speed;
                    this.pos = start.clone().add(dir.clone().multiply(Math.min(this.s, fdist)));
                    if (this.s >= fdist) {
                        if (d.axe && src.alive()) {
                            this.back = true;
                            this.hit.clear();
                        } else {
                            this.finish();
                            return;
                        }
                    }
                } else {
                    Location home = src.loc();
                    if (home == null) {
                        this.finish();
                        return;
                    }

                    home = home.clone().add(0.0, d.hitboxH * 0.6, 0.0);
                    Vector to = home.toVector().subtract(this.pos.toVector()).setY(0.0);
                    if (to.length() <= speed * 1.2) {
                        this.finish();
                        return;
                    }

                    this.pos.add(to.normalize().multiply(speed));
                }

                // 효과
                if (d.roll) {
                    if (frock != null && frock.isValid()) {
                        Location rp = this.pos.clone();
                        rp.setDirection(dir);
                        rp.setPitch(0.0F);
                        frock.teleport(rp);
                    } else {
                        w.spawnParticle(Particle.BLOCK, this.pos.clone().add(0.0, 0.5, 0.0), 6, 0.4, 0.4, 0.4, 0.0, Material.COBBLESTONE.createBlockData());
                    }

                    w.spawnParticle(Particle.BLOCK, this.pos.clone().add(0.0, 0.1, 0.0), 3, 0.4, 0.05, 0.4, 0.0, Material.DIRT.createBlockData());
                } else if (d.axe) {
                    if (frock != null && frock.isValid()) {
                        frock.teleport(this.pos.clone().add(0.0, -0.5, 0.0));
                    } else {
                        w.spawnParticle(Particle.SWEEP_ATTACK, this.pos, 1, 0.0, 0.0, 0.0, 0.0);
                    }
                    w.spawnParticle(Particle.CRIT, this.pos, 3, 0.2, 0.2, 0.2, 0.05);
                    if ((int)(this.s * 2) % 3 == 0) {
                        w.playSound(this.pos, "entity.player.attack.sweep", 0.4F, 1.4F);
                    }
                } else {
                    w.spawnParticle(Particle.END_ROD, this.pos, 2, 0.05, 0.05, 0.05, 0.0);
                    w.spawnParticle(Particle.DUST, this.pos, 3, 0.1, 0.1, 0.1, 0.0, new DustOptions(Color.fromRGB(80, 230, 220), 1.2F));
                }

                // 닿은 적
                for (Combatant e : new ArrayList<>(Battle.this.all)) {
                    if (!e.alive() || e.hidden || e.team == src.team || this.hit.contains(e.id) || (e.air && !hitAir)) {
                        continue;
                    }

                    boolean touch;
                    double[] b = Battle.this.structBox(e);
                    if (b != null) {
                        touch = this.pos.getX() > b[0] - half && this.pos.getX() < b[2] + half && this.pos.getZ() > b[1] - half && this.pos.getZ() < b[3] + half;
                    } else {
                        Location el = e.loc();
                        touch = el != null && flat(el, this.pos) <= half + e.radius;
                    }

                    if (touch) {
                        this.hit.add(e.id);
                        Battle.this.damage(e, e.isTower() && d.towerDamage > 0.0 ? d.towerDamage : dmg, src);
                        if (d.roll && e.kind == Combatant.Kind.TROOP) {
                            Battle.this.knockback(e, this.pos.clone().add(dir.clone().multiply(-1.0)), Math.max(3.0, d.knockback)); // 볼러: 최소 1타일 밀침 (예전 config 1.0 이어도)
                        }
                    }
                }
            }

            void finish() {
                this.cancel();
                Battle.this.running.remove(this);
                if (d.axe && body != null && body.isValid()) {
                    Battle.this.gm.models.part(body, "axe", true);
                }
                if (frock != null) {
                    Battle.this.gm.models.remove(frock);
                    Battle.this.fx.untrack(frock);
                    frock.remove();
                }
            }
        };
        this.running.add(r);
        r.runTaskTimer(this.gm.plugin, 0L, 1L);
        w.playSound(from, d.roll ? "entity.iron_golem.attack" : (d.axe ? "item.trident.throw" : "entity.arrow.shoot"), 0.9F, d.pierce ? 1.5F : 0.9F);
    }

    /** 마법사 불꽃 줄기: 손 → 대상까지 불꽃 파티클이 날아가서 범위 폭발 */
    private void flameStream(Combatant src, Combatant tgt, Location from, double dmg) {
        Location to0 = this.aim(tgt);
        if (to0 == null) {
            return;
        }

        World w = this.A().world;
        Vector dir0 = to0.toVector().subtract(from.toVector());
        if (dir0.lengthSquared() > 1.0E-4) {
            from.add(dir0.clone().normalize().multiply(0.5));
        }

        w.playSound(from, "entity.blaze.shoot", 0.7F, 1.3F);
        w.spawnParticle(Particle.FLAME, from, 8, 0.12, 0.12, 0.12, 0.03);
        int steps = Math.max(3, (int)Math.round(from.distance(to0) / 1.4));
        for (int i = 1; i <= steps; i++) {
            final int step = i;
            this.fx.later(i, () -> {
                if (this.gm.phase != GameManager.Phase.PLAYING) {
                    return;
                }

                Location to = tgt.alive() && this.aim(tgt) != null ? this.aim(tgt) : to0;
                double t = (double)step / steps;
                Vector seg = to.toVector().subtract(from.toVector());
                double prevT = (double)(step - 1) / steps;
                for (int k = 0; k < 4; k++) {
                    double tt = prevT + (t - prevT) * k / 3.0;
                    Location p = from.clone().add(seg.clone().multiply(tt));
                    w.spawnParticle(Particle.FLAME, p, 2, 0.06, 0.06, 0.06, 0.005);
                    w.spawnParticle(Particle.SMALL_FLAME, p, 1, 0.08, 0.08, 0.08, 0.0);
                }

                w.spawnParticle(Particle.DUST, from.clone().add(seg.clone().multiply(t)), 2, 0.1, 0.1, 0.1, 0.0, new DustOptions(Color.fromRGB(255, 140, 30), 1.4F));
                if (step == steps) {
                    double sp = Math.max(1.0, src.card.splash);
                    w.spawnParticle(Particle.FLAME, to, 30, sp / 3.0, 0.3, sp / 3.0, 0.04);
                    w.spawnParticle(Particle.LAVA, to, 3, 0.3, 0.2, 0.3, 0.0);
                    w.spawnParticle(Particle.SMOKE, to, 8, 0.3, 0.2, 0.3, 0.02);
                    w.playSound(to, "entity.generic.burn", 0.8F, 1.1F);
                    this.splash(src, tgt, to, dmg);
                    if (tgt.alive()) {
                        this.damage(tgt, dmg, src);
                    }
                }
            });
        }
    }

    /** 얼음 마법사: 손에서 눈발이 날아가 맞은 자리에 냉기 폭발 (범위 피해 + 감속) */
    private void snowStream(Combatant src, Combatant tgt, Location from, double dmg) {
        Location to0 = this.aim(tgt);
        if (to0 == null) {
            return;
        }

        World w = this.A().world;
        Vector dir0 = to0.toVector().subtract(from.toVector());
        if (dir0.lengthSquared() > 1.0E-4) {
            from.add(dir0.clone().normalize().multiply(0.5));
        }

        w.playSound(from, "entity.snowball.throw", 0.8F, 0.7F);
        w.spawnParticle(Particle.SNOWFLAKE, from, 8, 0.1, 0.1, 0.1, 0.03);
        int steps = Math.max(3, (int)Math.round(from.distance(to0) / 1.3));
        for (int i = 1; i <= steps; i++) {
            final int step = i;
            this.fx.later(i, () -> {
                if (this.gm.phase != GameManager.Phase.PLAYING) {
                    return;
                }

                Location to = tgt.alive() && this.aim(tgt) != null ? this.aim(tgt) : to0;
                double t = (double)step / steps;
                double prevT = (double)(step - 1) / steps;
                Vector seg = to.toVector().subtract(from.toVector());
                for (int k = 0; k < 3; k++) {
                    double tt = prevT + (t - prevT) * k / 2.0;
                    Location p = from.clone().add(seg.clone().multiply(tt)).add(0.0, Math.sin(Math.PI * tt) * 0.5, 0.0);
                    w.spawnParticle(Particle.ITEM_SNOWBALL, p, 2, 0.05, 0.05, 0.05, 0.0);
                    w.spawnParticle(Particle.SNOWFLAKE, p, 1, 0.08, 0.08, 0.08, 0.0);
                }

                if (step == steps) {
                    double sp = Math.max(1.0, src.card.splash);
                    w.spawnParticle(Particle.SNOWFLAKE, to, 26, sp / 3.0, 0.3, sp / 3.0, 0.03);
                    w.spawnParticle(Particle.ITEM_SNOWBALL, to, 14, sp / 4.0, 0.2, sp / 4.0, 0.05);
                    w.spawnParticle(Particle.DUST, to, 10, sp / 3.0, 0.2, sp / 3.0, 0.0, new DustOptions(Color.fromRGB(200, 240, 255), 1.4F));
                    w.playSound(to, "block.powder_snow.break", 0.9F, 1.0F);
                    this.splash(src, tgt, to, dmg);
                    if (tgt.alive()) {
                        this.damage(tgt, dmg, src);
                        this.hitSlow(src, tgt);
                    }
                }
            });
        }
    }

    /** 소환 직후 공통 설정: 실드, 스파키 충전, 유닛 소환 타이머 */
    private void initUnit(Combatant c) {
        CardDef d = c.card;
        if (d == null) {
            return;
        }

        c.shield = c.maxShield = d.shield;
        if (d.stunResetsCharge) {
            c.nextAttack = c.deployUntil + d.hitTicks();
        }

        if (!d.spawnCard.isEmpty() && d.spawnEvery > 0.0) {
            c.nextSpawn = c.deployUntil + Math.round(d.spawnFirst * 20.0);
        }
    }

    /** 매 틱: 스파키 충전 표시, 마녀/암흑 마녀 소환 */
    private void tickTroopExtras(Combatant c) {
        CardDef d = c.card;
        if (d == null || c.kind != Combatant.Kind.TROOP) {
            return;
        }

        long now = this.now();
        if (c.isPlayer() && now % 20L == 0L) {
            Player pu = c.player();
            if (pu != null) {
                this.playerUnitBody(c, pu);
            }
        }
        this.deployTimer(c);
        this.stunFx(c);
        this.snareFx(c);
        if (d.reflectDamage > 0.0) {
            this.tickReflect(c);
            // 반사 범위(2.5타일): 마법 장판처럼 연한 하늘색 바닥 + 진한 테두리 (탑뷰에서도 보임), 자이언트를 따라다님
            Location gl = c.loc();
            if (gl != null) {
                if (c.zoneDisc == null) {
                    c.zoneDisc = this.fx.floorDisc(gl, d.reflectRange + c.radius, Material.LIGHT_BLUE_STAINED_GLASS, 0.02F);
                    for (org.bukkit.entity.BlockDisplay bd : c.zoneDisc) {
                        bd.setTeleportDuration(2);
                    }
                    c.zoneAnchor = gl.clone();
                } else if (now % 2L == 0L) {
                    double dx = gl.getX() - c.zoneAnchor.getX(), dz = gl.getZ() - c.zoneAnchor.getZ();
                    if (dx * dx + dz * dz > 1.0E-4) {
                        for (org.bukkit.entity.BlockDisplay bd : c.zoneDisc) {
                            if (bd.isValid()) {
                                bd.teleport(bd.getLocation().add(dx, 0.0, dz));
                            }
                        }
                        c.zoneAnchor = gl.clone();
                    }
                }
                if (now % 4L == 0L) {
                    this.fx.edge(gl, d.reflectRange + c.radius, Color.fromRGB(70, 190, 255));
                }
            }
        }
        if (d.bolaDamage > 0.0 && now >= c.deployUntil && now >= c.nextBola && now >= c.stunUntil) {
            this.throwBola(c);
        }
        if (c.cursedBy != null && now < c.cursedUntil && now % 8L == 0L) {
            Location cl = c.loc();
            if (cl != null) {
                this.A().world.spawnParticle(Particle.WITCH, cl.clone().add(0.0, c.card.hitboxH + 0.2, 0.0), 3, 0.25, 0.1, 0.25, 0.0);
            }
        }
        if (d.stunResetsCharge && now >= c.deployUntil) {
            Location l = c.loc();
            if (l != null) {
                long left = c.nextAttack - now;
                Entity body = c.isPlayer() ? c.player() : c.mob;
                if (left == 20L && body != null) {
                    this.gm.models.anim(body, "charge");
                    this.A().world.playSound(l, "block.beacon.power_select", 0.6F, 1.8F);
                }

                Location coil = l.clone().add(0.0, d.hitboxH * 0.8, 0.0);
                World cw = this.A().world;
                if (left <= 0L) {
                    // 충전 완료: 코일 주위로 번개가 튐 + 하늘색 빛
                    if (now % 2L == 0L) {
                        cw.spawnParticle(Particle.ELECTRIC_SPARK, coil, 6, 0.35, 0.3, 0.35, 0.08);
                        cw.spawnParticle(Particle.DUST, coil, 3, 0.3, 0.25, 0.3, 0.0, new DustOptions(Color.fromRGB(120, 230, 255), 1.6F));
                    }

                    if (now % 6L == 0L) {
                        cw.spawnParticle(Particle.END_ROD, coil.clone().add(0.0, 0.4, 0.0), 2, 0.15, 0.15, 0.15, 0.02);
                    }

                    if (now % 20L == 0L) {
                        cw.playSound(coil, "block.beacon.ambient", 0.5F, 2.0F);
                    }
                } else {
                    // 충전 중: 코일 둘레로 도는 전기 고리, 충전될수록 빨라지고 많아짐
                    double prog = 1.0 - Math.max(0.0, Math.min(1.0, (double)left / Math.max(1, d.hitTicks())));
                    int n = 1 + (int)Math.round(prog * 3.0);
                    double ang = now * (0.25 + prog * 0.5);
                    double rr = 0.55 - prog * 0.2;
                    DustOptions cd = new DustOptions(Color.fromRGB((int)(60 + 120 * prog), (int)(140 + 100 * prog), 255), 0.8F + (float)prog);
                    for (int k = 0; k < n; k++) {
                        double a = ang + k * Math.PI * 2.0 / n;
                        cw.spawnParticle(Particle.DUST, coil.getX() + Math.cos(a) * rr, coil.getY() + (k % 2 == 0 ? 0.1 : -0.1), coil.getZ() + Math.sin(a) * rr, 1, 0.0, 0.0, 0.0, 0.0, cd);
                    }

                    if (now % Math.max(2L, 10L - (long)(prog * 8.0)) == 0L) {
                        cw.spawnParticle(Particle.ELECTRIC_SPARK, coil, 1 + (int)(prog * 3.0), 0.2, 0.15, 0.2, 0.02);
                    }

                    if (now % 10L == 0L) {
                        cw.playSound(coil, "block.beacon.ambient", 0.25F, 0.8F + (float)prog);
                    }
                }

                if (c.isPlayer() && now % 5L == 0L) {
                    Player p = c.player();
                    if (p != null && !d.charge) {
                        int total = Math.max(1, d.hitTicks());
                        int bars = (int)Math.max(0L, Math.min(10L, 10L - left * 10L / total));
                        p.sendActionBar(left <= 0L ? "§b§l⚡ 충전 완료!" : "§7충전 §b" + "▮".repeat(bars) + "§8" + "▮".repeat(10 - bars));
                    }
                }
            }
        }

        if (!d.spawnCard.isEmpty() && d.spawnEvery > 0.0 && now >= c.deployUntil && now >= c.stunUntil) {
            if (c.nextSpawn == 0L) {
                c.nextSpawn = c.deployUntil + Math.round(d.spawnFirst * 20.0);
            }

            if (now >= c.nextSpawn) {
                CardDef sc = this.gm.cards.get(d.spawnCard);
                Location l = c.loc();
                if (sc != null && l != null) {
                    Location at = l.clone();
                    at.setY(this.groundY());
                    this.spawnAiGroup(c.team, sc, at, d.spawnCount, 6);
                    Entity body = c.isPlayer() ? c.player() : c.mob;
                    if (body != null) {
                        this.gm.models.anim(body, "summon");
                    }

                    this.A().world.spawnParticle(Particle.WITCH, at.clone().add(0.0, 0.6, 0.0), 24, 0.9, 0.4, 0.9, 0.05);
                    this.A().world.spawnParticle(Particle.LARGE_SMOKE, at.clone().add(0.0, 0.3, 0.0), 8, 0.8, 0.2, 0.8, 0.01);
                    this.A().world.playSound(at, "entity.evoker.prepare_summon", 0.8F, 1.2F);
                }

                double ev = d.spawnEvery * 20.0;
                if (now < c.rageUntil) {
                    ev /= 1.0 + c.rageBoost;
                }

                c.nextSpawn = now + (long)ev;
            }
        }
    }

    /** 대포 카트: 체력이 절반 아래로 떨어지면 바퀴가 부서져 그 자리에서 대포 건물로 */
    private void transform(Combatant c) {
        CardDef into = this.gm.cards.get(c.card.transformInto);
        Location l = c.loc();
        if (into == null || l == null || !into.isBuilding()) {
            return;
        }

        c.transformed = true;
        double hpLeft = c.hp;
        Location at = l.clone();
        at.setY(this.groundY());
        at.setPitch(0.0F);
        c.dead = true;
        c.hp = 0.0;
        if (c.isPlayer()) {
            this.playerUnitDied(c, true);
        } else {
            this.removeBody(c);
        }

        World w = this.A().world;
        w.spawnParticle(Particle.BLOCK, at.clone().add(0.0, 0.5, 0.0), 30, 0.6, 0.3, 0.6, 0.0, Material.OAK_PLANKS.createBlockData());
        w.spawnParticle(Particle.LARGE_SMOKE, at.clone().add(0.0, 0.6, 0.0), 12, 0.5, 0.3, 0.5, 0.02);
        w.playSound(at, "entity.zombie.break_wooden_door", 0.9F, 1.3F);
        w.playSound(at, "block.anvil.place", 0.6F, 0.8F);
        Combatant b = this.spawnBuilding(c.team, into, at);
        if (b != null) {
            b.maxHp = into.hp;
            b.hp = Math.max(1.0, Math.min(into.hp, hpLeft));
            b.target = c.target;
            this.refreshName(b);
        }
    }

    /** 상대 팀 엘릭서 증가 (엘릭서 골렘 조각이 죽을 때) */
    private void giveElixir(TeamColor t, double amt, Location l) {
        GameTeam gt = this.gm.teams.get(t);
        if (gt == null) {
            return;
        }

        gt.elixir = Math.min(this.gm.maxElixir, gt.elixir + amt);
        World w = this.A().world;
        w.spawnParticle(Particle.DUST, l.clone().add(0.0, 1.0, 0.0), 24, 0.5, 0.5, 0.5, 0.0, new DustOptions(Color.fromRGB(230, 60, 220), 1.5F));
        w.spawnParticle(Particle.WITCH, l.clone().add(0.0, 1.0, 0.0), 10, 0.4, 0.4, 0.4, 0.05);
        w.playSound(l, "block.brewing_stand.brew", 0.8F, 1.4F);
        Player k = gt.kingPlayer();
        if (k != null) {
            k.playSound(k.getLocation(), "entity.experience_orb.pickup", 0.7F, 1.4F);
        }
    }

    /** 힐링 스피릿: 터진 자리에서 여러 번 나눠 아군 유닛 회복 */
    private void healBurst(Combatant src, Location center) {
        CardDef d = src.card;
        TeamColor team = src.team;
        double r = Math.max(1.0, d.healRadius);
        for (int i = 0; i < d.healPulses; i++) {
            this.fx.later(i * 5L, () -> {
                if (this.gm.phase != GameManager.Phase.PLAYING) {
                    return;
                }

                World w = this.A().world;
                this.fx.ring(center, r, Color.fromRGB(255, 230, 120));
                w.spawnParticle(Particle.HAPPY_VILLAGER, center.clone().add(0.0, 0.5, 0.0), 10, r / 2.0, 0.3, r / 2.0, 0.0);
                for (Combatant c : this.area(center, r, team, true, true)) {
                    if (c.isStructure() || c.hp <= 0.0 || c.hp >= c.maxHp) {
                        continue;
                    }

                    c.hp = Math.min(c.maxHp, c.hp + d.heal);
                    Location l = c.loc();
                    if (l != null) {
                        w.spawnParticle(Particle.HEART, l.clone().add(0.0, (c.card == null ? 1.5 : c.card.hitboxH) + 0.2, 0.0), 1, 0.2, 0.1, 0.2, 0.0);
                    }

                    if (c.isPlayer()) {
                        Player p = c.player();
                        if (p != null) {
                            p.setHealth(Math.max(0.5, Math.min(20.0, 20.0 * c.hp / c.maxHp)));
                        }
                    }

                    this.refreshName(c);
                }
            });
        }
    }

    /** 선분 (x0,z0)→(x1,z1) 이 사각형 {x0,z0,x1,z1} 에 처음 들어가는 지점 t (0~1), 안 닿으면 -1 */
    private static double segBox(double ax, double az, double bx, double bz, double[] b) {
        double t0 = 0.0, t1 = 1.0;
        double dx = bx - ax, dz = bz - az;
        double[] p = {-dx, dx, -dz, dz};
        double[] q = {ax - b[0], b[2] - ax, az - b[1], b[3] - az};
        for (int i = 0; i < 4; i++) {
            if (Math.abs(p[i]) < 1.0E-9) {
                if (q[i] < 0.0) {
                    return -1.0;
                }
            } else {
                double r = q[i] / p[i];
                if (p[i] < 0.0) {
                    if (r > t1) {
                        return -1.0;
                    }
                    if (r > t0) {
                        t0 = r;
                    }
                } else {
                    if (r < t0) {
                        return -1.0;
                    }
                    if (r < t1) {
                        t1 = r;
                    }
                }
            }
        }

        return t0 <= t1 ? t0 : -1.0;
    }

    /**
     * 지상 유닛이 가려는 길을 타워·건물이 막고 있으면 그 구조물의 모서리를 돌아가는 경유점을 돌려줌.
     * (겹침 방지가 구조물 밖으로 밀어내기만 해서, 타워 뒤에서 앞으로 가려는 유닛이 벽에 붙어 낑기던 문제)
     */
    private Location avoid(Combatant c, Location from, Location wp, Combatant target) {
        if (wp == null || from == null || c.air || !this.collideOn) {
            return wp;
        }

        double r = bodyRadius(c);
        List<double[]> boxes = new ArrayList<>();
        for (Combatant s : this.all) {
            if (!s.alive() || s == target) {
                continue;
            }

            double[] b = this.structBox(s);
            if (b == null) {
                continue;
            }

            // 목적지가 그 구조물 안이면 (그 구조물로 가는 중) 피하지 않음
            if (wp.getX() > b[0] - r && wp.getX() < b[2] + r && wp.getZ() > b[1] - r && wp.getZ() < b[3] + r) {
                continue;
            }

            boxes.add(b.clone());
        }

        // 유닛이 못 지나갈 만큼 붙어 있는 구조물(타워 옆 건물 등)은 하나로 합침
        double gap = 2.0 * r + 0.1;
        boolean merged = true;
        while (merged) {
            merged = false;
            outer:
            for (int i = 0; i < boxes.size(); i++) {
                for (int j = i + 1; j < boxes.size(); j++) {
                    double[] a = boxes.get(i), b = boxes.get(j);
                    if (a[0] - gap < b[2] && b[0] - gap < a[2] && a[1] - gap < b[3] && b[1] - gap < a[3]) {
                        boxes.set(i, new double[]{Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[2], b[2]), Math.max(a[3], b[3])});
                        boxes.remove(j);
                        merged = true;
                        break outer;
                    }
                }
            }
        }

        double[] hit = null;
        double[] hitE = null;
        double bestT = 2.0;
        for (double[] b : boxes) {
            double[] e = {b[0] - r + 0.05, b[1] - r + 0.05, b[2] + r - 0.05, b[3] + r - 0.05};
            double t = segBox(from.getX(), from.getZ(), wp.getX(), wp.getZ(), e);
            if (t >= 0.0 && t < bestT) {
                bestT = t;
                hit = b;
                hitE = e;
            }
        }

        if (hit == null) {
            return wp;
        }

        double m = r + 0.45;
        double[][] cs = {{hit[0] - m, hit[1] - m}, {hit[2] + m, hit[1] - m}, {hit[2] + m, hit[3] + m}, {hit[0] - m, hit[3] + m}};
        int best = -1;
        double bestCost = Double.MAX_VALUE;
        for (int pass = 0; pass < 2 && best < 0; pass++) {
            for (int i = 0; i < 4; i++) {
                double cx = cs[i][0], cz = cs[i][1];
                if (pass == 0 && segBox(from.getX(), from.getZ(), cx, cz, hitE) >= 0.0) {
                    continue;
                }

                double d0 = Math.hypot(cx - from.getX(), cz - from.getZ());
                double rest;
                if (segBox(cx, cz, wp.getX(), wp.getZ(), hitE) < 0.0) {
                    rest = Math.hypot(wp.getX() - cx, wp.getZ() - cz);
                } else {
                    rest = Double.MAX_VALUE;
                    for (int k = -1; k <= 1; k += 2) {
                        double[] n = cs[(i + k + 4) % 4];
                        rest = Math.min(rest, Math.hypot(n[0] - cx, n[1] - cz) + Math.hypot(wp.getX() - n[0], wp.getZ() - n[1]));
                    }
                }

                double cost = d0 + rest;
                if (cost < bestCost) {
                    bestCost = cost;
                    best = i;
                }
            }
        }

        if (best < 0) {
            return wp;
        }

        Location out = new Location(this.A().world, cs[best][0], this.groundY(), cs[best][1]);
        // 경기장 밖으로 나가는 모서리는 쓰지 않음
        if (!this.A().inField(out)) {
            return wp;
        }

        return out;
    }

    private Location aroundKing(Combatant var1, Location var2, Location var3) {
        Combatant var4 = this.tower(var1.team, Combatant.Kind.KING_TOWER, false);
        if (var4 != null && var4.alive() && var4.towerTiles > 0) {
            double var5 = this.A().minX + var4.towerTx * 3 - 0.6;
            int var10001 = var4.towerTx + var4.towerTiles;
            double var7 = this.A().minX + var10001 * 3 + 0.6;
            double var9 = this.A().minZ + var4.towerTz * 3 - 0.6;
            var10001 = var4.towerTz + var4.towerTiles;
            double var11 = this.A().minZ + var10001 * 3 + 0.6;
            boolean var13 = false;

            for (int var14 = 1; var14 <= 12 && !var13; var14++) {
                double var15 = var14 / 12.0;
                double var17 = var2.getX() + (var3.getX() - var2.getX()) * var15;
                double var19 = var2.getZ() + (var3.getZ() - var2.getZ()) * var15;
                var13 = var17 > var5 && var17 < var7 && var19 > var9 && var19 < var11;
            }

            if (!var13) {
                return null;
            } else {
                boolean var21 = var1.lane != null ? var1.lane : var3.getX() < (var5 + var7) / 2.0;
                double var22 = var21 ? var5 - 0.5 : var7 + 0.5;
                if (Math.abs(var2.getX() - var22) > 0.4) {
                    return new Location(this.A().world, var22, this.groundY(), Math.max(var9 - 0.4, Math.min(var11 + 0.4, var2.getZ())));
                } else {
                    boolean var23 = var3.getZ() > var2.getZ();
                    return new Location(this.A().world, var22, this.groundY(), var23 ? var11 + 0.6 : var9 - 0.6);
                }
            }
        } else {
            return null;
        }
    }

    private void step(Combatant var1, Location var2, Location var3) {
        double var4 = (var1.kind == Combatant.Kind.BARREL ? 3.0 : var1.card.speedBlocks) / 20.0;
        if (this.now() < var1.slowUntil) {
            var4 *= 1.0 - var1.slowAmt;
        }

        if (this.now() < var1.rageUntil) {
            var4 *= 1.0 + var1.rageBoost;
        }

        if (var1.card != null && var1.card.charge) {
            if (var1.charging) {
                var4 *= 2.0;
            } else if (var1.chargeDist >= var1.card.chargeDistance) {
                var1.charging = true;
                this.chargeStartFx(var2);
                var4 *= 2.0;
            }
        }

        Vector var6 = new Vector(var3.getX() - var2.getX(), 0.0, var3.getZ() - var2.getZ());
        double var7 = var6.length();
        if (!(var7 < 0.05)) {
            var6.multiply(Math.min(var7, var4) / var7);
            Location var9 = var2.clone().add(var6);
            double var10 = var1.air ? this.airY() : this.groundY();
            if (!var1.air && var1.card.riverJump && this.A().isRiverRow(this.A().tileZ(var9.getZ()))) {
                double var12 = (var9.getZ() - this.A().riverMinZ()) / (this.A().riverMaxZ() - this.A().riverMinZ());
                var10 = this.groundY() + Math.sin(Math.PI * Math.max(0.0, Math.min(1.0, var12))) * 2.5;
            }

            var9.setY(var10);
            var9.setDirection(var6);
            var9.setPitch(0.0F);
            var1.pendingMove = var9;
            var1.moveDx = var6.getX();
            var1.moveDz = var6.getZ();
            var1.moveTick = this.now();
            if (var1.card != null && var1.card.charge) {
                var1.chargeDist = var1.chargeDist + var6.length();
                if (var1.charging && this.now() % 2L == 0L) {
                    this.A().world.spawnParticle(Particle.CLOUD, var9.clone().add(0.0, 0.2, 0.0), 2, 0.3, 0.05, 0.3, 0.01);
                    this.A().world.spawnParticle(Particle.CRIT, var9.clone().add(0.0, 1.2, 0.0), 2, 0.3, 0.3, 0.3, 0.05);
                }
            }

            var1.lastMoveTick = this.now();
            this.setWalking(var1, var1.mob, true);
        }
    }

    void slow(Combatant var1, double var2, int var4) {
        if (var1 != null && !var1.isTower()) {
            if (this.now() >= var1.slowUntil || !(var1.slowAmt > var2)) {
                var1.slowAmt = var2;
                var1.slowUntil = Math.max(var1.slowUntil, this.now() + var4);
            }
        }
    }

    private long hitTicks(Combatant var1) {
        long var2 = var1.card.hitTicks();
        if (this.now() < var1.rageUntil) {
            var2 = Math.max(1L, Math.round(var2 / (1.0 + var1.rageBoost)));
        }

        return var2;
    }

    private double slowOf() {
        CardDef var1 = this.gm.cards.get("poison");
        return var1 == null ? 0.15 : var1.slow;
    }

    private void face(Combatant var1, Location var2, Location var3) {
        if (var3 != null && var1.mob != null) {
            Vector var4 = var3.toVector().subtract(var2.toVector()).setY(0.0);
            if (!(var4.lengthSquared() < 1.0E-4)) {
                Location var5 = var2.clone();
                var5.setDirection(var4);
                var5.setPitch(0.0F);
                float dyaw = ((var5.getYaw() - var2.getYaw()) % 360.0F + 540.0F) % 360.0F - 180.0F;
                if (Math.abs(dyaw) >= 3.0F) {
                    var1.pendingMove = var5;
                }
            }
        }
    }

    Location aim(Combatant var1) {
        if (var1 != null && var1.alive()) {
            Location var2 = var1.loc();
            if (var2 == null) {
                return null;
            } else {
                double var3 = var1.isTower()
                    ? (var1.kind == Combatant.Kind.KING_TOWER ? 4.5 * KING_S : 3.5 * PRIN_S)
                    : (var1.kind == Combatant.Kind.BUILDING ? 1.2 : (var1.card == null ? 1.0 : var1.card.hitboxH * 0.55));
                return var2.clone().add(0.0, var3, 0.0);
            }
        } else {
            return null;
        }
    }

    /** 미니언류: 다크 엘릭서 침 모델 (보랏빛 검정) */
    private static boolean minionGoo(CardDef d) {
        return d != null && (d.id.equals("minions") || d.id.equals("minion_horde") || d.id.equals("mega_minion"));
    }

    private Fx.Shot shotOf(CardDef var1) {
        if (!var1.shot.isEmpty()) {
            try {
                return Fx.Shot.valueOf(var1.shot);
            } catch (IllegalArgumentException var4) {
            }
        }

        String var2 = var1.id;
        switch (var2) {
            case "musketeer":
                return Fx.Shot.BULLET;
            case "archers":
                return Fx.Shot.ARROW;
            case "baby_dragon":
                return Fx.Shot.FIREBALL;
            case "minions":
            case "minion_horde":
            case "mega_minion":
                return Fx.Shot.GOOP;
            default:
                return var1.range > 3.0 ? Fx.Shot.ARROW : null;
        }
    }

    void attack(Combatant var1, Combatant var2) {
        CardDef var3 = var1.card;
        double var4 = var3.damage;
        if (var2.isTower() && var3.towerDamage > 0.0 && var3.isTroop()) {
            var4 = var3.towerDamage;
        }

        if (var3.charge) {
            if (var1.charging) {
                var4 = var3.chargeDamage;
                Location var6 = var2.loc();
                if (var6 != null) {
                    this.A().world.spawnParticle(Particle.EXPLOSION, var6.clone().add(0.0, 1.0, 0.0), 1, 0.0, 0.0, 0.0, 0.0);
                    this.A().world.playSound(var6, "entity.player.attack.knockback", 1.0F, 0.7F);
                }
            }

            var1.charging = false;
            var1.chargeDist = 0.0;
        }

        double var14 = var4;
        Location var8 = var1.loc();
        if (var8 != null && var2.loc() != null) {
            Object var9 = var1.isPlayer() ? var1.player() : var1.mob;
            var1.lastHit = var2;
            if (var3.id.equals("lava_hound") || var3.id.equals("lava_pup")) {
                // 용암 뱉기: 입 앞에서 용암 튀김 + 불꽃
                Location tl = var2.loc();
                Vector dir = tl == null ? new Vector(0, 0, 0) : tl.toVector().subtract(var8.toVector()).setY(0.0);
                if (dir.lengthSquared() > 1.0E-4) {
                    dir.normalize().multiply(var3.hitboxW * 0.7);
                }

                Location mouth = var8.clone().add(dir).add(0.0, var3.hitboxH * 0.55, 0.0);
                World lw = this.A().world;
                lw.spawnParticle(Particle.LAVA, mouth, var3.id.equals("lava_hound") ? 8 : 3, 0.2, 0.2, 0.2, 0.0);
                lw.spawnParticle(Particle.FLAME, mouth, var3.id.equals("lava_hound") ? 14 : 5, 0.25, 0.2, 0.25, 0.04);
                lw.playSound(mouth, "entity.blaze.shoot", var3.id.equals("lava_hound") ? 0.9F : 0.5F, var3.id.equals("lava_hound") ? 0.7F : 1.3F);
            }

            if (var3.stunResetsCharge) {
                // 스파키: 충전된 전기 대포 발사
                Location sm = var8.clone().add(0.0, var3.hitboxH * 0.7, 0.0);
                Location st = this.aim(var2);
                if (st != null) {
                    this.fx.lightning(sm, st, true);
                    this.fx.lightning(sm.clone().add(0.0, 0.3, 0.0), st, false);
                    this.A().world.spawnParticle(Particle.ELECTRIC_SPARK, st, 40, 0.8, 0.6, 0.8, 0.2);
                    this.A().world.spawnParticle(Particle.END_ROD, st, 20, 0.5, 0.5, 0.5, 0.15);
                    this.fx.ring(st.clone().add(0.0, -0.8, 0.0), Math.max(1.0, var3.splash), Color.fromRGB(120, 220, 255));
                }

                this.A().world.playSound(var8, "entity.lightning_bolt.thunder", 0.7F, 1.6F);
                this.A().world.playSound(var8, "entity.generic.explode", 0.6F, 1.4F);
                this.gm.models.anim((Entity)var9, "attack");
                this.splash(var1, var2, var2.loc(), var14);
                this.damage(var2, var14, var1);
                return;
            }

            if (!var3.damageStages.isEmpty() && var3.isTroop()) {
                // 인페르노 드래곤: 같은 대상을 계속 지지면 피해가 단계별로 커짐
                if (var1.infernoTarget != var2) {
                    var1.infernoTarget = var2;
                    var1.infernoSince = this.now();
                }

                int stg = (int)Math.min((double)(var3.damageStages.size() - 1), (this.now() - var1.infernoSince) / (var3.stageSeconds * 20.0));
                Color[] cols = new Color[]{Color.fromRGB(255, 200, 60), Color.fromRGB(255, 120, 30), Color.fromRGB(255, 40, 20)};
                Location it = this.aim(var2);
                Location mouth = var8.clone().add(0.0, var3.hitboxH * 0.5, 0.0);
                if (it != null) {
                    mouth.add(it.toVector().subtract(mouth.toVector()).setY(0.0).normalize().multiply(var3.hitboxW * 0.5));
                    this.fx.beam(mouth, it, null, new DustOptions(cols[Math.min(2, stg)], 0.8F + stg * 0.5F));
                    this.A().world.spawnParticle(Particle.FLAME, it, 2 + stg * 4, 0.2, 0.3, 0.2, 0.02);
                }

                if (this.now() % 10L == 0L) {
                    this.A().world.playSound(var8, "block.fire.ambient", 0.8F, 0.6F + stg * 0.3F);
                    this.gm.models.anim((Entity)var9, "attack");
                }

                this.damage(var2, var3.damageStages.get(stg), var1);
                return;
            }

            if (var3.pellets > 0) {
                this.gm.models.anim((Entity)var9, "attack");
                this.hunterShot(var1, var2, var8.clone().add(0.0, var3.hitboxH * 0.6, 0.0), var14);
                return;
            }

            if (var3.axe || var3.pierce || var3.roll) {
                this.gm.models.anim((Entity)var9, "attack");
                Location lf = var8.clone().add(0.0, var3.roll ? 0.0 : var3.hitboxH * 0.6, 0.0);
                if (var3.roll || var3.axe) {
                    // 볼러: 공을 던지는 동작 뒤에 굴러감 / 도끼맨: 팔을 휘두르는 순간 도끼가 손을 떠남
                    this.fx.later(var3.roll ? 8L : 5L, () -> {
                        if (var1.alive()) {
                            this.lineAttack(var1, var2, lf, var14);
                        }
                    });
                } else {
                    this.lineAttack(var1, var2, lf, var14);
                }

                return;
            }

            if (var3.explodeOnHit) {
                // 해골 돌격병: 건물에 닿으면 폭탄과 함께 터짐
                Location bl = var2.loc() != null ? var2.loc() : var8;
                World bw = this.A().world;
                bw.spawnParticle(Particle.EXPLOSION, bl.clone().add(0.0, 0.8, 0.0), 3, 0.5, 0.3, 0.5, 0.0);
                bw.spawnParticle(Particle.LARGE_SMOKE, bl.clone().add(0.0, 0.8, 0.0), 12, 0.6, 0.4, 0.6, 0.02);
                this.fx.ring(bl, Math.max(1.0, var3.splash), Color.fromRGB(255, 140, 50));
                bw.playSound(bl, "entity.generic.explode", 1.0F, 1.1F);
                this.damage(var2, var14, var1);
                for (Combatant ec : this.area(bl, Math.max(0.5, var3.splash), var2.team, true, false)) {
                    if (ec != var2) {
                        this.damage(ec, var14, var1);
                    }
                }

                this.kill(var1);
                return;
            }

            if ("SNOW".equals(var3.shot) || var3.id.equals("ice_wizard") && "SNOWBALL".equals(var3.shot)) {
                // 얼음 마법사: 큰 눈덩이 대신 손에서 눈보라를 뿌림
                this.gm.models.anim((Entity)var9, "attack");
                this.snowStream(var1, var2, var8.clone().add(0.0, var3.hitboxH * 0.6, 0.0), var14);
                return;
            }

            if ("FLAME".equals(var3.shot)) {
                // 마법사: 화염구 대신 손에서 불꽃 줄기가 날아가 터짐
                this.gm.models.anim((Entity)var9, "attack");
                this.flameStream(var1, var2, var8.clone().add(0.0, var3.hitboxH * 0.6, 0.0), var14);
                return;
            }

            if (var3.zap) {
                // 감전돌이: 총에서 바로 전기 → 피해 + 0.5초 스턴 (스파키 충전도 초기화)
                Location zm = var8.clone().add(0.0, var1.air ? var3.hitboxH * 0.4 : var3.hitboxH * 0.6, 0.0);
                Location zt = this.aim(var2);
                if (zt != null) {
                    this.fx.lightning(zm, zt, true);
                    this.A().world.spawnParticle(Particle.ELECTRIC_SPARK, zt, 12, 0.3, 0.3, 0.3, 0.1);
                }

                this.A().world.playSound(var8, "entity.bee.sting", 0.6F, 0.6F);
                this.gm.models.anim((Entity)var9, "attack");
                this.damage(var2, var14, var1);
                this.stun(var2, var3.stun);
                if (var3.chain > 0) {
                    // 일렉트로 드래곤: 번개가 가까운 적에게 튀어감
                    this.chainZap(var1, var2, var14, var3.chain, var3.chainRange > 0.0 ? var3.chainRange : 8.0);
                }
                return;
            }

            if (var3.breakOnHit && var2.isStructure()) {
                // 배틀 램: 건물을 들이받고 부서지면서 바바리안 소환
                this.gm.models.anim((Entity)var9, "attack");
                this.fx.melee(var3, var8, var2.loc());
                this.damage(var2, var14, var1);
                this.A().world.playSound(var8, "entity.zombie.break_wooden_door", 1.0F, 0.8F);
                this.A().world.spawnParticle(Particle.BLOCK, var8.clone().add(0.0, 0.8, 0.0), 30, 0.6, 0.4, 0.6, 0.0, Material.OAK_LOG.createBlockData());
                this.fx.later(3L, () -> {
                    if (var1.alive()) {
                        this.kill(var1);
                    }
                });
                return;
            }

            if (var3.kamikaze) {
                this.kamikaze(var1, var2);
            } else {
                this.gm.models.anim((Entity)var9, "attack");
                if (!var3.id.equals("electro_wizard")) {
                    Fx.Shot var15 = this.shotOf(var3);
                    if (var15 == null) {
                        this.fx.melee(var3, var8, var2.loc());
                        if (var3.reflectDamage > 0.0) {
                            // 일렉트로 자이언트: 내리칠 때 손에서 전기가 튐
                            Location zt = this.aim(var2);
                            if (zt != null) {
                                Location zh = var8.clone().add(0.0, var3.hitboxH * 0.55, 0.0);
                                this.fx.lightning(zh, zt, true);
                                this.A().world.spawnParticle(Particle.ELECTRIC_SPARK, zt, 24, 0.5, 0.5, 0.5, 0.15);
                                this.A().world.spawnParticle(Particle.END_ROD, zt, 6, 0.3, 0.3, 0.3, 0.05);
                                this.A().world.playSound(zt, "entity.lightning_bolt.impact", 0.6F, 1.6F);
                            }
                        }
                        if (var3.splashSelf) {
                            // 발키리: 자기 주위 360도
                            this.spinFx(var8, var3.splash);
                        }

                        this.splash(var1, var2, var3.splashSelf ? var8 : var2.loc(), var14);
                        this.damage(var2, var14, var1);
                    } else {
                        Location var17 = var8.clone().add(0.0, var1.air ? var3.hitboxH * 0.4 : var3.hitboxH * 0.7, 0.0);
                        Location var19 = this.aim(var2);
                        if (var19 != null) {
                            var17.add(var19.toVector().subtract(var17.toVector()).normalize().multiply(0.6));
                        }

                        if (var3.recoil > 0.0 && var2.loc() != null) {
                            // 로켓병: 쏘는 반동으로 뒤로 밀림
                            this.knockback(var1, var2.loc(), var3.recoil, true, true);
                        }
                        if (var3.id.equals("princess")) {
                            // 프린세스: 불화살을 3갈래로 동시에, 화살마다 맞은 자리에 범위 피해
                            Location a0 = this.aim(var2);
                            if (a0 != null) {
                                Vector fw = a0.toVector().subtract(var17.toVector()).setY(0.0);
                                if (fw.lengthSquared() > 1.0E-4) {
                                    Vector side = new Vector(-fw.getZ(), 0.0, fw.getX()).normalize().multiply(Math.max(1.2, fw.length() * 0.22));
                                    for (int ex = -1; ex <= 1; ex += 2) {
                                        Location end = a0.clone().add(side.clone().multiply(ex));
                                        this.fx.shoot(Fx.Shot.ARROW, var17.clone(), () -> end, p -> {
                                            // 양옆 화살도 맞은 자리에 범위 피해
                                            this.A().world.spawnParticle(Particle.FLAME, p, 14, Math.max(0.3, var3.splash / 3.0), 0.15, Math.max(0.3, var3.splash / 3.0), 0.03);
                                            if (this.gm.phase == GameManager.Phase.PLAYING) {
                                                for (Combatant e : this.area(p, var3.splash, var2.team, true, true)) {
                                                    if (this.canTarget(var1, e)) {
                                                        this.damage(e, var14, var1);
                                                    }
                                                }
                                            }
                                        });
                                    }
                                }
                            }
                        }
                        this.fx.shoot(var15, var17, () -> this.aim(var2), var7 -> {
                            if (var3.id.equals("princess")) {
                                this.A().world.spawnParticle(Particle.FLAME, var7, 14, Math.max(0.3, var3.splash / 3.0), 0.15, Math.max(0.3, var3.splash / 3.0), 0.03);
                                this.A().world.playSound(var7, "entity.generic.burn", 0.5F, 1.4F);
                            }
                            this.fx.impact(var15, var7, var3.splash);
                            if (this.gm.phase == GameManager.Phase.PLAYING) {
                                this.splash(var1, var2, var7, var14);
                                if (var2.alive()) {
                                    this.curse(var2, var1);
                                    this.damage(var2, var14, var1);
                                    this.hitSlow(var1, var2);
                                }
                                if (var3.sparks > 0) {
                                    this.sparks(var1, var17, var7);
                                }
                            }
                        }, minionGoo(var3) ? "clash_minion_goo" : null, null);
                    }
                } else {
                    // 일렉트로 마법사: 두 번째 대상 = 첫 대상 말고 사거리 안에서 나와 가장 가까운 적
                    Combatant var10 = null;
                    double bestD = Double.MAX_VALUE;
                    for (Combatant var12 : this.all) {
                        if (var12 != var2 && var12.alive() && this.canTarget(var1, var12) && !var12.hidden && this.inRange(var1, var8, var12, var3.range)) {
                            Location l12 = var12.loc();
                            double d12 = l12 == null ? Double.MAX_VALUE : flat(l12, var8) - var12.radius;
                            if (d12 < bestD) {
                                bestD = d12;
                                var10 = var12;
                            }
                        }
                    }

                    // 양손에서 한 줄기씩 (몸 옆으로 살짝 벌림)
                    double yawR = Math.toRadians(var8.getYaw());
                    double side = Math.max(0.3, var3.hitboxW * 0.3);
                    Vector sideV = new Vector(Math.cos(yawR) * side, 0.0, Math.sin(yawR) * side);
                    Location var16 = var8.clone().add(0.0, var3.hitboxH * 0.6, 0.0).add(sideV);
                    Location var16b = var8.clone().add(0.0, var3.hitboxH * 0.6, 0.0).add(sideV.clone().multiply(-1.0));
                    Location var18 = this.aim(var2);
                    if (var18 != null) {
                        this.fx.lightning(var16, var18, true);
                        if (var10 == null) {
                            this.fx.lightning(var16b, var18, false);
                        }
                    }

                    if (var10 != null) {
                        Location var13 = this.aim(var10);
                        if (var13 != null) {
                            this.fx.lightning(var16b, var13, false);
                        }

                        this.damage(var2, var14 / 2.0, var1);
                        this.damage(var10, var14 / 2.0, var1);
                        this.stun(var10, var3.stun);
                    } else {
                        this.damage(var2, var14, var1);
                    }

                    this.stun(var2, var3.stun);
                }
            }
        }
    }

    private void splash(Combatant var1, Combatant var2, Location var3, double var4) {
        if (!(var1.card.splash <= 0.0) && var3 != null) {
            Location var6 = var3.clone();

            for (Combatant var8 : this.area(var6, var1.card.splash, var2.team, true, true)) {
                if (var8 != var2 && this.canTarget(var1, var8)) {
                    this.curse(var8, var1);
                    this.damage(var8, var4, var1);
                    this.hitSlow(var1, var8);
                }
            }
        }
    }

    private static Location midpoint(Location var0, Location var1) {
        return var1 == null ? var0.clone() : var0.clone().add(var1.toVector().subtract(var0.toVector()).multiply(0.5));
    }

    private void beam(Location var1, Combatant var2, Particle var3) {
        Location var4 = var2.loc();
        if (var1 != null && var4 != null) {
            var4 = var4.clone().add(0.0, var2.isTower() ? (var2.kind == Combatant.Kind.KING_TOWER ? 3.0 * KING_S : 3.0 * PRIN_S) : 1.0, 0.0);
            Vector var5 = var4.toVector().subtract(var1.toVector());
            double var6 = var5.length();
            if (!(var6 < 0.1)) {
                var5.multiply(1.0 / var6);

                for (double var8 = 0.0; var8 < var6; var8 += 0.6) {
                    Location var10 = var1.clone().add(var5.clone().multiply(var8));
                    this.A().world.spawnParticle(var3, var10, 1, 0.0, 0.0, 0.0, 0.0);
                }
            }
        }
    }

    private void lightning(Location var1, Combatant var2) {
        this.beam(var1.clone().add(0.0, 1.4, 0.0), var2, Particle.ELECTRIC_SPARK);
        this.A().world.playSound(var1, "entity.lightning_bolt.impact", 0.4F, 1.8F);
    }

    void damage(Combatant var1, double var2, Combatant var4) {
        if (var1 != null && var4 != null && var1.alive() && var4.alive() && var4 != var1 && !this.reflecting
            && var1.card != null && var1.card.reflectDamage > 0.0 && var4.team != var1.team) {
            this.reflect(var1, var4);
        }
        if (var1 != null && var1.alive() && !(var2 <= 0.0)) {
            if (!var1.hidden) {
                if (!var1.isTower() || !this.gm.test.active || !this.gm.test.godTowers) {
                    if (var1.card != null && var1.card.dash && this.now() < var1.dashUntil) {
                        return;
                    }

                    if (var1.isTower() || this.now() >= var1.deployUntil) {
                        if (var1.shield > 0.0) {
                            // 실드가 공격을 통째로 막음 (깨지는 공격의 남은 피해는 버려짐)
                            var1.shield -= var2;
                            var1.lastDamaged = this.now();
                            Location sl = var1.loc();
                            if (var1.shield <= 0.0) {
                                var1.shield = 0.0;
                                if (sl != null) {
                                    this.A().world.playSound(sl, "item.shield.break", 1.0F, 0.9F);
                                    this.A().world.spawnParticle(Particle.BLOCK, sl.clone().add(0.0, 1.0, 0.0), 24, 0.4, 0.4, 0.4, 0.0, Material.IRON_BLOCK.createBlockData());
                                }

                                this.gm.models.hideBone(var1.isPlayer() ? var1.player() : var1.mob, "shield");
                            } else if (sl != null) {
                                this.A().world.playSound(sl, "item.shield.block", 0.7F, 1.0F);
                                this.fx.damageNumber(sl.clone().add(0.0, (var1.card == null ? 1.5 : var1.card.hitboxH) + 0.1, 0.0), var2, false, false);
                            }

                            if (var1.mob != null) {
                                this.gm.models.anim(var1.mob, "hit");
                            }

                            this.refreshName(var1);
                            return;
                        }

                        var1.hp -= var2;
                        var1.lastDamaged = this.now();
                        Location var5 = var1.loc();
                        if (var5 != null) {
                            double var6 = var1.isTower()
                                ? (var1.kind == Combatant.Kind.KING_TOWER ? 8.0 * KING_S : 6.2 * PRIN_S)
                                : (var1.card == null ? 1.5 : var1.card.hitboxH + 0.1);
                            this.fx.damageNumber(var5.clone().add(0.0, var6, 0.0), var2, var1.isTower(), var2 >= 300.0);
                            if (var1.isTower()) {
                                this.A()
                                    .world
                                    .spawnParticle(
                                        Particle.BLOCK, var5.clone().add(0.0, 3.0, 0.0), 8, 1.5, 1.5, 1.5, 0.0, Material.STONE_BRICKS.createBlockData()
                                    );

                                for (Entity var9 : var1.extras) {
                                    this.gm.models.anim(var9, "hit");
                                }
                            } else if (var1.mob != null) {
                                this.gm.models.anim(var1.mob, "hit");
                                if (var1.kind == Combatant.Kind.BUILDING) {
                                    for (Entity var13 : var1.extras) {
                                        this.gm.models.anim(var13, "hit");
                                    }
                                }

                                try {
                                    var1.mob.playHurtAnimation(0.0F);
                                } catch (Throwable var10) {
                                }
                            }
                        }

                        if (var1.kind == Combatant.Kind.KING_TOWER && !var1.active) {
                            this.activateKing(var1);
                        }

                        if (var1.isPlayer()) {
                            Player var11 = var1.player();
                            if (var11 != null) {
                                var11.setHealth(Math.max(0.5, Math.min(20.0, 20.0 * Math.max(0.0, var1.hp) / var1.maxHp)));
                                var11.playSound(var11.getLocation(), "entity.player.hurt", 0.6F, 1.0F);
                            }

                            this.gm.models.anim(var11, "hit");
                        }

                        this.refreshName(var1);
                        if (var1.hp <= 0.0) {
                            this.kill(var1);
                        } else if (var1.card != null && var1.card.transformAt > 0.0 && !var1.transformed && var1.kind == Combatant.Kind.TROOP
                            && var1.hp <= var1.maxHp * var1.card.transformAt) {
                            this.transform(var1);
                        }
                    }
                }
            }
        }
    }

    private void activateKing(Combatant var1) {
        if (!var1.active) {
            var1.active = true;
            this.gm.titleAll(var1.team.label() + " §f킹 타워 활성화!", "");
            this.A().world.playSound(var1.fixed, "entity.iron_golem.repair", 1.0F, 0.8F);
        }
    }

    void kill(Combatant var1) {
        if (var1.zoneDisc != null) {
            this.fx.fadeDisc(var1.zoneDisc);
            var1.zoneDisc = null;
        }
        if (var1.deployMark != null) {
            var1.deployMark.remove();
            var1.deployMark = null;
        }
        if (!var1.dead) {
            Location var2 = var1.loc();
            var1.dead = true;
            var1.hp = 0.0;
            if (var1.card != null && var2 != null && !var1.isTower() && this.gm.phase == GameManager.Phase.PLAYING) {
                this.deathEffects(var1, var2.clone());
                if (var1.card.deathElixir > 0.0 && !var1.clone) {
                    this.giveElixir(var1.team.other(), var1.card.deathElixir, var2);
                }

                if (var1.card.deathElixirSelf > 0.0 && !var1.clone) {
                    // 엘릭서 정제소: 부서지면 우리 팀 엘릭서 1
                    this.giveElixir(var1.team, var1.card.deathElixirSelf, var2);
                }
            }

            if (var1.kind == Combatant.Kind.TROOP && var1.cursedBy != null && this.now() < var1.cursedUntil && var2 != null
                && this.gm.phase == GameManager.Phase.PLAYING && var1.curseInto != null) {
                // 엄마 마녀 저주: 저주받은 채 죽으면 저주한 쪽의 저주 호그가 됨
                CardDef hog = this.gm.cards.get(var1.curseInto);
                if (hog != null) {
                    Location hl = var2.clone();
                    hl.setY(this.groundY());
                    TeamColor ht = var1.cursedBy;
                    this.A().world.spawnParticle(Particle.WITCH, hl.clone().add(0.0, 0.8, 0.0), 30, 0.4, 0.5, 0.4, 0.05);
                    this.A().world.playSound(hl, "entity.pig.ambient", 1.0F, 0.8F);
                    this.fx.later(4L, () -> {
                        if (this.gm.phase == GameManager.Phase.PLAYING) {
                            this.spawnAiGroup(ht, hog, hl, 1, 10);
                        }
                    });
                }
            }

            switch (var1.kind) {
                case KING_TOWER:
                case PRINCESS_TOWER:
                    this.destroyTower(var1);
                    break;
                case BUILDING:
                    this.removeBody(var1);
                    this.A().world.spawnParticle(Particle.POOF, var1.fixed, 20, 0.6, 0.6, 0.6, 0.02);
                    break;
                case BARREL:
                    this.popBarrel(var1);
                    this.removeBody(var1);
                    break;
                case TROOP:
                    if (var1.isPlayer()) {
                        this.playerUnitDied(var1, true);
                    } else {
                        this.removeBody(var1);
                    }
            }
        }
    }

    private void deathEffects(Combatant var1, Location var2) {
        CardDef var3 = var1.card;
        World var4 = this.A().world;
        Location var5 = var2.clone();
        var5.setY(var1.air ? this.airY() : this.groundY());
        if (var3.deathDamage > 0.0 && !var1.clone) {
            double var6 = Math.max(1.0, var3.deathRadius);
            if (var3.deathBomb && var1.air) {
                // 해골 비행선: 죽은 자리에서 폭탄이 떨어져 땅에서 터짐 (지상 + 건물만)
                Location bombFrom = var5.clone().add(0.0, 0.4, 0.0);
                Location bombAt = var5.clone();
                bombAt.setY(this.groundY());
                TeamColor enemy = var1.team.other();
                double bombDmg = var3.deathDamage;
                var4.playSound(bombFrom, "entity.tnt.primed", 1.0F, 1.2F);
                this.fx.shoot(Fx.Shot.BOMB, bombFrom, () -> bombAt, hit -> {
                    if (this.gm.phase == GameManager.Phase.PLAYING) {
                        this.fx.impact(Fx.Shot.BOMB, bombAt, var6);
                        this.fx.ring(bombAt, var6, Color.fromRGB(255, 150, 60));
                        this.A().world.playSound(bombAt, "entity.generic.explode", 1.0F, 0.9F);
                        for (Combatant c : this.area(bombAt, var6, enemy, true, false)) {
                            this.damage(c, bombDmg, null);
                        }
                    }
                });
            } else if (var3.deathSlow > 0.0) {
                // 얼음 골렘: 얼음 폭발 → 피해 + 감속 (넉백 없음)
                var4.spawnParticle(Particle.SNOWFLAKE, var5.clone().add(0.0, 0.8, 0.0), 120, var6 / 2.0, 0.6, var6 / 2.0, 0.05);
                var4.spawnParticle(Particle.BLOCK, var5.clone().add(0.0, 0.5, 0.0), 50, var6 / 2.0, 0.4, var6 / 2.0, 0.0, Material.PACKED_ICE.createBlockData());
                this.fx.ring(var5, var6, Color.fromRGB(170, 230, 255));
                var4.playSound(var5, "block.glass.break", 1.0F, 0.7F);
                var4.playSound(var5, "entity.player.hurt_freeze", 1.0F, 0.9F);
                int slowTicks = (int)Math.round(var3.deathSlowDuration * 20.0);

                for (Combatant var9 : this.area(var5, var6, var1.team.other(), true, true)) {
                    this.damage(var9, var3.deathDamage, null);
                    this.slow(var9, var3.deathSlow, slowTicks);
                }
            } else if (var3.deathDelay > 0.0) {
                // 폭탄 타워: 부서진 자리에 폭탄이 떨어지고 잠시 뒤 터짐 (공중 + 지상)
                Location bl = var2.clone();
                bl.setY(this.groundY());
                TeamColor enemy = var1.team.other();
                double bombDmg = var3.deathDamage;
                long delay = Math.max(1L, Math.round(var3.deathDelay * 20.0));
                var4.playSound(bl, "entity.tnt.primed", 1.0F, 0.8F);
                Material[] fuse = {Material.TNT};
                org.bukkit.entity.BlockDisplay bomb = null;
                // 직접 만든 폭탄 모델 (clash_bomb). 모델이 없으면 TNT 블록
                ArmorStand bombStand = null;
                if (this.gm.models.enabled() && !var3.deathModel.isEmpty()) {
                    ArmorStand st = (ArmorStand)var4.spawn(bl.clone(), ArmorStand.class);
                    st.addScoreboardTag("clashmc");
                    stand(st, true);
                    st.addScoreboardTag("clashmc_nohit");
                    if (this.gm.models.apply(st, var3.deathModel, true, var1.team.color)) {
                        this.gm.models.anim(st, "deploy");
                        this.fx.track(st);
                        bombStand = st;
                    } else {
                        st.remove();
                    }
                }

                if (bombStand == null) try {
                    bomb = (org.bukkit.entity.BlockDisplay)var4.spawn(bl.clone().add(-0.45, 0.0, -0.45), org.bukkit.entity.BlockDisplay.class);
                    bomb.setBlock(fuse[0].createBlockData());
                    bomb.setTransformation(new org.bukkit.util.Transformation(new org.joml.Vector3f(), new org.joml.Quaternionf(), new org.joml.Vector3f(0.9F, 0.9F, 0.9F), new org.joml.Quaternionf()));
                    bomb.addScoreboardTag("clashmc");
                } catch (Throwable ignored) {
                }

                org.bukkit.entity.BlockDisplay fbomb = bomb;
                ArmorStand fstand = bombStand;
                for (long t = 0L; t < delay; t += 5L) {
                    this.fx.later(t, () -> {
                        if (this.gm.phase == GameManager.Phase.PLAYING) {
                            this.A().world.spawnParticle(Particle.SMOKE, bl.clone().add(0.0, 1.1, 0.0), 3, 0.1, 0.1, 0.1, 0.01);
                            this.A().world.spawnParticle(Particle.FLAME, bl.clone().add(0.0, 1.0, 0.0), 1, 0.05, 0.05, 0.05, 0.01);
                            this.fx.edge(bl, var6, Color.fromRGB(255, 80, 40));
                        }
                    });
                }

                this.fx.later(delay, () -> {
                    if (fbomb != null && fbomb.isValid()) {
                        fbomb.remove();
                    }

                    if (fstand != null) {
                        this.gm.models.remove(fstand);
                        this.fx.untrack(fstand);
                        fstand.remove();
                    }

                    if (this.gm.phase == GameManager.Phase.PLAYING) {
                        this.fx.impact(Fx.Shot.BOMB, bl, var6);
                        this.fx.ring(bl, var6, Color.fromRGB(255, 150, 60));
                        this.A().world.spawnParticle(Particle.EXPLOSION_EMITTER, bl.clone().add(0.0, 0.5, 0.0), 1, 0.0, 0.0, 0.0, 0.0);
                        this.A().world.playSound(bl, "entity.generic.explode", 1.2F, 0.7F);
                        for (Combatant c : this.area(bl, var6, enemy, true, true)) {
                            this.damage(c, bombDmg, null);
                        }
                    }
                });
            } else {
                var4.spawnParticle(Particle.EXPLOSION, var5.clone().add(0.0, 0.6, 0.0), 2, var6 / 3.0, 0.2, var6 / 3.0, 0.0);
                var4.spawnParticle(Particle.BLOCK, var5.clone().add(0.0, 0.5, 0.0), 40, var6 / 2.0, 0.4, var6 / 2.0, 0.0, Material.STONE.createBlockData());
                this.fx.ring(var5, var6, Color.fromRGB(160, 150, 140));
                var4.playSound(var5, "entity.generic.explode", 0.8F, 0.8F);

                for (Combatant var9 : this.area(var5, var6, var1.team.other(), true, true)) {
                    this.damage(var9, var3.deathDamage, null);
                    if (!var9.isStructure()) {
                        this.knockback(var9, var5, 1.0);
                    }
                }
            }
        }

        if (var1.air && !var3.deathSpawn.isEmpty() && var3.deathSpawnCount > 0 && !var1.clone) {
            // 라바 하운드: 터지면서 용암 조각이 사방으로
            var4.spawnParticle(Particle.FLAME, var5.clone().add(0.0, 0.5, 0.0), 60, 1.2, 0.6, 1.2, 0.08);
            var4.spawnParticle(Particle.LARGE_SMOKE, var5.clone().add(0.0, 0.5, 0.0), 30, 1.0, 0.5, 1.0, 0.03);
            var4.spawnParticle(Particle.BLOCK, var5.clone().add(0.0, 0.5, 0.0), 40, 1.0, 0.5, 1.0, 0.0, Material.MAGMA_BLOCK.createBlockData());
            var4.playSound(var5, "entity.blaze.death", 1.0F, 0.6F);
            var4.playSound(var5, "block.lava.extinguish", 1.0F, 0.8F);
        }

        if (var3.id.equals("lava_pup")) {
            // 라바 펍: 죽을 때 작은 용암 덩어리처럼 펑
            Location pl = var5.clone().add(0.0, 0.6, 0.0);
            var4.spawnParticle(Particle.LAVA, pl, 10, 0.3, 0.3, 0.3, 0.0);
            var4.spawnParticle(Particle.FLAME, pl, 25, 0.25, 0.25, 0.25, 0.09);
            var4.spawnParticle(Particle.EXPLOSION, pl, 1, 0.0, 0.0, 0.0, 0.0);
            var4.spawnParticle(Particle.BLOCK, pl, 15, 0.3, 0.3, 0.3, 0.0, Material.MAGMA_BLOCK.createBlockData());
            var4.playSound(pl, "entity.magma_cube.squish", 1.0F, 1.4F);
            var4.playSound(pl, "block.fire.extinguish", 0.6F, 1.6F);
        }

        if (!var3.deathSpell.isEmpty() && !var1.clone) {
            // 나무꾼: 죽은 자리에 분노 마법
            CardDef sp = this.gm.cards.get(var3.deathSpell);
            if (sp != null && sp.isSpell()) {
                Location sl = var5.clone();
                sl.setY(this.groundY());
                this.castSpell(var1.team, sp, sl);
            }
        }

        if (!var3.deathSpawn.isEmpty() && var3.deathSpawnCount > 0 && !var1.clone) {
            CardDef var10 = this.gm.cards.get(var3.deathSpawn);
            if (var10 != null) {
                Location var7 = var5.clone();
                var7.setY(this.groundY());
                // 배틀 램 / 고블린 우리: 부서지는 모션이 끝난 뒤에 유닛이 나옴
                long dl = deathSpawnDelay(var3);
                if (dl <= 0L && var1.air && var10.air) {
                    // 라바 하운드: 펍들이 터지듯 사방으로 튀어나감
                    this.burstSpawn(var1.team, var10, var5.clone(), var3.deathSpawnCount);
                } else if (dl <= 0L) {
                    this.spawnAiGroup(var1.team, var10, var7, var3.deathSpawnCount, var10.air ? 4 : 10);
                } else {
                    TeamColor tm = var1.team;
                    int cnt = var3.deathSpawnCount;
                    this.fx.later(dl, () -> {
                        if (this.gm.phase == GameManager.Phase.PLAYING) {
                            this.spawnAiGroup(tm, var10, var7, cnt, var10.air ? 4 : 10);
                        }
                    });
                }
            }
        }
    }

    private void removeBody(Combatant var1) {
        if (var1.mob != null) {
            LivingEntity var2 = var1.mob;
            this.byEntity.remove(var2.getUniqueId());
            var2.setCustomNameVisible(false);
            if (this.gm.models.anim(var2, "death") && this.gm.phase == GameManager.Phase.PLAYING) {
                this.fx.track(var2);
                // 폭탄 타워: 모델의 죽는 모습(무너진 탑 위 폭탄)을 폭탄이 터질 때까지 남겨둠
                long keep = var1.card != null && var1.card.deathDelay > 0.0 ? 20L : Math.max(14L, deathSpawnDelay(var1.card));
                this.fx.later(keep, () -> {
                    if (var2.isValid()) {
                        this.A().world.spawnParticle(Particle.POOF, var2.getLocation().add(0.0, 0.6, 0.0), 10, 0.3, 0.3, 0.3, 0.02);
                    }

                    this.gm.models.remove(var2);
                    this.fx.untrack(var2);
                    var2.remove();
                });
            } else {
                this.A().world.spawnParticle(Particle.POOF, var2.getLocation().add(0.0, 0.6, 0.0), 10, 0.3, 0.3, 0.3, 0.02);
                this.gm.models.remove(var2);
                var2.remove();
            }
        }

        if (var1.hitbox != null) {
            this.byEntity.remove(var1.hitbox.getUniqueId());
            var1.hitbox.remove();
        }

        if (var1.label != null && var1.label != var1.mob) {
            var1.label.remove();
        }

        for (Entity var3 : var1.extras) {
            this.gm.models.remove(var3);
            var3.remove();
        }
    }

    private void destroyTower(Combatant var1) {
        Location var2 = var1.fixed;
        World var3 = this.A().world;
        var3.spawnParticle(Particle.EXPLOSION_EMITTER, var2.clone().add(0.0, 3.0, 0.0), 1);
        var3.spawnParticle(Particle.LARGE_SMOKE, var2.clone().add(0.0, 3.0, 0.0), 60, 2.0, 2.0, 2.0, 0.05);
        var3.playSound(var2, "entity.generic.explode", 1.5F, 0.7F);
        this.clearTowerBlocks(var1, true);
        if (var1.hitbox != null) {
            this.byEntity.remove(var1.hitbox.getUniqueId());
            var1.hitbox.remove();
        }

        if (var1.label != null) {
            var1.label.remove();
        }

        for (Entity var5 : var1.extras) {
            this.gm.models.remove(var5);
            var5.remove();
        }

        boolean var6 = var1.kind == Combatant.Kind.KING_TOWER;
        if (!var6) {
            Combatant var7 = this.tower(var1.team, Combatant.Kind.KING_TOWER, false);
            if (var7 != null && var7.alive()) {
                this.activateKing(var7);
            }
        }

        this.gm.onCrown(var1.team.other(), var6);
    }

    private void tickPlayerUnit(Combatant var1) {
        Player var2 = var1.player();
        if (var2 != null && var2.isOnline()) {
            if (var1.air) {
                if (!var2.getAllowFlight()) {
                    var2.setAllowFlight(true);
                }

                if (!var2.isFlying()) {
                    var2.setFlying(true);
                }
            }

            float var3 = (float)Math.min(1.0, var1.card.speedBlocks * this.gm.walkPerBlock);
            float var4 = this.now() < var1.slowUntil ? var3 * (float)(1.0 - var1.slowAmt) : var3;
            if (this.now() < var1.rageUntil) {
                var4 *= (float)(1.0 + var1.rageBoost);
            }

            if (var1.card.charge) {
                Location var5 = var2.getLocation();
                if (var1.lastPos != null && var1.lastPos.getWorld() == var5.getWorld()) {
                    var1.chargeDist = var1.chargeDist + Math.hypot(var5.getX() - var1.lastPos.getX(), var5.getZ() - var1.lastPos.getZ());
                }

                if (!var1.charging && var1.chargeDist >= var1.card.chargeDistance) {
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
                }
            }

            var4 = Math.min(1.0F, var4);
            if (Math.abs(var2.getWalkSpeed() - var4) > 0.001) {
                var2.setWalkSpeed(var4);
            }

            Location var11 = var2.getLocation();
            if (var1.lastPos != null && var1.lastPos.getWorld() == var11.getWorld()) {
                double var6 = var11.getX() - var1.lastPos.getX();
                double var8 = var11.getZ() - var1.lastPos.getZ();
                if (var6 * var6 + var8 * var8 > 0.0016) {
                    var1.lastMoveTick = this.now();
                }
            }

            var1.lastPos = var11;
            this.chargeIdleCheck(var1);
            this.setWalking(var1, var2, this.now() - var1.lastMoveTick <= 3L);
            if (var2.getFoodLevel() != 6) {
                var2.setFoodLevel(6);
            }
        } else {
            var1.dead = true;
        }
    }

    void playerSwing(Player var1) {
        Combatant var2 = this.byEntity.get(var1.getUniqueId());
        if (var2 != null && var2.kind == Combatant.Kind.TROOP && var2.alive()) {
            if (this.now() >= var2.deployUntil && this.now() >= var2.stunUntil && this.now() >= var2.nextAttack) {
                CardDef var3 = var2.card;
                Location var4 = var1.getEyeLocation();
                RayTraceResult var5 = var1.getWorld().rayTraceEntities(var4, var4.getDirection(), var3.range + 6.0, 0.4, var3x -> {
                    if (var3x.getUniqueId().equals(var1.getUniqueId())) {
                        return false;
                    } else {
                        Combatant var4x = this.byEntity.get(var3x.getUniqueId());
                        return var4x != null && var4x != var2 && !var4x.hidden && this.canTarget(var2, var4x);
                    }
                });
                if (var5 != null && var5.getHitEntity() != null) {
                    Combatant var6 = this.byEntity.get(var5.getHitEntity().getUniqueId());
                    if (var6 != null) {
                        if (!this.inRange(var2, var1.getLocation(), var6, var3.range)) {
                            GameManager.actionbar(var1, "§c사거리 밖 §7(" + String.format("%.1f", var3.range) + "블록)");
                        } else {
                            var2.nextAttack = this.now() + var3.hitTicks();
                            this.swingAnimAt.put(var1.getUniqueId(), var2.nextAttack);
                            this.attack(var2, var6);
                            return;
                        }
                    }
                }

                // 허공 / 사거리 밖: 데미지는 없지만 공격 모션은 보여 줌 (연타해도 공격 속도만큼만)
                if (var2.modeled && this.now() >= this.swingAnimAt.getOrDefault(var1.getUniqueId(), 0L)) {
                    this.swingAnimAt.put(var1.getUniqueId(), this.now() + Math.max(6L, var3.hitTicks()));
                    this.gm.models.anim(var1, "attack");
                }
            }
        }
    }

    /** 플레이어 유닛 휘두르기 모션 다음 가능 틱 */
    private final Map<UUID, Long> swingAnimAt = new HashMap<>();

    private void playerUnitDied(Combatant var1, boolean var2) {
        UUID var3 = var1.playerId;
        this.byEntity.remove(var3);
        this.gm.activeUnits.remove(var3);
        Player var4 = Bukkit.getPlayer(var3);
        GameTeam var5 = this.gm.teams.get(var1.team);
        if (var4 != null) {
            this.gm.models.anim(var4, "death");
            this.gm.models.remove(var4);
            this.gm.resetPlayer(var4);
            try {
                var4.removePotionEffect(org.bukkit.potion.PotionEffectType.INVISIBILITY);
                var4.removePotionEffect(org.bukkit.potion.PotionEffectType.JUMP_BOOST);
            } catch (Throwable ignored) {
            }
            var4.setGameMode(GameMode.SPECTATOR);
            var4.teleport(this.A().spectate(var1.team));
        }

        if (this.gm.test.isAdmin(var3)) {
            this.gm.test.unitDied(var3);
        } else {
            if (this.gm.assault) {
                if (var4 != null) {
                    var4.sendTitle("§c쓰러졌습니다", "§7남은 아군을 응원하세요 (관전)", 0, 40, 10);
                }
            } else if (var2 && var5 != null && var5.members.contains(var3) && !var5.queue.contains(var3)) {
                var5.queue.addLast(var3);
                if (var4 != null) {
                    var4.sendTitle("§c쓰러졌습니다", "§f대기열 §e" + var5.queuePos(var3) + "번째", 0, 40, 10);
                }
            }
        }
    }

    void playerLeft(Player var1) {
        Combatant var2 = this.byEntity.get(var1.getUniqueId());
        if (var2 != null && var2.kind == Combatant.Kind.TROOP && !var2.dead) {
            var2.dead = true;
            var2.hp = 0.0;
            this.playerUnitDied(var2, false);
        }

        this.reserved.remove(var1.getUniqueId());

        for (Combatant var4 : this.all) {
            if (var1.getUniqueId().equals(var4.reservedPlayer)) {
                var4.reservedPlayer = null;
            }
        }
    }

    Combatant unitOf(UUID var1) {
        Combatant var2 = this.byEntity.get(var1);
        return var2 != null && var2.isPlayer() && var2.alive() ? var2 : null;
    }

    boolean isReserved(UUID var1) {
        return this.reserved.contains(var1);
    }

    List<Combatant> playerUnits(TeamColor var1) {
        ArrayList var2 = new ArrayList();

        for (Combatant var4 : this.all) {
            if (var4.team == var1 && var4.isPlayer() && var4.alive()) {
                var2.add(var4);
            }
        }

        return var2;
    }

    boolean isGameEntity(Entity var1) {
        return this.byEntity.containsKey(var1.getUniqueId());
    }

    boolean frozen(Combatant var1) {
        return this.now() < var1.deployUntil || this.now() < var1.stunUntil;
    }

    void refreshName(Combatant var1) {
        LivingEntity var2 = var1.label != null ? var1.label : var1.mob;
        if (var2 != null) {
            if (this.gm.hpDisplays) {
                var2.setCustomNameVisible(false);
            } else {
                int var3 = (int)Math.ceil(Math.max(0.0, var1.hp));
                String var4;
                if (var1.isTower()) {
                    var4 = var1.displayName() + (var1.kind == Combatant.Kind.KING_TOWER && !var1.active ? " §8(비활성)" : "") + " " + hpBar(var1) + " §f" + var3;
                } else {
                    var4 = var1.team.cc + (var1.card == null ? "" : (var1.kind == Combatant.Kind.BARREL ? "해골통" : var1.card.name)) + " §f" + var3;
                }

                var2.setCustomName(var4);
            }
        }
    }

    private static String hpBar(Combatant var0) {
        byte var1 = 10;
        int var2 = (int)Math.round(var1 * Math.max(0.0, var0.hp) / var0.maxHp);
        StringBuilder var3 = new StringBuilder("§a");

        for (int var4 = 0; var4 < var1; var4++) {
            if (var4 == var2) {
                var3.append("§8");
            }

            var3.append('|');
        }

        return var3.toString();
    }

    void clearAll() {
        this.glowBase.clear();
        this.glowLevel.clear();
        this.sweepDeployMarks(true);
        for (BukkitRunnable var2 : new ArrayList<>(this.running)) {
            try {
                var2.cancel();
            } catch (IllegalStateException var5) {
            }
        }

        for (Battle.Outline o : this.outlines.values()) {
            for (BlockDisplay d : o.bars) {
                d.remove();
            }
        }

        this.outlines.clear();
        this.running.clear();
        this.zones.clear();
        this.reserved.clear();
        this.bars.clear();
        this.fx.clear();

        for (Combatant var7 : this.all) {
            if (var7.isTower()) {
                this.clearTowerBlocks(var7, false);
                if (var7.hitbox != null) {
                    var7.hitbox.remove();
                }

                if (var7.label != null) {
                    var7.label.remove();
                }

                for (Entity var4 : var7.extras) {
                    this.gm.models.remove(var4);
                    var4.remove();
                }
            } else if (!var7.isPlayer()) {
                this.removeBody(var7);
            }
        }

        this.all.clear();
        this.byEntity.clear();
    }

    Combatant testPlayerUnit(GameTeam var1, CardDef var2, Player var3, Location var4) {
        return this.spawnPlayerUnit(var1, var2, var3, var4, var2.deployTicks());
    }

    int clearUnits(TeamColor var1) {
        int var2 = 0;

        for (Combatant var4 : new ArrayList<>(this.all)) {
            if (!var4.isTower() && !var4.isPlayer() && !var4.dead && (var1 == null || var4.team == var1)) {
                var4.dead = true;
                var4.hp = 0.0;
                if (var4.reservedPlayer != null) {
                    this.reserved.remove(var4.reservedPlayer);
                    var4.reservedPlayer = null;
                }

                this.removeBody(var4);
                var2++;
            }
        }

        this.all.removeIf(var0 -> var0.dead && !var0.isTower());
        if (var1 == null) {
            this.zones.clear();
        }

        return var2;
    }

    Combatant towerOf(TeamColor var1, String var2) {
        switch (var2) {
            case "king":
                return this.tower(var1, Combatant.Kind.KING_TOWER, false);
            case "left":
                return this.tower(var1, Combatant.Kind.PRINCESS_TOWER, true);
            case "right":
                return this.tower(var1, Combatant.Kind.PRINCESS_TOWER, false);
            default:
                return null;
        }
    }

    int healTowers() {
        int var1 = 0;

        for (Combatant var3 : this.all) {
            if (var3.isTower() && var3.alive()) {
                var3.hp = var3.maxHp;
                this.refreshName(var3);
                var1++;
            }
        }

        return var1;
    }

    void rebuild() {
        this.clearAll();
        this.buildTowers();
    }

    void drawHitboxes(Player var1, boolean var2) {
        for (Combatant var4 : this.all) {
            if (var4.alive()) {
                Location var5 = var4.loc();
                if (var5 != null && var5.getWorld() == var1.getWorld()) {
                    double var6;
                    double var8;
                    if (var4.isTower()) {
                        var6 = var4.radius;
                        var8 = var4.kind == Combatant.Kind.KING_TOWER ? 6.0 * KING_S : 5.0 * PRIN_S;
                    } else if (var4.kind == Combatant.Kind.BUILDING) {
                        var6 = var4.card.hitboxW / 2.0;
                        var8 = var4.card.hitboxH;
                    } else {
                        var6 = var4.radius;
                        var8 = var4.card == null ? 2.0 : var4.card.hitboxH;
                    }

                    Color var10 = var4.team == TeamColor.BLUE ? Color.fromRGB(70, 140, 255) : Color.fromRGB(255, 70, 70);
                    DustOptions var11 = new DustOptions(var10, 0.7F);
                    double var12 = var5.getY();
                    int var14 = Math.max(8, (int)(var6 * 10.0));

                    for (int var15 = 0; var15 < var14; var15++) {
                        double var16 = (Math.PI * 2) * var15 / var14;
                        double var18 = var5.getX() + Math.cos(var16) * var6;
                        double var20 = var5.getZ() + Math.sin(var16) * var6;
                        var1.spawnParticle(Particle.DUST, var18, var12 + 0.05, var20, 1, 0.0, 0.0, 0.0, 0.0, var11);
                        var1.spawnParticle(Particle.DUST, var18, var12 + var8, var20, 1, 0.0, 0.0, 0.0, 0.0, var11);
                    }

                    for (int var22 = 0; var22 < 4; var22++) {
                        double var24 = (Math.PI / 2) * var22;

                        for (double var26 = 0.0; var26 <= var8; var26 += 0.5) {
                            var1.spawnParticle(
                                Particle.DUST,
                                var5.getX() + Math.cos(var24) * var6,
                                var12 + var26,
                                var5.getZ() + Math.sin(var24) * var6,
                                1,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                var11
                            );
                        }
                    }

                    if (var2 && var4.isStructure()) {
                        // 타워·건물 사거리: 히트박스(사각형) 끝에서 사거리만큼 바깥 (모서리는 둥글게)
                        double R = var4.isTower() ? (var4.kind == Combatant.Kind.KING_TOWER ? this.gm.kingRange : this.gm.princessRange)
                            : (var4.card != null ? var4.card.range : 0.0);
                        double[] bx = this.structBox(var4);
                        if (bx != null && R > 0.0) {
                            DustOptions ro = new DustOptions(Color.fromRGB(255, 220, 80), 0.9F);
                            double cx = (bx[0] + bx[2]) / 2.0, cz = (bx[1] + bx[3]) / 2.0, hx = (bx[2] - bx[0]) / 2.0, hz = (bx[3] - bx[1]) / 2.0;
                            int nseg = Math.max(48, (int)((hx + hz + R) * 8.0));
                            for (int k = 0; k < nseg; k++) {
                                double an = Math.PI * 2.0 * k / nseg;
                                double ux = Math.cos(an), uz = Math.sin(an);
                                double px = cx + Math.signum(ux) * hx + ux * R, pz = cz + Math.signum(uz) * hz + uz * R;
                                var1.spawnParticle(Particle.DUST, px, var12 + 0.2, pz, 1, 0.0, 0.0, 0.0, 0.0, ro);
                            }
                        }
                    }

                    if (var2 && var4.card != null && var4.card.range > 0.0 && !var4.isTower() && !var4.isStructure()) {
                        DustOptions var23 = new DustOptions(Color.fromRGB(255, 220, 80), 0.6F);
                        double var25 = var4.card.range + var6;
                        int var27 = Math.max(12, (int)(var25 * 6.0));

                        for (int var19 = 0; var19 < var27; var19++) {
                            double var28 = (Math.PI * 2) * var19 / var27;
                            var1.spawnParticle(
                                Particle.DUST,
                                var5.getX() + Math.cos(var28) * var25,
                                var12 + 0.15,
                                var5.getZ() + Math.sin(var28) * var25,
                                1,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                var23
                            );
                        }
                    }
                }
            }
        }
    }

    // ===================== 프린스 돌진 =====================

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

    /** 유닛·건물 모델 적용 + 팀 색 테두리 발광 (config game.team-glow) */
    private boolean applyUnit(org.bukkit.entity.Entity e, String model, boolean hideBase, Color c) {
        boolean ok = this.gm.models.apply(e, model, hideBase, c);
        if (ok && c != null && this.gm.plugin.getConfig().getBoolean("game.team-glow", true)
            && (!this.gm.assault || this.gm.plugin.getConfig().getBoolean("assault.team-glow", false))) {
            // 테두리 세기: 색을 어둡게 해서 약하게 (config game.team-glow-strength, 0~1)
            this.glowBase.put(e, c);
            this.glowLevel.remove(e.getUniqueId());
            this.refreshGlow(e, c);
        }
        return ok;
    }

    /** 발광 테두리 원래 색 (거리에 따라 다시 칠함) */
    private final java.util.Map<org.bukkit.entity.Entity, Color> glowBase = new java.util.HashMap<>();
    private final java.util.Map<java.util.UUID, Integer> glowLevel = new java.util.HashMap<>();

    /**
     * 테두리는 화면에서 굵기가 같아서 멀리 있을수록 모델에 비해 진해 보임
     * → 가장 가까운 플레이어와의 거리만큼 색을 낮춰서 어디서 봐도 비슷하게 연하게 (config game.team-glow-near)
     */
    private void refreshGlow(org.bukkit.entity.Entity e, Color c) {
        org.bukkit.configuration.file.FileConfiguration cfg = this.gm.plugin.getConfig();
        double k = Math.max(0.05, Math.min(1.0, cfg.getDouble("game.team-glow-strength", 0.45)));
        double near = Math.max(1.0, cfg.getDouble("game.team-glow-near", 12.0));
        double best = Double.MAX_VALUE;
        Location el = e.getLocation();
        for (Player p : el.getWorld().getPlayers()) {
            if (p.equals(e)) {
                continue;
            }
            double d = p.getEyeLocation().distanceSquared(el);
            if (d < best) {
                best = d;
            }
        }
        double dist = best == Double.MAX_VALUE ? near : Math.sqrt(best);
        double f = Math.max(0.25, Math.min(1.0, near / Math.max(near, dist)));
        int level = (int)Math.round(k * f * 40.0);
        Integer prev = this.glowLevel.get(e.getUniqueId());
        if (prev != null && prev == level) {
            return;
        }
        this.glowLevel.put(e.getUniqueId(), level);
        double m = level / 40.0;
        this.gm.models.glow(e, Color.fromRGB((int)(c.getRed() * m), (int)(c.getGreen() * m), (int)(c.getBlue() * m)));
    }

    private void refreshGlows() {
        java.util.Iterator<java.util.Map.Entry<org.bukkit.entity.Entity, Color>> it = this.glowBase.entrySet().iterator();
        while (it.hasNext()) {
            java.util.Map.Entry<org.bukkit.entity.Entity, Color> en = it.next();
            if (!en.getKey().isValid()) {
                this.glowLevel.remove(en.getKey().getUniqueId());
                it.remove();
            } else {
                this.refreshGlow(en.getKey(), en.getValue());
            }
        }
    }

    /** 죽을 때 유닛이 나오는 카드 중 부서지는 모션이 있는 것 (배틀 램, 고블린 우리) → 모션 길이만큼 기다림 (틱) */
    /** 라바 하운드가 터질 때: 펍들을 가운데서 만들고 8틱 동안 사방(1.5타일)으로 튀어나가게 */
    private void burstSpawn(TeamColor tm, CardDef pc, Location c, int n) {
        World w = this.A().world;
        Arena ar = this.A();
        double R = 1.5 * CardDef.TILE;
        double a0 = this.gm.rng.nextDouble() * Math.PI * 2.0;
        Location mid = c.clone();
        mid.setY(this.airY());
        w.spawnParticle(Particle.EXPLOSION_EMITTER, mid, 1, 0.0, 0.0, 0.0, 0.0);
        w.spawnParticle(Particle.LAVA, mid, 40, 1.2, 0.8, 1.2, 0.0);
        w.playSound(mid, "entity.generic.explode", 1.2F, 1.3F);
        w.playSound(mid, "entity.magma_cube.jump", 1.2F, 0.7F);
        for (int i = 0; i < n; i++) {
            double a = a0 + Math.PI * 2.0 * i / n;
            double tx = Math.max(ar.minX + 1.5, Math.min(ar.minX + Arena.HX * 2 - 1.5, mid.getX() + Math.cos(a) * R));
            double tz = Math.max(ar.minZ + 1.5, Math.min(ar.minZ + Arena.HZ * 2 - 1.5, mid.getZ() + Math.sin(a) * R));
            Combatant u = this.spawnAi(tm, pc, mid.clone(), 12);
            u.leader = null;
            LivingEntity m = u.mob;
            if (m == null) {
                continue;
            }
            Location from = m.getLocation().clone();
            for (int t = 1; t <= 8; t++) {
                double f = t / 8.0;
                double e = 1.0 - (1.0 - f) * (1.0 - f);
                double lift = Math.sin(f * Math.PI) * 2.2;
                this.fx.later(t, () -> {
                    if (!m.isValid() || !u.alive() || this.gm.phase != GameManager.Phase.PLAYING) {
                        return;
                    }
                    Location p = from.clone().add((tx - from.getX()) * e, lift, (tz - from.getZ()) * e);
                    p.setYaw(m.getLocation().getYaw());
                    m.teleport(p);
                    w.spawnParticle(Particle.FLAME, p.clone().add(0.0, 0.4, 0.0), 3, 0.1, 0.1, 0.1, 0.01);
                    w.spawnParticle(Particle.LAVA, p.clone().add(0.0, 0.4, 0.0), 1, 0.05, 0.05, 0.05, 0.0);
                });
            }
        }
    }

    static long deathSpawnDelay(CardDef d) {
        if (d == null || d.deathSpawn.isEmpty()) {
            return 0L;
        }
        return d.id.equals("battle_ram") ? 18L : (d.id.equals("goblin_cage") ? 20L : 0L);
    }

    /** 평면에서 (x, z) 에서 (dx, dz) 방향으로 갈 때 상자 [minX, minZ, maxX, maxZ] 에 닿는 거리 (안 닿으면 -1) */
    static double rayBoxEnter(double x, double z, double dx, double dz, double[] b) {
        double t0 = -1.0E9, t1 = 1.0E9;
        double[] o = {x, z}, d = {dx, dz}, lo = {b[0], b[1]}, hi = {b[2], b[3]};
        for (int i = 0; i < 2; i++) {
            if (Math.abs(d[i]) < 1.0E-9) {
                if (o[i] < lo[i] || o[i] > hi[i]) {
                    return -1.0;
                }
            } else {
                double a = (lo[i] - o[i]) / d[i], c = (hi[i] - o[i]) / d[i];
                t0 = Math.max(t0, Math.min(a, c));
                t1 = Math.min(t1, Math.max(a, c));
            }
        }
        return t1 >= t0 && t1 >= 0.0 ? Math.max(0.0, t0) : -1.0;
    }

    private boolean reflecting;

    /** 일렉트로 드래곤: 대상에서 가까운 다른 적에게 번개가 차례로 튐 */
    private void chainZap(Combatant src, Combatant first, double dmg, int n, double range) {
        Set<Integer> hit = new HashSet<>();
        hit.add(first.id);
        Combatant prev = first;
        for (int i = 0; i < n; i++) {
            Location pl = prev.loc();
            if (pl == null) {
                break;
            }
            Combatant best = null;
            double bd = range;
            for (Combatant e : this.all) {
                if (!e.alive() || e.hidden || e.team == src.team || hit.contains(e.id) || !this.canTarget(src, e)) {
                    continue;
                }
                Location el = e.loc();
                if (el != null && flat(el, pl) < bd) {
                    bd = flat(el, pl);
                    best = e;
                }
            }
            if (best == null) {
                break;
            }
            Location a = this.aim(prev), z = this.aim(best);
            if (a != null && z != null) {
                this.fx.lightning(a, z, true);
                this.A().world.spawnParticle(Particle.ELECTRIC_SPARK, z, 10, 0.3, 0.3, 0.3, 0.1);
            }
            hit.add(best.id);
            this.damage(best, dmg, src);
            this.stun(best, src.card.stun);
            prev = best;
        }
    }

    /**
     * 플레이어가 유닛이 됐을 때: 모델만 보이게 플레이어 몸은 투명(입자 없음), 점프 못 하게 (점프 강화 250 = 점프 불가).
     * 2.5초짜리 효과를 1초마다 갱신 → 유닛이 끝나면 저절로 풀림.
     */
    /** 유닛 플레이어가 F 키로 자기 모델 보기/숨기기 */
    void toggleSelfModel(Player p) {
        Combatant c = this.byEntity.get(p.getUniqueId());
        if (c == null || !c.modeled) {
            return;
        }
        c.selfModel = !c.selfModel;
        this.gm.models.selfView(p, c.selfModel);
        p.sendActionBar("§f내 모델 " + (c.selfModel ? "§a보기" : "§7숨김"));
    }

    private void playerUnitBody(Combatant c, Player p) {
        try {
            if (c.modeled) {
                // 투명 효과는 쓰면 안 됨: BetterModel 이 투명한 플레이어의 모델을 숨겨 버림 (몸은 BetterModel 이 패킷으로 숨김)
                p.removePotionEffect(org.bukkit.potion.PotionEffectType.INVISIBILITY);
                p.setInvisible(false);
                this.gm.models.selfView(p, c.selfModel);
            }
            p.addPotionEffect(new org.bukkit.potion.PotionEffect(org.bukkit.potion.PotionEffectType.JUMP_BOOST, 50, 250, false, false, false));
        } catch (Throwable ignored) {
        }
    }

    /** 배치 시간 타이머: 배치 중인 유닛 위에 크게 (어두운 배경 + 시계 + 남은 초 + 진행 막대) */
    /** 배치 타이머 표시 → 마지막으로 갱신된 틱 (주인이 사라져도 안 남게 따로 관리) */
    private final Map<org.bukkit.entity.TextDisplay, Long> deployMarks = new HashMap<>();

    /** 몇 틱 동안 갱신 안 된 배치 타이머는 지움 (유닛이 사라졌거나 게임이 끝난 경우) */
    private void sweepDeployMarks(boolean all) {
        long now = this.now();
        var it = this.deployMarks.entrySet().iterator();
        while (it.hasNext()) {
            var e = it.next();
            if (all || now - e.getValue() > 4L || !e.getKey().isValid()) {
                if (e.getKey().isValid()) {
                    e.getKey().remove();
                }
                it.remove();
            }
        }
    }

    private void deployTimer(Combatant c) {
        long now = this.now();
        if (now < c.deployUntil && !c.dead) {
            Location l = c.loc();
            if (l == null) {
                return;
            }
            if (c.deployMark != null) {
                this.deployMarks.put(c.deployMark, now);
            }
            l.add(0.0, (c.card == null ? 1.6 : c.card.barHeight) + 1.3, 0.0);
            if (c.deployMark == null || !c.deployMark.isValid()) {
                org.bukkit.entity.TextDisplay t = (org.bukkit.entity.TextDisplay)this.A().world.spawn(l, org.bukkit.entity.TextDisplay.class);
                t.addScoreboardTag("clashmc");
                t.setPersistent(false);
                t.setBillboard(org.bukkit.entity.Display.Billboard.CENTER);
                t.setBackgroundColor(Color.fromARGB(150, 16, 20, 40));
                t.setShadowed(true);
                t.setSeeThrough(true);
                t.setLineWidth(200);
                t.setBrightness(new Brightness(15, 15));
                t.setTransformation(new org.bukkit.util.Transformation(new org.joml.Vector3f(0.0F, 0.0F, 0.0F), new org.joml.Quaternionf(),
                    new org.joml.Vector3f(1.7F, 1.7F, 1.7F), new org.joml.Quaternionf()));
                c.deployMark = t;
                this.deployMarks.put(t, now);
                c.deployTotal = Math.max(1L, c.deployUntil - now);
            } else if (now % 2L == 0L) {
                c.deployMark.teleport(l);
            }
            if (now % 2L == 0L) {
                long left = c.deployUntil - now;
                int filled = (int)Math.max(0L, Math.min(10L, 10L - left * 10L / Math.max(1L, c.deployTotal)));
                c.deployMark.setText("§e§l⏱ §f§l" + String.format("%.1f", left / 20.0) + "\n§a" + "▮".repeat(filled) + "§8" + "▮".repeat(10 - filled));
            }
        } else if (c.deployMark != null) {
            if (c.deployMark.isValid()) {
                c.deployMark.remove();
            }
            c.deployMark = null;
        }
    }

    /** 스턴: 스턴된 동안 머리 둘레로 전기 별이 빙글빙글 */
    private void stunFx(Combatant c) {
        long now = this.now();
        if (now >= c.stunUntil || now % 2L != 0L) {
            return;
        }
        Location l = c.loc();
        if (l == null) {
            return;
        }
        double h = (c.card == null ? 1.6 : c.card.hitboxH) + 0.25;
        double r = Math.max(0.45, c.radius * 0.9);
        World w = this.A().world;
        for (int k = 0; k < 3; k++) {
            double a = now * 0.35 + k * Math.PI * 2 / 3;
            Location p = l.clone().add(Math.cos(a) * r, h, Math.sin(a) * r);
            w.spawnParticle(Particle.DUST, p, 1, 0.0, 0.0, 0.0, 0.0, new DustOptions(Color.fromRGB(255, 230, 80), 1.1F));
            w.spawnParticle(Particle.ELECTRIC_SPARK, p, 1, 0.03, 0.03, 0.03, 0.0);
        }
    }

    /**
     * 일렉트로 자이언트 "전기 팩": 2.5타일 안에서 자기를 때린 적을 맞은 횟수만큼 기억해 뒀다가 한 명씩 차례로 전기로 되갚음
     * (1대 맞으면 1번, 2대면 2번 / 범위 공격 아님 / 아무도 안 때리면 아무 일 없음). 같은 공격의 여러 발(산탄)은 1대로.
     */
    private void reflect(Combatant giant, Combatant attacker) {
        Location gl = giant.loc(), al = attacker.isStructure() && attacker.fixed != null ? attacker.fixed : attacker.loc();
        if (gl == null || al == null || flat(gl, al) - attacker.radius - giant.radius > giant.card.reflectRange) {
            return;
        }
        long key = (long)giant.id * 1000003L + attacker.id;
        Long last = this.reflectCd.get(key);
        if (last != null && this.now() - last < 3L) {
            return;
        }
        this.reflectCd.put(key, this.now());
        if (this.reflectCd.size() > 512) {
            this.reflectCd.entrySet().removeIf(e -> this.now() - e.getValue() > 40L);
        }
        giant.reflectQueue.add(attacker);
    }

    private final java.util.Map<Long, Long> reflectCd = new java.util.HashMap<>();

    /** 쌓인 반격을 0.25초에 한 명씩 처리 */
    private void tickReflect(Combatant giant) {
        if (giant.reflectQueue.isEmpty() || this.now() < giant.nextReflect || this.now() < giant.stunUntil) {
            return;
        }
        Location gl = giant.loc();
        while (!giant.reflectQueue.isEmpty()) {
            Combatant a = giant.reflectQueue.poll();
            Location al = a.isStructure() && a.fixed != null ? a.fixed : a.loc();
            if (gl == null || al == null || !a.alive() || flat(gl, al) - a.radius - giant.radius > giant.card.reflectRange + 1.0) {
                continue;                                                    // 죽었거나 멀어진 공격자는 건너뜀
            }
            giant.nextReflect = this.now() + 5L;
            this.reflecting = true;
            try {
                World w = this.A().world;
                Location chest = gl.clone().add(0.0, giant.card.hitboxH * 0.75, 0.0);
                Location z = a.isStructure() ? al.clone().add(0.0, a.isTower() ? (a.kind == Combatant.Kind.KING_TOWER ? 4.0 * KING_S : 4.0 * PRIN_S) : 1.5, 0.0) : this.aim(a);
                if (z != null) {
                    this.fx.lightning(chest, z, true);
                    w.spawnParticle(Particle.ELECTRIC_SPARK, z, 16, 0.3, 0.3, 0.3, 0.12);
                }
                w.spawnParticle(Particle.ELECTRIC_SPARK, chest, 8, 0.5, 0.4, 0.5, 0.06);
                w.playSound(gl, "entity.bee.sting", 0.7F, 0.5F);
                this.damage(a, giant.card.reflectDamage, giant);
                this.stun(a, giant.card.reflectStun);
            } finally {
                this.reflecting = false;
            }
            return;
        }
    }

    /** 엄마 마녀: 맞은 부대에 저주 (보라 연기). 저주받은 채 죽으면 저주 호그로 */
    private void curse(Combatant t, Combatant src) {
        if (src == null || src.card == null || src.card.curseCard.isEmpty() || t == null || !t.alive() || t.kind != Combatant.Kind.TROOP
            || t.card == null || t.card.id.equals(src.card.curseCard)) {
            return;
        }
        t.cursedUntil = this.now() + Math.round(src.card.curseDuration * 20.0);
        t.cursedBy = src.team;
        t.curseInto = src.card.curseCard;
        Location l = t.loc();
        if (l != null) {
            this.A().world.spawnParticle(Particle.WITCH, l.clone().add(0.0, 1.0, 0.0), 12, 0.3, 0.4, 0.3, 0.02);
        }
    }

    /** 램 라이더: 가까운 부대에게 볼라를 던져 피해 + 강한 감속 */
    private void throwBola(Combatant c) {
        CardDef d = c.card;
        Location me = c.loc();
        if (me == null) {
            return;
        }
        Combatant best = null;
        double bd = d.bolaRange;
        for (Combatant e : this.all) {
            if (!e.alive() || e.hidden || e.team == c.team || e.kind != Combatant.Kind.TROOP || this.now() < e.snareUntil) {
                continue;
            }
            Location el = e.loc();
            if (el != null && flat(el, me) < bd) {
                bd = flat(el, me);
                best = e;
            }
        }
        c.nextBola = this.now() + Math.round(d.bolaEvery * 20.0);
        if (best == null) {
            return;
        }
        final Combatant tgt = best;
        final Entity body = c.isPlayer() ? c.player() : c.mob;
        this.gm.models.anim(body, "throw");
        final World w = this.A().world;
        final Location from = me.clone().add(0.0, d.hitboxH * 0.95, 0.0);
        w.playSound(from, "entity.snowball.throw", 1.0F, 0.6F);
        w.playSound(from, "item.trident.throw", 0.8F, 1.3F);
        // 손의 볼라는 던지는 동안 숨김 (날아가는 볼라가 따로 보임)
        this.gm.models.part(body, "bola", false);
        this.fx.later(18L, () -> {
            if (body != null && body.isValid()) {
                this.gm.models.part(body, "bola", true);
            }
        });
        // 날아가는 볼라: 볼라 모델 (빙글빙글 돌며 포물선)
        this.fx.shoot(Fx.Shot.SPEAR, from, () -> tgt.alive() ? this.aim(tgt) : null, p -> {
            if (this.gm.phase != GameManager.Phase.PLAYING) {
                return;
            }
            w.spawnParticle(Particle.BLOCK, p, 14, 0.3, 0.3, 0.3, 0.0, Material.HAY_BLOCK.createBlockData());
            w.playSound(p, "entity.leash_knot.place", 1.2F, 0.7F);
            w.playSound(p, "block.chain.place", 1.0F, 0.8F);
            if (tgt.alive()) {
                this.damage(tgt, d.bolaDamage, c);
                int dur = (int)Math.round(d.bolaDuration * 20.0);
                this.slow(tgt, d.bolaSlow, dur);
                tgt.snareUntil = this.now() + dur;
            }
        }, "clash_bola", c.team.color);
    }

    /** 볼라에 묶인 유닛: 발 주변을 도는 밧줄 + 돌 */
    private void snareFx(Combatant c) {
        if (this.now() >= c.snareUntil || this.now() % 2L != 0L) {
            return;
        }
        Location l = c.loc();
        if (l == null) {
            return;
        }
        World w = this.A().world;
        double r = Math.max(0.35, c.radius * 0.8);
        double y = (c.air ? l.getY() : this.groundY()) + 0.35;
        DustOptions rope = new DustOptions(Color.fromRGB(176, 136, 80), 0.9F);
        double base = this.now() * 0.4;
        for (int k = 0; k < 10; k++) {
            double a = base + Math.PI * 2 * k / 10;
            w.spawnParticle(Particle.DUST, new Location(w, l.getX() + Math.cos(a) * r, y + (k % 2) * 0.12, l.getZ() + Math.sin(a) * r), 1, 0.0, 0.0, 0.0, 0.0, rope);
        }
        w.spawnParticle(Particle.DUST, new Location(w, l.getX() + Math.cos(base) * r, y, l.getZ() + Math.sin(base) * r), 1, 0.0, 0.0, 0.0, 0.0, new DustOptions(Color.fromRGB(70, 66, 62), 1.4F));
    }

    /** 로켓병: 터진 자리 뒤로 불꽃이 부채꼴로 튀며 지나가는 적에게 피해 */
    private void sparks(Combatant src, Location from, Location at) {
        CardDef d = src.card;
        Vector fw = at.toVector().subtract(from.toVector()).setY(0.0);
        if (fw.lengthSquared() < 1.0E-4) {
            return;
        }
        fw.normalize();
        World w = this.A().world;
        w.spawnParticle(Particle.FIREWORK, at, 30, 0.3, 0.3, 0.3, 0.15);
        w.playSound(at, "entity.firework_rocket.blast", 1.0F, 1.0F);
        Set<Integer> hit = new HashSet<>();
        int n = d.sparks;
        for (int k = 0; k < n; k++) {
            double ang = Math.toRadians(n == 1 ? 0.0 : -30.0 + 60.0 * k / (n - 1));
            Vector dir = fw.clone().rotateAroundY(ang);
            for (double s = 0.4; s <= d.sparkRange; s += 0.4) {
                Location p = at.clone().add(dir.clone().multiply(s));
                w.spawnParticle(Particle.DUST, p, 1, 0.02, 0.02, 0.02, 0.0, new DustOptions(k % 2 == 0 ? Color.fromRGB(255, 200, 60) : Color.fromRGB(80, 170, 255), 1.0F));
                for (Combatant e : this.area(p, 0.5, src.team.other(), true, true)) {
                    if (!hit.contains(e.id) && this.canTarget(src, e)) {
                        hit.add(e.id);
                        this.damage(e, d.sparkDamage, src);
                    }
                }
            }
        }
    }

    /** 타워 모델 배율 (킹 4x4타일=12블록, 프린세스 3x3타일=9블록) */
    static final double KING_S = 1.8007, PRIN_S = 1.4529;
    static final double PRINCESS_TOP_Y = 78.0 / 16.0 * PRIN_S;

    /** 타워 꼭대기 프린세스가 대상 쪽으로 몸을 돌림 (한 틱에 최대 20도) */
    private void turnTop(Combatant tw, Combatant tgt) {
        ArmorStand top = tw.turret;
        if (top == null || !top.isValid() || tgt == null) {
            return;
        }
        Location tl = tgt.loc();
        if (tl == null) {
            return;
        }
        Vector v = tl.toVector().subtract(tw.fixed.toVector()).setY(0.0);
        if (v.lengthSquared() < 1.0E-4) {
            return;
        }
        float want = (float)Math.toDegrees(Math.atan2(-v.getX(), v.getZ()));
        float cur = top.getLocation().getYaw();
        float d = ((want - cur) % 360.0F + 540.0F) % 360.0F - 180.0F;
        if (Math.abs(d) < 0.5F) {
            return;
        }
        Location l = tw.fixed.clone().add(0.0, PRINCESS_TOP_Y, 0.0);
        l.setYaw(cur + Math.max(-20.0F, Math.min(20.0F, d)));
        l.setPitch(0.0F);
        top.teleport(l);
    }

    /** 3.6.0 부터 clash_princess 는 프린세스 카드 유닛 → 예전 설정값이면 타워 모델로 */
    static String ptower(String m) {
        return "clash_princess".equals(m) ? "clash_princess_tower" : m;
    }

    // ===================== 탑뷰 =====================

    boolean inTopView(Player p) {
        return this.topView.contains(p.getUniqueId());
    }

    /** 경기장 가운데 상공, 바로 아래를 봄. 자기 팀 쪽이 화면 아래 */
    Location topViewLoc(TeamColor t) {
        Arena a = this.A();
        Location l = new Location(a.world, a.px + 0.5, a.floorY + 1 + this.topViewHeight, a.pz + 0.5);
        l.setYaw(t == TeamColor.BLUE ? 0.0F : 180.0F);
        l.setPitch(90.0F);
        return l;
    }

    /** 탑뷰 이동 제한: x·높이는 고정, z 는 경기장 앞뒤로 (config game.top-view.scroll, 기본 30칸) */
    Location topViewClamp(TeamColor t, Location to) {
        Location l = this.topViewLoc(t);
        double r = this.gm.plugin.getConfig().getDouble("game.top-view.scroll", 80.0);
        if (r > 0.0) {
            r = Math.max(r, 80.0); // 킹 타워 뒤까지 충분히 (예전 config 62 도 80 으로)
        }
        double z = Math.max(l.getZ() - r, Math.min(l.getZ() + r, to.getZ()));
        l.setZ(z);
        return l;
    }

    void toggleTopView(Player p, GameTeam team) {
        if (!this.topViewOn) {
            p.sendActionBar("§c탑뷰가 꺼져 있습니다 (config game.top-view.enabled)");
        } else if (this.topView.remove(p.getUniqueId())) {
            p.teleport(this.A().balcony(team.color));
            p.setFlySpeed((float)Math.max(0.01, Math.min(1.0, this.gm.kingFlySpeed)));
            if (this.gm.kingFly) {
                p.setAllowFlight(true);
                p.setFlying(true);
            } else {
                p.setFlying(false);
                p.setAllowFlight(false);
            }

            p.playSound(p.getLocation(), "entity.ender_dragon.flap", 0.6F, 1.4F);
            p.sendActionBar("§7지휘대 시점 §8| §fF§7: 탑뷰");
        } else {
            this.topView.add(p.getUniqueId());
            p.setAllowFlight(true);
            p.setFlying(true);
            // 탑뷰는 높이 떠 있어서 기본 비행 속도로는 너무 느림 (config game.top-view.fly-speed, 마크 기본 0.1)
            p.setFlySpeed((float)Math.max(0.01, Math.min(1.0, this.gm.plugin.getConfig().getDouble("game.top-view.fly-speed", 0.35))));
            p.teleport(this.topViewLoc(team.color));
            p.playSound(p.getLocation(), "entity.ender_dragon.flap", 0.6F, 0.8F);
            p.sendActionBar("§b§l탑뷰 §7바라보는 칸에 카드 사용 §8| §fWASD§7: 앞뒤 이동 §8| §fF§7: 돌아가기");
        }
    }

    /** 이번 틱에 모인 이동을 한 번에 텔레포트 (바뀐 게 거의 없으면 안 보냄) */
    private void flushMoves() {
        for (Combatant c : this.all) {
            Location to = c.pendingMove;
            if (to == null) {
                continue;
            }

            c.pendingMove = null;
            if (c.dead || c.mob == null || !c.mob.isValid()) {
                continue;
            }

            Location cur = c.mob.getLocation();
            double ddx = to.getX() - cur.getX();
            double ddy = to.getY() - cur.getY();
            double ddz = to.getZ() - cur.getZ();
            float dyaw = Math.abs(((to.getYaw() - cur.getYaw()) % 360.0F + 540.0F) % 360.0F - 180.0F);
            if (ddx * ddx + ddy * ddy + ddz * ddz > 4.0E-6 || dyaw > 1.0F) {
                c.mob.teleport(to);
            }
        }
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

    /** 위치가 살아 있는 타워/건물 사각형 안인지 */
    private boolean insideTowerBox(Location l) {
        for (Combatant c : this.all) {
            if (!c.alive()) {
                continue;
            }
            double[] b = this.structBox(c);
            if (b != null && l.getX() > b[0] && l.getX() < b[2] && l.getZ() > b[1] && l.getZ() < b[3]) {
                return true;
            }
        }
        return false;
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

    /**
     * 오두막·무덤·죽으면 나오는 유닛이 강물 위에 생기지 않게:
     * 무리 가운데가 다리 위면 다리 폭 안으로, 아니면 가운데가 있는 쪽 강둑으로 (가운데가 강이면 자기 진영 쪽)
     */
    private Location dryLand(TeamColor team, Location center, Location l) {
        Arena a = this.A();
        double z0 = a.riverMinZ(), z1 = a.riverMaxZ();
        if (l.getZ() <= z0 - 0.4 || l.getZ() >= z1 + 0.4) {
            return l;
        }
        Location o = l.clone();
        boolean centerInRiver = center.getZ() > z0 - 0.4 && center.getZ() < z1 + 0.4;
        if (centerInRiver && a.onBridge(center.getX())) {
            double half = a.bridgeHalf() - 0.5;
            double bx = Math.abs(center.getX() - a.bridgeX(true)) < Math.abs(center.getX() - a.bridgeX(false)) ? a.bridgeX(true) : a.bridgeX(false);
            o.setX(Math.max(bx - half, Math.min(bx + half, o.getX())));
            return o;
        }
        if (!this.inRiverOffBridge(o.getX(), o.getZ()) && a.onBridge(o.getX())) {
            return o;
        }
        boolean low;
        if (centerInRiver) {
            low = team.dir > 0; // 파랑은 z 작은 쪽이 자기 진영
        } else {
            low = center.getZ() < z0;
        }
        o.setZ(low ? z0 - 0.7 : z1 + 0.7);
        return o;
    }

    /** 다리 밖 강물 안이면 빠져나갈 곳 (가까운 강둑 또는 다리 위), 아니면 null */
    private Location riverExit(Location l) {
        if (l == null || !this.inRiverOffBridge(l.getX(), l.getZ())) {
            return null;
        }
        Arena a = this.A();
        double z0 = a.riverMinZ(), z1 = a.riverMaxZ();
        double bankZ = l.getZ() - z0 < z1 - l.getZ() ? z0 - 0.7 : z1 + 0.7;
        double bankD = Math.abs(bankZ - l.getZ());
        double half = a.bridgeHalf() - 0.6;
        double bx = Math.abs(l.getX() - a.bridgeX(true)) < Math.abs(l.getX() - a.bridgeX(false)) ? a.bridgeX(true) : a.bridgeX(false);
        double bridgeEdge = l.getX() < bx ? bx - half : bx + half;
        double bridgeD = Math.abs(bridgeEdge - l.getX());
        Location o = l.clone();
        if (bridgeD < bankD) {
            o.setX(bridgeEdge);
        } else {
            o.setZ(bankZ);
        }
        return o;
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

            if (c.dashUntil > this.now()) {
                continue;
            }

            if (!c.isPlayer() && (c.mob == null || !c.mob.isValid())) {
                continue;
            }

            Location l = !c.isPlayer() && c.pendingMove != null ? c.pendingMove : c.loc();
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

        // 유닛끼리 미는 양은 한 틱에 너무 크지 않게, 아주 작은 밀기는 무시 (제자리 떨림 / 쓸데없는 패킷 방지)
        for (int i = 0; i < n; i++) {
            double len = Math.sqrt(dx[i] * dx[i] + dz[i] * dz[i]);
            if (len < 0.025) {
                dx[i] = 0.0;
                dz[i] = 0.0;
            } else if (len > this.collideMaxPush) {
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
                c.pendingMove = to;
            }
        }
    }

    private static double flat(Location var0, Location var1) {
        if (var0 != null && var1 != null) {
            double var2 = var0.getX() - var1.getX();
            double var4 = var0.getZ() - var1.getZ();
            return Math.sqrt(var2 * var2 + var4 * var4);
        } else {
            return Double.MAX_VALUE;
        }
    }

    private static final class Zone {
        TeamColor team;
        CardDef card;
        Location center;
        long until;
        long nextTick;
        int ticksLeft = -1;
        List<BlockDisplay> disc;
    }
}
