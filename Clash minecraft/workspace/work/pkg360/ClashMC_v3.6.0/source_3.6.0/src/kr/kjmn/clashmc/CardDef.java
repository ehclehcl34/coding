package kr.kjmn.clashmc;

import java.util.ArrayList;
import java.util.List;
import org.bukkit.Material;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.entity.EntityType;

public final class CardDef {
    public final String id;
    public final String name;
    public final int elixir;
    public final CardDef.Type type;
    public final int count;
    public final double hp;
    public final double damage;
    public final double towerDamage;
    public final double hitSpeed;
    public final double speedBlocks;
    public final double range;
    public final CardDef.Targets targets;
    public final boolean air;
    public final double splash;
    public final double deploy;
    public final double lifetime;
    public final double size;
    public final double radius;
    public final double duration;
    public final double stun;
    public final double slow;
    public final double knockback;
    public final double length;
    public final double width;
    public final boolean anywhere;
    public final boolean ownSide;
    public final double spawnDamage;
    public final double spawnRadius;
    public final List<Double> damageStages = new ArrayList<>();
    public final double stageSeconds;
    public final double barrelHp;
    public final double barrelDeathDamage;
    public final double barrelDeathRadius;
    public final String barrelModel;
    public final String projectileModel;
    public final Material icon;
    public final Material weapon;
    public final Material helmet;
    public final EntityType mob;
    public final boolean baby;
    public final String model;
    public final double hitboxW;
    public final double hitboxH;
    public final boolean aiOnly;
    public final boolean kamikaze;
    public final int chain;
    public final double chainRange;
    public final double slowDuration;
    public final int waves;
    public final String shot;
    public final double jump;
    public final String spawnCard;
    public final double spawnEvery;
    public final int spawnCount;
    public final boolean spawnWhenEnemy;
    public final String deathSpawn;
    public final int deathSpawnCount;
    public final double deathDamage;
    public final double deathRadius;
    /** 죽을 때 범위 안 적 감속 비율 (얼음 골렘 0.35) */
    public final double deathSlow;
    public final double deathSlowDuration;
    /** 공중 유닛이 죽으면 그 자리에서 폭탄이 떨어져 지상에만 피해 (해골 비행선) */
    public final boolean deathBomb;
    public final boolean charge;
    public final double chargeDistance;
    public final double chargeDamage;
    public final double boost;
    public final double buildingDamage;
    public final double pull;
    public final boolean deckable;
    public final boolean riverJump;
    public final List<String[]> mix = new ArrayList<>();
    /** 실드 체력 (다크 프린스): 실드가 먼저 맞고, 실드가 깨지는 공격의 남은 피해는 버려짐 */
    public final double shield;
    /** 유닛이 소환하는 첫 웨이브까지 걸리는 시간 (배치 끝난 뒤, 초) */
    public final double spawnFirst;
    /** 감전(스턴)되면 충전 초기화 (스파키) */
    public final boolean stunResetsCharge;
    /** 터질 때 아군 회복량 (한 번에), 횟수, 반경 */
    public final double heal;
    public final int healPulses;
    public final double healRadius;
    /** 죽으면 상대 팀이 얻는 엘릭서 (엘릭서 골렘) */
    public final double deathElixir;
    /** 죽은 뒤 폭탄이 터지기까지 시간 (초, 폭탄 타워) */
    public final double deathDelay;
    /** 체력이 이 비율 이하로 떨어지면 다른 카드(건물)로 변신 (대포 카트 → 부서진 대포) */
    public final double transformAt;
    public final String transformInto;
    /** 건물을 한 번 치면 부서짐 (배틀 램) */
    public final boolean breakOnHit;
    /** 건물: 위쪽(포탑)이 따로 돌아가는 모델 (base / top 본) */
    public final boolean turret;
    /** 즉발 전기 공격 + 스턴 (감전돌이) */
    public final boolean zap;
    /** 건물 투사체가 나가는 높이 (블록, 0 이하면 기본) */
    public final double shotHeight;
    /** 체력바 높이 (블록, 발 기준). 없으면 히트박스 높이 */
    public final double barHeight;
    /** 죽은 자리에 남는 모델 (폭탄 타워 폭탄) */
    public final String deathModel;
    // ---- 3.6.0 새 카드 기능
    /** 범위 공격 중심이 자기 자신 (발키리 360도) */
    public final boolean splashSelf;
    /** 건물에 닿으면 자폭 (해골 돌격병) */
    public final boolean explodeOnHit;
    /** 산탄 개수 (사냥꾼) */
    public final int pellets;
    /** 도끼를 던져 갔다가 돌아옴 (도끼맨) */
    public final boolean axe;
    /** 화살이 일직선으로 꿰뚫음 (마법 아처) */
    public final boolean pierce;
    /** 바위를 굴림 (볼러) */
    public final boolean roll;
    /** 일직선 공격이 대상 뒤로 더 가는 거리 (블록) */
    public final double pierceExtra;
    /** 죽을 때 그 자리에 쓰는 스펠 (나무꾼 → 분노) */
    public final String deathSpell;
    /** 돌진 대시 (도둑): 최소/최대 거리(블록), 대시 피해 */
    public final boolean dash;
    public final double dashMin;
    public final double dashMax;
    public final double dashDamage;
    /** 점프 (메가 나이트): 최소/최대 거리(블록), 점프 피해 */
    public final double jumpMin;
    public final double jumpMax;
    public final double jumpDamage;
    /** 엘릭서 생산 (엘릭서 정제소): 몇 초마다 몇 개 */
    public final double elixirEvery;
    public final double elixirAmount;
    /** 맞은 적 감속 (얼음 마법사) */
    public final double hitSlow;
    public final double hitSlowDuration;
    /** 죽으면 우리 팀이 얻는 엘릭서 (엘릭서 정제소) */
    public final double deathElixirSelf;

