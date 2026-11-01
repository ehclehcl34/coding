package kr.kjmn.clashmc;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.UUID;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.block.Block;
import org.bukkit.boss.BarColor;
import org.bukkit.boss.BarFlag;
import org.bukkit.boss.BarStyle;
import org.bukkit.entity.Player;

public final class TestMode {
    private final GameManager gm;
    boolean active;
    UUID admin;
    TeamColor side = TeamColor.BLUE;
    boolean infiniteElixir;
    boolean freePlace;
    boolean godTowers;
    boolean timerFrozen;
    boolean freeMove;
    boolean showHitbox;
    boolean showRange;
    static final List<String> SUBS = List.of(
        "start",
        "unit",
        "king",
        "spawn",
        "bot",
        "elixir",
        "place",
        "god",
        "time",
        "freeze",
        "overtime",
        "hitbox",
        "range",
        "fly",
        "clear",
        "heal",
        "reset",
        "break",
        "info",
        "stop"
    );

    TestMode(GameManager var1) {
        this.gm = var1;
    }

    boolean isAdmin(UUID var1) {
        return this.active && var1 != null && var1.equals(this.admin);
    }

    TeamColor enemy() {
        return this.side.other();
    }

    void start(Player var1, TeamColor var2) {
        if (this.gm.arena == null) {
            var1.sendMessage("§c경기장이 설정되지 않았습니다. /clash setarena");
        } else if (this.gm.phase != GameManager.Phase.LOBBY) {
            var1.sendMessage("§c이미 경기 중입니다. /clash stop 후 다시 시도하세요.");
        } else if (this.gm.cards.size() < 8) {
            var1.sendMessage("§c카드가 8장 미만이라 시작할 수 없습니다.");
        } else {
            this.gm.sendUiPack(var1);
            this.gm.core.lobby.leaveLobby(var1);
            this.active = true;
            this.admin = var1.getUniqueId();
            this.side = var2;
            this.gm.teams.clear();
            GameTeam var3 = new GameTeam(this.side);
            GameTeam var4 = new GameTeam(this.enemy());
            this.gm.teams.put(TeamColor.BLUE, this.side == TeamColor.BLUE ? var3 : var4);
            this.gm.teams.put(TeamColor.RED, this.side == TeamColor.RED ? var3 : var4);
            var3.members.add(this.admin);
            var3.king = this.admin;
            this.gm.teamOf.put(this.admin, this.side);
            this.fillDeck(var3, this.gm.core.profiles.get(this.admin).deck());
            this.gm.bot = new Bot(this.gm, this.enemy(), Bot.Level.NORMAL);
            this.gm.bot.interval = 4.0;
            this.fillDeck(var4, null);

            for (GameTeam var6 : this.gm.teams.values()) {
                var6.deckReady = true;
                var6.elixir = this.gm.startElixir;
            }

            this.gm.battle.buildTowers();
            this.gm.bar = Bukkit.createBossBar("§e1인 테스트", BarColor.YELLOW, BarStyle.SOLID, new BarFlag[0]);

            for (GameTeam var8 : this.gm.teams.values()) {
                this.gm.createBoard(var8);
            }

            this.gm.resetPlayer(var1);
            var1.setScoreboard(var3.board);
            this.gm.bar.addPlayer(var1);
            var1.setGameMode(GameMode.ADVENTURE);
            this.gm.beginPlay();
            var1.sendTitle("§e1인 테스트", this.side.label() + " §f킹 · 상대는 봇", 5, 50, 10);
            this.help(var1);
        }
    }

    private void fillDeck(GameTeam var1, List<String> var2) {
        var1.deck.clear();
        if (var2 != null) {
            for (String var4 : var2) {
                if (this.gm.cards.containsKey(var4) && var1.deck.size() < 8 && !var1.deck.contains(var4)) {
                    var1.deck.add(var4);
                }
            }
        }

        ArrayList var6 = new ArrayList<>(this.gm.cards.keySet());
        Collections.shuffle(var6, this.gm.rng);

        for (String var5 : var6) {
            if (var1.deck.size() < 8 && !var1.deck.contains(var5)) {
                var1.deck.add(var5);
            }
        }
    }

    void reset() {
        this.active = false;
        this.admin = null;
        this.showHitbox = false;
        this.showRange = false;
        this.timerFrozen = false;
    }

    void tick() {
        if (this.active && this.gm.phase == GameManager.Phase.PLAYING) {
            if (this.infiniteElixir) {
                GameTeam var1 = this.gm.teams.get(this.side);
                if (var1 != null) {
                    var1.elixir = this.gm.maxElixir;
                }
            }

            Player var2 = Bukkit.getPlayer(this.admin);
            if (var2 != null && (this.showHitbox || this.showRange) && this.gm.tick % 5L == 0L) {
                this.gm.battle.drawHitboxes(var2, this.showRange);
            }
        }
    }

