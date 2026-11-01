package kr.kjmn.clashmc;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.bukkit.Bukkit;
import org.bukkit.Color;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.World;
import org.bukkit.Particle.DustOptions;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.entity.ArmorStand;
import org.bukkit.entity.Entity;
import org.bukkit.entity.Interaction;
import org.bukkit.entity.Player;
import org.bukkit.entity.TextDisplay;
import org.bukkit.entity.Display.Billboard;
import org.bukkit.inventory.ItemStack;
import org.bukkit.scoreboard.DisplaySlot;
import org.bukkit.scoreboard.Objective;
import org.bukkit.scoreboard.Scoreboard;
import org.bukkit.util.Transformation;
import org.joml.Quaternionf;
import org.joml.Vector3f;

final class Lobby {
    static final List<Lobby.Portal> PORTALS = List.of(
        new Lobby.Portal("ai", -13.0, 0.0, -19.0, "§a§lAI 대전", "§7봇 상대로 연습 · 친구들과 협동", "§a"),
        new Lobby.Portal("ranked", 0.0, 0.0, -21.0, "§6§l랭크전", "§7트로피를 걸고 매칭", "§6"),
        new Lobby.Portal("friendly", 13.0, 0.0, -19.0, "§b§l친선전", "§7방을 만들고 친구 초대", "§b")
    );
    private final Clash core;
    boolean enabled;
    Location origin;
    private final List<Entity> decor = new ArrayList<>();
    private final Map<Entity, String> clickables = new HashMap<>();
    private TextDisplay leaderboard;
    private final List<ArmorStand> showcase = new ArrayList<>();
    private final List<TextDisplay> showcaseLabels = new ArrayList<>();
    private final Map<UUID, Scoreboard> boards = new HashMap<>();
    private final Map<UUID, List<String>> boardLines = new HashMap<>();
    private final Set<UUID> inPortal = new HashSet<>();
    private int showcaseRot;
    private static final double[] SHOW_Z = new double[]{-6.0, -2.0, 2.0, 6.0};
    private final List<Skins.Skin> showSkin = new ArrayList<>();

    Lobby(Clash var1) {
        this.core = var1;
    }

    void load() {
        FileConfiguration var1 = this.core.plugin.getConfig();
        this.enabled = var1.getBoolean("lobby.enabled", true);
        String var2 = var1.getString("lobby.world", "");
        World var3 = var2 != null && !var2.isEmpty() ? Bukkit.getWorld(var2) : null;
        this.origin = var3 == null
            ? null
            : new Location(
                var3, var1.getDouble("lobby.x"), var1.getDouble("lobby.y"), var1.getDouble("lobby.z"), (float)var1.getDouble("lobby.yaw", 180.0), 0.0F
            );
    }

    Location spawn() {
        if (this.origin != null) {
            return this.origin.clone().add(0.5, 0.0, 0.5);
        } else {
            return !this.core.arenas.slots.isEmpty()
                ? this.core.arenas.slots.values().iterator().next().arena.world.getSpawnLocation()
                : ((World)Bukkit.getWorlds().get(0)).getSpawnLocation();
        }
    }

    Location at(double var1, double var3, double var5) {
        return this.origin == null ? null : this.origin.clone().add(var1 + 0.5, var3, var5 + 0.5);
    }

    void onJoin(Player var1) {
        this.core.profiles.get(var1);
        if (!this.core.inGame(var1)) {
            this.toLobby(var1);
            this.core.sendUiPack(var1);
        }
    }

    void onQuit(Player var1) {
        this.boards.remove(var1.getUniqueId());
        this.boardLines.remove(var1.getUniqueId());
        this.inPortal.remove(var1.getUniqueId());
    }

    void toLobby(Player var1) {
        if (this.enabled || this.origin != null) {
            var1.teleport(this.spawn());
        }

        var1.setGameMode(GameMode.ADVENTURE);
        var1.setAllowFlight(false);
        var1.setFlying(false);
        var1.setHealth(20.0);
        var1.setFoodLevel(20);
        var1.setLevel(0);
        var1.setExp(0.0F);
        this.giveHotbar(var1);
        this.showBoard(var1);
    }

