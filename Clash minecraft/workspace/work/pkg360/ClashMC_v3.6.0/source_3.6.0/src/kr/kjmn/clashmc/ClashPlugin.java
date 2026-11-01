package kr.kjmn.clashmc;

import java.io.File;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import org.bukkit.Bukkit;
import org.bukkit.Location;
import org.bukkit.command.Command;
import org.bukkit.command.CommandExecutor;
import org.bukkit.command.CommandSender;
import org.bukkit.command.PluginCommand;
import org.bukkit.command.TabCompleter;
import org.bukkit.entity.Player;
import org.bukkit.plugin.java.JavaPlugin;

public final class ClashPlugin extends JavaPlugin implements CommandExecutor, TabCompleter {
    PackHost packHost;
    private Clash core;
    private static final List<String> SUBS = Arrays.asList("menu", "ranked", "ai", "room", "deck", "skin", "profile", "top", "ff", "leave", "status");
    private static final List<String> ADMIN = Arrays.asList("arena", "setlobby", "lobby", "start", "stop", "reload", "test", "trophy", "giveskin", "matches");

    public void onEnable() {
        this.saveDefaultConfig();
        File var1 = new File(this.getDataFolder(), "skins.yml");

        try {
            if (var1.exists() && new String(Files.readAllBytes(var1.toPath()), StandardCharsets.UTF_8).contains("(자동 생성)")) {
                Files.move(var1.toPath(), new File(this.getDataFolder(), "skins_old.yml").toPath(), StandardCopyOption.REPLACE_EXISTING);
                this.getLogger().info("예전 자동 생성 skins.yml → skins_old.yml 로 백업, 빈 스킨 목록으로 교체");
            }
        } catch (Exception var9) {
            this.getLogger().warning("skins.yml 교체 실패: " + var9);
        }

        try (InputStream var2 = this.getResource("clash_arena.schem")) {
            File var3 = new File(this.getDataFolder(), "clash_arena.schem");
            if (var2 != null && var3.exists()) {
                byte[] var4 = var2.readAllBytes();
                byte[] var5 = Files.readAllBytes(var3.toPath());
                if (!Arrays.equals(var4, var5)) {
                    Files.copy(var3.toPath(), new File(this.getDataFolder(), "clash_arena_old.schem").toPath(), StandardCopyOption.REPLACE_EXISTING);
                    Files.write(var3.toPath(), var4);
                    this.arenaSchemChanged = true;
                    this.getLogger().info("새 경기장 schem 으로 교체 (예전 것 → clash_arena_old.schem). 서버가 켜지면 경기장을 자동으로 다시 붙여넣음 (끄려면 arena-auto-repaste: false)");
                }
            }
        } catch (Exception var11) {
            this.getLogger().warning("경기장 schem 교체 실패: " + var11);
        }

        // 로비 schem 도 jar 에 든 것이 바뀌면 자동 교체 (붙여넣기는 /clash lobby repaste)
        try (InputStream lin = this.getResource("clash_lobby.schem")) {
            File lf = new File(this.getDataFolder(), "clash_lobby.schem");
            if (lin != null && lf.exists()) {
                byte[] nb = lin.readAllBytes();
                if (!Arrays.equals(nb, Files.readAllBytes(lf.toPath()))) {
                    Files.copy(lf.toPath(), new File(this.getDataFolder(), "clash_lobby_old.schem").toPath(), StandardCopyOption.REPLACE_EXISTING);
                    Files.write(lf.toPath(), nb);
                    this.getLogger().info("새 로비 schem 으로 교체 (예전 것 → clash_lobby_old.schem). 붙여넣기: /clash lobby repaste");
                }
            }
        } catch (Exception lex) {
            this.getLogger().warning("로비 schem 교체 실패: " + lex);
        }

        for (String var16 : new String[]{"skins.yml", "clash_arena.schem", "clash_lobby.schem"}) {
            if (!new File(this.getDataFolder(), var16).exists()) {
                try {
                    this.saveResource(var16, false);
                } catch (IllegalArgumentException var7) {
                }
            }
        }

        this.core = new Clash(this);
        this.core.load();
        this.packHost = new PackHost(this);
        this.packHost.start();
        Bukkit.getScheduler().runTaskLater(this, () -> this.core.checkModels(0), 100L);
        this.getServer().getPluginManager().registerEvents(new GameListener(this.core), this);
        PluginCommand var13 = this.getCommand("clash");
        if (var13 != null) {
            var13.setExecutor(this);
            var13.setTabCompleter(this);
        }

        this.core.start();
        // 서버 켜진 뒤 자동 리로드 (/cm reload 와 같음): 모델 플러그인이 늦게 로드돼도 로비 장식·UI 팩·카드 모델이 제대로 붙게
        if (this.getConfig().getBoolean("auto-reload.enabled", true)) {
            List<?> delays = this.getConfig().getList("auto-reload.delays", Arrays.asList(5, 30));
            for (Object d : delays) {
                if (d instanceof Number n) {
                    Bukkit.getScheduler().runTaskLater(this, this::autoReload, Math.max(1L, Math.round(n.doubleValue() * 20.0)));
                }
            }
        }

        this.getLogger().info("클래시 마크 활성화");
    }