    void becomeUnit(Player var1, CardDef var2) {
        if (var2.isSpell() || var2.type == CardDef.Type.BUILDING) {
            var1.sendMessage("§c유닛 카드만 직접 조종할 수 있습니다.");
        } else if (this.gm.activeUnits.contains(this.admin)) {
            var1.sendMessage("§c이미 유닛입니다. /clash test king 으로 먼저 돌아오세요.");
        } else {
            Location var3 = this.aimedTile(var1);
            if (var3 == null) {
                var3 = this.gm.arena.tileCenter(9, this.side == TeamColor.BLUE ? 10 : 21);
            }

            GameTeam var4 = this.gm.teams.get(this.side);
            this.gm.battle.testPlayerUnit(var4, var2, var1, var3);
            var1.sendMessage("§a" + var2.name + " §f유닛으로 소환됨 §7(죽거나 /clash test king 하면 킹으로 복귀)");
        }
    }

    void backToKing(Player var1) {
        Combatant var2 = this.gm.battle.unitOf(this.admin);
        if (var2 != null) {
            this.gm.battle.kill(var2);
        } else {
            this.restoreKing(var1);
        }
    }

    void unitDied(UUID var1) {
        Bukkit.getScheduler().runTaskLater(this.gm.plugin, () -> {
            Player var2 = Bukkit.getPlayer(var1);
            if (var2 != null && this.isAdmin(var1) && this.gm.phase == GameManager.Phase.PLAYING) {
                this.restoreKing(var2);
            }
        }, 30L);
    }

    private void restoreKing(Player var1) {
        GameTeam var2 = this.gm.teams.get(this.side);
        if (var2 != null) {
            this.gm.models.remove(var1);
            this.gm.resetPlayer(var1);
            this.gm.equipKing(var1, var2);
            GameManager.actionbar(var1, "§6킹으로 복귀");
        }
    }

    void spawn(Player var1, CardDef var2, TeamColor var3, int var4) {
        Location var5 = this.aimedTile(var1);
        if (var5 == null) {
            var1.sendMessage("§c경기장 칸을 바라보세요.");
        } else {
            int var6 = this.gm.arena.tileX(var5.getX());
            int var7 = this.gm.arena.tileZ(var5.getZ());
            GameTeam var8 = this.gm.teams.get(var3);

            for (int var9 = 0; var9 < var4; var9++) {
                this.gm.battle.deploy(var8, var2, var6, var7, var5);
            }

            var1.sendMessage("§a소환: " + var3.cc + var2.name + " §fx" + var4 + " §7(" + var6 + "," + var7 + ")");
        }
    }

    Location aimedTile(Player var1) {
        Block var2 = var1.getTargetBlockExact(160);
        if (var2 == null) {
            return null;
        } else {
            int var3 = this.gm.arena.tileX(var2.getX() + 0.5);
            int var4 = this.gm.arena.tileZ(var2.getZ() + 0.5);
            return !this.gm.arena.inField(var3, var4) ? null : this.gm.arena.tileCenter(var3, var4);
        }
    }

