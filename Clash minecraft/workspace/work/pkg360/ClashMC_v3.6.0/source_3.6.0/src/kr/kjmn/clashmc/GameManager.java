package kr.kjmn.clashmc;

import java.util.ArrayList;
import java.util.Collections;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import net.md_5.bungee.api.ChatMessageType;
import net.md_5.bungee.api.chat.TextComponent;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.block.Block;
import org.bukkit.boss.BarColor;
import org.bukkit.boss.BarFlag;
import org.bukkit.boss.BarStyle;
import org.bukkit.boss.BossBar;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.scoreboard.DisplaySlot;
import org.bukkit.scoreboard.Objective;

public final class GameManager {
    private static int SEQ = 0;
    final int id = ++SEQ;
    final Clash core;
    final ClashPlugin plugin;
    final Random rng = new Random();
    final NamespacedKey cardKey;
    final NamespacedKey previewKey;
    final ArenaPool.Slot slot;
    final Arena arena;
    final GameManager.Mode mode;
    final Room room;
    final ModelHook models;
    final Map<String, CardDef> cards;
    final Battle battle;
    final TestMode test = new TestMode(this);
    Bot bot;
    boolean botEnabled = true;
    GameManager.Phase phase = GameManager.Phase.LOBBY;
    boolean splitEnabled = true;
    double splitWidth = 2.2;
    final Map<TeamColor, GameTeam> teams = new EnumMap<>(TeamColor.class);
    final Map<UUID, TeamColor> teamOf = new ConcurrentHashMap<>();
    final Set<UUID> activeUnits = ConcurrentHashMap.newKeySet();
    final Map<UUID, Long> chatCooldown = new ConcurrentHashMap<>();
    long tick;
    int secondsLeft;
    int deckLeft;
    boolean overtime;
    BossBar bar;
    TeamColor winner;
    boolean surrendered;
    long playStartTick;
    final Map<UUID, Long> surrenderConfirm = new ConcurrentHashMap<>();
    String endReason = "";
    int matchSeconds;
    int doubleLast;
    int overtimeSeconds;
    int endDelay;
    int deckSeconds;
    double startElixir;
    double maxElixir;
    double elixirSeconds;
    double slowmode;
    double sight;
    double walkPerBlock;
    double flyPerBlock;
    double airHeight;
    double leash;
    double princessHp;
    double princessDmg;
    double princessHit;
    double princessRange;
    double kingHp;
    double kingDmg;
    double kingHit;
    double kingRange;
    String princessModel;
    String kingModel;
    boolean barrierCollision;
    boolean scalePlayers;
    boolean scaleModeledMobs;
    boolean modelFollowsScale;
    boolean hpDisplays;
    boolean unitHpNumbers;
    boolean damageNumbers;
    boolean kingFly;
    double kingFlySpeed;

    GameManager(Clash var1, ArenaPool.Slot var2, GameManager.Mode var3, Room var4) {
        this.core = var1;
        this.plugin = var1.plugin;
        this.cardKey = var1.cardKey;
        this.previewKey = var1.previewKey;
        this.slot = var2;
        this.arena = var2.arena;
        this.mode = var3;
        this.room = var4;
        this.models = var1.models;
        this.cards = var1.cards;
        this.load();
        this.battle = new Battle(this);
        var2.match = this;
    }

    void load() {
        FileConfiguration var1 = this.plugin.getConfig();
        this.matchSeconds = this.room != null ? this.room.matchSeconds : var1.getInt("game.match-seconds", 180);
        this.doubleLast = var1.getInt("game.double-elixir-last", 60);
        this.overtimeSeconds = var1.getInt("game.overtime-seconds", 120);
        this.endDelay = var1.getInt("game.end-delay", 8);
        this.deckSeconds = var1.getInt("game.deck-seconds", 25);
        this.startElixir = var1.getDouble("game.start-elixir", 5.0);
        this.maxElixir = var1.getDouble("game.max-elixir", 10.0);
        this.elixirSeconds = var1.getDouble("game.elixir-seconds", 2.8);
        this.slowmode = var1.getDouble("game.team-chat-slowmode", 5.0);
        this.sight = var1.getDouble("game.sight-range", 5.5) * 2.0;
        this.walkPerBlock = var1.getDouble("game.walk-speed-per-block", 0.0465);
        this.flyPerBlock = var1.getDouble("game.fly-speed-per-block", 0.0092);
        this.airHeight = var1.getDouble("game.air-height", 4.0);
        this.leash = var1.getDouble("game.follower-leash", 6.0);
        this.princessHp = var1.getDouble("towers.princess.hp", 3052.0);
        this.princessDmg = var1.getDouble("towers.princess.damage", 109.0);
        this.princessHit = var1.getDouble("towers.princess.hit-speed", 0.8);
        this.princessRange = var1.getDouble("towers.princess.range", 7.5) * 2.0;
        this.kingHp = var1.getDouble("towers.king.hp", 4824.0);
        this.kingDmg = var1.getDouble("towers.king.damage", 109.0);
        this.kingHit = var1.getDouble("towers.king.hit-speed", 1.0);
        this.kingRange = var1.getDouble("towers.king.range", 7.0) * 2.0;
        this.princessModel = var1.getString("towers.princess-model", "");
        this.kingModel = var1.getString("towers.king-model", "");
        this.barrierCollision = var1.getBoolean("hitbox.barrier-collision", var1.getBoolean("towers.barrier-collision", true));
        this.splitEnabled = var1.getBoolean("game.split.enabled", true);
        this.splitWidth = var1.getDouble("game.split.width", 2.2);
        this.scalePlayers = var1.getBoolean("hitbox.scale-players", true);
        this.scaleModeledMobs = var1.getBoolean("hitbox.scale-modeled-mobs", false);
        this.modelFollowsScale = var1.getBoolean("hitbox.model-follows-scale", false);
        this.hpDisplays = var1.getBoolean("ui.hp-bars", true);
        this.unitHpNumbers = var1.getBoolean("ui.unit-hp-numbers", true);
        this.damageNumbers = var1.getBoolean("ui.damage-numbers", true);
        this.kingFly = var1.getBoolean("game.king-fly", true);
        this.kingFlySpeed = var1.getDouble("game.king-fly-speed", 0.06);
    }