    /** 이번 시작 때 jar 의 새 경기장 schem 으로 교체됐는지 */
    private boolean arenaSchemChanged;

    /** 경기장 schem 이 바뀌었으면 비어 있는 경기장을 전부 다시 붙여넣음 (서버 켜질 때 한 번) */
    private void autoRepasteArenas() {
        if (!this.arenaSchemChanged || this.core == null || !this.getConfig().getBoolean("arena-auto-repaste", true)) {
            return;
        }

        this.arenaSchemChanged = false;
        File f = new File(this.getDataFolder(), "clash_arena.schem");
        int n = 0;
        for (ArenaPool.Slot slot : this.core.arenas.slots.values()) {
            if (!slot.free()) {
                continue;
            }

            String err = ArenaPool.paste(f, slot.arena.world, slot.arena.px, slot.arena.py, slot.arena.pz);
            if (err != null) {
                this.getLogger().warning("경기장 자동 다시 붙여넣기 실패 (" + slot.name + "): " + err);
                return;
            }

            n++;
        }

        this.getLogger().info("새 경기장 schem 으로 경기장 " + n + "개 자동으로 다시 붙여넣음");
    }

    private void autoReload() {
        if (this.core == null || !this.isEnabled()) {
            return;
        }

        if (this.core.matches.isEmpty()) {
            try {
                this.autoRepasteArenas();
            } catch (Throwable e) {
                this.getLogger().warning("경기장 자동 다시 붙여넣기 오류: " + e);
            }
        }

        if (!this.core.matches.isEmpty()) {
            this.getLogger().info("자동 리로드 건너뜀 (진행 중인 경기 " + this.core.matches.size() + "개)");
            return;
        }

        try {
            this.reloadConfig();
            this.core.load();
            this.core.lobby.spawnDecor();
            this.packHost.start();
            this.core.resendUiPack();
            this.getLogger().info("자동 리로드 완료 (카드 " + this.core.cards.size() + "장, 스킨 " + this.core.skins.all.size() + "개, 경기장 " + this.core.arenas.slots.size() + "개)");
        } catch (Exception e) {
            this.getLogger().warning("자동 리로드 실패: " + e);
        }
    }

    public void onDisable() {
        if (this.core != null) {
            this.core.shutdown();
        }

        if (this.packHost != null) {
            this.packHost.stop();
        }
    }

