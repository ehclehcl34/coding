package kr.kjmn.clashmc;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.entity.ArmorStand;
import org.bukkit.entity.Entity;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Player;

public final class Combatant {
    private static int SEQ = 0;
    public final int id = ++SEQ;
    public final Combatant.Kind kind;
    public final TeamColor team;
    public final CardDef card;
    public double hp;
    public double maxHp;
    public double radius = 0.5;
    public boolean air;
    public LivingEntity mob;
    public Entity hitbox;
    public ArmorStand label;
    public final List<Entity> extras = new ArrayList<>();
    public UUID playerId;
    public UUID reservedPlayer;
    public Location fixed;
    public String towerModel;
    public int modelTries;
    public boolean modeled;
    public long lastSeenTarget;
    public long lastDamaged = -1000L;
    public boolean walking;
    public long lastMoveTick;
    public Location lastPos;
    public Boolean lane;
    public ArmorStand turret;
    public long deployUntil;
    public long stunUntil;
    public long slowUntil;
    public long nextAttack;
    public double slowAmt = 0.15;
    public long rageUntil;
    public double rageBoost;
    public long nextSpawn;
    public double chargeDist;
    public boolean charging;
    /** 이번 틱에 AI가 걸어간 방향 (겹침 방지에서 건물 옆으로 미끄러질 때 사용) */
    public double moveDx;
    public double moveDz;
    public long moveTick = -1L;
    /** 이번 틱에 옮길 위치 (이동·방향·겹침 밀기를 모아서 틱 끝에 한 번만 텔레포트) */
    public Location pendingMove;
    public boolean clone;
    /** 남은 실드 (다크 프린스) */
    public double shield;
    public double maxShield;
    /** 이미 다른 카드로 변신함 (대포 카트) */
    public boolean transformed;
    /** 대시/점프 중 (이 틱까지 무적·이동 안 함) */
    public long dashUntil;
    /** 다음 대시/점프 가능 시각 */
    public long nextSpecial;
    public long expireAt;
    public Combatant target;
    public Combatant lastHit;
    public Combatant leader;
    public Combatant infernoTarget;
    public long infernoSince;
    public boolean active = true;
    public boolean hidden;
    public boolean dead;
    public boolean left;
    public int towerTx;
    public int towerTz;
    public int towerTiles;
    public boolean crossed;
    public boolean onBridge;

    public Combatant(Combatant.Kind var1, TeamColor var2, CardDef var3) {
        this.kind = var1;
        this.team = var2;
        this.card = var3;
    }

    public boolean isTower() {
        return this.kind == Combatant.Kind.KING_TOWER || this.kind == Combatant.Kind.PRINCESS_TOWER;
    }

    public boolean isStructure() {
        return this.isTower() || this.kind == Combatant.Kind.BUILDING;
    }

    public boolean isPlayer() {
        return this.playerId != null;
    }

    public Player player() {
        return this.playerId == null ? null : Bukkit.getPlayer(this.playerId);
    }

    public Location loc() {
        if (this.playerId != null) {
            Player var1 = this.player();
            if (var1 != null) {
                return var1.getLocation();
            }
        }

        if (this.mob != null) {
            return this.mob.getLocation();
        } else {
            return this.fixed == null ? null : this.fixed.clone();
        }
    }

    public boolean alive() {
        return !this.dead && this.hp > 0.0;
    }

    public String displayName() {
        switch (this.kind) {
            case KING_TOWER:
                return this.team.cc + "킹 타워";
            case PRINCESS_TOWER:
                return this.team.cc + "프린세스 타워";
            case BUILDING:
            case TROOP:
            default:
                return this.team.cc + (this.card == null ? "?" : this.card.name);
            case BARREL:
                return this.team.cc + "해골통";
        }
    }

    public static enum Kind {
        KING_TOWER,
        PRINCESS_TOWER,
        BUILDING,
        TROOP,
        BARREL;
    }
}
