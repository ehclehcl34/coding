package kr.kjmn.clashmc;

import java.io.File;
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.Particle;
import org.bukkit.command.CommandSender;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;
import org.bukkit.entity.Player;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.player.AsyncPlayerChatEvent;
import org.bukkit.event.player.PlayerCommandPreprocessEvent;

/**
 * 스트리머 모드.
 * - 관리자가 지정한 스트리머만 켤 수 있음 (/스트리머)
 * - 켜면: LIVE 표시, F3 좌표 숨김, 방 코드·대기열 인원 숨김, 매칭 시작 랜덤 지연,
 *   채팅 필터(욕설·링크), 귓속말/방 초대 차단, (선택) 전체채팅 끄기, 승패 연출 강화
 * - 스트리머가 있는 경기는 관전 불가. 전체 관전은 관리자가 켜고 끔.
 */
final class Streamers implements Listener {
    static final class Opt {
        String name = "?";
        boolean on;
        boolean whisperBlock = true;
        boolean chatOff;
        boolean filter = true;
    }

    private final Clash core;
    /** 관리자가 지정한 스트리머 */
    final Map<UUID, Opt> streamers = new ConcurrentHashMap<>();
    /** 관전 중인 플레이어 → 보고 있는 경기 */
    final Map<UUID, GameManager> spectating = new ConcurrentHashMap<>();
    /** 랭크전 매칭에 실제로 들어가는 tick (스트리머 랜덤 지연) */
    final Map<UUID, Long> queueHold = new ConcurrentHashMap<>();
    boolean spectateEnabled = true;
    int queueDelayMax = 10;
    private final List<String> badWords = new ArrayList<>();
    private static final Pattern LINK = Pattern.compile(
        "(?i)(https?://\\S+|www\\.\\S+|\\b\\d{1,3}(\\.\\d{1,3}){3}(:\\d+)?\\b|\\b[\\w-]+\\.(com|net|org|kr|gg|io|me|xyz|co|tv|ly|be|link|site|shop)\\b\\S*)");
    private static final Set<String> WHISPER = new HashSet<>(Arrays.asList(
        "msg", "tell", "w", "m", "t", "whisper", "pm", "dm", "emsg", "etell", "ew", "ewhisper", "em", "et", "epm", "귓", "귓말", "귓속말"));
    private static final List<String> DEFAULT_BAD = Arrays.asList(
        "시발", "씨발", "씨바", "시바", "ㅅㅂ", "ㅆㅂ", "ㅅ1ㅂ", "병신", "븅신", "ㅂㅅ", "좆", "ㅈ같", "개새끼", "개새", "새끼", "ㅅㄲ", "지랄", "ㅈㄹ",
        "니애미", "느금", "엠창", "애미", "애비", "미친놈", "미친년", "ㅁㅊ", "닥쳐", "꺼져", "fuck", "shit", "bitch", "sibal", "tlqkf", "qudtls");
    /** 팀 채팅인지 (GameListener → 같은 스레드의 MONITOR 핸들러로 전달) */
    static final ThreadLocal<Boolean> TEAM_CHAT = ThreadLocal.withInitial(() -> false);

    /** Room 처럼 core 를 모르는 곳에서 쓰는 용도 */
    static Streamers instance;

    Streamers(Clash core) {
        this.core = core;
        instance = this;
    }

    private File file() {
        return new File(this.core.plugin.getDataFolder(), "streamers.yml");
    }

    void load() {
        this.streamers.clear();
        this.badWords.clear();
        File f = this.file();
        YamlConfiguration y = f.exists() ? YamlConfiguration.loadConfiguration(f) : new YamlConfiguration();
        this.spectateEnabled = !f.exists() || y.getBoolean("spectate-enabled", true);
        this.queueDelayMax = Math.max(0, y.getInt("queue-random-delay", 10));
        List<String> words = f.exists() ? y.getStringList("filter-words") : null;
        this.badWords.addAll(words == null || words.isEmpty() ? DEFAULT_BAD : words);
        ConfigurationSection s = y.getConfigurationSection("streamers");
        if (s != null) {
            for (String k : s.getKeys(false)) {
                try {
                    UUID id = UUID.fromString(k);
                    Opt o = new Opt();
                    o.name = s.getString(k + ".name", "?");
                    o.on = s.getBoolean(k + ".on", false);
                    o.whisperBlock = s.getBoolean(k + ".whisper-block", true);
                    o.chatOff = s.getBoolean(k + ".chat-off", false);
                    o.filter = s.getBoolean(k + ".filter", true);
                    this.streamers.put(id, o);
                } catch (Exception ignored) {
                }
            }
        }

        if (!f.exists()) {
            this.save();
        }
    }