    void leaveLobby(Player var1) {
        var1.getInventory().clear();
        this.boards.remove(var1.getUniqueId());
        this.boardLines.remove(var1.getUniqueId());
    }

    ItemStack tagged(ItemStack var1, String var2) {
        return Ui.tag(var1, this.core.uiKey, var2);
    }

    void giveHotbar(Player var1) {
        if (!this.core.inGame(var1)) {
            var1.getInventory().clear();
            boolean var2 = this.core.queued(var1.getUniqueId());
            var1.getInventory().setItem(0, this.tagged(Ui.icon("play", Material.COMPASS, "§a§l플레이 §7(우클릭)", "§7AI 대전 · 랭크전 · 친선전"), "menu"));
            var1.getInventory().setItem(1, this.tagged(Ui.icon("deck", Material.BOOK, "§b§l덱 편집", "§7덱 3칸 · 8장"), "deck"));
            var1.getInventory().setItem(2, this.tagged(Ui.icon("skins", Material.ARMOR_STAND, "§d§l스킨", "§7유닛 / 타워 스킨"), "skins"));
            if (var2) {
                var1.getInventory().setItem(4, this.tagged(Ui.icon("cancel", Material.BARRIER, "§c§l랭크전 매칭 취소"), "cancel"));
            } else if (this.core.roomOf.containsKey(var1.getUniqueId())) {
                var1.getInventory().setItem(4, this.tagged(Ui.icon("friendly", Material.CAKE, "§b§l친선전 방", "§7방 메뉴 열기"), "room"));
            }

            var1.getInventory().setItem(6, this.tagged(Ui.icon("leaderboard", Material.GOLD_BLOCK, "§e§l랭킹"), "leaderboard"));
            var1.getInventory().setItem(7, this.tagged(Ui.icon("profile", Material.NAME_TAG, "§6§l프로필", "§7티어 · 트로피 · 전적"), "profile"));
            var1.getInventory().setItem(8, this.tagged(Ui.icon("menu", Material.NETHER_STAR, "§f§l메인 메뉴"), "menu"));
            var1.getInventory().setHeldItemSlot(0);
        }
    }

    void action(Player var1, String var2) {
        switch (var2) {
            case "menu":
                new Menus.MainMenu(this.core, var1).open();
                break;
            case "deck":
                new Menus.DeckMenu(this.core, var1, null, null).open();
                break;
            case "skins":
                new Menus.SkinListMenu(this.core, var1).open();
                break;
            case "profile":
                new Menus.ProfileMenu(this.core, var1).open();
                break;
            case "leaderboard":
                new Menus.LeaderboardMenu(this.core, var1).open();
                break;
            case "cancel":
                this.core.leaveRanked(var1);
                break;
            case "room":
                new Menus.RoomMenu(this.core, var1).open();
                break;
            case "ai":
                new Menus.AiMenu(this.core, var1).open();
                break;
            case "ranked":
                if (this.core.queued(var1.getUniqueId())) {
                    this.core.leaveRanked(var1);
                } else {
                    this.core.joinRanked(var1);
                }
                break;
            case "friendly":
                new Menus.RoomMenu(this.core, var1).open();
        }
    }

    void showBoard(Player var1) {
        Scoreboard var2 = Bukkit.getScoreboardManager().getNewScoreboard();
        Objective var3 = var2.registerNewObjective("lobby", "dummy", "§6§l⚔ 클래시 마크 ⚔");
        var3.setDisplaySlot(DisplaySlot.SIDEBAR);
        this.boards.put(var1.getUniqueId(), var2);
        this.boardLines.put(var1.getUniqueId(), new ArrayList<>());
        var1.setScoreboard(var2);
        this.updateBoard(var1);
    }