    void command(Player var1, String[] var2) {
        String var3 = var2.length < 2 ? "help" : var2[1].toLowerCase();
        if (!var3.equals("start") && !var3.equals("help") && !this.active) {
            var1.sendMessage("§c테스트 중이 아닙니다. §f/clash test start [blue|red]");
        } else {
            switch (var3) {
                case "start":
                    TeamColor var19 = var2.length >= 3 && var2[2].equalsIgnoreCase("red") ? TeamColor.RED : TeamColor.BLUE;
                    this.start(var1, var19);
                    return;
                case "unit":
                    CardDef var18 = this.card(var1, var2, 2);
                    if (var18 != null) {
                        this.becomeUnit(var1, var18);
                    }

                    return;
                case "king":
                    this.backToKing(var1);
                    return;
                case "spawn":
                    CardDef var17 = this.card(var1, var2, 2);
                    if (var17 == null) {
                        return;
                    }

                    TeamColor var21 = this.enemy();
                    int var22 = 1;

                    for (int var9 = 3; var9 < var2.length; var9++) {
                        String var10 = var2[var9].toLowerCase();
                        if (var10.equals("blue") || var10.equals("파랑")) {
                            var21 = TeamColor.BLUE;
                        } else if (var10.equals("red") || var10.equals("빨강")) {
                            var21 = TeamColor.RED;
                        } else if (!var10.equals("me") && !var10.equals("아군")) {
                            try {
                                var22 = Math.max(1, Math.min(10, Integer.parseInt(var10)));
                            } catch (NumberFormatException var12) {
                            }
                        } else {
                            var21 = this.side;
                        }
                    }

                    this.spawn(var1, var17, var21, var22);
                    return;
                case "bot":
                    String var16 = var2.length >= 3 ? var2[2].toLowerCase() : "toggle";
                    if (this.gm.bot == null) {
                        return;
                    }

                    if (var16.equals("speed") && var2.length >= 4) {
                        this.gm.bot.interval = Math.max(0.5, parseD(var2[3], this.gm.bot.interval));
                        var1.sendMessage("§a봇 카드 사용 간격: " + this.gm.bot.interval + "초");
                    } else if (var16.equals("elixir")) {
                        this.gm.bot.infinite = !this.gm.bot.infinite;
                        var1.sendMessage("§a봇 무한 엘릭서: " + onOff(this.gm.bot.infinite));
                    } else if (var16.equals("now")) {
                        this.gm.bot.now();
                    } else if (!var16.equals("easy") && !var16.equals("normal") && !var16.equals("hard")) {
                        this.gm.botEnabled = var16.equals("on") || !var16.equals("off") && !this.gm.botEnabled;
                        var1.sendMessage("§a봇 킹: " + onOff(this.gm.botEnabled));
                    } else {
                        this.gm.bot.level = Bot.Level.valueOf(var16.toUpperCase());
                        this.gm.bot.interval = this.gm.bot.level.interval;
                        var1.sendMessage("§a봇 난이도: " + this.gm.bot.level.ko);
                    }

                    return;
                case "elixir":
                    GameTeam var15 = this.gm.teams.get(this.side);
                    if (var2.length >= 3) {
                        this.infiniteElixir = false;
                        var15.elixir = Math.max(0.0, Math.min(this.gm.maxElixir, parseD(var2[2], var15.elixir)));
                        var1.sendMessage("§a엘릭서 = " + var15.elixir);
                    } else {
                        this.infiniteElixir = !this.infiniteElixir;
                        var1.sendMessage("§a무한 엘릭서: " + onOff(this.infiniteElixir));
                    }

                    return;
                case "place":
                    this.freePlace = !this.freePlace;
                    var1.sendMessage("§a자유 배치 (진영/강/타워 무시): " + onOff(this.freePlace));
                    return;
                case "god":
                    this.godTowers = !this.godTowers;
                    var1.sendMessage("§a타워 무적: " + onOff(this.godTowers));
                    return;
                case "time":
                    if (var2.length >= 3) {
                        this.gm.secondsLeft = Math.max(1, (int)parseD(var2[2], this.gm.secondsLeft));
                        var1.sendMessage("§a남은 시간 " + this.gm.secondsLeft + "초" + (this.gm.secondsLeft <= this.gm.doubleLast ? " §d(더블 엘릭서)" : ""));
                    } else {
                        var1.sendMessage("§c/clash test time <초>");
                    }

                    return;
                case "freeze":
                    this.timerFrozen = !this.timerFrozen;
                    var1.sendMessage("§a시간 정지: " + onOff(this.timerFrozen));
                    return;
                case "overtime":
                    this.gm.overtime = true;
                    this.gm.secondsLeft = this.gm.overtimeSeconds;
                    this.gm.titleAll("§c§l연장전! §7(테스트)", "");
                    return;
                case "hitbox":
                    this.showHitbox = !this.showHitbox;
                    var1.sendMessage("§a히트박스 표시 (파랑/빨강 원기둥): " + onOff(this.showHitbox));
                    return;
                case "range":
                    this.showRange = !this.showRange;
                    var1.sendMessage("§a사거리 표시 (노란 원): " + onOff(this.showRange));
                    return;
                case "fly":
                    this.freeMove = !this.freeMove;
                    if (!this.gm.activeUnits.contains(this.admin)) {
                        var1.setAllowFlight(true);
                        var1.setFlying(true);
                    }

                    var1.sendMessage("§a킹 이동 범위 제한 해제 (경기장 밖까지): " + onOff(this.freeMove));
                    return;
                case "clear":
                    TeamColor var14 = null;
                    if (var2.length >= 3 && var2[2].equalsIgnoreCase("blue")) {
                        var14 = TeamColor.BLUE;
                    }

                    if (var2.length >= 3 && var2[2].equalsIgnoreCase("red")) {
                        var14 = TeamColor.RED;
                    }

                    var1.sendMessage("§a유닛 " + this.gm.battle.clearUnits(var14) + "개 제거");
                    return;
                case "heal":
                    var1.sendMessage("§a타워 " + this.gm.battle.healTowers() + "개 체력 회복");
                    return;
                case "reset":
                    if (this.gm.activeUnits.contains(this.admin)) {
                        this.backToKing(var1);
                    }

                    this.gm.battle.rebuild();

                    for (GameTeam var20 : this.gm.teams.values()) {
                        var20.crowns = 0;
                        var20.elixir = this.gm.startElixir;
                    }

                    this.gm.secondsLeft = this.gm.matchSeconds;
                    this.gm.overtime = false;
                    var1.sendMessage("§a경기장 초기화 (타워 재건, 유닛 제거, 시간/크라운 리셋)");
                    return;
                case "break":
                    if (var2.length < 4) {
                        var1.sendMessage("§c/clash test break <blue|red> <left|right|king>");
                        return;
                    } else {
                        TeamColor var6 = var2[2].equalsIgnoreCase("red") ? TeamColor.RED : TeamColor.BLUE;
                        Combatant var7 = this.gm.battle.towerOf(var6, var2[3].toLowerCase());
                        if (var7 != null && var7.alive()) {
                            boolean var8 = this.godTowers;
                            this.godTowers = false;
                            this.gm.battle.kill(var7);
                            this.godTowers = var8;
                            return;
                        }

                        var1.sendMessage("§c이미 없거나 잘못된 타워");
                        return;
                    }
                case "info":
                    this.info(var1);
                    return;
                case "stop":
                    this.gm.stopMatch("테스트 종료");
                    return;
                default:
                    this.help(var1);
            }
        }
    }