    String tag() {
        return this.mode.cc + this.mode.ko + " §8#" + this.id + " §7(" + this.slot.name + ")";
    }

    void broadcastGame(String var1) {
        for (GameTeam var3 : this.teams.values()) {
            for (UUID var5 : var3.members) {
                Player var6 = Bukkit.getPlayer(var5);
                if (var6 != null) {
                    var6.sendMessage("§8[" + this.mode.cc + this.mode.ko + "§8] §r" + var1);
                }
            }
        }
    }

    void titleAll(String var1, String var2) {
        for (GameTeam var4 : this.teams.values()) {
            for (UUID var6 : var4.members) {
                Player var7 = Bukkit.getPlayer(var6);
                if (var7 != null) {
                    var7.sendTitle(var1, var2, 5, 40, 10);
                }
            }
        }
    }

    void broadcastTeam(GameTeam var1, String var2) {
        for (UUID var4 : var1.members) {
            Player var5 = Bukkit.getPlayer(var4);
            if (var5 != null) {
                var5.sendMessage(var1.color.cc + "[팀] §r" + var2);
            }
        }
    }

    void playAll(String var1, float var2, float var3) {
        for (GameTeam var5 : this.teams.values()) {
            for (UUID var7 : var5.members) {
                Player var8 = Bukkit.getPlayer(var7);
                if (var8 != null) {
                    var8.playSound(var8.getLocation(), var1, var2, var3);
                }
            }
        }
    }

    static void actionbar(Player var0, String var1) {
        var0.spigot().sendMessage(ChatMessageType.ACTION_BAR, TextComponent.fromLegacyText(var1));
    }

    static String nameOf(UUID var0) {
        if (var0 == null) {
            return "-";
        } else {
            Player var1 = Bukkit.getPlayer(var0);
            return var1 == null ? "(나감)" : var1.getName();
        }
    }

    void start(List<UUID> var1, Bot.Level var2) {
        ArrayList var3 = new ArrayList();

        for (UUID var5 : var1) {
            if (Bukkit.getPlayer(var5) != null) {
                var3.add(var5);
            }
        }

        Collections.shuffle(var3, this.rng);
        this.teams.clear();
        GameTeam var15 = new GameTeam(TeamColor.BLUE);
        GameTeam var16 = new GameTeam(TeamColor.RED);
        this.teams.put(TeamColor.BLUE, var15);
        this.teams.put(TeamColor.RED, var16);
        boolean var6 = this.mode == GameManager.Mode.AI;
        int var7 = var6 ? var3.size() : var3.size() / 2;

        for (int var8 = 0; var8 < var3.size(); var8++) {
            GameTeam var9 = var8 < var7 ? var15 : var16;
            var9.members.add((UUID)var3.get(var8));
            this.teamOf.put((UUID)var3.get(var8), var9.color);
        }

        for (GameTeam var20 : this.teams.values()) {
            var20.elixir = this.startElixir;
            if (!var20.members.isEmpty()) {
                ArrayList var10 = new ArrayList();

                for (UUID var12 : var20.members) {
                    if (!this.core.profiles.get(var12).lastWasKing) {
                        var10.add(var12);
                    }
                }

                if (var10.isEmpty()) {
                    var10.addAll(var20.members);
                }

                var20.king = (UUID)var10.get(this.rng.nextInt(var10.size()));
                ArrayList var25 = new ArrayList();

                for (UUID var13 : var20.members) {
                    if (!var13.equals(var20.king)) {
                        var25.add(var13);
                    }
                }

                Collections.shuffle(var25, this.rng);
                var20.queue.addAll(var25);

                for (UUID var32 : var20.members) {
                    Profile var14 = this.core.profiles.get(var32);
                    var14.lastWasKing = var32.equals(var20.king);
                    if (var14.lastWasKing) {
                        var14.kingGames++;
                    }

                    var14.dirty = true;
                }

                for (String var33 : this.core.profiles.get(var20.king).deck()) {
                    if (this.cards.containsKey(var33) && var20.deck.size() < 8 && !var20.deck.contains(var33)) {
                        var20.deck.add(var33);
                    }
                }
            }
        }

        if (var6) {
            this.fillRandom(var16);
            var16.deckReady = true;
            this.bot = new Bot(this, TeamColor.RED, var2 == null ? Bot.Level.NORMAL : var2);
        }

        this.battle.buildTowers();
        this.bar = Bukkit.createBossBar("§6덱 확인 중...", BarColor.YELLOW, BarStyle.SOLID, new BarFlag[0]);

        for (GameTeam var21 : this.teams.values()) {
            this.createBoard(var21);

            for (UUID var26 : var21.members) {
                Player var31 = Bukkit.getPlayer(var26);
                if (var31 != null) {
                    this.core.lobby.leaveLobby(var31);
                    this.resetPlayer(var31);
                    var31.setScoreboard(var21.board);
                    this.bar.addPlayer(var31);
                    if (var26.equals(var21.king)) {
                        var31.setGameMode(GameMode.ADVENTURE);
                        var31.teleport(this.arena.balcony(var21.color));
                        var31.sendTitle("§6당신은 킹입니다", var21.color.label() + " 팀 §7- " + this.mode.ko, 5, 60, 10);
                        var31.sendMessage("§6[킹] §f카드를 들고 경기장 칸을 우클릭하면 소환됩니다.");
                    } else {
                        var31.setGameMode(GameMode.SPECTATOR);
                        var31.teleport(this.arena.spectate(var21.color));
                        var31.sendTitle(var21.color.label() + " 팀 유닛", "§f소환 대기열 §e" + var21.queuePos(var26) + "번째", 5, 60, 10);
                        var31.sendMessage("§b[유닛] §f킹이 카드를 쓰면 대기열 순서대로 그 유닛으로 소환됩니다. 팀 채팅으로 의견을 보낼 수 있어요 (슬로우모드).");
                    }
                }
            }

            if (var21.king != null) {
                this.broadcastTeam(
                    var21,
                    "§f킹: §6"
                        + nameOf(var21.king)
                        + " §7| 인원 "
                        + var21.members.size()
                        + "명"
                        + (var6 && var21.color == TeamColor.BLUE ? " §7| 상대: §a봇 (" + this.bot.level.ko + ")" : "")
                );
            }
        }

        this.phase = GameManager.Phase.DECK;
        this.deckLeft = this.deckSeconds;
        boolean var19 = true;

        for (GameTeam var24 : this.teams.values()) {
            if (var24.king != null) {
                Player var27 = var24.kingPlayer();
                if (var24.deck.size() == 8) {
                    var24.deckReady = true;
                    if (var27 != null) {
                        var27.sendMessage("§a저장된 덱으로 출전합니다. §7(바꾸려면 " + this.deckSeconds + "초 안에 덱 메뉴)");
                    }
                } else if (var27 != null) {
                    Bukkit.getScheduler().runTaskLater(this.plugin, () -> this.openDeck(var27), 15L);
                }

                var19 &= var24.deckReady;
            }
        }

        if (var19) {
            this.deckLeft = Math.min(this.deckLeft, 4);
        }
    }