    void updateBoard(Player var1) {
        Scoreboard var2 = this.boards.get(var1.getUniqueId());
        if (var2 != null) {
            Objective var3 = var2.getObjective("lobby");
            if (var3 != null) {
                Profile var4 = this.core.profiles.get(var1);
                ArrayList var5 = new ArrayList();
                var5.add("§8" + "─".repeat(14));
                var5.add(Ranks.label(var4.trophies));
                var5.add("§6\ud83c\udfc6 §f" + var4.trophies + " §7(최고 " + var4.best + ")");
                Ranks.Tier var6 = Ranks.next(var4.trophies);
                if (var6 != null) {
                    var5.add("§7다음 " + var6.color() + var6.name() + " §7까지 " + (var6.min() - var4.trophies));
                }

                int var7 = this.core.profiles.rankOf(var1.getUniqueId());
                var5.add("§7서버 순위 §f" + (var7 > 0 ? var7 + "위" : "-"));
                var5.add(" ");
                var5.add("§a승 " + var4.wins + " §c패 " + var4.losses + " §7(" + var4.winRate() + ")");
                var5.add("§7연승 " + (var4.streak > 0 ? "§a" + var4.streak : "§70"));
                var5.add("  ");
                if (this.core.queued(var1.getUniqueId())) {
                    long var8 = (this.core.tick - this.core.rankedQueue.get(var1.getUniqueId())) / 20L;
                    var5.add("§6매칭 중 §f" + var8 / 60L + ":" + String.format("%02d", var8 % 60L));
                } else if (this.core.roomOf.containsKey(var1.getUniqueId())) {
                    Room var12 = this.core.roomOf.get(var1.getUniqueId());
                    var5.add("§b친선전 방 §f" + var12.code + " §7(" + var12.members.size() + "명)");
                } else {
                    var5.add("§7대기 중");
                }

                var5.add("§7진행 중 경기 §f" + this.core.matches.size() + " §8/ " + this.core.arenas.slots.size());
                var5.add("§7랭크 대기열 §f" + this.core.rankedQueue.size() + "명");
                var5.add("§8" + "─".repeat(14) + " ");
                List<String> var13 = this.boardLines.get(var1.getUniqueId());
                ArrayList var9 = new ArrayList();

                for (int var10 = 0; var10 < var5.size(); var10++) {
                    var9.add((String)var5.get(var10) + "§" + Integer.toHexString(var10 % 16) + "§r");
                }

                for (String var11 : var13) {
                    if (!var9.contains(var11)) {
                        var2.resetScores(var11);
                    }
                }

                for (int var15 = 0; var15 < var9.size(); var15++) {
                    var3.getScore((String)var9.get(var15)).setScore(var9.size() - var15);
                }

                var13.clear();
                var13.addAll(var9);
            }
        }
    }

