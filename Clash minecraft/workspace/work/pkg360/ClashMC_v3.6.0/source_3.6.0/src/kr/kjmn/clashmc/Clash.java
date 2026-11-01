package kr.kjmn.clashmc;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;
import java.util.TreeSet;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.NamespacedKey;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;
import org.bukkit.persistence.PersistentDataType;
import org.bukkit.scheduler.BukkitTask;

public final class Clash {
    final ClashPlugin plugin;
    final NamespacedKey cardKey;
    final NamespacedKey previewKey;
    final NamespacedKey uiKey;
    final Map<String, CardDef> cards = new LinkedHashMap<>();
    final Random rng = new Random();
    ModelHook models;
    final Profiles profiles;
    final Skins skins;
    final ArenaPool arenas;
    final Lobby lobby;
    /** 배경음악 */
    final Bgm bgm = new Bgm(this);
    final List<GameManager> matches = new ArrayList<>();
    final Map<String, Room> rooms = new LinkedHashMap<>();
    final Map<UUID, Room> roomOf = new ConcurrentHashMap<>();
    final Map<UUID, Long> rankedQueue = new LinkedHashMap<>();
    final Map<UUID, Long> cooldown = new HashMap<>();
    final Set<UUID> packSent = ConcurrentHashMap.newKeySet();
    /** 플레이어별로 마지막에 보낸 리소스팩 sha1 (같으면 다시 안 보냄 → 리로드해도 화면 안 멈춤) */
    final Map<UUID, String> packSentSha = new ConcurrentHashMap<>();
    long tick;
    BukkitTask task;
    boolean skinsEnabled;
    float kingBarScale;
    float princessBarScale;
    String packUrl;
    String packSha1;
    double kingLossMul;
    double unitLossMul;
    int surrenderAfter;
    int rankedMin;
    int rankedMax;
    int rankedPreferred;
    int rankedMaxWait;
    int rankedMinWait;
    int rankedWindow;
    int rankedWindowGrow;

    Clash(ClashPlugin var1) {
        this.plugin = var1;
        this.cardKey = new NamespacedKey(var1, "card");
        this.previewKey = new NamespacedKey(var1, "preview");
        this.uiKey = new NamespacedKey(var1, "ui");
        this.profiles = new Profiles(var1.getDataFolder(), var1.getLogger());
        this.skins = new Skins(var1.getLogger());
        this.arenas = new ArenaPool(var1);
        this.lobby = new Lobby(this);
    }

    void checkModels(int var1) {
        if (this.models.enabled()) {
            TreeSet<String> var2 = new TreeSet<>();
            Consumer<String> var3 = var1x -> {
                if (var1x != null && !var1x.isEmpty()) {
                    String var2x = var1x;
                    int var3x = var1x.indexOf(35);
                    if (var3x > 0) {
                        var2x = var1x.substring(0, var3x);
                    }

                    int var4 = var2x.indexOf(58);
                    if (var4 > 0) {
                        var2x = var2x.substring(0, var4);
                    }

                    if (var2x.contains("{team}")) {
                        var2.add(var2x.replace("{team}", "blue"));
                        var2.add(var2x.replace("{team}", "red"));
                    } else {
                        var2.add(var2x);
                    }
                }
            };

            for (CardDef var5 : this.cards.values()) {
                var3.accept(var5.model);
                var3.accept(var5.barrelModel);
                var3.accept(var5.projectileModel);
            }

            var3.accept(this.plugin.getConfig().getString("towers.princess-model", ""));
            var3.accept(this.plugin.getConfig().getString("towers.king-model", ""));
            if (this.skinsEnabled) {
                for (Skins.Skin var9 : this.skins.all.values()) {
                    var3.accept(var9.model());
                    var3.accept(var9.barrelModel());
                }
            }

            ArrayList var8 = new ArrayList();

            for (String var6 : var2) {
                if (!this.models.exists(var6)) {
                    var8.add(var6);
                }
            }

            if (var8.isEmpty()) {
                this.plugin.getLogger().info("모델 점검 OK (" + var2.size() + "개)");
            } else if (var8.size() == var2.size() && var1 < 6) {
                Bukkit.getScheduler().runTaskLater(this.plugin, () -> this.checkModels(var1 + 1), 200L);
            } else {
                this.plugin.getLogger().warning("BetterModel 에 없는 모델 " + var8.size() + "/" + var2.size() + "개: " + String.join(", ", var8));
                this.plugin
                    .getLogger()
                    .warning("→ plugins/BetterModel/models/ 바로 안에 .bbmodel 파일을 넣고 /bettermodel reload (스킨 안 쓸 거면 config skins.enabled: false)");
            }
        }
    }