    CardDef(String var1, ConfigurationSection var2, double var3, double var5) {
        this.id = var1;
        this.name = var2.getString("name", var1);
        this.elixir = var2.getInt("elixir", 3);
        this.type = CardDef.Type.valueOf(var2.getString("type", "TROOP").toUpperCase());
        this.count = Math.max(1, var2.getInt("count", 1));
        this.hp = var2.getDouble("hp", 100.0);
        this.damage = var2.getDouble("damage", 0.0);
        this.towerDamage = var2.getDouble("tower-damage", 0.0);
        this.hitSpeed = var2.getDouble("hit-speed", 1.0);
        this.speedBlocks = speedOf(var2.getString("speed", "MEDIUM")) / 60.0 * 2.0 * var5;
        this.range = var2.getDouble("range", 1.0) * 2.0;
        this.targets = CardDef.Targets.valueOf(var2.getString("targets", "GROUND").toUpperCase());
        this.air = var2.getBoolean("air", false);
        this.splash = var2.getDouble("splash", 0.0) * 2.0;
        this.deploy = var2.getDouble("deploy", 1.0);
        this.lifetime = var2.getDouble("lifetime", 30.0);
        this.size = var2.getDouble("size", 3.0) * 2.0;
        this.radius = var2.getDouble("radius", 0.0) * 2.0;
        this.duration = var2.getDouble("duration", 0.0);
        this.stun = var2.getDouble("stun", 0.0);
        this.slow = var2.getDouble("slow", 0.0);
        this.knockback = var2.getDouble("knockback", 0.0) * 2.0;
        this.length = var2.getDouble("length", 0.0) * 2.0;
        this.width = var2.getDouble("width", 0.0) * 2.0;
        this.anywhere = var2.getBoolean("anywhere", false);
        this.ownSide = var2.getBoolean("own-side", false);
        this.spawnDamage = var2.getDouble("spawn-damage", 0.0);
        this.spawnRadius = var2.getDouble("spawn-radius", 0.0) * 2.0;

        for (Object var8 : var2.getList("damage-stages", new ArrayList())) {
            if (var8 instanceof Number var9) {
                this.damageStages.add(var9.doubleValue());
            }
        }

        this.stageSeconds = var2.getDouble("stage-seconds", 2.0);
        this.barrelHp = var2.getDouble("barrel-hp", 0.0);
        this.barrelDeathDamage = var2.getDouble("barrel-death-damage", 0.0);
        this.barrelDeathRadius = var2.getDouble("barrel-death-radius", 0.0) * 2.0;
        this.barrelModel = var2.getString("barrel-model", "");
        this.projectileModel = var2.getString("projectile-model", "");
        this.icon = mat(var2.getString("icon", "PAPER"), Material.PAPER);
        this.weapon = mat(var2.getString("weapon", "AIR"), Material.AIR);
        this.helmet = mat(var2.getString("helmet", "AIR"), Material.AIR);

        EntityType var17;
        try {
            var17 = EntityType.valueOf(var2.getString("mob", "ZOMBIE").toUpperCase());
        } catch (IllegalArgumentException var16) {
            var17 = EntityType.ZOMBIE;
        }

        this.mob = var17;
        this.baby = var2.getBoolean("baby", false);
        this.model = var2.getString("model", "");
        List var18 = var2.getList("hitbox", new ArrayList());
        double var19 = var18.size() > 0 && var18.get(0) instanceof Number var11 ? var11.doubleValue() : (this.type == CardDef.Type.BUILDING ? this.size : 0.8);
        double var20 = var18.size() > 1 && var18.get(1) instanceof Number var13 ? var13.doubleValue() : (this.type == CardDef.Type.BUILDING ? 2.5 : 1.8);
        this.hitboxW = Math.max(0.2, var19);
        this.hitboxH = Math.max(0.2, var20);
        this.aiOnly = var2.getBoolean("ai-only", this.targets == CardDef.Targets.BUILDINGS);
        this.kamikaze = var2.getBoolean("kamikaze", false);
        this.chain = var2.getInt("chain", 0);
        this.chainRange = var2.getDouble("chain-range", 0.0) * 2.0;
        this.slowDuration = var2.getDouble("slow-duration", 0.0);
        this.waves = Math.max(1, var2.getInt("waves", 1));
        this.shot = var2.getString("shot", "").toUpperCase();
        this.jump = var2.getDouble("jump", 0.0) * 2.0;
        this.spawnCard = var2.getString("spawn", "");
        this.spawnEvery = var2.getDouble("spawn-every", 0.0);
        this.spawnCount = Math.max(1, var2.getInt("spawn-count", 1));
        this.spawnWhenEnemy = var2.getBoolean("spawn-when-enemy", false);
        this.deathSpawn = var2.getString("death-spawn", "");
        this.deathSpawnCount = var2.getInt("death-spawn-count", 0);
        this.deathDamage = var2.getDouble("death-damage", 0.0);
        this.deathRadius = var2.getDouble("death-radius", 0.0) * 2.0;
        this.deathSlow = var2.getDouble("death-slow", 0.0);
        this.deathSlowDuration = var2.getDouble("death-slow-duration", 1.0);
        this.deathBomb = var2.getBoolean("death-bomb", false);
        this.charge = var2.getBoolean("charge", false);
        this.chargeDistance = var2.getDouble("charge-distance", 2.0) * 2.0;
        this.chargeDamage = var2.getDouble("charge-damage", 0.0);
        this.boost = var2.getDouble("boost", 0.0);
        this.buildingDamage = var2.getDouble("building-damage", 0.0);
        this.pull = var2.getDouble("pull", 0.0);
        this.deckable = var2.getBoolean("deck", true);
        this.riverJump = var2.getBoolean("river-jump", var1.equals("hog_rider"));

        this.shield = var2.getDouble("shield", 0.0);
        this.spawnFirst = var2.getDouble("spawn-first", 1.0);
        this.stunResetsCharge = var2.getBoolean("stun-resets-charge", false);
        this.heal = var2.getDouble("heal", 0.0);
        this.healPulses = Math.max(1, var2.getInt("heal-pulses", 1));
        this.healRadius = var2.getDouble("heal-radius", 0.0) * 2.0;
        this.deathElixir = var2.getDouble("death-elixir", 0.0);
        this.deathDelay = var2.getDouble("death-delay", 0.0);
        this.transformAt = var2.getDouble("transform-at", 0.0);
        this.transformInto = var2.getString("transform-into", "");
        this.breakOnHit = var2.getBoolean("break-on-hit", false);
        this.turret = var2.getBoolean("turret", var1.equals("cannon"));
        this.zap = var2.getBoolean("zap", false);
        this.shotHeight = var2.getDouble("shot-height", 0.0);
        this.barHeight = var2.getDouble("bar-height", this.hitboxH);
        this.deathModel = var2.getString("death-model", "");
        this.splashSelf = var2.getBoolean("splash-self", false);
        this.explodeOnHit = var2.getBoolean("explode-on-hit", false);
        this.pellets = Math.max(0, var2.getInt("pellets", 0));
        this.axe = var2.getBoolean("axe", false);
        this.pierce = var2.getBoolean("pierce", false);
        this.roll = var2.getBoolean("roll", false);
        this.pierceExtra = var2.getDouble("pierce-extra", 0.0) * 2.0;
        this.deathSpell = var2.getString("death-spell", "");
        this.dash = var2.getBoolean("dash", false);
        this.dashMin = var2.getDouble("dash-min", 3.5) * 2.0;
        this.dashMax = var2.getDouble("dash-max", 6.0) * 2.0;
        this.dashDamage = var2.getDouble("dash-damage", 0.0);
        this.jumpMin = var2.getDouble("jump-min", 0.0) * 2.0;
        this.jumpMax = var2.getDouble("jump-max", 0.0) * 2.0;
        this.jumpDamage = var2.getDouble("jump-damage", 0.0);
        this.elixirEvery = var2.getDouble("elixir-every", 0.0);
        this.elixirAmount = var2.getDouble("elixir-amount", 1.0);
        this.hitSlow = var2.getDouble("hit-slow", 0.0);
        this.hitSlowDuration = var2.getDouble("hit-slow-duration", 2.5);
        this.deathElixirSelf = var2.getDouble("death-elixir-self", 0.0);

        for (Object var22 : var2.getList("mix", new ArrayList())) {
            String[] var15 = String.valueOf(var22).split(":");
            if (var15.length == 2) {
                this.mix.add(new String[]{var15[0].trim(), var15[1].trim()});
            }
        }
    }