    void tick() {
        if (this.core.tick % 20L == 0L) {
            for (Player var2 : Bukkit.getOnlinePlayers()) {
                if (!this.core.inGame(var2)) {
                    this.updateBoard(var2);
                    if (this.core.queued(var2.getUniqueId())) {
                        long var3 = (this.core.tick - this.core.rankedQueue.get(var2.getUniqueId())) / 20L;
                        GameManager.actionbar(
                            var2,
                            "§6⚔ 랭크전 매칭 중 §f"
                                + var3 / 60L
                                + ":"
                                + String.format("%02d", var3 % 60L)
                                + " §7· 대기 "
                                + this.core.rankedQueue.size()
                                + "명"
                                + (this.core.arenas.freeCount() == 0 ? " §c(빈 경기장 대기)" : "")
                        );
                    }
                }
            }
        }

        if (this.origin != null) {
            if (this.enabled && this.core.tick % 40L == 0L && this.origin.getWorld().isChunkLoaded(this.origin.getBlockX() >> 4, this.origin.getBlockZ() >> 4)) {
                boolean var11 = this.decor.isEmpty();

                for (Entity var20 : this.decor) {
                    if (!var20.isValid() && !this.showcase.contains(var20)) {
                        var11 = true;
                        break;
                    }
                }

                if (var11) {
                    this.spawnDecor();
                } else {
                    for (int var16 = 0; var16 < this.showcase.size(); var16++) {
                        ArmorStand var21 = this.showcase.get(var16);
                        if (!var21.isValid() && this.chunkLoaded(SHOW_Z[var16])) {
                            this.replaceStand(var16);
                        }
                    }
                }
            }

            if (this.core.tick % 5L == 0L) {
                for (Player var17 : Bukkit.getOnlinePlayers()) {
                    if (!this.core.inGame(var17) && var17.getWorld() == this.origin.getWorld()) {
                        String var22 = null;

                        for (Lobby.Portal var5 : PORTALS) {
                            Location var6 = this.at(var5.dx, var5.dy, var5.dz);
                            double var7 = var17.getLocation().getX() - var6.getX();
                            double var9 = var17.getLocation().getZ() - var6.getZ();
                            if (Math.abs(var7) <= 2.0 && Math.abs(var9) <= 1.2 && Math.abs(var17.getLocation().getY() - var6.getY()) < 2.5) {
                                var22 = var5.action;
                            }
                        }

                        if (var22 != null && this.inPortal.add(var17.getUniqueId())) {
                            var17.playSound(var17.getLocation(), "block.portal.trigger", 0.4F, 1.8F);
                            this.action(var17, var22);
                            var17.teleport(var17.getLocation().add(0.0, 0.0, 2.2).setDirection(var17.getLocation().getDirection()));
                        } else if (var22 == null) {
                            this.inPortal.remove(var17.getUniqueId());
                        }
                    }
                }
            }

            if (this.core.tick % 4L == 0L) {
                for (Lobby.Portal var18 : PORTALS) {
                    Location var23 = this.at(var18.dx, var18.dy + 1.6, var18.dz);
                    Color var25 = var18.action.equals("ai")
                        ? Color.fromRGB(90, 230, 90)
                        : (var18.action.equals("ranked") ? Color.fromRGB(255, 200, 60) : Color.fromRGB(90, 190, 255));
                    this.origin.getWorld().spawnParticle(Particle.DUST, var23, 6, 1.0, 1.2, 0.1, 0.0, new DustOptions(var25, 1.2F));
                    this.origin.getWorld().spawnParticle(Particle.END_ROD, var23, 1, 0.9, 1.0, 0.1, 0.01);
                }
            }

            if (!this.showcase.isEmpty()) {
                for (ArmorStand var19 : this.showcase) {
                    if (var19.isValid() && this.core.tick % 2L == 0L) {
                        Location var24 = var19.getLocation();
                        var24.setYaw(var24.getYaw() + 2.0F);
                        var19.teleport(var24);
                    }
                }

                if (this.core.tick % 600L == 0L) {
                    this.rotateShowcase();
                }
            }
        }
    }

    void spawnDecor() {
        this.clearDecor();
        if (this.origin != null && this.enabled) {
            World var1 = this.origin.getWorld();

            for (Lobby.Portal var3 : PORTALS) {
                this.text(this.at(var3.dx, var3.dy + 4.4, var3.dz + 2.4), var3.label + "\n" + var3.sub + "\n§f▼ 들어가기 / 클릭 ▼", 2.2F, true);  // 아치 앞으로 (블록에 안 가리게)
                Interaction var4 = (Interaction)var1.spawn(this.at(var3.dx, var3.dy, var3.dz), Interaction.class);
                var4.addScoreboardTag("clashmc");
                var4.setInteractionWidth(4.0F);
                var4.setInteractionHeight(4.0F);
                var4.setPersistent(false);
                this.decor.add(var4);
                this.clickables.put(var4, var3.action);
            }

            this.leaderboard = this.text(this.at(18.4, 3.0, 0.0), "", 1.6F, false);
            this.refreshLeaderboard();
            this.text(
                this.at(0.0, 4.0, 15.4),
                "§6§l클래시 마크\n§f킹이 되어 카드를 쓰고, 나머지는 유닛으로 전장에!\n§7핫바 §f플레이§7 · §f덱§7 · §f스킨§7 · §f프로필\n§7랭크전에서 지면 §c킹§7이 트로피를 더 많이 잃어요",
                1.3F,
                false
            );
            this.showSkin.clear();

            for (double var5 : SHOW_Z) {
                ArmorStand var7 = this.newStand(var5);
                this.showcase.add(var7);
                this.decor.add(var7);
                this.showSkin.add(null);
                this.showcaseLabels.add(this.text(this.at(-17.0, 4.3, var5), "", 1.0F, true));
            }

            Bukkit.getScheduler().runTaskLater(this.core.plugin, this::rotateShowcase, 20L);
        }
    }