    public boolean onCommand(CommandSender var1, Command var2, String var3, String[] var4) {
        Player var5 = var1 instanceof Player var6 ? var6 : null;
        boolean var17 = var1.hasPermission("clash.admin");
        String var7 = var4.length == 0 ? (var5 != null ? "menu" : "help") : var4[0].toLowerCase();
        switch (var7) {
            case "menu":
            case "play":
            case "메뉴":
                if (var5 != null) {
                    this.core.lobby.action(var5, "menu");
                }

                return true;
            case "ranked":
            case "join":
            case "랭크":
                if (var5 == null) {
                    return true;
                }

                if (this.core.queued(var5.getUniqueId())) {
                    this.core.leaveRanked(var5);
                } else {
                    this.core.joinRanked(var5);
                }

                return true;
            case "ai":
                if (var5 == null) {
                    return true;
                }

                if (var4.length >= 2) {
                    Bot.Level var20;
                    try {
                        var20 = Bot.Level.valueOf(var4[1].toUpperCase());
                    } catch (IllegalArgumentException var15) {
                        var20 = Bot.Level.NORMAL;
                    }

                    this.core.startAi(var5, var20);
                } else {
                    this.core.lobby.action(var5, "ai");
                }

                return true;
            case "room":
            case "방":
                if (var5 != null) {
                    this.room(var5, var4);
                }

                return true;
            case "deck":
            case "덱":
                if (var5 == null) {
                    return true;
                }

                GameManager var19 = this.core.matchOf(var5);
                if (var19 != null) {
                    var19.openDeck(var5);
                } else {
                    this.core.lobby.action(var5, "deck");
                }

                return true;
            case "skin":
            case "스킨":
                if (var5 != null) {
                    this.core.lobby.action(var5, "skins");
                }

                return true;
            case "profile":
            case "프로필":
                if (var5 != null) {
                    this.core.lobby.action(var5, "profile");
                }

                return true;
            case "top":
            case "랭킹":
                if (var5 != null) {
                    this.core.lobby.action(var5, "leaderboard");
                }

                return true;
            case "bgm":
            case "music":
            case "음악":
                if (var5 != null) {
                    this.core.bgm.toggle(var5);
                }

                return true;
            case "ff":
            case "surrender":
            case "항복":
                if (var5 == null) {
                    return true;
                }

                GameManager var22 = this.core.matchOf(var5);
                if (var22 == null) {
                    var5.sendMessage("§c경기 중이 아닙니다.");
                } else {
                    var22.surrender(var5);
                }

                return true;
            case "leave":
            case "나가기":
                if (var5 == null) {
                    return true;
                }

                if (this.core.queued(var5.getUniqueId())) {
                    this.core.leaveRanked(var5);
                } else if (this.core.roomOf.containsKey(var5.getUniqueId())) {
                    this.core.leaveRoom(var5);
                    this.core.lobby.giveHotbar(var5);
                } else {
                    var5.sendMessage("§7대기 중인 것이 없습니다.");
                }

                return true;
            case "status":
                var1.sendMessage(
                    "§6[클래시] §f진행 중 경기 "
                        + this.core.matches.size()
                        + " §7/ 경기장 "
                        + this.core.arenas.slots.size()
                        + " §7| 랭크 대기 "
                        + this.core.rankedQueue.size()
                        + "명 | 친선전 방 "
                        + this.core.rooms.size()
                        + "개"
                );

                for (GameManager var28 : this.core.matches) {
                    var1.sendMessage(" §8- " + var28.tag() + " §7" + var28.phase + " · " + var28.teamOf.size() + "명");
                }

                return true;
            default:
                if (!var17) {
                    this.help(var1, false);
                    return true;
                } else {
                    switch (var7) {
                        case "arena":
                            this.arena(var1, var5, var4);
                            return true;
                        case "setarena":
                            if (var5 == null) {
                                return true;
                            }

                            this.core.arenas.add(var4.length >= 2 ? var4[1] : "main", var5.getLocation());
                            var1.sendMessage("§a경기장 저장 (" + (var4.length >= 2 ? var4[1] : "main") + ")");
                            return true;
                        case "setlobby":
                            if (var5 == null) {
                                return true;
                            }

                            Location var10 = var5.getLocation();
                            this.getConfig().set("lobby.world", var10.getWorld().getName());
                            this.getConfig().set("lobby.x", var10.getBlockX());
                            this.getConfig().set("lobby.y", var10.getBlockY());
                            this.getConfig().set("lobby.z", var10.getBlockZ());
                            this.getConfig().set("lobby.yaw", 180.0);
                            this.saveConfig();
                            this.core.lobby.load();
                            this.core.lobby.spawnDecor();
                            this.core.checkModels(6);
                            var1.sendMessage("§a로비 기준점 저장 §7(clash_lobby.schem 붙여넣은 자리) - 포털 / 랭킹판 / 전시대 생성");
                            return true;
                        case "lobby":
                            if (var5 == null) {
                                return true;
                            } else {
                                if (var4.length >= 2 && var4[1].equalsIgnoreCase("paste")) {
                                    Location var21 = var5.getLocation();
                                    String var24 = ArenaPool.paste(
                                        new File(this.getDataFolder(), "clash_lobby.schem"),
                                        var21.getWorld(),
                                        var21.getBlockX(),
                                        var21.getBlockY(),
                                        var21.getBlockZ()
                                    );
                                    if (var24 != null) {
                                        var1.sendMessage("§c" + var24);
                                        return true;
                                    }

                                    this.onCommand(var1, var2, var3, new String[]{"setlobby"});
                                } else if (var4.length >= 2 && var4[1].equalsIgnoreCase("repaste")) {
                                    Location lo = this.core.lobby.origin;
                                    if (lo == null) {
                                        var1.sendMessage("§c로비가 지정돼 있지 않습니다. 로비 자리에서 /clash lobby paste");
                                        return true;
                                    }

                                    String err = ArenaPool.paste(new File(this.getDataFolder(), "clash_lobby.schem"), lo.getWorld(), lo.getBlockX(), lo.getBlockY(), lo.getBlockZ());
                                    if (err != null) {
                                        var1.sendMessage("§c" + err);
                                        return true;
                                    }

                                    this.core.lobby.spawnDecor();
                                    var1.sendMessage("§a로비를 원래 자리에 새로 붙여넣음 §7(" + lo.getBlockX() + ", " + lo.getBlockY() + ", " + lo.getBlockZ() + ")");
                                } else if (var4.length >= 2 && var4[1].equalsIgnoreCase("refresh")) {
                                    this.core.lobby.spawnDecor();
                                    var1.sendMessage("§a로비 장식 다시 생성");
                                } else {
                                    var1.sendMessage("§f/clash lobby paste §7- 서 있는 자리에 로비 schem 붙여넣고 로비로 지정 §8| §f/clash lobby repaste §7- 지금 로비 자리에 새로 붙여넣기 §8| §f/clash lobby refresh");
                                }

                                return true;
                            }
                        case "start":
                            if (var5 == null) {
                                return true;
                            }

                            GameManager var11 = this.core.matchOf(var5);
                            if (var11 == null) {
                                var1.sendMessage("§c참가 중인 경기가 없습니다.");
                            } else {
                                var11.forceStart();
                            }

                            return true;
                        case "stop":
                            if (var4.length >= 2 && var4[1].equalsIgnoreCase("all")) {
                                for (GameManager var27 : new ArrayList<>(this.core.matches)) {
                                    var27.stopMatch("관리자가 경기를 중단했습니다.");
                                }

                                var1.sendMessage("§a모든 경기 중단");
                                return true;
                            } else {
                                GameManager var12 = null;
                                if (var4.length >= 2) {
                                    for (GameManager var30 : this.core.matches) {
                                        if (("#" + var30.id).equals(var4[1]) || String.valueOf(var30.id).equals(var4[1]) || var30.slot.name.equals(var4[1])) {
                                            var12 = var30;
                                        }
                                    }
                                } else if (var5 != null) {
                                    var12 = this.core.matchOf(var5);
                                }

                                if (var12 == null) {
                                    var1.sendMessage("§c경기를 찾을 수 없습니다. §7(/clash stop <번호|경기장|all>)");
                                    return true;
                                }

                                var12.stopMatch("관리자가 경기를 중단했습니다.");
                                return true;
                            }
                        case "reload":
                            this.reloadConfig();
                            this.core.load();
                            this.core.lobby.spawnDecor();
                            this.packHost.start();
                            this.core.resendUiPack();
                            var1.sendMessage(
                                "§a설정 리로드 (카드 "
                                    + this.core.cards.size()
                                    + "장, 스킨 "
                                    + this.core.skins.all.size()
                                    + "개, 경기장 "
                                    + this.core.arenas.slots.size()
                                    + "개)"
                            );
                            return true;
                        case "test":
                        case "테스트":
                            if (var5 != null) {
                                this.core.testCommand(var5, var4);
                            }

                            return true;
                        case "trophy":
                            if (var4.length < 3) {
                                var1.sendMessage("§f/clash trophy <플레이어> <값|+값|-값>");
                                return true;
                            } else {
                                Profile var13 = this.profileByName(var4[1]);
                                if (var13 == null) {
                                    var1.sendMessage("§c플레이어 없음");
                                    return true;
                                }

                                try {
                                    int var29 = Integer.parseInt(var4[2].replace("+", ""));
                                    var13.trophies = Math.max(0, !var4[2].startsWith("+") && !var4[2].startsWith("-") ? var29 : var13.trophies + var29);
                                    var13.best = Math.max(var13.best, var13.trophies);
                                    var13.dirty = true;
                                    this.core.profiles.rebuildTop();
                                    this.core.lobby.refreshLeaderboard();
                                    var1.sendMessage("§a" + var13.name + " 트로피 = " + var13.trophies);
                                } catch (NumberFormatException var16) {
                                    var1.sendMessage("§c숫자를 입력하세요");
                                }

                                return true;
                            }
                        case "giveskin":
                            if (var4.length < 3) {
                                var1.sendMessage("§f/clash giveskin <플레이어> <스킨id|all>");
                                return true;
                            } else {
                                Profile var14 = this.profileByName(var4[1]);
                                if (var14 == null) {
                                    var1.sendMessage("§c플레이어 없음");
                                    return true;
                                } else {
                                    if (var4[2].equalsIgnoreCase("all")) {
                                        var14.skins.addAll(this.core.skins.all.keySet());
                                    } else {
                                        if (!this.core.skins.all.containsKey(var4[2])) {
                                            var1.sendMessage("§c없는 스킨: " + var4[2]);
                                            return true;
                                        }

                                        var14.skins.add(var4[2]);
                                    }

                                    var14.dirty = true;
                                    var1.sendMessage("§a" + var14.name + " 에게 스킨 지급: " + var4[2]);
                                    return true;
                                }
                            }
                        case "matches":
                            return this.onCommand(var1, var2, var3, new String[]{"status"});
                        default:
                            this.help(var1, true);
                            return true;
                    }
                }
        }
    }