    void load() {
        FileConfiguration var1 = this.plugin.getConfig();
        Glyphs.pack = var1.getBoolean("ui.resource-pack", true);
        this.kingBarScale = (float)var1.getDouble("ui.king-bar-scale", 2.6);
        this.princessBarScale = (float)var1.getDouble("ui.princess-bar-scale", 1.7);
        this.packUrl = var1.getString("ui.pack-url", "");
        this.packSha1 = var1.getString("ui.pack-sha1", "");
        this.skinsEnabled = var1.getBoolean("skins.enabled", true);
        this.rankedMin = Math.max(2, var1.getInt("ranked.min-players", 2));
        this.rankedMax = Math.min(10, var1.getInt("ranked.max-players", 10));
        this.rankedPreferred = var1.getInt("ranked.preferred-players", 4);
        this.rankedMinWait = var1.getInt("ranked.min-wait", 8);
        this.rankedMaxWait = var1.getInt("ranked.max-wait", 30);
        this.rankedWindow = var1.getInt("ranked.trophy-window", 200);
        this.rankedWindowGrow = var1.getInt("ranked.window-grow-per-second", 15);
        this.kingLossMul = var1.getDouble("ranked.king-loss-multiplier", 1.3);
        this.unitLossMul = var1.getDouble("ranked.unit-loss-multiplier", 0.5);
        this.surrenderAfter = var1.getInt("game.surrender-after", 60);
        double var2 = var1.getDouble("game.speed-scale", 1.0);
        this.cards.clear();
        ConfigurationSection var4 = var1.getConfigurationSection("cards");
        org.bukkit.configuration.Configuration defs0 = var1.getDefaults();
        ConfigurationSection defCards0 = defs0 == null ? null : defs0.getConfigurationSection("cards");
        if (var4 != null) {
            for (String var6 : var4.getKeys(false)) {
                ConfigurationSection var7 = var4.getConfigurationSection(var6);
                if (var7 != null) {
                    // 서버 config 의 카드에 없는 항목(새 버전에 추가된 설정)은 jar 기본값으로 채움
                    ConfigurationSection defSec = defCards0 == null ? null : defCards0.getConfigurationSection(var6);
                    if (defSec != null) {
                        for (String dk : defSec.getKeys(false)) {
                            if (!var7.isSet(dk)) {
                                var7.set(dk, defSec.get(dk));
                            }
                        }
                    }

                    try {
                        this.cards.put(var6, new CardDef(var6, var7, 1.0, var2));
                    } catch (Exception var9) {
                        this.plugin.getLogger().warning("카드 설정 오류 (" + var6 + "): " + var9.getMessage());
                    }
                }
            }
        }

        // 서버 config.yml 에 없는 새 카드는 jar 기본 config 에서 가져옴 (config 를 안 바꿔도 새 카드 사용 가능)
        org.bukkit.configuration.Configuration defs = var1.getDefaults();
        ConfigurationSection defCards = defs == null ? null : defs.getConfigurationSection("cards");
        if (defCards != null) {
            List<String> added = new ArrayList<>();
            for (String id : defCards.getKeys(false)) {
                ConfigurationSection sec = defCards.getConfigurationSection(id);
                if (!this.cards.containsKey(id) && sec != null) {
                    try {
                        this.cards.put(id, new CardDef(id, sec, 1.0, var2));
                        added.add(id);
                    } catch (Exception var10) {
                        this.plugin.getLogger().warning("기본 카드 설정 오류 (" + id + "): " + var10.getMessage());
                    }
                }
            }

            if (!added.isEmpty()) {
                this.plugin.getLogger().info("config.yml 에 없는 새 카드 기본값으로 추가: " + String.join(", ", added));
            }
        }

        this.plugin.getLogger().info("카드 " + this.cards.size() + "장 로드");
        if (this.models == null) {
            this.models = new ModelHook(this.plugin.getLogger(), var1.getBoolean("modelengine.enabled", true), var1.getString("modelengine.backend", "auto"));
        }

        File var10 = new File(this.plugin.getDataFolder(), "skins.yml");
        if (!var10.exists()) {
            this.plugin.saveResource("skins.yml", false);
        }

        this.skins.load(var10);
        this.arenas.load();
        this.lobby.load();
        this.bgm.load(var1.getConfigurationSection("bgm"));
    }