    void save() {
        try {
            YamlConfiguration y = new YamlConfiguration();
            y.set("spectate-enabled", this.spectateEnabled);
            y.set("queue-random-delay", this.queueDelayMax);
            y.set("filter-words", new ArrayList<>(this.badWords));
            for (Map.Entry<UUID, Opt> e : this.streamers.entrySet()) {
                String k = "streamers." + e.getKey();
                Opt o = e.getValue();
                y.set(k + ".name", o.name);
                y.set(k + ".on", o.on);
                y.set(k + ".whisper-block", o.whisperBlock);
                y.set(k + ".chat-off", o.chatOff);
                y.set(k + ".filter", o.filter);
            }

            y.save(this.file());
        } catch (Exception e) {
            this.core.plugin.getLogger().warning("streamers.yml 저장 실패: " + e);
        }
    }

    // ------------------------------------------------------------ 상태

    boolean live(UUID id) {
        Opt o = id == null ? null : this.streamers.get(id);
        return o != null && o.on;
    }

    boolean live(Player p) {
        return p != null && this.live(p.getUniqueId());
    }

    /** 스트리머(모드 켬)가 들어 있는 경기인지 */
    boolean liveMatch(GameManager gm) {
        for (UUID id : gm.teamOf.keySet()) {
            if (this.live(id)) {
                return true;
            }
        }

        return false;
    }

    boolean blocksInvite(Player p) {
        Opt o = this.streamers.get(p.getUniqueId());
        return o != null && o.on && o.whisperBlock;
    }

    boolean spectating(Player p) {
        return this.spectating.containsKey(p.getUniqueId());
    }

    // ------------------------------------------------------------ 랭크전 매칭 지연

    void onQueueJoin(Player p) {
        if (this.live(p) && this.queueDelayMax > 0) {
            this.queueHold.put(p.getUniqueId(), this.core.tick + this.core.rng.nextInt(this.queueDelayMax * 20 + 1));
        }
    }

    boolean ready(UUID id) {
        Long t = this.queueHold.get(id);
        if (t == null) {
            return true;
        } else if (t <= this.core.tick) {
            this.queueHold.remove(id);
            return true;
        } else {
            return false;
        }
    }

    // ------------------------------------------------------------ 명령어

    private static String onOff(boolean b) {
        return b ? "§a켜짐" : "§7꺼짐";
    }

