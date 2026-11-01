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
    /** 설정 거리 단위: 1타일 = 3블록 (경기장 1칸) */
    static final double TILE = 3.0;
    public final double range;
    public final CardDef.Targets targets;
    public final boolean air;
    public final double splash;
    public final double deploy;
    public final double lifetime;
    public final double size;
    /** 유닛 배치 칸 (블록, 미리보기 테두리용) */
    public final double footprint;
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
    /** 대형 유닛: 통나무 말고는 넉백 안 받음 (config heavy) */
    public final boolean heavy;
    static final java.util.Set<String> HEAVY = java.util.Set.of("giant", "royal_giant", "electro_giant", "giant_skeleton", "golem", "elixir_golem", "pekka", "mega_knight", "lava_hound", "goblin_brawler", "bowler", "ice_golem");
    public final double chargeDistance;
    public final double chargeDamage;
    public final double boost;
    public final double buildingDamage;
    public final double pull;
    public final boolean deckable;
    /** 희귀도: 0 일반, 1 레어, 2 에픽, 3 전설 (config 의 rarity 로 바꿀 수 있음) */
    public final int rarity;
    static final java.util.Map<String, Integer> RARITY = new java.util.HashMap<>();
    static {
        RARITY.put("skeleton_army", 2);
        RARITY.put("goblin_barrel", 2);
        RARITY.put("baby_dragon", 2);
        RARITY.put("prince", 2);
        RARITY.put("dark_prince", 2);
        RARITY.put("witch", 2);
        RARITY.put("balloon", 2);
        RARITY.put("golem", 2);
        RARITY.put("giant_skeleton", 2);
        RARITY.put("bowler", 2);
        RARITY.put("executioner", 2);
        RARITY.put("guards", 2);
        RARITY.put("lightning", 2);
        RARITY.put("rage", 2);
        RARITY.put("freeze", 2);
        RARITY.put("poison", 2);
        RARITY.put("mirror", 2);
        RARITY.put("clone", 2);
        RARITY.put("tornado", 2);
        RARITY.put("x_bow", 2);
        RARITY.put("pekka", 2);
        RARITY.put("electro_giant", 2);
        RARITY.put("barbarian_barrel", 2);
        RARITY.put("cannon_cart", 2);
        RARITY.put("wall_breakers", 2);
        RARITY.put("hunter", 2);
        RARITY.put("electro_dragon", 2);
        RARITY.put("mini_pekka", 1);
        RARITY.put("musketeer", 1);
        RARITY.put("valkyrie", 1);
        RARITY.put("hog_rider", 1);
        RARITY.put("giant", 1);
        RARITY.put("fireball", 1);
        RARITY.put("three_musketeers", 1);
        RARITY.put("battle_ram", 1);
        RARITY.put("wizard", 1);
        RARITY.put("mega_minion", 1);
        RARITY.put("dart_goblin", 1);
        RARITY.put("ice_golem", 1);
        RARITY.put("royal_hogs", 1);
        RARITY.put("heal_spirit", 1);
        RARITY.put("elixir_golem", 1);
        RARITY.put("bomb_tower", 1);
        RARITY.put("elixir_collector", 1);
        RARITY.put("inferno_tower", 1);
        RARITY.put("goblin_hut", 1);
        RARITY.put("barbarian_hut", 1);
        RARITY.put("tombstone", 1);
        RARITY.put("goblin_cage", 1);
        RARITY.put("zappies", 1);
        RARITY.put("flying_machine", 1);
        RARITY.put("rocket", 1);
        RARITY.put("earthquake", 1);
        RARITY.put("miner", 3);
        RARITY.put("electro_wizard", 3);
        RARITY.put("the_log", 3);
        RARITY.put("sparky", 3);
        RARITY.put("night_witch", 3);
        RARITY.put("lava_hound", 3);
        RARITY.put("ice_wizard", 3);
        RARITY.put("princess", 3);
        RARITY.put("lumberjack", 3);
        RARITY.put("magic_archer", 3);
        RARITY.put("bandit", 3);
        RARITY.put("inferno_dragon", 3);
        RARITY.put("mega_knight", 3);
        RARITY.put("graveyard", 3);
        RARITY.put("ram_rider", 3);
        RARITY.put("mother_witch", 3);
    }

    String rarityKo() {
        return switch (this.rarity) {
            case 1 -> "§6레어";
            case 2 -> "§d에픽";
            case 3 -> "§e전설";
            default -> "§7일반";
        };
    }

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
    /** 램 라이더: 볼라 (부대에게 피해 + 강한 감속) */
    public final double bolaDamage, bolaRange, bolaSlow, bolaDuration, bolaEvery;
    /** 일렉트로 자이언트: 반사 (가까이서 때린 적에게 전기) */
    public final double reflectDamage, reflectRange, reflectStun;
    /** 엄마 마녀: 저주 (저주받은 부대가 죽으면 우리 편 유닛으로) */
    public final String curseCard;
    public final double curseDuration;
    /** 로켓병: 터진 자리 뒤로 불꽃 + 쏠 때 뒤로 밀림 */
    public final int sparks;
    public final double sparkDamage, sparkRange, recoil;

    CardDef(String var1, ConfigurationSection var2, double var3, double var5) {
        this.id = var1;
        String nm = var2.getString("name", var1);
        if (var1.equals("pekka") && nm.equals("페카")) {
            nm = "P.E.K.K.A";                      // 3.7.0: 예전 config 이름도 원작 표기로
        } else if (var1.equals("mini_pekka") && nm.equals("미니 페카")) {
            nm = "미니 P.E.K.K.A";
        }
        this.name = nm;
        this.elixir = var2.getInt("elixir", 3);
        this.type = CardDef.Type.valueOf(var2.getString("type", "TROOP").toUpperCase());
        this.count = Math.max(1, var2.getInt("count", 1));
        this.hp = var2.getDouble("hp", 100.0);
        this.damage = var2.getDouble("damage", 0.0);
        this.towerDamage = var2.getDouble("tower-damage", 0.0);
        this.hitSpeed = var2.getDouble("hit-speed", 1.0);
        this.speedBlocks = speedOf(var2.getString("speed", "MEDIUM")) / 60.0 * 2.0 * var5;
        this.range = var2.getDouble("range", 1.0) * TILE;
        this.targets = CardDef.Targets.valueOf(var2.getString("targets", "GROUND").toUpperCase());
        this.air = var2.getBoolean("air", false);
        this.splash = var2.getDouble("splash", 0.0) * TILE;
        this.deploy = var2.getDouble("deploy", 1.0);
        this.lifetime = var2.getDouble("lifetime", 30.0);
        this.size = var2.getDouble("size", 3.0) * 2.0;   // 건물 크기: size 3 = 6블록 = 2x2타일 (이전 그대로)
        this.footprint = var2.getDouble("footprint", 1.0) * 3.0;
        this.heavy = var2.getBoolean("heavy", HEAVY.contains(var1));
        this.radius = var2.getDouble("radius", 0.0) * TILE;
        this.duration = var2.getDouble("duration", 0.0);
        this.stun = var2.getDouble("stun", 0.0);
        this.slow = var2.getDouble("slow", 0.0);
        this.knockback = var2.getDouble("knockback", 0.0) * TILE;
        this.length = var2.getDouble("length", 0.0) * TILE;
        this.width = var2.getDouble("width", 0.0) * TILE;
        this.anywhere = var2.getBoolean("anywhere", false);
        this.ownSide = var2.getBoolean("own-side", false);
        this.spawnDamage = var2.getDouble("spawn-damage", 0.0);
        this.spawnRadius = var2.getDouble("spawn-radius", 0.0) * TILE;

        for (Object var8 : var2.getList("damage-stages", new ArrayList())) {
            if (var8 instanceof Number var9) {
                this.damageStages.add(var9.doubleValue());
            }
        }

        this.stageSeconds = var2.getDouble("stage-seconds", 2.0);
        this.barrelHp = var2.getDouble("barrel-hp", 0.0);
        this.barrelDeathDamage = var2.getDouble("barrel-death-damage", 0.0);
        this.barrelDeathRadius = var2.getDouble("barrel-death-radius", 0.0) * TILE;
        this.barrelModel = var2.getString("barrel-model", "");
        this.projectileModel = var2.getString("projectile-model", var2.getBoolean("axe", false) ? "clash_executioner_axe" : "");
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
        this.chainRange = var2.getDouble("chain-range", 0.0) * TILE;
        this.slowDuration = var2.getDouble("slow-duration", 0.0);
        this.waves = Math.max(1, var2.getInt("waves", 1));
        this.shot = var2.getString("shot", "").toUpperCase();
        this.jump = var2.getDouble("jump", 0.0) * TILE;
        this.spawnCard = var2.getString("spawn", "");
        this.spawnEvery = var2.getDouble("spawn-every", 0.0);
        this.spawnCount = Math.max(1, var2.getInt("spawn-count", 1));
        this.spawnWhenEnemy = var2.getBoolean("spawn-when-enemy", false);
        this.deathSpawn = var2.getString("death-spawn", "");
        this.deathSpawnCount = var2.getInt("death-spawn-count", 0);
        this.deathDamage = var2.getDouble("death-damage", 0.0);
        this.deathRadius = var2.getDouble("death-radius", 0.0) * TILE;
        this.deathSlow = var2.getDouble("death-slow", 0.0);
        this.deathSlowDuration = var2.getDouble("death-slow-duration", 1.0);
        this.deathBomb = var2.getBoolean("death-bomb", false);
        this.charge = var2.getBoolean("charge", false);
        this.chargeDistance = var2.getDouble("charge-distance", 2.0) * TILE;
        this.chargeDamage = var2.getDouble("charge-damage", 0.0);
        this.boost = var2.getDouble("boost", 0.0);
        this.buildingDamage = var2.getDouble("building-damage", 0.0);
        this.pull = var2.getDouble("pull", 0.0);
        this.deckable = var2.getBoolean("deck", true);
        String rr = var2.getString("rarity", "");
        this.rarity = switch (rr == null ? "" : rr.toLowerCase()) {
            case "common", "일반" -> 0;
            case "rare", "레어" -> 1;
            case "epic", "에픽" -> 2;
            case "legendary", "전설" -> 3;
            default -> RARITY.getOrDefault(var1, 0);
        };
        this.riverJump = var2.getBoolean("river-jump", var1.equals("hog_rider"));

        this.shield = var2.getDouble("shield", 0.0);
        this.spawnFirst = var2.getDouble("spawn-first", 1.0);
        this.stunResetsCharge = var2.getBoolean("stun-resets-charge", false);
        this.heal = var2.getDouble("heal", 0.0);
        this.healPulses = Math.max(1, var2.getInt("heal-pulses", 1));
        this.healRadius = var2.getDouble("heal-radius", 0.0) * TILE;
        this.deathElixir = var2.getDouble("death-elixir", 0.0);
        this.deathDelay = var2.getDouble("death-delay", 0.0);
        this.transformAt = var2.getDouble("transform-at", 0.0);
        this.transformInto = var2.getString("transform-into", "");
        this.breakOnHit = var2.getBoolean("break-on-hit", false);
        this.turret = var2.getBoolean("turret", var1.equals("cannon"));
        this.zap = var2.getBoolean("zap", false);
        this.shotHeight = var2.getDouble("shot-height", 0.0);
        // 체력바: 모델 맨 위 (config bar-height 는 최소값으로만)
        this.barHeight = Math.max(var2.getDouble("bar-height", 0.0), Math.max(this.hitboxH, ModelHeights.of(this.model)));
        this.deathModel = var2.getString("death-model", "");
        this.splashSelf = var2.getBoolean("splash-self", false);
        this.explodeOnHit = var2.getBoolean("explode-on-hit", false);
        this.pellets = Math.max(0, var2.getInt("pellets", 0));
        this.axe = var2.getBoolean("axe", false);
        this.pierce = var2.getBoolean("pierce", false);
        this.roll = var2.getBoolean("roll", false);
        this.pierceExtra = var2.getDouble("pierce-extra", 0.0) * TILE;
        this.deathSpell = var2.getString("death-spell", "");
        this.dash = var2.getBoolean("dash", false);
        this.dashMin = var2.getDouble("dash-min", 3.5) * TILE;
        this.dashMax = var2.getDouble("dash-max", 6.0) * TILE;
        this.dashDamage = var2.getDouble("dash-damage", 0.0);
        this.jumpMin = var2.getDouble("jump-min", 0.0) * TILE;
        this.jumpMax = var2.getDouble("jump-max", 0.0) * TILE;
        this.jumpDamage = var2.getDouble("jump-damage", 0.0);
        this.elixirEvery = var2.getDouble("elixir-every", 0.0);
        this.elixirAmount = var2.getDouble("elixir-amount", 1.0);
        this.hitSlow = var2.getDouble("hit-slow", 0.0);
        this.hitSlowDuration = var2.getDouble("hit-slow-duration", 2.5);
        this.deathElixirSelf = var2.getDouble("death-elixir-self", 0.0);
        this.bolaDamage = var2.getDouble("bola-damage", 0.0);
        this.bolaRange = var2.getDouble("bola-range", 5.5) * TILE;
        this.bolaSlow = var2.getDouble("bola-slow", 0.7);
        this.bolaDuration = var2.getDouble("bola-duration", 2.0);
        this.bolaEvery = var2.getDouble("bola-every", 1.1);
        this.reflectDamage = var2.getDouble("reflect-damage", 0.0);
        this.reflectRange = var2.getDouble("reflect-range", 2.5) * TILE;
        this.reflectStun = var2.getDouble("reflect-stun", 0.5);
        this.curseCard = var2.getString("curse", "");
        this.curseDuration = var2.getDouble("curse-duration", 5.0);
        this.sparks = var2.getInt("sparks", 0);
        this.sparkDamage = var2.getDouble("spark-damage", 0.0);
        this.sparkRange = var2.getDouble("spark-range", 2.5) * TILE;
        this.recoil = var2.getDouble("recoil", 0.0) * TILE;

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