    void start() {
        this.profiles.loadAll();
        this.task = Bukkit.getScheduler().runTaskTimer(this.plugin, this::onTick, 1L, 1L);
        Bukkit.getScheduler().runTaskLater(this.plugin, () -> {
            this.lobby.spawnDecor();

            for (Player var2 : Bukkit.getOnlinePlayers()) {
                this.lobby.onJoin(var2);
            }
        }, 40L);
    }

    void shutdown() {
        for (GameManager var2 : new ArrayList<>(this.matches)) {
            var2.cleanup();
        }

        this.lobby.clearDecor();
        this.bgm.stopAll();
        if (this.task != null) {
            this.task.cancel();
        }

        this.profiles.saveDirty();
    }

    void onTick() {
        this.tick++;

        for (GameManager var2 : new ArrayList<>(this.matches)) {
            try {
                var2.onTick();
            } catch (Throwable var4) {
                this.plugin.getLogger().severe("경기 #" + var2.id + " 오류: " + var4);
                var4.printStackTrace();
                var2.stopMatch("오류로 경기가 중단되었습니다.");
            }
        }

        if (this.tick % 20L == 0L) {
            this.matchmake();
        }

        this.lobby.tick();
        if (this.tick % 10L == 0L) {
            try {
                this.bgm.tick();
            } catch (Throwable var5) {
                this.plugin.getLogger().warning("배경음악 오류: " + var5);
            }
        }

        if (this.tick % 1200L == 0L) {
            this.profiles.saveDirty();
        }

        if (this.tick % 600L == 0L) {
            this.profiles.rebuildTop();
            this.lobby.refreshLeaderboard();
        }
    }

    GameManager matchOf(Player var1) {
        for (GameManager var3 : this.matches) {
            if (var3.has(var1)) {
                return var3;
            }
        }

        return null;
    }

    GameManager matchOfEntity(Entity var1) {
        for (GameManager var3 : this.matches) {
            if (var3.battle.isGameEntity(var1)) {
                return var3;
            }
        }

        return null;
    }

    boolean inGame(Player var1) {
        return this.matchOf(var1) != null;
    }

    boolean queued(UUID var1) {
        return this.rankedQueue.containsKey(var1);
    }

    boolean busy(Player var1, boolean var2) {
        if (this.inGame(var1)) {
            if (var2) {
                var1.sendMessage("§c이미 경기 중입니다.");
            }

            return true;
        } else if (this.queued(var1.getUniqueId())) {
            if (var2) {
                var1.sendMessage("§c랭크전 매칭 중입니다. 먼저 매칭을 취소하세요.");
            }

            return true;
        } else {
            return false;
        }
    }

    void startAi(Player var1, Bot.Level var2) {
        Room var3 = this.roomOf.get(var1.getUniqueId());
        ArrayList var4 = new ArrayList();
        if (var3 != null) {
            if (!var3.host.equals(var1.getUniqueId())) {
                var1.sendMessage("§c방장만 시작할 수 있습니다.");
                return;
            }

            for (UUID var6 : var3.members) {
                Player var7 = Bukkit.getPlayer(var6);
                if (var7 != null && !this.busy(var7, false)) {
                    var4.add(var6);
                }
            }
        } else {
            if (this.busy(var1, true)) {
                return;
            }

            var4.add(var1.getUniqueId());
        }

        GameManager var8 = this.create(GameManager.Mode.AI, var3);
        if (var8 == null) {
            var1.sendMessage("§c지금은 빈 경기장이 없습니다. 잠시 후 다시 시도하세요.");
        } else {
            if (var3 != null) {
                var3.match = var8;
            }

            var8.start(var4, var2);
        }
    }