    /** /스트리머 */
    void command(CommandSender s, String[] a) {
        boolean admin = s.hasPermission("clash.admin");
        Player p = s instanceof Player pp ? pp : null;
        String sub = a.length == 0 ? "" : a[0].toLowerCase();
        if (admin) {
            switch (sub) {
                case "지정":
                case "add": {
                    if (a.length < 2) {
                        s.sendMessage("§f/스트리머 지정 <닉네임>");
                        return;
                    }

                    UUID id = null;
                    String name = a[1];
                    Player t = Bukkit.getPlayerExact(a[1]);
                    if (t != null) {
                        id = t.getUniqueId();
                        name = t.getName();
                    } else {
                        for (Profile pr : this.core.profiles.top(100000)) {
                            if (pr.name.equalsIgnoreCase(a[1])) {
                                id = pr.id;
                                name = pr.name;
                                break;
                            }
                        }
                    }

                    if (id == null) {
                        s.sendMessage("§c" + a[1] + " 님을 찾을 수 없습니다. (한 번이라도 접속한 플레이어만)");
                        return;
                    }

                    this.designate(s, id, name);
                    return;
                }
                case "해제":
                case "remove": {
                    if (a.length < 2) {
                        s.sendMessage("§f/스트리머 해제 <닉네임>");
                        return;
                    }

                    UUID found = null;
                    for (Map.Entry<UUID, Opt> e : this.streamers.entrySet()) {
                        if (e.getValue().name.equalsIgnoreCase(a[1])) {
                            found = e.getKey();
                        }
                    }

                    if (found == null) {
                        s.sendMessage("§c스트리머 목록에 없는 닉네임입니다.");
                        return;
                    }

                    this.undesignate(s, found);
                    return;
                }
                case "목록":
                case "list": {
                    s.sendMessage("§d[스트리머] §f지정된 스트리머 " + this.streamers.size() + "명 §8| §f전체 관전 " + onOff(this.spectateEnabled));
                    for (Opt o : this.streamers.values()) {
                        s.sendMessage(" §8- §f" + o.name + " " + (o.on ? "§c● 방송 모드" : "§7꺼짐"));
                    }

                    return;
                }
                default:
            }
        }

        if (p == null) {
            s.sendMessage("§f/스트리머 지정|해제 <닉> §8| §f/스트리머 목록 §8| §f/관전 켜기|끄기");
            return;
        }

        if (sub.isEmpty() || sub.equals("메뉴") || sub.equals("menu")) {
            StreamerMenus.openFor(this.core, p);
            return;
        }

        if (admin && (sub.equals("관리") || sub.equals("admin"))) {
            new StreamerMenus.AdminMenu(this.core, p).open();
            return;
        }

        Opt o = this.streamers.get(p.getUniqueId());
        if (o == null) {
            p.sendMessage("§c관리자가 지정한 스트리머만 쓸 수 있습니다.");
            if (admin) {
                p.sendMessage("§7관리자: §f/스트리머 지정|해제 <닉> §8| §f/스트리머 목록 §8| §f/관전 켜기|끄기");
            }

            return;
        }

        o.name = p.getName();
        switch (sub) {
            case "귓말":
            case "귓속말":
            case "whisper":
                o.whisperBlock = !o.whisperBlock;
                p.sendMessage("§d[스트리머] §f귓속말·방 초대 차단 " + onOff(o.whisperBlock));
                break;
            case "채팅":
            case "chat":
                o.chatOff = !o.chatOff;
                p.sendMessage("§d[스트리머] §f전체채팅 끄기 " + onOff(o.chatOff) + " §7(켜면 팀 채팅·게임 메시지만 보임)");
                break;
            case "필터":
            case "filter":
                o.filter = !o.filter;
                p.sendMessage("§d[스트리머] §f욕설·링크 가리기 " + onOff(o.filter));
                break;
            case "상태":
            case "설정":
            case "status":
                this.status(p, o);
                return;
            case "켜기":
            case "끄기":
            case "on":
            case "off":
                this.setOn(p, sub.equals("켜기") || sub.equals("on"));
                return;
            default:
                this.status(p, o);
                return;
        }

        this.save();
    }

    // ------------------------------------------------------------ GUI · 명령어 공용 동작

    void designate(CommandSender s, UUID id, String name) {
        Opt o = this.streamers.computeIfAbsent(id, k -> new Opt());
        o.name = name;
        this.save();
        s.sendMessage("§d[스트리머] §f" + name + " 님을 스트리머로 지정했습니다.");
        Player t = Bukkit.getPlayer(id);
        if (t != null) {
            t.sendMessage("§d[스트리머] §f스트리머로 지정됐습니다! §e/스트리머 §f로 설정 메뉴를 열 수 있어요.");
            t.playSound(t.getLocation(), "entity.player.levelup", 0.7F, 1.4F);
        }
    }

    void undesignate(CommandSender s, UUID id) {
        Opt o = this.streamers.get(id);
        if (o == null) {
            return;
        }

        Player t = Bukkit.getPlayer(id);
        if (t != null) {
            this.applyOff(t);
            t.sendMessage("§d[스트리머] §7스트리머 지정이 해제됐습니다.");
        }

        this.streamers.remove(id);
        this.save();
        s.sendMessage("§d[스트리머] §f" + o.name + " 님 스트리머 지정 해제");
    }

    void setOn(Player p, boolean want) {
        Opt o = this.streamers.get(p.getUniqueId());
        if (o == null) {
            return;
        }

        o.name = p.getName();
        o.on = want;
        if (want) {
            this.applyOn(p);
            p.sendMessage("§c● §d[스트리머] §f스트리머 모드 §a켜짐");
            p.playSound(p.getLocation(), "block.note_block.pling", 0.8F, 1.6F);
        } else {
            this.applyOff(p);
            p.sendMessage("§d[스트리머] §f스트리머 모드 §7꺼짐");
            p.playSound(p.getLocation(), "block.note_block.bass", 0.8F, 0.8F);
        }

        this.save();
    }