    private Profile profileByName(String var1) {
        Player var2 = Bukkit.getPlayerExact(var1);
        if (var2 != null) {
            return this.core.profiles.get(var2);
        } else {
            for (Profile var4 : this.core.profiles.top(100000)) {
                if (var4.name.equalsIgnoreCase(var1)) {
                    return var4;
                }
            }

            return null;
        }
    }

    private void room(Player var1, String[] var2) {
        String var3 = var2.length < 2 ? "menu" : var2[1].toLowerCase();
        switch (var3) {
            case "create":
                this.core.createRoom(var1);
                new Menus.RoomMenu(this.core, var1).open();
                break;
            case "invite":
                if (var2.length >= 3) {
                    this.core.invite(var1, var2[2]);
                } else {
                    var1.sendMessage("§f/clash room invite <닉네임>");
                }
                break;
            case "join":
                if (var2.length >= 3) {
                    this.core.joinRoom(var1, var2[2]);
                } else {
                    new Menus.RoomListMenu(this.core, var1).open();
                }
                break;
            case "leave":
                this.core.leaveRoom(var1);
                this.core.lobby.giveHotbar(var1);
                break;
            case "kick":
                if (var2.length >= 3) {
                    this.core.kick(var1, var2[2]);
                }
                break;
            case "start":
                this.core.startFriendly(var1);
                break;
            case "ai":
                new Menus.AiMenu(this.core, var1).open();
                break;
            default:
                new Menus.RoomMenu(this.core, var1).open();
        }
    }