    GameManager create(GameManager.Mode var1, Room var2) {
        ArenaPool.Slot var3 = this.arenas.acquire();
        if (var3 == null) {
            return null;
        } else {
            GameManager var4 = new GameManager(this, var3, var1, var2);
            this.matches.add(var4);
            return var4;
        }
    }

    void joinRanked(Player var1) {
        if (!this.busy(var1, true)) {
            if (this.roomOf.containsKey(var1.getUniqueId())) {
                var1.sendMessage("§c친선전 방에 있는 동안은 랭크전에 참가할 수 없습니다.");
            } else if (this.arenas.slots.isEmpty()) {
                var1.sendMessage("§c경기장이 설정되지 않았습니다. (관리자: /clash arena add)");
            } else {
                Profile var2 = this.profiles.get(var1);
                if (var2.deck().size() < 8) {
                    var1.sendMessage("§e덱이 8장이 아니라서 남은 칸은 경기 시작 때 자동으로 채워집니다.");
                }

                this.rankedQueue.put(var1.getUniqueId(), this.tick);
                this.sendUiPack(var1);
                var1.playSound(var1.getLocation(), "block.note_block.chime", 1.0F, 1.2F);
                var1.sendMessage("§6[랭크전] §f매칭 시작 §7(" + Ranks.label(var2.trophies) + " §7" + var2.trophies + "\ud83c\udfc6)");
                this.lobby.giveHotbar(var1);
            }
        }
    }

    void leaveRanked(Player var1) {
        if (this.rankedQueue.remove(var1.getUniqueId()) != null) {
            var1.sendMessage("§7랭크전 매칭을 취소했습니다.");
            this.lobby.giveHotbar(var1);
        }
    }

    private void matchmake() {
        this.rankedQueue.keySet().removeIf(var0 -> Bukkit.getPlayer(var0) == null);
        if (this.rankedQueue.size() >= this.rankedMin && this.arenas.freeCount() != 0) {
            for (UUID var3 : new ArrayList<>(this.rankedQueue.keySet())) {
                long var4 = (this.tick - this.rankedQueue.get(var3)) / 20L;
                int var6 = this.profiles.get(var3).trophies;
                int var7 = this.rankedWindow + (int)(var4 * this.rankedWindowGrow);
                ArrayList<UUID> var8 = new ArrayList<>();

                for (UUID var10 : this.rankedQueue.keySet()) {
                    if (Math.abs(this.profiles.get(var10).trophies - var6) <= var7) {
                        var8.add(var10);
                    }
                }

                var8.sort(Comparator.comparingInt(var2 -> Math.abs(this.profiles.get(var2).trophies - var6)));
                int var16 = Math.min(this.rankedMax, var8.size());
                if (var16 % 2 == 1) {
                    var16--;
                }

                boolean var17 = var16 >= this.rankedMax
                    || var16 >= this.rankedPreferred && var4 >= this.rankedMinWait
                    || var16 >= this.rankedMin && var4 >= this.rankedMaxWait;
                if (var17) {
                    ArrayList<UUID> var11 = new ArrayList<>(var8.subList(0, var16));
                    if (!var11.contains(var3)) {
                        var11.remove(var11.size() - 1);
                        var11.add(var3);
                    }

                    GameManager var12 = this.create(GameManager.Mode.RANKED, null);
                    if (var12 == null) {
                        return;
                    }

                    for (UUID var14 : var11) {
                        this.rankedQueue.remove(var14);
                    }

                    for (UUID var19 : var11) {
                        Player var15 = Bukkit.getPlayer(var19);
                        if (var15 != null) {
                            var15.sendMessage("§6[랭크전] §a매칭 완료! §f" + var16 + "명 §7(" + var12.slot.name + ")");
                            var15.playSound(var15.getLocation(), "entity.player.levelup", 1.0F, 1.2F);
                        }
                    }

                    var12.start(var11, null);
                    return;
                }
            }
        }
    }