    void fillRandom(GameTeam var1) {
        ArrayList var2 = new ArrayList();

        for (CardDef var4 : this.cards.values()) {
            if (var4.deckable) {
                var2.add(var4.id);
            }
        }

        Collections.shuffle(var2, this.rng);

        for (String var6 : var2) {
            if (var1.deck.size() < 8 && !var1.deck.contains(var6)) {
                var1.deck.add(var6);
            }
        }
    }

    void openDeck(Player var1) {
        GameTeam var2 = this.kingTeam(var1);
        if (this.phase == GameManager.Phase.DECK && var2 != null) {
            new Menus.DeckMenu(this.core, var1, var2.deck, this).open();
        } else if (this.phase == GameManager.Phase.PLAYING && var2 != null) {
            var1.sendMessage("§c경기 중에는 덱을 바꿀 수 없습니다.");
        } else {
            new Menus.DeckMenu(this.core, var1, null, null).open();
        }
    }

    void confirmDeck(Player var1) {
        GameTeam var2 = this.kingTeam(var1);
        if (var2 != null && this.phase == GameManager.Phase.DECK) {
            if (var2.deck.size() != 8) {
                var1.sendMessage("§c덱은 8장을 꽉 채워야 합니다.");
            } else {
                Profile var3 = this.core.profiles.get(var1);
                var3.deck().clear();
                var3.deck().addAll(var2.deck);
                var3.dirty = true;
                var2.deckReady = true;
                var1.closeInventory();
                this.broadcastGame(var2.color.label() + " §f팀 킹 덱 준비 완료");
                boolean var4 = true;

                for (GameTeam var6 : this.teams.values()) {
                    var4 &= var6.deckReady || var6.king == null && this.bot == null;
                }

                if (var4) {
                    this.deckLeft = Math.min(this.deckLeft, 3);
                }
            }
        }
    }

    void forceStart() {
        if (this.phase == GameManager.Phase.DECK) {
            for (GameTeam var2 : this.teams.values()) {
                this.fillRandom(var2);
                var2.deckReady = true;
            }

            this.beginPlay();
        }
    }

    void beginPlay() {
        for (GameTeam var2 : this.teams.values()) {
            if (var2.deck.size() < 8) {
                this.fillRandom(var2);
            }

            ArrayList var3 = new ArrayList<>(var2.deck);
            Collections.shuffle(var3, this.rng);

            for (int var4 = 0; var4 < 4; var4++) {
                var2.hand[var4] = (String)var3.get(var4);
            }

            var2.pending.clear();

            for (int var5 = 4; var5 < 8; var5++) {
                var2.pending.add((String)var3.get(var5));
            }

            var2.elixir = this.startElixir;
            Player var6 = var2.kingPlayer();
            if (var6 != null) {
                var6.closeInventory();
                this.equipKing(var6, var2);
            }
        }

        this.secondsLeft = this.matchSeconds;
        this.overtime = false;
        this.phase = GameManager.Phase.PLAYING;
        this.playStartTick = this.tick;
        this.bar.setColor(BarColor.WHITE);
        this.titleAll("§6§l전투 시작!", "§f킹 타워를 부수면 승리");
        this.playAll("entity.ender_dragon.growl", 0.6F, 1.2F);
    }

    void equipKing(Player var1, GameTeam var2) {
        var1.setGameMode(GameMode.ADVENTURE);
        var1.teleport(this.arena.balcony(var2.color));
        if (this.kingFly) {
            var1.setAllowFlight(true);
            var1.setFlying(true);
            var1.setFlySpeed((float)Math.max(0.01, Math.min(1.0, this.kingFlySpeed)));
        }

        var2.handMask = -1;
        this.giveHand(var2);
    }

