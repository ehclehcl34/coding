package kr.kjmn.clashmc;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.Deque;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.boss.BarColor;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.entity.Player;

/**
 * 돌격전: 킹이 엘릭서 한도(기본 40) 안에서 유닛 카드만(중복 가능) 골라 군대를 짜고,
 * 시작하면 양쪽 군대가 한꺼번에 나와서 싸움. 마지막까지 유닛이 남은 팀 승리.
 * 렉 방지: 팀당 유닛 수 상한, 카드는 몇 틱 간격으로 나눠서 소환, 유닛 수 세기·적 찾기는 10틱마다.
 */
final class Assault {
    final GameManager gm;
    final int budget;
    final int maxUnits;
    final int pickSeconds;
    final int seconds;
    final int interval;
    private final Map<TeamColor, Deque<Object[]>> plan = new EnumMap<>(TeamColor.class);
    private final Map<TeamColor, Integer> alive = new EnumMap<>(TeamColor.class);
    private final Map<TeamColor, Long> emptySince = new EnumMap<>(TeamColor.class);
    private long checkFrom = Long.MAX_VALUE;
    private boolean queued;

    Assault(GameManager gm) {
        this.gm = gm;
        FileConfiguration c = gm.plugin.getConfig();
        this.budget = Math.max(1, c.getInt("assault.elixir", 40));
        this.maxUnits = Math.max(1, c.getInt("assault.max-units", 40));
        this.pickSeconds = Math.max(10, c.getInt("assault.pick-seconds", 45));
        this.seconds = Math.max(30, c.getInt("assault.match-seconds", 180));
        this.interval = Math.max(1, c.getInt("assault.deploy-interval", 3));
        // 데미지 숫자는 유닛이 많으면 텍스트 엔티티가 쏟아져서 렉 → 기본 끔
        if (!c.getBoolean("assault.damage-numbers", false)) {
            gm.damageNumbers = false;
        }
    }

    // ---------- 카드 규칙 ----------

    /** 돌격전에 쓸 수 있는 카드: 유닛만 (마법·건물 제외) */
    static boolean allowed(Clash core, CardDef c) {
        return core.usable(c) && (c.type == CardDef.Type.TROOP || c.type == CardDef.Type.SQUAD) && !c.aiOnly;
    }

    /** 카드 한 장이 소환하는 유닛 수 */
    static int units(Clash core, CardDef c) {
        if (c == null) {
            return 0;
        }
        if (!c.mix.isEmpty()) {
            int n = 0;
            for (String[] m : c.mix) {
                CardDef s = core.cards.get(m[0]);
                try {
                    n += Integer.parseInt(m[1]);
                } catch (NumberFormatException ex) {
                    n += s == null ? 1 : Math.max(1, s.count);
                }
            }
            return Math.max(1, n);
        }
        return Math.max(1, c.count);
    }

    static int cost(Clash core, List<String> army) {
        int n = 0;
        for (String id : army) {
            CardDef c = core.cards.get(id);
            if (c != null) {
                n += c.elixir;
            }
        }
        return n;
    }

    static int unitCount(Clash core, List<String> army) {
        int n = 0;
        for (String id : army) {
            n += units(core, core.cards.get(id));
        }
        return n;
    }

    /** 이 카드를 더 넣을 수 있으면 null, 아니면 이유 */
    String cantAdd(List<String> army, CardDef c) {
        if (!allowed(this.gm.core, c)) {
            return "돌격전에는 유닛 카드만 쓸 수 있습니다";
        }
        if (cost(this.gm.core, army) + c.elixir > this.budget) {
            return "엘릭서 한도 " + this.budget + " 초과";
        }
        if (unitCount(this.gm.core, army) + units(this.gm.core, c) > this.maxUnits) {
            return "유닛 수 한도 " + this.maxUnits + "마리 초과 (렉 방지)";
        }
        return null;
    }

    /** 못 쓰는 카드는 빼고, 한도를 넘으면 뒤에서부터 덜어냄 */
    void sanitize(List<String> army) {
        army.removeIf(id -> !allowed(this.gm.core, this.gm.cards.get(id)));
        while (!army.isEmpty() && (cost(this.gm.core, army) > this.budget || unitCount(this.gm.core, army) > this.maxUnits)) {
            army.remove(army.size() - 1);
        }
    }

    /** 남은 엘릭서를 무작위 유닛으로 채움 */
    void fillRandom(List<String> army) {
        this.sanitize(army);
        List<CardDef> pool = new ArrayList<>();
        for (CardDef c : this.gm.cards.values()) {
            if (allowed(this.gm.core, c)) {
                pool.add(c);
            }
        }
        if (pool.isEmpty()) {
            return;
        }
        for (int tries = 0; tries < 300; tries++) {
            int left = this.budget - cost(this.gm.core, army);
            if (left <= 0) {
                break;
            }
            CardDef c = pool.get(this.gm.rng.nextInt(pool.size()));
            if (this.cantAdd(army, c) == null) {
                army.add(c.id);
            }
        }
    }

    // ---------- 경기 ----------