    Room createRoom(Player var1) {
        if (this.busy(var1, true)) {
            return null;
        } else {
            Room var2 = this.roomOf.get(var1.getUniqueId());
            if (var2 != null) {
                return var2;
            } else {
                String var3;
                do {
                    var3 = String.valueOf(1000 + this.rng.nextInt(9000));
                } while (this.rooms.containsKey(var3));

                Room var4 = new Room(var3, var1.getUniqueId());
                this.rooms.put(var3, var4);
                this.roomOf.put(var1.getUniqueId(), var4);
                this.sendUiPack(var1);
                var1.sendMessage("§b[친선전] §f방 생성 §7(코드 §f" + var3 + "§7) §8· §f/clash room invite <닉네임>");
                return var4;
            }
        }
    }

    void invite(Player var1, String var2) {
        Room var3 = this.roomOf.get(var1.getUniqueId());
        if (var3 == null) {
            var3 = this.createRoom(var1);
        }

        if (var3 != null) {
            Player var4 = Bukkit.getPlayerExact(var2);
            if (var4 == null) {
                var1.sendMessage("§c" + var2 + " 님은 접속 중이 아닙니다.");
            } else if (!var4.equals(var1)) {
                var3.invited.add(var4.getUniqueId());
                var1.sendMessage("§b[친선전] §f" + var4.getName() + " 님을 초대했습니다.");
                Ui.clickable(var4, "§b[친선전] §f" + var1.getName() + " 님의 방 초대 §7(코드 " + var3.code + ") ", "§a§l[수락]", "/clash room join " + var3.code);
                var4.playSound(var4.getLocation(), "block.note_block.bell", 1.0F, 1.4F);
            }
        }
    }

    void joinRoom(Player var1, String var2) {
        if (!this.busy(var1, true)) {
            Room var3 = this.rooms.get(var2);
            if (var3 == null) {
                Player var4 = Bukkit.getPlayerExact(var2);
                if (var4 != null) {
                    var3 = this.roomOf.get(var4.getUniqueId());
                }
            }

            if (var3 == null) {
                var1.sendMessage("§c방을 찾을 수 없습니다.");
            } else if (!var3.openToAll && !var3.invited.contains(var1.getUniqueId())) {
                var1.sendMessage("§c초대받지 않은 방입니다.");
            } else if (var3.members.size() >= 10) {
                var1.sendMessage("§c방이 가득 찼습니다 (10명).");
            } else if (var3.match != null) {
                var1.sendMessage("§c이미 경기 중인 방입니다.");
            } else {
                Room var5 = this.roomOf.get(var1.getUniqueId());
                if (var5 != null && var5 != var3) {
                    this.leaveRoom(var1);
                }

                var3.members.add(var1.getUniqueId());
                this.roomOf.put(var1.getUniqueId(), var3);
                this.sendUiPack(var1);
                var3.broadcast("§a" + var1.getName() + " 입장 §7(" + var3.members.size() + "/10)");
                new Menus.RoomMenu(this, var1).open();
            }
        }
    }

    void leaveRoom(Player var1) {
        Room var2 = this.roomOf.remove(var1.getUniqueId());
        if (var2 != null) {
            var2.members.remove(var1.getUniqueId());
            var1.sendMessage("§7방에서 나갔습니다.");
            if (var2.members.isEmpty()) {
                this.rooms.remove(var2.code);
            } else {
                if (var2.host.equals(var1.getUniqueId())) {
                    var2.host = var2.members.iterator().next();
                    var2.broadcast("§e방장이 " + GameManager.nameOf(var2.host) + " 님으로 바뀌었습니다.");
                }

                var2.broadcast("§7" + var1.getName() + " 퇴장 (" + var2.members.size() + "/10)");
            }
        }
    }