    private void arena(CommandSender var1, Player var2, String[] var3) {
        String var4 = var3.length < 2 ? "list" : var3[1].toLowerCase();
        switch (var4) {
            case "add":
                if (var2 != null && var3.length >= 3) {
                    this.core.arenas.add(var3[2], var2.getLocation());
                    var1.sendMessage("§a경기장 추가: " + var3[2] + " §7(총 " + this.core.arenas.slots.size() + "개)");
                    return;
                }

                var1.sendMessage("§f/clash arena add <이름> §7- 서 있는 자리를 경기장 기준점으로 (schem 붙여넣은 자리)");
                return;
            case "paste":
                if (var2 != null && var3.length >= 3) {
                    Location var17 = var2.getLocation();
                    String var20 = ArenaPool.paste(
                        new File(this.getDataFolder(), "clash_arena.schem"), var17.getWorld(), var17.getBlockX(), var17.getBlockY(), var17.getBlockZ()
                    );
                    if (var20 != null) {
                        var1.sendMessage("§c" + var20);
                        return;
                    }

                    this.core.arenas.add(var3[2], var17);
                    var1.sendMessage("§a경기장 붙여넣기 + 등록: " + var3[2]);
                    return;
                }

                var1.sendMessage("§f/clash arena paste <이름> §7- 서 있는 자리에 경기장 schem 붙여넣고 등록 (FAWE)");
                return;
            case "repaste":
                File var16 = new File(this.getDataFolder(), "clash_arena.schem");
                int var19 = 0;
                int var22 = 0;

                for (ArenaPool.Slot var24 : this.core.arenas.slots.values()) {
                    if (!var24.free()) {
                        var22++;
                    } else {
                        String var25 = ArenaPool.paste(var16, var24.arena.world, var24.arena.px, var24.arena.py, var24.arena.pz);
                        if (var25 != null) {
                            var1.sendMessage("§c" + var24.name + ": " + var25);
                            break;
                        }

                        var19++;
                    }
                }

                var1.sendMessage("§a경기장 " + var19 + "개 다시 붙여넣음" + (var22 > 0 ? " §7(경기 중 " + var22 + "개 건너뜀)" : ""));
                return;
            case "grid":
                if (var2 == null) {
                    return;
                }

                int var15 = var3.length >= 3 ? Integer.parseInt(var3[2]) : 4;
                int var18 = var3.length >= 4 ? Integer.parseInt(var3[3]) : 90;
                Location var21 = var2.getLocation();
                int var10 = 0;

                for (int var11 = 0; var11 < var15; var11++) {
                    Location var12 = var21.clone().add(var11 * var18, 0.0, 0.0);
                    String var13 = ArenaPool.paste(
                        new File(this.getDataFolder(), "clash_arena.schem"), var12.getWorld(), var12.getBlockX(), var12.getBlockY(), var12.getBlockZ()
                    );
                    if (var13 != null) {
                        var1.sendMessage("§c" + var13);
                        break;
                    }

                    String var14 = "arena" + (this.core.arenas.slots.size() + 1);

                    while (this.core.arenas.slots.containsKey(var14)) {
                        var14 = var14 + "_";
                    }

                    this.core.arenas.add(var14, var12);
                    var10++;
                }

                var1.sendMessage("§a경기장 " + var10 + "개 생성 (" + var18 + "블록 간격, +X 방향)");
                return;
            case "remove":
                if (var3.length < 3) {
                    return;
                }

                var1.sendMessage(this.core.arenas.remove(var3[2]) ? "§a삭제: " + var3[2] : "§c없거나 경기 중인 경기장");
                return;
            case "tp":
                if (var2 != null && var3.length >= 3) {
                    ArenaPool.Slot var7 = this.core.arenas.slots.get(var3[2]);
                    if (var7 != null) {
                        var2.teleport(var7.arena.overview());
                    }

                    return;
                }

                return;
            default:
                var1.sendMessage("§6경기장 " + this.core.arenas.slots.size() + "개 §7(빈 곳 " + this.core.arenas.freeCount() + ")");

                for (ArenaPool.Slot var9 : this.core.arenas.slots.values()) {
                    var1.sendMessage(
                        " §8- §f"
                            + var9.name
                            + " §7"
                            + var9.arena.world.getName()
                            + " "
                            + var9.arena.px
                            + ","
                            + var9.arena.py
                            + ","
                            + var9.arena.pz
                            + (var9.free() ? " §a비어 있음" : " §c" + var9.match.tag())
                    );
                }

                var1.sendMessage("§7/clash arena add|paste|grid <개수> [간격]|remove|tp");
        }
    }