    /** whisper / chat / filter 켜고 끄기 */
    void setOption(Player p, String key) {
        Opt o = this.streamers.get(p.getUniqueId());
        if (o == null) {
            return;
        }

        switch (key) {
            case "whisper":
                o.whisperBlock = !o.whisperBlock;
                break;
            case "chat":
                o.chatOff = !o.chatOff;
                break;
            case "filter":
                o.filter = !o.filter;
                break;
            default:
                return;
        }

        this.save();
    }

    void setSpectateEnabled(CommandSender s, boolean on) {
        this.spectateEnabled = on;
        this.save();
        s.sendMessage("§b[관전] §f전체 관전 " + onOff(on));
        if (!on) {
            for (UUID id : new ArrayList<>(this.spectating.keySet())) {
                Player sp = Bukkit.getPlayer(id);
                if (sp != null) {
                    this.stopSpectate(sp, "§c관리자가 관전을 껐습니다.");
                }
            }
        }
    }

    private void status(Player p, Opt o) {
        p.sendMessage("§d§l[스트리머 모드] " + onOff(o.on));
        p.sendMessage(" §f귓속말·방 초대 차단 " + onOff(o.whisperBlock) + " §8(/스트리머 귓말)");
        p.sendMessage(" §f욕설·링크 가리기 " + onOff(o.filter) + " §8(/스트리머 필터)");
        p.sendMessage(" §f전체채팅 끄기 " + onOff(o.chatOff) + " §8(/스트리머 채팅)");
        p.sendMessage(" §7켜져 있으면: LIVE 표시 · F3 좌표 숨김 · 방 코드/대기열 숨김 · 매칭 랜덤 지연 · 관전 차단");
    }

    /** /관전 */
    void spectateCommand(CommandSender s, String[] a) {
        boolean admin = s.hasPermission("clash.admin");
        Player p = s instanceof Player pp ? pp : null;
        String sub = a.length == 0 ? "" : a[0];
        if (admin && (sub.equals("켜기") || sub.equalsIgnoreCase("on") || sub.equals("끄기") || sub.equalsIgnoreCase("off"))) {
            this.setSpectateEnabled(s, sub.equals("켜기") || sub.equalsIgnoreCase("on"));
            return;
        }

        if (p == null) {
            s.sendMessage("§f/관전 켜기|끄기");
            return;
        }

        if (sub.isEmpty() || sub.equals("목록") || sub.equalsIgnoreCase("list")) {
            new StreamerMenus.SpectateMenu(this.core, p).open();
            return;
        }

        if (sub.equals("나가기") || sub.equalsIgnoreCase("leave") || sub.equalsIgnoreCase("stop")) {
            if (this.spectating(p)) {
                this.stopSpectate(p, "§7관전을 그만뒀습니다.");
            } else {
                p.sendMessage("§7관전 중이 아닙니다.");
            }

            return;
        }

        this.spectate(p, sub);
    }

    void spectate(Player p, String targetName) {
        Player t = Bukkit.getPlayerExact(targetName);
        if (t == null) {
            t = Bukkit.getPlayer(targetName);
        }

        if (t == null) {
            p.sendMessage("§c" + targetName + " 님은 접속 중이 아닙니다.");
            return;
        }

        GameManager gm = this.core.matchOf(t);
        if (gm == null) {
            p.sendMessage("§c" + t.getName() + " 님은 경기 중이 아닙니다.");
            return;
        }

        this.spectateMatch(p, gm, gm.teamOf.get(t.getUniqueId()));
    }