    /** 전투 시작: 양 팀 군대를 소환 순서대로 줄 세움 (탱커 앞줄 → 원거리 뒷줄) */
    void begin() {
        this.plan.clear();
        for (GameTeam t : this.gm.teams.values()) {
            List<CardDef> list = new ArrayList<>();
            for (String id : t.deck) {
                CardDef c = this.gm.cards.get(id);
                if (c != null) {
                    list.add(c);
                }
            }
            // 체력 높은(탱커) 카드부터 앞줄, 사거리 긴 카드는 뒤로
            list.sort(Comparator.<CardDef>comparingDouble(c -> -(c.hp * (c.range <= 2.0 ? 1.5 : 1.0))));
            Deque<Object[]> q = new ArrayDeque<>();
            int[] cols = {7, 10, 5, 12, 3, 14, 1, 16};
            for (int i = 0; i < list.size(); i++) {
                int row = i / cols.length;
                int tx = cols[i % cols.length];
                int tz = t.color == TeamColor.BLUE ? Math.max(0, 11 - row * 2) : Math.min(31, 20 + row * 2);
                q.add(new Object[]{list.get(i), tx, tz});
            }
            this.plan.put(t.color, q);
            this.alive.put(t.color, 0);
            // 킹도 유닛 하나를 직접 조종 (다른 팀원 다음 순서)
            if (t.king != null && !t.queue.contains(t.king)) {
                t.queue.addLast(t.king);
            }
        }
        this.emptySince.clear();
        this.checkFrom = Long.MAX_VALUE;
        this.queued = true;
    }

    void tick() {
        // 카드 소환 (팀마다 interval 틱에 한 장씩 → 한 틱에 몰려서 렉 걸리지 않게)
        if (this.queued && this.gm.tick % this.interval == 0L) {
            boolean any = false;
            for (GameTeam t : this.gm.teams.values()) {
                Deque<Object[]> q = this.plan.get(t.color);
                if (q != null && !q.isEmpty()) {
                    Object[] p = q.poll();
                    CardDef c = (CardDef)p[0];
                    int tx = (Integer)p[1];
                    int tz = (Integer)p[2];
                    Location at = this.gm.arena.tileCenter(tx, tz);
                    this.gm.battle.assaultDeploy(t, c, tx, tz, at);
                    any |= !q.isEmpty();
                }
            }
            if (!any) {
                this.queued = false;
                // 통·광부처럼 늦게 나오는 유닛 기다렸다가 승패 판정 시작
                this.checkFrom = this.gm.tick + 100L;
            }
        }

        if (this.gm.tick % 10L != 0L) {
            return;
        }
        for (TeamColor tc : TeamColor.values()) {
            this.alive.put(tc, 0);
        }
        for (Combatant c : this.gm.battle.all) {
            if ((c.kind == Combatant.Kind.TROOP || c.kind == Combatant.Kind.BARREL) && c.alive()) {
                this.alive.merge(c.team, 1, Integer::sum);
            }
        }
        if (this.gm.tick < this.checkFrom) {
            return;
        }
        // 죽으면서 나오는 유닛(골렘 등)이 늦게 나올 수 있으니 2초 동안 0이어야 전멸
        boolean blueOut = this.out(TeamColor.BLUE);
        boolean redOut = this.out(TeamColor.RED);
        if (blueOut && redOut) {
            this.gm.endMatch(null, "동시 전멸");
        } else if (blueOut) {
            this.gm.endMatch(TeamColor.RED, TeamColor.BLUE.ko + " 팀 전멸");
        } else if (redOut) {
            this.gm.endMatch(TeamColor.BLUE, TeamColor.RED.ko + " 팀 전멸");
        }
    }

    private boolean out(TeamColor tc) {
        if (this.alive.getOrDefault(tc, 0) > 0) {
            this.emptySince.remove(tc);
            return false;
        }
        Long s = this.emptySince.get(tc);
        if (s == null) {
            this.emptySince.put(tc, this.gm.tick);
            return false;
        }
        return this.gm.tick - s >= 40L;
    }

    /** 시간 종료: 남은 체력 합이 많은 팀 승리 */
    void timeUp() {
        double b = 0.0;
        double r = 0.0;
        for (Combatant c : this.gm.battle.all) {
            if ((c.kind == Combatant.Kind.TROOP || c.kind == Combatant.Kind.BARREL) && c.alive()) {
                if (c.team == TeamColor.BLUE) {
                    b += c.hp;
                } else {
                    r += c.hp;
                }
            }
        }
        if (Math.abs(b - r) < 1.0) {
            this.gm.endMatch(null, "시간 종료 - 무승부");
        } else {
            this.gm.endMatch(b > r ? TeamColor.BLUE : TeamColor.RED, "시간 종료 - 남은 체력 승리");
        }
    }

    int alive(TeamColor tc) {
        return this.alive.getOrDefault(tc, 0);
    }

    String score() {
        return "§9파랑 " + this.alive(TeamColor.BLUE) + "마리 §7vs §c빨강 " + this.alive(TeamColor.RED) + "마리";
    }

    void hud() {
        if (this.gm.bar != null) {
            this.gm.bar.setTitle("§c§l돌격전 §r" + this.score() + " §8| §f" + this.gm.secondsLeft / 60 + ":" + String.format("%02d", Math.max(0, this.gm.secondsLeft % 60)));
            this.gm.bar.setProgress(Math.max(0.0, Math.min(1.0, (double)this.gm.secondsLeft / this.seconds)));
            this.gm.bar.setColor(BarColor.RED);
        }
        for (GameTeam t : this.gm.teams.values()) {
            for (UUID id : t.members) {
                Player p = Bukkit.getPlayer(id);
                if (p == null) {
                    continue;
                }
                Combatant u = this.gm.battle.unitOf(id);
                if (u != null) {
                    String dep = this.gm.tick < u.deployUntil ? " §b⏳ 배치 중" : "";
                    GameManager.actionbar(p, u.team.cc + u.card.name + " §c❤ " + (int)Math.ceil(u.hp) + "/" + (int)u.maxHp + dep + " §8| " + this.score());
                } else {
                    GameManager.actionbar(p, (this.queued ? "§e군대 소환 중... §8| " : "§7관전 중 §8| ") + this.score());
                }
            }
        }
    }
}