    private CardDef card(Player var1, String[] var2, int var3) {
        if (var2.length <= var3) {
            var1.sendMessage("§c카드 id 를 입력하세요: §f" + String.join(", ", this.gm.cards.keySet()));
            return null;
        } else {
            CardDef var4 = this.gm.cards.get(var2[var3].toLowerCase());
            if (var4 == null) {
                for (CardDef var6 : this.gm.cards.values()) {
                    if (var6.name.equals(var2[var3])) {
                        var4 = var6;
                    }
                }
            }

            if (var4 == null) {
                var1.sendMessage("§c없는 카드: " + var2[var3] + " §7(" + String.join(", ", this.gm.cards.keySet()) + ")");
            }

            return var4;
        }
    }

    private static double parseD(String var0, double var1) {
        try {
            return Double.parseDouble(var0);
        } catch (NumberFormatException var4) {
            return var1;
        }
    }

    private static String onOff(boolean var0) {
        return var0 ? "§aON" : "§cOFF";
    }

    void info(Player var1) {
        var1.sendMessage(
            "§e[1인 테스트] §f내 팀 "
                + this.side.label()
                + " §7| 봇 "
                + onOff(this.gm.botEnabled)
                + (
                    this.gm.bot == null
                        ? ""
                        : " §7(" + this.gm.bot.level.ko + ", " + this.gm.bot.interval + "초" + (this.gm.bot.infinite ? ", 무한 엘릭서" : "") + ")"
                )
        );
        var1.sendMessage(
            "§7무한 엘릭서 "
                + onOff(this.infiniteElixir)
                + " §7| 자유 배치 "
                + onOff(this.freePlace)
                + " §7| 타워 무적 "
                + onOff(this.godTowers)
                + " §7| 시간 정지 "
                + onOff(this.timerFrozen)
        );
        var1.sendMessage(
            "§7히트박스 "
                + onOff(this.showHitbox)
                + " §7| 사거리 "
                + onOff(this.showRange)
                + " §7| 자유 이동 "
                + onOff(this.freeMove)
                + " §7| 남은 시간 "
                + this.gm.secondsLeft
                + "초 §7| 유닛 "
                + this.gm.battle.all.size()
                + "개"
        );
    }

    void help(Player var1) {
        var1.sendMessage("§e§l[1인 테스트 명령어] §7/clash test ...");
        var1.sendMessage("§fstart [blue|red] §7- 혼자 시작 (상대는 봇 킹)");
        var1.sendMessage("§funit <카드> §7- 바라보는 칸에 내가 그 유닛으로 소환 §8| §fking §7- 킹으로 복귀");
        var1.sendMessage("§fspawn <카드> [blue|red|me] [개수] §7- 바라보는 칸에 AI 소환 (기본: 상대 팀)");
        var1.sendMessage("§fbot [on|off|now|elixir|easy|normal|hard|speed <초>] §7- 봇 킹 설정");
        var1.sendMessage("§felixir [값] §7- 무한 엘릭서 토글 / 값 지정 §8| §fplace §7- 배치 규칙 무시");
        var1.sendMessage("§fgod §7- 타워 무적 §8| §fheal §7- 타워 회복 §8| §fbreak <팀> <left|right|king> §7- 타워 파괴");
        var1.sendMessage("§ftime <초> §8| §ffreeze §8| §fovertime §7- 시간 조작");
        var1.sendMessage("§fhitbox §8| §frange §7- 히트박스 / 사거리 표시 §8| §ffly §7- 비행 범위 제한 해제");
        var1.sendMessage("§fclear [blue|red] §8| §freset §8| §finfo §8| §fstop");
    }
}