    void spectateMatch(Player p, GameManager gm, TeamColor tc) {
        if (!this.spectateEnabled) {
            p.sendMessage("§c지금은 관전이 꺼져 있습니다.");
            return;
        }

        if (this.core.inGame(p)) {
            p.sendMessage("§c경기 중에는 관전할 수 없습니다.");
            return;
        }

        if (this.core.queued(p.getUniqueId())) {
            p.sendMessage("§c랭크전 매칭 중입니다. 먼저 매칭을 취소하세요.");
            return;
        }

        if (this.core.roomOf.containsKey(p.getUniqueId())) {
            p.sendMessage("§c친선전 방에서 나간 뒤 관전하세요.");
            return;
        }

        if (!this.core.matches.contains(gm) || gm.mode == GameManager.Mode.TEST || gm.phase == GameManager.Phase.ENDING || gm.phase == GameManager.Phase.DONE) {
            p.sendMessage("§c이미 끝난 경기입니다.");
            return;
        }

        if (this.liveMatch(gm)) {
            p.sendMessage("§c스트리머 경기는 관전할 수 없습니다.");
            return;
        }

        GameManager old = this.spectating.remove(p.getUniqueId());
        if (old != null && old.bar != null) {
            old.bar.removePlayer(p);
        }

        this.core.lobby.leaveLobby(p);
        p.setScoreboard(Bukkit.getScoreboardManager().getNewScoreboard());
        p.setGameMode(GameMode.SPECTATOR);
        p.teleport(gm.arena.spectate(tc == null ? TeamColor.BLUE : tc));
        if (gm.bar != null) {
            gm.bar.addPlayer(p);
        }

        this.spectating.put(p.getUniqueId(), gm);
        p.sendMessage("§b[관전] §f경기 #" + gm.id + " 관전 중 §8(" + gm.modeName() + "§8) §7- 나가기: §f/관전 나가기");
    }

    void stopSpectate(Player p, String msg) {
        GameManager gm = this.spectating.remove(p.getUniqueId());
        if (gm == null) {
            return;
        }

        if (gm.bar != null) {
            gm.bar.removePlayer(p);
        }

        if (p.isOnline()) {
            this.core.lobby.toLobby(p);
            if (msg != null) {
                p.sendMessage("§b[관전] " + msg);
            }
        }
    }

    // ------------------------------------------------------------ 켜기/끄기 효과

    void applyOn(Player p) {
        try {
            p.setPlayerListName("§c● §f" + p.getName() + " §c§lLIVE");
        } catch (Throwable ignored) {
        }

        reducedDebug(p, true);
        GameManager gm = this.core.matchOf(p);
        if (gm != null) {
            this.kickSpectators(gm);
        }
    }

    void applyOff(Player p) {
        Opt o = this.streamers.get(p.getUniqueId());
        if (o != null) {
            o.on = false;
        }

        try {
            p.setPlayerListName(null);
        } catch (Throwable ignored) {
        }

        reducedDebug(p, false);
        this.queueHold.remove(p.getUniqueId());
    }

    void kickSpectators(GameManager gm) {
        for (Map.Entry<UUID, GameManager> e : new ArrayList<>(this.spectating.entrySet())) {
            if (e.getValue() == gm) {
                Player sp = Bukkit.getPlayer(e.getKey());
                if (sp != null) {
                    this.stopSpectate(sp, "§c스트리머 경기라 관전이 끝났습니다.");
                } else {
                    this.spectating.remove(e.getKey());
                }
            }
        }
    }

    void onJoin(Player p) {
        Opt o = this.streamers.get(p.getUniqueId());
        if (o != null) {
            o.name = p.getName();
            if (o.on) {
                Bukkit.getScheduler().runTaskLater(this.core.plugin, () -> {
                    if (p.isOnline() && this.live(p)) {
                        this.applyOn(p);
                        p.sendMessage("§c● §d[스트리머] §f스트리머 모드가 켜져 있습니다. §7(/스트리머 로 끄기)");
                    }
                }, 20L);
            }
        }
    }

    void onQuit(Player p) {
        GameManager gm = this.spectating.remove(p.getUniqueId());
        if (gm != null && gm.bar != null) {
            gm.bar.removePlayer(p);
        }

        this.queueHold.remove(p.getUniqueId());
    }