    void onTick() {
        this.tick++;
        switch (this.phase) {
            case DECK:
                if (this.tick % 20L == 0L) {
                    this.deckLeft--;
                    boolean var1 = true;

                    for (GameTeam var3 : this.teams.values()) {
                        if (var3.king != null) {
                            var1 &= var3.deckReady;
                            Player var4 = var3.kingPlayer();
                            if (var4 != null) {
                                actionbar(
                                    var4,
                                    var3.deckReady
                                        ? "§a준비 완료 §7- " + this.deckLeft + "초 후 시작"
                                        : "§e덱 " + var3.deck.size() + "/8 §7- §f" + this.deckLeft + "초 §7(시간이 지나면 자동 완성)"
                                );
                            }

                            for (UUID var6 : var3.queue) {
                                Player var7 = Bukkit.getPlayer(var6);
                                if (var7 != null) {
                                    actionbar(var7, "§7킹이 덱을 고르는 중... §f대기열 " + var3.queuePos(var6) + "번째 §8· " + this.deckLeft + "초");
                                }
                            }
                        }
                    }

                    if (this.bar != null) {
                        this.bar.setTitle("§6덱 확인 §f" + this.deckLeft + "초");
                        this.bar.setProgress(Math.max(0.0, Math.min(1.0, (double)this.deckLeft / Math.max(1, this.deckSeconds))));
                    }

                    if (var1 && this.deckLeft > 3) {
                        this.deckLeft = 3;
                    }

                    if (this.deckLeft <= 0) {
                        this.beginPlay();
                    }

                    this.updateBoards();
                }
                break;
            case PLAYING:
                this.battle.tick();
                if (this.phase == GameManager.Phase.PLAYING) {
                    this.test.tick();
                    if (this.bot != null && this.botEnabled) {
                        this.bot.tick();
                    }

                    this.regenElixir();
                    if (this.tick % 20L == 0L) {
                        this.timerSecond();
                    }

                    if (this.tick % 2L == 0L) {
                        this.updateHud();
                    }

                    if (this.tick % 20L == 0L) {
                        this.updateBoards();
                    }
                }
        }
    }

    boolean doubleElixir() {
        return this.overtime || this.secondsLeft <= this.doubleLast;
    }

    void regenElixir() {
        double var1 = 1.0 / (this.elixirSeconds * 20.0) * (this.doubleElixir() ? 2 : 1);

        for (GameTeam var4 : this.teams.values()) {
            var4.elixir = Math.min(this.maxElixir, var4.elixir + var1);
        }
    }

    void timerSecond() {
        if (!this.test.active || !this.test.timerFrozen) {
            this.secondsLeft--;
            if (!this.overtime && this.secondsLeft == this.doubleLast) {
                this.titleAll("§d더블 엘릭서!", "§f남은 " + this.doubleLast + "초");
                this.playAll("block.note_block.pling", 1.0F, 1.5F);
            }

            if (this.secondsLeft <= 0) {
                GameTeam var1 = this.teams.get(TeamColor.BLUE);
                GameTeam var2 = this.teams.get(TeamColor.RED);
                if (!this.overtime) {
                    if (var1.crowns != var2.crowns) {
                        this.endMatch(var1.crowns > var2.crowns ? TeamColor.BLUE : TeamColor.RED, "시간 종료 - 크라운 승리");
                    } else {
                        this.overtime = true;
                        this.secondsLeft = this.overtimeSeconds;
                        this.titleAll("§c§l연장전!", "§f먼저 타워를 부수는 팀이 승리 (서든데스)");
                        this.playAll("entity.wither.spawn", 0.5F, 1.4F);
                    }
                } else {
                    double var3 = this.battle.lowestTowerRatio(TeamColor.BLUE);
                    double var5 = this.battle.lowestTowerRatio(TeamColor.RED);
                    if (Math.abs(var3 - var5) < 1.0E-6) {
                        this.endMatch(null, "무승부");
                    } else {
                        this.endMatch(var3 > var5 ? TeamColor.BLUE : TeamColor.RED, "타이브레이커 - 남은 타워 체력");
                    }
                }
            }
        }
    }

    void onCrown(TeamColor var1, boolean var2) {
        GameTeam var3 = this.teams.get(var1);
        if (var2) {
            var3.crowns = 3;
            this.endMatch(var1, "킹 타워 파괴!");
        } else {
            var3.crowns = Math.min(3, var3.crowns + 1);
            this.titleAll(var1.label() + " §f팀 크라운 +1", "§f" + this.teams.get(TeamColor.BLUE).crowns + " : " + this.teams.get(TeamColor.RED).crowns);
            this.playAll("entity.generic.explode", 0.8F, 0.8F);
            if (this.overtime) {
                this.endMatch(var1, "연장전 크라운");
            }
        }
    }

    void endMatch(TeamColor var1, String var2) {
        if (this.phase != GameManager.Phase.ENDING && this.phase != GameManager.Phase.DONE) {
            this.phase = GameManager.Phase.ENDING;
            this.winner = var1;
            this.endReason = var2;
            Map var3 = this.core.matchEnded(this, var1);

            for (GameTeam var5 : this.teams.values()) {
                for (UUID var7 : var5.members) {
                    Player var8 = Bukkit.getPlayer(var7);
                    if (var8 != null) {
                        String var9 = var3.getOrDefault(var7, "");
                        if (var1 == null) {
                            var8.sendTitle("§e무승부", "§7" + var2 + var9, 5, 90, 20);
                        } else if (var1 == var5.color) {
                            var8.sendTitle("§6§l승리!", "§f" + var2 + var9, 5, 90, 20);
                        } else {
                            var8.sendTitle("§c§l패배", "§7" + var2 + var9, 5, 90, 20);
                        }
                    }
                }
            }

            this.broadcastGame(
                "§f결과: "
                    + (var1 == null ? "§e무승부" : var1.label() + " §f팀 승리")
                    + " §7("
                    + var2
                    + ") §f"
                    + this.teams.get(TeamColor.BLUE).crowns
                    + " : "
                    + this.teams.get(TeamColor.RED).crowns
            );
            this.playAll("ui.toast.challenge_complete", 1.0F, 1.0F);
            if (this.bar != null) {
                this.bar.setTitle("§6경기 종료 - " + (var1 == null ? "무승부" : var1.ko + " 승리"));
            }

            Bukkit.getScheduler().runTaskLater(this.plugin, this::cleanup, this.endDelay * 20L);
        }
    }