    void kick(Player var1, String var2) {
        Room var3 = this.roomOf.get(var1.getUniqueId());
        if (var3 != null && var3.host.equals(var1.getUniqueId())) {
            Player var4 = Bukkit.getPlayerExact(var2);
            if (var4 != null && var3.members.contains(var4.getUniqueId()) && !var4.equals(var1)) {
                this.leaveRoom(var4);
                var3.invited.remove(var4.getUniqueId());
                var4.sendMessage("§c방에서 추방되었습니다.");
            } else {
                var1.sendMessage("§c방에 없는 플레이어입니다.");
            }
        } else {
            var1.sendMessage("§c방장만 할 수 있습니다.");
        }
    }

    void startFriendly(Player var1) {
        Room var2 = this.roomOf.get(var1.getUniqueId());
        if (var2 == null) {
            var1.sendMessage("§c방이 없습니다.");
        } else if (!var2.host.equals(var1.getUniqueId())) {
            var1.sendMessage("§c방장만 시작할 수 있습니다.");
        } else if (var2.match != null) {
            var1.sendMessage("§c이미 경기 중입니다.");
        } else {
            ArrayList<UUID> var3 = new ArrayList<>();

            for (UUID var5 : var2.members) {
                Player var6 = Bukkit.getPlayer(var5);
                if (var6 != null && !this.inGame(var6)) {
                    var3.add(var5);
                }
            }

            if (var3.size() >= 2 && var3.size() % 2 == 0) {
                for (UUID var9 : var3) {
                    this.rankedQueue.remove(var9);
                }

                GameManager var8 = this.create(GameManager.Mode.FRIENDLY, var2);
                if (var8 == null) {
                    var1.sendMessage("§c지금은 빈 경기장이 없습니다.");
                } else {
                    var2.match = var8;
                    var2.broadcast("§a경기 시작! §7(" + var8.slot.name + ")");
                    var8.start(var3, null);
                }
            } else {
                var1.sendMessage("§c친선전은 짝수 인원(2~10명)이 필요합니다. §7(현재 " + var3.size() + "명) §f- AI 대전은 인원 상관없이 가능");
            }
        }
    }

    void testCommand(Player var1, String[] var2) {
        GameManager var3 = this.matchOf(var1);
        String var4 = var2.length < 2 ? "help" : var2[1].toLowerCase();
        if (var4.equals("start")) {
            if (var3 != null) {
                var1.sendMessage("§c이미 경기 중입니다. §f/clash test stop");
            } else {
                this.leaveRanked(var1);
                GameManager var5 = this.create(GameManager.Mode.TEST, null);
                if (var5 == null) {
                    var1.sendMessage("§c빈 경기장이 없습니다.");
                } else {
                    var5.test.command(var1, var2);
                    if (!var5.test.active) {
                        var5.cleanup();
                    }
                }
            }
        } else {
            if (var3 == null || !var3.test.active) {
                var3 = null;
            }

            if (var3 == null) {
                if (var4.equals("help")) {
                    new TestMode(null).help(var1);
                } else {
                    var1.sendMessage("§c테스트 중이 아닙니다. §f/clash test start [blue|red]");
                }
            } else {
                var3.test.command(var1, var2);
            }
        }
    }