    private void help(CommandSender var1, boolean var2) {
        var1.sendMessage("§6§l[클래시 마크]");
        var1.sendMessage("§f/clash §7- 메인 메뉴 (로비 핫바 / F키로도 열림)");
        var1.sendMessage("§f/clash ranked §7- 랭크전 매칭 / 취소 §8| §f/clash ai [easy|normal|hard]");
        var1.sendMessage("§f/clash room [create|invite <닉>|join <코드>|leave|kick <닉>|start]");
        var1.sendMessage("§f/clash deck | skin | profile | top | ff(항복) | leave | status");
        if (var2) {
            var1.sendMessage("§c/clash arena [add|paste|grid|remove|tp|list] §8| §c/clash lobby paste|refresh §8| §c/clash setlobby");
            var1.sendMessage("§c/clash start | stop [번호|all] | reload | test ... | trophy <닉> <값> | giveskin <닉> <id|all>");
        }
    }

    public List<String> onTabComplete(CommandSender var1, Command var2, String var3, String[] var4) {
        ArrayList<String> var5 = new ArrayList<>();
        boolean var6 = var1.hasPermission("clash.admin");
        if (var4.length == 1) {
            var5.addAll(SUBS);
            if (var6) {
                var5.addAll(ADMIN);
            }
        } else {
            String var7 = var4[0].toLowerCase();
            if (var7.equals("room") && var4.length == 2) {
                var5.addAll(Arrays.asList("create", "invite", "join", "leave", "kick", "start", "ai"));
            } else if (var7.equals("room") && var4.length == 3 && (var4[1].equalsIgnoreCase("invite") || var4[1].equalsIgnoreCase("kick"))) {
                for (Player var15 : Bukkit.getOnlinePlayers()) {
                    var5.add(var15.getName());
                }
            } else if (var7.equals("room") && var4.length == 3 && var4[1].equalsIgnoreCase("join")) {
                var5.addAll(this.core.rooms.keySet());
            } else if (var7.equals("ai") && var4.length == 2) {
                var5.addAll(Arrays.asList("easy", "normal", "hard"));
            } else if (var6 && var7.equals("arena") && var4.length == 2) {
                var5.addAll(Arrays.asList("add", "paste", "repaste", "grid", "remove", "tp", "list"));
            } else if (!var6 || !var7.equals("arena") || var4.length != 3 || !var4[1].equalsIgnoreCase("remove") && !var4[1].equalsIgnoreCase("tp")) {
                if (var6 && var7.equals("lobby") && var4.length == 2) {
                    var5.addAll(Arrays.asList("paste", "refresh"));
                } else if (var6 && var7.equals("stop") && var4.length == 2) {
                    var5.add("all");

                    for (GameManager var14 : this.core.matches) {
                        var5.add(String.valueOf(var14.id));
                    }
                } else if (var6 && (var7.equals("trophy") || var7.equals("giveskin")) && var4.length == 2) {
                    for (Player var9 : Bukkit.getOnlinePlayers()) {
                        var5.add(var9.getName());
                    }
                } else if (var6 && var7.equals("giveskin") && var4.length == 3) {
                    var5.add("all");
                    var5.addAll(this.core.skins.all.keySet());
                } else if (var6 && var7.equals("test")) {
                    if (var4.length == 2) {
                        var5.addAll(TestMode.SUBS);
                    } else {
                        String var8 = var4[1].toLowerCase();
                        if (var4.length != 3 || !var8.equals("unit") && !var8.equals("spawn")) {
                            if (var8.equals("spawn")) {
                                var5.addAll(Arrays.asList("blue", "red", "me", "3"));
                            } else if (var4.length != 3 || !var8.equals("start") && !var8.equals("clear") && !var8.equals("break")) {
                                if (var4.length == 4 && var8.equals("break")) {
                                    var5.addAll(Arrays.asList("left", "right", "king"));
                                } else if (var4.length == 3 && var8.equals("bot")) {
                                    var5.addAll(Arrays.asList("on", "off", "now", "elixir", "easy", "normal", "hard", "speed"));
                                }
                            } else {
                                var5.addAll(Arrays.asList("blue", "red"));
                            }
                        } else {
                            var5.addAll(this.core.cards.keySet());
                        }
                    }
                }
            } else {
                var5.addAll(this.core.arenas.names());
            }
        }

        String var10 = var4[var4.length - 1].toLowerCase();
        var5.removeIf(var1x -> !var1x.toLowerCase().startsWith(var10));
        return var5;
    }

    static UUID id(Player var0) {
        return var0.getUniqueId();
    }
}