    void stopMatch(String var1) {
        if (this.phase != GameManager.Phase.DONE) {
            this.broadcastGame("§c" + var1);
            this.cleanup();
        }
    }

    void cleanup() {
        if (this.phase != GameManager.Phase.DONE) {
            this.phase = GameManager.Phase.DONE;
            this.battle.clearAll();
            ArrayList var1 = new ArrayList();

            for (GameTeam var3 : this.teams.values()) {
                for (UUID var5 : var3.members) {
                    Player var6 = Bukkit.getPlayer(var5);
                    if (var6 != null) {
                        this.models.remove(var6);
                        this.resetPlayer(var6);
                        var1.add(var6);
                    }
                }
            }

            if (this.bar != null) {
                this.bar.removeAll();
                this.bar = null;
            }

            this.test.reset();
            this.teams.clear();
            this.teamOf.clear();
            this.activeUnits.clear();
            this.chatCooldown.clear();
            this.slot.match = null;
            this.core.matchClosed(this);

            for (Player var8 : var1) {
                if (var8.isOnline()) {
                    this.core.lobby.toLobby(var8);
                }
            }
        }
    }

    void giveHand(GameTeam var1) {
        Player var2 = var1.kingPlayer();
        if (var2 != null) {
            if (!this.activeUnits.contains(var1.king)) {
                var2.getInventory().clear();
                int var3 = 0;

                for (int var4 = 0; var4 < 4; var4++) {
                    CardDef var5 = this.cards.get(var1.hand[var4]);
                    boolean var6 = var5 != null
                        && var1.elixir + 1.0E-9 >= this.costOf(var1, var5)
                        && (var5 == null || !var5.id.equals("mirror") || var1.lastPlayed != null);
                    if (var6) {
                        var3 |= 1 << var4;
                    }

                    var2.getInventory()
                        .setItem(var4, var5 != null && var5.id.equals("mirror") ? this.mirrorItem(var1, var5, false, !var6) : this.cardItem(var5, false, !var6));
                }

                var1.handMask = var3;
                String var7 = var1.pending.peek();
                CardDef var8 = var7 == null ? null : this.cards.get(var7);
                if (var8 != null) {
                    var2.getInventory().setItem(4, var8.id.equals("mirror") ? this.mirrorItem(var1, var8, true, true) : this.cardItem(var8, true, true));
                }

                boolean var9 = (this.tick - this.playStartTick) / 20L >= this.core.surrenderAfter;
                var2.getInventory()
                    .setItem(
                        8,
                        this.core
                            .lobby
                            .tagged(
                                Ui.icon(
                                    var9 ? "surrender" : "surrender_off",
                                    Material.WHITE_BANNER,
                                    var9 ? "§c§l항복" : "§7항복 §8(" + this.core.surrenderAfter + "초 후 가능)",
                                    "§7우클릭 두 번: 항복",
                                    this.mode == GameManager.Mode.RANKED ? "§7랭크전: 킹만 트로피 감소, 유닛은 보호" : "§7트로피 변동 없음"
                                ),
                                "surrender"
                            )
                    );
            }
        }
    }

    ItemStack cardItem(CardDef var1, boolean var2, boolean var3) {
        return this.core.cardItem(var1, var2, var3);
    }

    ItemStack mirrorItem(GameTeam var1, CardDef var2, boolean var3, boolean var4) {
        CardDef var5 = var1.lastPlayed == null ? null : this.cards.get(var1.lastPlayed);
        if (var5 == null) {
            ItemStack var10 = this.cardItem(var2, var3, true);
            ItemMeta var11 = var10.getItemMeta();
            if (var11 != null) {
                var11.setDisplayName((var3 ? "§7다음 카드 ▶ " : "§7") + "반사경 §8(아직 낸 카드 없음)");
                var11.setLore(List.of("§7마지막에 낸 카드를 한 번 더 냅니다", "§7비용 = 그 카드 + 1"));
                var10.setItemMeta(var11);
            }

            return var10;
        } else {
            int var6 = this.costOf(var1, var2);
            ItemStack var7 = this.cardItem(var5, var3, var4);
            ItemMeta var8 = var7.getItemMeta();
            if (var8 != null) {
                var8.setDisplayName(
                    (var3 ? "§7다음 카드 ▶ " : (var4 ? "§7" : "§b§l")) + "반사경 §f→ " + (var4 ? "§7" : "§e§l") + var5.name + " §d" + var6 + "\ud83d\udca7"
                );
                ArrayList var9 = new ArrayList();
                var9.add("§7반사경: 마지막 카드 §f" + var5.name + " §7를 한 번 더");
                var9.add("§d엘릭서 " + var6 + " §8(" + var5.name + " " + var5.elixir + " + 1)");
                if (!var3) {
                    var9.add(var4 ? "§c엘릭서 부족" : "§e우클릭: 바라보는 칸에 사용");
                }

                var8.setLore(var9);
                var8.getPersistentDataContainer().set(this.cardKey, PersistentDataType.STRING, var2.id);
                var7.setItemMeta(var8);
            }

            var7.setAmount(Math.max(1, var6));
            return Ui.glow(var7, true);
        }
    }