    Map<UUID, String> matchEnded(GameManager var1, TeamColor var2) {
        HashMap<UUID, String> var3 = new HashMap<>();
        if (var1.mode == GameManager.Mode.TEST) {
            return var3;
        } else {
            HashMap<TeamColor, Double> var4 = new HashMap<>();

            for (GameTeam var6 : var1.teams.values()) {
                double var7 = 0.0;
                int var9 = 0;

                for (UUID var11 : var6.members) {
                    var7 += this.profiles.get(var11).trophies;
                    var9++;
                }

                var4.put(var6.color, var9 == 0 ? 0.0 : var7 / var9);
            }

            for (GameTeam var23 : var1.teams.values()) {
                for (UUID var8 : var23.members) {
                    Profile var25 = this.profiles.get(var8);
                    boolean var26 = var2 == var23.color;
                    boolean var27 = var2 == null;
                    int var12 = Ranks.TIERS.indexOf(Ranks.tier(var25.trophies));
                    if (var27) {
                        var25.draws++;
                    } else if (var26) {
                        var25.wins++;
                        var25.streak = Math.max(1, var25.streak + 1);
                    } else {
                        var25.losses++;
                        var25.streak = Math.min(-1, var25.streak - 1);
                    }

                    String var13 = "";
                    switch (var1.mode) {
                        case RANKED:
                            double var14 = (Double)var4.get(var23.color);
                            double var16 = var4.getOrDefault(var23.color.other(), var14);
                            if (var27) {
                                var13 = " §7(트로피 ±0)";
                            } else if (var26) {
                                int var18 = Ranks.gain(var14, var16, var25.streak);
                                var25.trophies += var18;
                                var25.rankedWins++;
                                var13 = " §6+" + var18 + "\ud83c\udfc6";
                            } else {
                                boolean var30 = var8.equals(var23.king);
                                double var19 = var30 ? this.kingLossMul : (var1.surrendered ? 0.0 : this.unitLossMul);
                                int var21 = (int)Math.round(Ranks.loss(var14, var16, var25.trophies) * var19);
                                var25.trophies = Math.max(0, var25.trophies - var21);
                                var25.rankedLosses++;
                                var13 = var21 == 0 ? " §7(항복 - 유닛 트로피 보호)" : " §c-" + var21 + "\ud83c\udfc6" + (var30 ? " §7(킹)" : "");
                            }

                            var25.best = Math.max(var25.best, var25.trophies);
                            break;
                        case AI:
                            if (var26) {
                                var25.aiWins++;
                            }
                            break;
                        case FRIENDLY:
                            if (var26) {
                                var25.friendlyWins++;
                            }
                    }

                    var25.dirty = true;
                    var3.put(var8, var13);
                    Player var28 = Bukkit.getPlayer(var8);
                    int var15 = Ranks.TIERS.indexOf(Ranks.tier(var25.trophies));
                    if (var28 != null && var1.mode == GameManager.Mode.RANKED) {
                        var28.sendMessage(
                            "§6[랭크전] §f"
                                + (var26 ? "§a승리" : (var27 ? "§e무승부" : "§c패배"))
                                + var13
                                + " §7→ §f"
                                + var25.trophies
                                + "\ud83c\udfc6 "
                                + Ranks.label(var25.trophies)
                        );
                        if (var15 > var12) {
                            Bukkit.getScheduler().runTaskLater(this.plugin, () -> {
                                if (var28.isOnline()) {
                                    var28.sendTitle("§6§l승급!", Ranks.label(var25.trophies), 10, 60, 20);
                                    var28.playSound(var28.getLocation(), "ui.toast.challenge_complete", 1.0F, 1.2F);
                                }
                            }, (var1.endDelay + 1) * 20L);
                            Bukkit.broadcastMessage("§6[클래시] §f" + var25.name + " 님이 " + Ranks.label(var25.trophies) + " §f티어로 승급했습니다!");
                        }
                    }

                    if (var28 != null) {
                        for (Skins.Skin var17 : this.skins.all.values()) {
                            if (!var17.unlock().equals("default") && this.skins.owns(var25, var17) && var25.skins.add(var17.id())) {
                                var28.sendMessage("§d[스킨] §f새 스킨 해금: " + var17.rarityColor() + var17.name() + " §7(/clash skin)");
                            }
                        }
                    }
                }
            }

            this.profiles.rebuildTop();
            return var3;
        }
    }

    void matchClosed(GameManager var1) {
        this.matches.remove(var1);
        if (var1.room != null) {
            var1.room.match = null;
        }

        this.lobby.refreshLeaderboard();
    }