    void tick() {
        if (this.core.tick % 20L == 0L && !this.spectating.isEmpty()) {
            for (Map.Entry<UUID, GameManager> e : new ArrayList<>(this.spectating.entrySet())) {
                Player p = Bukkit.getPlayer(e.getKey());
                GameManager gm = e.getValue();
                if (p == null) {
                    this.spectating.remove(e.getKey());
                } else if (gm.phase == GameManager.Phase.DONE || !this.core.matches.contains(gm)) {
                    this.stopSpectate(p, "§7경기가 끝나 로비로 돌아갑니다.");
                } else if (!this.spectateEnabled) {
                    this.stopSpectate(p, "§c관리자가 관전을 껐습니다.");
                } else if (this.liveMatch(gm)) {
                    this.stopSpectate(p, "§c스트리머 경기라 관전이 끝났습니다.");
                } else {
                    Location l = p.getLocation();
                    double dx = l.getX() - gm.arena.px;
                    double dz = l.getZ() - gm.arena.pz;
                    if (l.getWorld() != gm.arena.world || dx * dx + dz * dz > 110.0 * 110.0 || p.getGameMode() != GameMode.SPECTATOR) {
                        p.setGameMode(GameMode.SPECTATOR);
                        p.teleport(gm.arena.spectate(TeamColor.BLUE));
                    }
                }
            }
        }

        // 리스폰·월드 이동 때 클라이언트 F3 설정이 초기화돼서 5초마다 다시 보냄
        if (this.core.tick % 100L == 0L) {
            for (Map.Entry<UUID, Opt> e : this.streamers.entrySet()) {
                if (e.getValue().on) {
                    Player p = Bukkit.getPlayer(e.getKey());
                    if (p != null) {
                        reducedDebug(p, true);
                    }
                }
            }
        }
    }

    // ------------------------------------------------------------ 승패 연출

    /** result: 1 승리, 0 무승부, -1 패배 */
    void celebrate(Player p, int result, String reason, int blue, int red) {
        String score = "§9파랑 " + blue + " §f: §c" + red + " 빨강";
        if (result > 0) {
            p.sendTitle("§6§l✦ 승리! ✦", score + " §8· §f" + reason, 5, 100, 20);
            p.playSound(p.getLocation(), "ui.toast.challenge_complete", 1.0F, 1.0F);
            for (int i = 0; i < 6; i++) {
                int n = i;
                Bukkit.getScheduler().runTaskLater(this.core.plugin, () -> {
                    if (!p.isOnline()) {
                        return;
                    }

                    Location l = p.getLocation();
                    double ang = n * Math.PI / 3.0;
                    Location fx = l.clone().add(Math.cos(ang) * 2.5, 2.0 + n * 0.3, Math.sin(ang) * 2.5);
                    p.getWorld().spawnParticle(Particle.FIREWORK, fx, 40, 0.4, 0.4, 0.4, 0.15);
                    p.getWorld().spawnParticle(Particle.TOTEM_OF_UNDYING, l.clone().add(0.0, 1.5, 0.0), 30, 0.8, 0.8, 0.8, 0.3);
                    p.playSound(l, n % 2 == 0 ? "entity.firework_rocket.blast" : "entity.firework_rocket.twinkle", 1.0F, 1.0F + n * 0.05F);
                }, 6L + i * 8L);
            }

            Bukkit.getScheduler().runTaskLater(this.core.plugin, () -> {
                if (p.isOnline()) {
                    p.playSound(p.getLocation(), "entity.player.levelup", 1.0F, 1.0F);
                }
            }, 50L);
        } else if (result < 0) {
            p.sendTitle("§c§l패배...", score + " §8· §7" + reason, 5, 100, 20);
            p.playSound(p.getLocation(), "entity.wither.death", 0.5F, 1.4F);
            Bukkit.getScheduler().runTaskLater(this.core.plugin, () -> {
                if (p.isOnline()) {
                    p.getWorld().spawnParticle(Particle.LARGE_SMOKE, p.getLocation().add(0.0, 1.0, 0.0), 40, 0.6, 0.8, 0.6, 0.02);
                }
            }, 5L);
        } else {
            p.sendTitle("§e§l무승부", score + " §8· §7" + reason, 5, 100, 20);
            p.playSound(p.getLocation(), "block.note_block.pling", 1.0F, 0.8F);
        }
    }

    // ------------------------------------------------------------ 채팅