    String cardIdOf(ItemStack var1) {
        if (var1 != null && var1.hasItemMeta()) {
            ItemMeta var2 = var1.getItemMeta();
            if (var2 == null) {
                return null;
            } else {
                return var2.getPersistentDataContainer().has(this.previewKey, PersistentDataType.STRING)
                    ? null
                    : (String)var2.getPersistentDataContainer().get(this.cardKey, PersistentDataType.STRING);
            }
        } else {
            return null;
        }
    }

    int costOf(GameTeam var1, CardDef var2) {
        if (var2 == null) {
            return 99;
        } else if (var2.id.equals("mirror")) {
            CardDef var3 = var1.lastPlayed == null ? null : this.cards.get(var1.lastPlayed);
            return var3 == null ? 99 : Math.min(10, var3.elixir + 1);
        } else {
            return var2.elixir;
        }
    }

    void kingUseCard(Player var1, int var2) {
        if (this.phase == GameManager.Phase.PLAYING) {
            GameTeam var3 = this.kingTeam(var1);
            if (var3 != null && var2 >= 0 && var2 <= 3) {
                CardDef var4 = this.cards.get(var3.hand[var2]);
                if (var4 != null) {
                    Block var5 = var1.getTargetBlockExact(160);
                    if (var5 == null) {
                        this.warn(var1, "§c경기장 칸을 바라보세요");
                    } else {
                        int var6 = this.arena.tileX(var5.getX() + 0.5);
                        int var7 = this.arena.tileZ(var5.getZ() + 0.5);
                        String var8 = this.test.isAdmin(var1.getUniqueId()) && this.test.freePlace
                            ? (this.arena.inField(var6, var7) ? null : "경기장 밖입니다")
                            : this.battle.placementError(var3.color, var4, var6, var7);
                        if (var8 != null) {
                            this.warn(var1, "§c" + var8);
                        } else if (!var4.id.equals("mirror") || var3.lastPlayed != null && this.cards.get(var3.lastPlayed) != null) {
                            if (var4.id.equals("mirror")) {
                                String var9 = this.battle.placementError(var3.color, this.cards.get(var3.lastPlayed), var6, var7);
                                if (var9 != null && (!this.test.isAdmin(var1.getUniqueId()) || !this.test.freePlace)) {
                                    this.warn(var1, "§c" + var9);
                                    return;
                                }
                            }

                            int var12 = this.costOf(var3, var4);
                            if (var3.elixir + 1.0E-9 < var12) {
                                var3.alertUntil = this.tick + 30L;
                                var3.alertNeed = var12;
                                double var13 = (var12 - var3.elixir) * this.elixirSeconds / (this.doubleElixir() ? 2 : 1);
                                var1.sendTitle(
                                    " ",
                                    "§c§l엘릭서 부족! §f"
                                        + String.format("%.1f", var3.elixir)
                                        + " §7/ §d"
                                        + var12
                                        + " §8· §7"
                                        + String.format("%.1f", var13)
                                        + "초 후 가능",
                                    0,
                                    22,
                                    6
                                );
                                var1.playSound(var1.getLocation(), "block.note_block.bass", 1.0F, 0.5F);
                                var1.playSound(var1.getLocation(), "entity.villager.no", 0.6F, 1.3F);
                                this.updateHud();
                            } else {
                                var1.playSound(var1.getLocation(), "block.amethyst_block.chime", 0.8F, 1.4F);
                                var3.elixir -= var12;
                                String var10 = var3.pending.poll();
                                var3.pending.add(var4.id);
                                var3.hand[var2] = var10;
                                this.giveHand(var3);
                                var1.getInventory().setHeldItemSlot(var2);
                                String var11 = var4.id.equals("mirror") && var3.lastPlayed != null && this.cards.get(var3.lastPlayed) != null
                                    ? "반사경 → " + this.cards.get(var3.lastPlayed).name + " §d(" + var12 + "\ud83d\udca7)"
                                    : var4.name;
                                this.battle.deploy(var3, var4, var6, var7, var5.getLocation());
                                this.broadcastTeam(var3, "§6킹 §f→ §b" + var11 + " §7(" + var6 + "," + var7 + ")");
                            }
                        } else {
                            this.warn(var1, "§c반사경: 아직 낸 카드가 없습니다");
                        }
                    }
                }
            }
        }
    }

    void surrender(Player var1) {
        GameTeam var2 = this.kingTeam(var1);
        if (var2 == null) {
            var1.sendMessage("§c항복은 킹만 할 수 있습니다.");
        } else if (this.phase == GameManager.Phase.PLAYING) {
            long var3 = (this.tick - this.playStartTick) / 20L;
            if (var3 < this.core.surrenderAfter) {
                this.warn(var1, "§c항복은 " + (this.core.surrenderAfter - var3) + "초 후부터 가능");
            } else {
                Long var5 = this.surrenderConfirm.get(var1.getUniqueId());
                if (var5 != null && this.tick - var5 <= 100L) {
                    this.surrendered = true;
                    this.broadcastGame(var2.color.label() + " §f팀 킹이 §c항복§f했습니다.");
                    this.endMatch(var2.color.other(), var2.color.ko + " 팀 항복");
                } else {
                    this.surrenderConfirm.put(var1.getUniqueId(), this.tick);
                    var1.sendTitle(
                        "§c항복하시겠습니까?", "§f5초 안에 한 번 더 누르면 항복 §7(" + (this.mode == GameManager.Mode.RANKED ? "킹만 트로피 감소" : "트로피 변동 없음") + ")", 0, 60, 10
                    );
                    var1.playSound(var1.getLocation(), "block.note_block.bass", 1.0F, 0.8F);
                }
            }
        }
    }

    void botPlayed(GameTeam var1, CardDef var2, int[] var3) {
        if (this.mode == GameManager.Mode.TEST) {
            Player var4 = this.test.admin == null ? null : Bukkit.getPlayer(this.test.admin);
            if (var4 != null) {
                var4.sendMessage("§8[봇] " + var1.color.cc + var2.name + " §7(" + var3[0] + "," + var3[1] + ")");
            }
        }
    }