    private static double speedOf(String var0) {
        String var1 = var0.toUpperCase();
        switch (var1) {
            case "SLOW":
                return 45.0;
            case "FAST":
                return 90.0;
            case "VERY_FAST":
                return 120.0;
            default:
                return 60.0;
        }
    }

    private static Material mat(String var0, Material var1) {
        Material var2 = Material.matchMaterial(var0);
        return var2 == null ? var1 : var2;
    }

    public boolean isSpell() {
        return this.type == CardDef.Type.SPELL;
    }

    public boolean isBuilding() {
        return this.type == CardDef.Type.BUILDING;
    }

    public boolean isTroop() {
        return this.type == CardDef.Type.TROOP || this.type == CardDef.Type.SQUAD;
    }

    public int hitTicks() {
        return Math.max(1, (int)Math.round(this.hitSpeed * 20.0));
    }

    public int deployTicks() {
        return Math.max(1, (int)Math.round(this.deploy * 20.0));
    }

    public String typeKo() {
        switch (this.type) {
            case TROOP:
                return this.aiOnly ? "유닛 (AI)" : "유닛 (플레이어)";
            case SQUAD:
                return this.aiOnly ? "군단 (AI)" : "군단 (우두머리 + AI)";
            case BUILDING:
                return "건물 (AI)";
            default:
                return "스펠 (킹)";
        }
    }

    public static enum Targets {
        GROUND,
        AIR_GROUND,
        BUILDINGS;
    }

    public static enum Type {
        TROOP,
        SQUAD,
        BUILDING,
        SPELL;
    }
}