    ItemStack cardItem(CardDef var1, boolean var2, boolean var3) {
        if (var1 == null) {
            return new ItemStack(Material.BARRIER);
        } else {
            ItemStack var4 = new ItemStack(var1.icon == Material.AIR ? Material.PAPER : var1.icon);
            if (!var2) {
                var4.setAmount(Math.max(1, var1.elixir));
            }

            ItemMeta var5 = var4.getItemMeta();
            if (var5 != null) {
                var5.setDisplayName(var2 ? "§7다음 카드 ▶ §f" + var1.name : (var3 ? "§7" : "§b§l") + var1.name + " §d" + var1.elixir + "\ud83d\udca7");
                ArrayList var6 = new ArrayList();
                var6.add("§7" + var1.typeKo() + " §8· §d엘릭서 " + var1.elixir);
                if (var1.hp > 0.0 && !var1.isSpell()) {
                    var6.add("§c❤ " + (int)var1.hp + (var1.count > 1 ? " §7×" + var1.count : "") + "  §6⚔ " + (int)var1.damage);
                } else if (var1.damage > 0.0) {
                    var6.add("§6⚔ " + (int)var1.damage + (var1.towerDamage > 0.0 ? " §7(타워 " + (int)var1.towerDamage + ")" : ""));
                }

                if (!var2) {
                    var6.add(var3 ? "§c엘릭서 부족" : "§e우클릭: 바라보는 칸에 사용");
                }

                var5.setLore(var6);
                if (Glyphs.pack) {
                    try {
                        var5.setItemModel(new NamespacedKey("clashmc", "card_" + var1.id + (var3 ? "_off" : "")));
                    } catch (Throwable var8) {
                    }
                }

                var5.getPersistentDataContainer().set(this.cardKey, PersistentDataType.STRING, var1.id);
                if (var2) {
                    var5.getPersistentDataContainer().set(this.previewKey, PersistentDataType.STRING, "1");
                }

                var4.setItemMeta(var5);
            }

            return var4;
        }
    }

    void sendUiPack(Player var1) {
        {
            String var2 = this.packUrl;
            String var3 = this.packSha1;
            if (var2 == null || var2.isEmpty()) {
                PackHost var4 = this.plugin.packHost;
                var2 = var4 == null ? null : var4.urlFor(var1);
                var3 = var4 == null ? "" : var4.sha1;
            }

            if (var3 != null && !var3.isEmpty() && var3.equals(this.packSentSha.get(var1.getUniqueId()))) {
                return;
            }

            // 접속할 때 서버 기본 팩(server.properties)으로 이미 같은 버전을 받았으면 다시 안 보냄
            if (var3 != null && !var3.isEmpty() && !this.packSentSha.containsKey(var1.getUniqueId())) {
                String serverSha = Bukkit.getResourcePackHash();
                if (serverSha != null && serverSha.equalsIgnoreCase(var3)) {
                    this.packSent.add(var1.getUniqueId());
                    this.packSentSha.put(var1.getUniqueId(), var3);
                    return;
                }
            }

            if (var2 != null && !var2.isEmpty()) {
                String var9 = var2;
                String var5 = var3;

                try {
                    byte[] var6 = null;
                    if (var5 != null && var5.length() == 40) {
                        var6 = new byte[20];

                        for (int var7 = 0; var7 < 20; var7++) {
                            var6[var7] = (byte)Integer.parseInt(var5.substring(var7 * 2, var7 * 2 + 2), 16);
                        }
                    }

                    // 고정 id → 새 팩이 예전 팩을 덮어씀 (쌓이지 않음)
                    UUID var10 = PackHost.PACK_ID;
                    var1.addResourcePack(var10, var9, var6, "§6클래시 마크 리소스팩 §7(UI + 모델)", false);
                    this.packSent.add(var1.getUniqueId());
                    this.packSentSha.put(var1.getUniqueId(), var5 == null ? "" : var5);
                } catch (Throwable var8) {
                    this.plugin.getLogger().warning("UI 리소스팩 전송 실패: " + var8);
                }
            }
        }
    }

    void resendUiPack() {

        for (Player var2 : Bukkit.getOnlinePlayers()) {
            this.sendUiPack(var2);
        }
    }

    void onQuit(Player var1) {
        this.packSent.remove(var1.getUniqueId());
        this.packSentSha.remove(var1.getUniqueId());
        this.rankedQueue.remove(var1.getUniqueId());
        GameManager var2 = this.matchOf(var1);
        if (var2 != null) {
            var2.handleQuit(var1);
        }

        Room var3 = this.roomOf.get(var1.getUniqueId());
        if (var3 != null && var3.match == null) {
            this.leaveRoom(var1);
        }

        this.lobby.onQuit(var1);
        Profile var4 = this.profiles.get(var1.getUniqueId());
        this.profiles.save(var4);
    }
}