    void warn(Player var1, String var2) {
        var1.sendTitle(" ", var2, 0, 18, 6);
        var1.playSound(var1.getLocation(), "block.note_block.bass", 1.0F, 0.6F);
    }

    String skinModel(TeamColor var1, String var2, String var3, UUID var4, boolean var5) {
        if (!this.core.skinsEnabled) {
            return var3;
        } else {
            Profile var6 = null;
            if (var4 != null) {
                Profile var7 = this.core.profiles.get(var4);
                if (this.core.skins.selected(var7, var2) != null) {
                    var6 = var7;
                }
            }

            if (var6 == null) {
                GameTeam var9 = this.teams.get(var1);
                if (var9 != null && var9.king != null) {
                    var6 = this.core.profiles.get(var9.king);
                }
            }

            Skins.Skin var10 = this.core.skins.selected(var6, var2);
            if (var10 == null) {
                return var3;
            } else {
                String var8 = var5 ? var10.barrelModel() : var10.model();
                return var8 != null && !var8.isEmpty() ? var8 : var3;
            }
        }
    }

    void updateHud() {
        GameTeam var1 = this.teams.get(TeamColor.BLUE);
        GameTeam var2 = this.teams.get(TeamColor.RED);
        if (this.bar != null) {
            this.bar.setTitle(Glyphs.scoreLine(var1.crowns, var2.crowns, this.secondsLeft, this.overtime, this.doubleElixir()));
            double var3 = this.overtime ? this.overtimeSeconds : this.matchSeconds;
            this.bar.setProgress(Math.max(0.0, Math.min(1.0, this.secondsLeft / var3)));
            this.bar.setColor(this.overtime ? BarColor.RED : (this.doubleElixir() ? BarColor.PURPLE : BarColor.WHITE));
        }

        for (GameTeam var4 : this.teams.values()) {
            Player var5 = var4.kingPlayer();
            if (var5 != null && !this.activeUnits.contains(var4.king)) {
                var5.setLevel((int)Math.floor(var4.elixir));
                var5.setExp((float)Math.min(0.999, var4.elixir - Math.floor(var4.elixir)));
                boolean var6 = this.tick < var4.alertUntil;
                int var7 = 0;
                String var8 = this.cardIdOf(var5.getInventory().getItemInMainHand());
                if (var8 != null && this.cards.get(var8) != null) {
                    var7 = this.cards.get(var8).elixir;
                }

                if (var6) {
                    var7 = Math.max(var7, var4.alertNeed);
                }

                boolean var9 = var6 && this.tick / 4L % 2L == 0L;
                actionbar(var5, Glyphs.elixirBar(var4.elixir, (int)this.maxElixir, var7, var9, this.doubleElixir()));
                int var10 = 0;

                for (int var11 = 0; var11 < 4; var11++) {
                    CardDef var12 = this.cards.get(var4.hand[var11]);
                    if (var12 != null && var4.elixir + 1.0E-9 >= this.costOf(var4, var12)) {
                        var10 |= 1 << var11;
                    }
                }

                if (!var4.surrenderShown && this.tick - this.playStartTick >= this.core.surrenderAfter * 20L) {
                    var4.surrenderShown = true;
                    var4.handMask = -1;
                }

                if (var10 != var4.handMask) {
                    int var20 = var5.getInventory().getHeldItemSlot();
                    this.giveHand(var4);
                    var5.getInventory().setHeldItemSlot(var20);
                }

                this.battle.previewPlacement(var5, var4);
            }

            for (UUID var15 : var4.members) {
                if (!var15.equals(var4.king) || this.activeUnits.contains(var15)) {
                    Player var16 = Bukkit.getPlayer(var15);
                    if (var16 != null) {
                        Combatant var17 = this.battle.unitOf(var15);
                        if (var17 != null) {
                            long var18 = Math.max(0L, var17.nextAttack - this.tick);
                            String var21 = this.tick < var17.deployUntil
                                ? " §b⏳ 배치 중 (무적) " + String.format("%.1f", (var17.deployUntil - this.tick) / 20.0) + "초"
                                : "";
                            actionbar(
                                var16,
                                var17.team.cc
                                    + var17.card.name
                                    + " §c❤ "
                                    + (int)Math.ceil(var17.hp)
                                    + "/"
                                    + (int)var17.maxHp
                                    + (var21.isEmpty() ? (var18 > 0L ? " §7공격 대기 " + String.format("%.1f", var18 / 20.0) + "초" : " §a공격 가능") : var21)
                            );
                        } else if (this.battle.isReserved(var15)) {
                            actionbar(var16, "§e해골통 탑승 중 - 터지면 해골로 소환");
                        } else {
                            int var19 = var4.queuePos(var15);
                            if (var19 == 1) {
                                actionbar(var16, "§a▶ 다음 카드에 소환됩니다!");
                            } else if (var19 > 1) {
                                actionbar(var16, "§e소환 대기 §f" + var19 + "번째");
                            }
                        }
                    }
                }
            }
        }
    }

    void createBoard(GameTeam var1) {
        var1.board = Bukkit.getScoreboardManager().getNewScoreboard();
        Objective var2 = var1.board.registerNewObjective("clash", "dummy", "§6§l클래시 마크 §7" + this.mode.ko);
        var2.setDisplaySlot(DisplaySlot.SIDEBAR);
        var1.boardLines.clear();
    }