    private boolean chunkLoaded(double var1) {
        Location var3 = this.at(-17.0, 1.0, var1);
        return var3.getWorld().isChunkLoaded(var3.getBlockX() >> 4, var3.getBlockZ() >> 4);
    }

    private ArmorStand newStand(double var1) {
        Location var3 = this.at(-17.0, 1.0, var1);
        var3.setYaw(90.0F);
        ArmorStand var4 = (ArmorStand)var3.getWorld().spawn(var3, ArmorStand.class);
        var4.addScoreboardTag("clashmc");
        var4.setInvisible(true);
        var4.setGravity(false);
        var4.setInvulnerable(true);
        var4.setPersistent(false);
        var4.setBasePlate(false);
        var4.setMarker(true);
        var4.setCustomName("");
        var4.setCustomNameVisible(false);
        return var4;
    }

    private void replaceStand(int var1) {
        ArmorStand var2 = this.showcase.get(var1);
        Location var3 = var2.isValid() ? var2.getLocation() : null;
        this.core.models.remove(var2);
        var2.remove();
        this.decor.remove(var2);
        ArmorStand var4 = this.newStand(SHOW_Z[var1]);
        if (var3 != null) {
            Location var5 = var4.getLocation();
            var5.setYaw(var3.getYaw());
            var4.teleport(var5);
        }

        this.showcase.set(var1, var4);
        this.decor.add(var4);
        Skins.Skin var6 = this.showSkin.get(var1);
        if (var6 != null) {
            this.applyRetry(var4, var6.model(), var1 % 2 == 0 ? TeamColor.BLUE.color : TeamColor.RED.color, 0);
        }
    }

    private void applyRetry(ArmorStand var1, String var2, Color var3, int var4) {
        if (var1.isValid() && this.showcase.contains(var1)) {
            if (!this.core.models.apply(var1, var2, true, var3)) {
                if (var4 < 40) {
                    Bukkit.getScheduler().runTaskLater(this.core.plugin, () -> this.applyRetry(var1, var2, var3, var4 + 1), 20L);
                }
            }
        }
    }

    private TextDisplay text(Location var1, String var2, float var3, boolean var4) {
        TextDisplay var5 = (TextDisplay)var1.getWorld().spawn(var1, TextDisplay.class);
        var5.addScoreboardTag("clashmc");
        var5.setText(var2);
        var5.setBillboard(var4 ? Billboard.CENTER : Billboard.FIXED);
        if (!var4) {
            Location var6 = var1.clone();
            var6.setYaw(var1.getX() > this.origin.getX() + 5.0 ? 90.0F : (var1.getZ() > this.origin.getZ() + 5.0 ? 180.0F : 0.0F));
            var5.teleport(var6);
        }

        var5.setBackgroundColor(Color.fromARGB(120, 10, 12, 20));
        var5.setShadowed(true);
        var5.setLineWidth(320);
        var5.setPersistent(false);
        var5.setTransformation(new Transformation(new Vector3f(), new Quaternionf(), new Vector3f(var3, var3, var3), new Quaternionf()));
        this.decor.add(var5);
        return var5;
    }