    String filter(String msg) {
        if (msg == null || msg.isEmpty()) {
            return msg;
        }

        Matcher m = LINK.matcher(msg);
        String out = m.replaceAll("§8[링크]§f");
        String lower = out.toLowerCase();
        StringBuilder sb = new StringBuilder(out);
        for (String w : this.badWords) {
            if (w == null || w.isEmpty()) {
                continue;
            }

            String lw = w.toLowerCase();
            int i = lower.indexOf(lw);
            while (i >= 0) {
                for (int k = i; k < i + lw.length() && k < sb.length(); k++) {
                    sb.setCharAt(k, '*');
                }

                i = lower.indexOf(lw, i + lw.length());
            }
        }

        return sb.toString();
    }

    @EventHandler(priority = EventPriority.MONITOR, ignoreCancelled = true)
    public void onChatView(AsyncPlayerChatEvent e) {
        boolean team = TEAM_CHAT.get();
        TEAM_CHAT.set(false);
        boolean any = false;
        for (Opt o : this.streamers.values()) {
            if (o.on) {
                any = true;
                break;
            }
        }

        if (!any) {
            return;
        }

        Player sender = e.getPlayer();
        String msg = e.getMessage();
        String filtered = null;
        String line = null;
        try {
            for (Player r : new ArrayList<>(e.getRecipients())) {
                Opt o = this.streamers.get(r.getUniqueId());
                if (o == null || !o.on || r.equals(sender)) {
                    continue;
                }

                if (o.chatOff && !team) {
                    e.getRecipients().remove(r);
                    continue;
                }

                if (o.filter) {
                    if (filtered == null) {
                        filtered = this.filter(msg);
                    }

                    if (!filtered.equals(msg)) {
                        e.getRecipients().remove(r);
                        if (line == null) {
                            try {
                                line = String.format(e.getFormat(), sender.getDisplayName(), filtered);
                            } catch (Exception ex) {
                                line = "<" + sender.getName() + "> " + filtered;
                            }
                        }

                        r.sendMessage(line);
                    }
                }
            }
        } catch (UnsupportedOperationException ignored) {
        }
    }

    @EventHandler(priority = EventPriority.LOW, ignoreCancelled = true)
    public void onCommand(PlayerCommandPreprocessEvent e) {
        String m = e.getMessage();
        if (m == null || m.length() < 2 || this.streamers.isEmpty()) {
            return;
        }

        String[] a = m.substring(1).trim().split(" +");
        if (a.length < 2) {
            return;
        }

        String cmd = a[0].toLowerCase();
        int c = cmd.indexOf(':');
        if (c >= 0) {
            cmd = cmd.substring(c + 1);
        }

        if (!WHISPER.contains(cmd)) {
            return;
        }

        Player sender = e.getPlayer();
        Player t = Bukkit.getPlayerExact(a[1]);
        if (t == null) {
            t = Bukkit.getPlayer(a[1]);
        }

        if (t != null && !t.equals(sender) && this.blocksInvite(t) && !sender.hasPermission("clash.admin")) {
            e.setCancelled(true);
            sender.sendMessage("§c" + t.getName() + " 님은 스트리머 모드라 귓속말을 받지 않습니다.");
        }
    }

    // ------------------------------------------------------------ F3 좌표 숨김 (reduced debug info)

    private static boolean nmsFailed;
    private static Method getHandle;
    private static Constructor<?> packetCtor;
    private static Field connField;
    private static Method sendMethod;

    void reducedDebug(Player p, boolean on) {
        if (nmsFailed) {
            return;
        }

        try {
            Object h = p.getClass().getMethod("getHandle").invoke(p);
            if (packetCtor == null) {
                Class<?> ent = Class.forName("net.minecraft.world.entity.Entity");
                Class<?> pk = Class.forName("net.minecraft.network.protocol.game.ClientboundEntityEventPacket");
                packetCtor = pk.getConstructor(ent, byte.class);
                connField = h.getClass().getField("connection");
                Class<?> packetIface = Class.forName("net.minecraft.network.protocol.Packet");
                sendMethod = connField.getType().getMethod("send", packetIface);
            }

            Object packet = packetCtor.newInstance(h, (byte)(on ? 22 : 23));
            Object conn = connField.get(h);
            sendMethod.invoke(conn, packet);
        } catch (Throwable t) {
            nmsFailed = true;
            this.core.plugin.getLogger().warning("스트리머 모드 F3 좌표 숨김 실패 (이 서버 버전에서는 안 됨): " + t);
        }
    }
}