    void updateBoards() {
        for (GameTeam var2 : this.teams.values()) {
            if (var2.board != null) {
                Objective var3 = var2.board.getObjective("clash");
                if (var3 != null) {
                    ArrayList var4 = new ArrayList();
                    var4.add("§7" + var2.color.label() + " 팀");
                    if (this.phase == GameManager.Phase.PLAYING) {
                        var4.add(
                            "§f시간 " + (this.overtime ? "§c연장 " : "") + this.secondsLeft / 60 + ":" + String.format("%02d", Math.max(0, this.secondsLeft % 60))
                        );
                        var4.add("§9" + this.teams.get(TeamColor.BLUE).crowns + " §f: §c" + this.teams.get(TeamColor.RED).crowns);

                        for (TeamColor var8 : TeamColor.values()) {
                            StringBuilder var9 = new StringBuilder(var8.cc + (var8 == var2.color ? "아군 " : "적 "));

                            for (Combatant var11 : this.battle.all) {
                                if (var11.isTower() && var11.team == var8) {
                                    int var12 = var11.dead ? 0 : (int)Math.ceil(var11.hp * 100.0 / var11.maxHp);
                                    var9.append(var11.kind == Combatant.Kind.KING_TOWER ? "§6♔" : "§7◆").append(var11.dead ? "§8✖ " : "§f" + var12 + "% ");
                                }
                            }

                            var4.add(var9.toString());
                        }
                    }

                    var4.add(" ");
                    var4.add("§6킹 §f" + (var2.king == null ? "§a봇" + (this.bot != null ? " (" + this.bot.level.ko + ")" : "") : nameOf(var2.king)));
                    List var13 = this.battle.playerUnits(var2.color);
                    if (!var13.isEmpty()) {
                        var4.add("§a전장");

                        for (Combatant var17 : var13) {
                            if (var4.size() >= 12) {
                                break;
                            }

                            var4.add(" §f" + nameOf(var17.playerId) + " §7" + var17.card.name);
                        }
                    }

                    if (!var2.queue.isEmpty()) {
                        var4.add("§e소환 대기열");
                        int var15 = 1;

                        for (UUID var22 : var2.queue) {
                            if (var4.size() >= 15) {
                                break;
                            }

                            var4.add(" §f" + var15++ + ". " + nameOf(var22));
                        }
                    }

                    ArrayList var16 = new ArrayList();

                    for (int var19 = 0; var19 < var4.size(); var19++) {
                        var16.add((String)var4.get(var19) + "§" + Integer.toHexString(var19 % 16) + "§r");
                    }

                    for (String var23 : var2.boardLines) {
                        if (!var16.contains(var23)) {
                            var2.board.resetScores(var23);
                        }
                    }

                    for (int var21 = 0; var21 < var16.size(); var21++) {
                        var3.getScore((String)var16.get(var21)).setScore(var16.size() - var21);
                    }

                    var2.boardLines.clear();
                    var2.boardLines.addAll(var16);
                }
            }
        }
    }

    GameTeam teamOf(Player var1) {
        TeamColor var2 = this.teamOf.get(var1.getUniqueId());
        return var2 == null ? null : this.teams.get(var2);
    }

    GameTeam kingTeam(Player var1) {
        GameTeam var2 = this.teamOf(var1);
        return var2 != null && var1.getUniqueId().equals(var2.king) ? var2 : null;
    }

    boolean has(Player var1) {
        return this.teamOf.containsKey(var1.getUniqueId());
    }

    boolean inMatch(Player var1) {
        return this.has(var1) && this.phase != GameManager.Phase.LOBBY && this.phase != GameManager.Phase.DONE;
    }

    void resetPlayer(Player var1) {
        var1.getInventory().clear();
        var1.setWalkSpeed(0.2F);
        var1.setFlySpeed(0.1F);
        var1.setFlying(false);
        var1.setAllowFlight(false);
        var1.setFoodLevel(20);
        var1.setSaturation(5.0F);
        var1.setHealth(20.0);
        var1.setFireTicks(0);
        var1.setLevel(0);
        var1.setExp(0.0F);
        Battle.applyScale(var1, 1.0);
    }

    void sendUiPack(Player var1) {
        this.core.sendUiPack(var1);
    }

    void handleQuit(Player var1) {
        UUID var2 = var1.getUniqueId();
        GameTeam var3 = this.teamOf(var1);
        if (var3 != null) {
            this.battle.playerLeft(var1);
            this.models.remove(var1);
            this.resetPlayer(var1);
            var3.queue.remove(var2);
            var3.members.remove(var2);
            this.teamOf.remove(var2);
            this.activeUnits.remove(var2);
            if (this.bar != null) {
                this.bar.removePlayer(var1);
            }

            if (var2.equals(var3.king) && (this.phase == GameManager.Phase.DECK || this.phase == GameManager.Phase.PLAYING)) {
                this.broadcastGame(var3.color.label() + " §f팀 킹이 나갔습니다.");
                if (this.phase == GameManager.Phase.DECK) {
                    this.stopMatch("킹 퇴장으로 경기 취소");
                    return;
                }

                this.endMatch(var3.color.other(), "상대 킹 퇴장");
            } else if (this.teams.values().stream().allMatch(var0 -> var0.members.isEmpty())) {
                this.stopMatch("참가자 없음");
            }
        }
    }

    static ItemStack named(Material var0, String var1) {
        ItemStack var2 = new ItemStack(var0);
        ItemMeta var3 = var2.getItemMeta();
        if (var3 != null) {
            var3.setDisplayName(var1);
            var2.setItemMeta(var3);
        }

        return var2;
    }

    public static enum Mode {
        RANKED("랭크전", "§6"),
        FRIENDLY("친선전", "§b"),
        AI("AI 대전", "§a"),
        TEST("테스트", "§e");

        final String ko;
        final String cc;

        private Mode(String nullxx, String nullxxx) {
            this.ko = nullxx;
            this.cc = nullxxx;
        }
    }

    public static enum Phase {
        LOBBY,
        DECK,
        PLAYING,
        ENDING,
        DONE;
    }
}