    void refreshLeaderboard() {
        if (this.leaderboard != null && this.leaderboard.isValid()) {
            StringBuilder var1 = new StringBuilder("§6§l\ud83c\udfc6 랭킹 TOP 10 \ud83c\udfc6\n§8────────────\n");
            List var2 = this.core.profiles.top(10);
            if (var2.isEmpty()) {
                var1.append("§7아직 기록이 없습니다\n");
            }

            for (int var3 = 0; var3 < var2.size(); var3++) {
                Profile var4 = (Profile)var2.get(var3);
                String var5 = var3 == 0 ? "§6①" : (var3 == 1 ? "§7②" : (var3 == 2 ? "§c③" : "§8" + (var3 + 1) + "."));
                var1.append(var5)
                    .append(" ")
                    .append(Ranks.badge(var4.trophies))
                    .append(" §f")
                    .append(var4.name)
                    .append(" §e")
                    .append(var4.trophies)
                    .append("\ud83c\udfc6\n");
            }

            var1.append("§8────────────\n§7랭크전 승리로 트로피 획득");
            this.leaderboard.setText(var1.toString());
        }
    }

    /** 쇼케이스: 유저가 쓸 수 있는 카드만, 건물은 빼고 */
    private boolean showable(CardDef c) {
        return c != null && this.core.usable(c) && !c.isBuilding();
    }

    private void rotateShowcase() {
        if (!this.showcase.isEmpty() && this.core.models.enabled()) {
            ArrayList var1 = new ArrayList();

            for (Skins.Skin var3 : this.core.skins.all.values()) {
                if (!var3.target().equals("princess") && !var3.target().equals("king") && !var3.model().isEmpty() && this.showable(this.core.cards.get(var3.target()))) {
                    var1.add(var3);
                }
            }

            boolean var6 = var1.isEmpty();
            if (var6) {
                for (CardDef var4 : this.core.cards.values()) {
                    String var5 = var4.isSpell() && var4.projectileModel != null && !var4.projectileModel.isEmpty()
                        ? var4.projectileModel
                        : (var4.barrelModel != null && !var4.barrelModel.isEmpty() ? var4.barrelModel : var4.model);
                    if (var5 != null
                        && !var5.isEmpty()
                        && this.showable(var4)
                        && (!var4.isSpell() || var4.projectileModel != null && !var4.projectileModel.isEmpty() || var4.id.equals("the_log"))) {
                        var1.add(new Skins.Skin("card_" + var4.id, var4.id, var4.name, "", var5, "", "common", "default", ""));
                    }
                }
            }

            if (!var1.isEmpty()) {
                for (int var8 = 0; var8 < this.showcase.size(); var8++) {
                    Skins.Skin var9 = (Skins.Skin)var1.get((this.showcaseRot * this.showcase.size() + var8) % var1.size());
                    this.showSkin.set(var8, var9);
                    this.replaceStand(var8);
                    CardDef var10 = this.core.cards.get(var9.target());
                    if (var6) {
                        this.showcaseLabels.get(var8).setText("§f§l" + var9.name() + "\n§7" + (var10 == null ? "" : var10.elixir + " 엘릭서"));
                    } else {
                        this.showcaseLabels
                            .get(var8)
                            .setText(
                                var9.rarityColor()
                                    + "§l"
                                    + var9.name()
                                    + "\n§7"
                                    + (var10 == null ? var9.target() : var10.name)
                                    + " 스킨\n"
                                    + this.core.skins.unlockText(var9)
                            );
                    }
                }

                this.showcaseRot++;
            }
        }
    }

    void clearDecor() {
        for (Entity var2 : this.decor) {
            this.core.models.remove(var2);
            var2.remove();
        }

        this.decor.clear();
        this.clickables.clear();
        this.showcase.clear();
        this.showcaseLabels.clear();
        this.showSkin.clear();
        this.leaderboard = null;
    }

    String clickAction(Entity var1) {
        return this.clickables.get(var1);
    }

    record Portal(String action, double dx, double dy, double dz, String label, String sub, String color) {
    }
}
