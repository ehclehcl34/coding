package kr.kjmn.clashmc;

import com.destroystokyo.paper.event.player.PlayerJumpEvent;
import java.util.ArrayList;
import java.util.UUID;
import org.bukkit.Bukkit;
import org.bukkit.GameMode;
import org.bukkit.Location;
import org.bukkit.entity.Entity;
import org.bukkit.entity.LivingEntity;
import org.bukkit.entity.Player;
import org.bukkit.event.Cancellable;
import org.bukkit.event.EventHandler;
import org.bukkit.event.EventPriority;
import org.bukkit.event.Listener;
import org.bukkit.event.block.Action;
import org.bukkit.event.block.BlockBreakEvent;
import org.bukkit.event.block.BlockPlaceEvent;
import org.bukkit.event.entity.EntityCombustEvent;
import org.bukkit.event.entity.EntityDamageByEntityEvent;
import org.bukkit.event.entity.EntityDamageEvent;
import org.bukkit.event.entity.EntityDeathEvent;
import org.bukkit.event.entity.FoodLevelChangeEvent;
import org.bukkit.event.inventory.InventoryClickEvent;
import org.bukkit.event.inventory.InventoryDragEvent;
import org.bukkit.event.player.AsyncPlayerChatEvent;
import org.bukkit.event.player.PlayerAnimationEvent;
import org.bukkit.event.player.PlayerAnimationType;
import org.bukkit.event.player.PlayerDropItemEvent;
import org.bukkit.event.player.PlayerInteractEntityEvent;
import org.bukkit.event.player.PlayerInteractEvent;
import org.bukkit.event.player.PlayerJoinEvent;
import org.bukkit.event.player.PlayerMoveEvent;
import org.bukkit.event.player.PlayerQuitEvent;
import org.bukkit.event.player.PlayerSwapHandItemsEvent;
import org.bukkit.event.player.PlayerToggleSprintEvent;
import org.bukkit.inventory.EquipmentSlot;

public final class GameListener implements Listener {
    private final Clash core;

    GameListener(Clash var1) {
        this.core = var1;
    }

    private org.bukkit.util.CachedServerIcon icon;
    private boolean iconTried;

    /** 서버 목록 아이콘 (plugins/ClashMC/server-icon.png, 64x64) */
    @EventHandler
    public void onPing(org.bukkit.event.server.ServerListPingEvent e) {
        if (!this.core.plugin.getConfig().getBoolean("server-icon.enabled", true)) {
            return;
        }

        if (!this.iconTried) {
            this.iconTried = true;
            try {
                java.io.File f = new java.io.File(this.core.plugin.getDataFolder(), "server-icon.png");
                if (!f.exists()) {
                    this.core.plugin.saveResource("server-icon.png", false);
                } else {
                    // 예전 기본 아이콘(3.4.0)이면 새 기본 아이콘으로 교체 (직접 바꾼 아이콘은 그대로)
                    byte[] cur = java.nio.file.Files.readAllBytes(f.toPath());
                    StringBuilder hx = new StringBuilder();
                    for (byte bt : java.security.MessageDigest.getInstance("SHA-1").digest(cur)) {
                        hx.append(String.format("%02x", bt));
                    }

                    if (hx.toString().equals("4a9f4a060e949f9cd4db4ba934917483afdc0db5")) {
                        this.core.plugin.saveResource("server-icon.png", true);
                    }
                }

                this.icon = Bukkit.loadServerIcon(f);
            } catch (Exception ex) {
                this.core.plugin.getLogger().warning("서버 아이콘 불러오기 실패: " + ex);
            }
        }

        if (this.icon != null) {
            try {
                e.setServerIcon(this.icon);
            } catch (Exception ignored) {
            }
        }
    }

    private boolean lobbyPlayer(Player var1) {
        return this.core.lobby.enabled && !this.core.inGame(var1) && (var1.getGameMode() != GameMode.CREATIVE || !var1.hasPermission("clash.admin"));
    }

    @EventHandler
    public void onPackStatus(org.bukkit.event.player.PlayerResourcePackStatusEvent e) {
        if (e.getStatus() == org.bukkit.event.player.PlayerResourcePackStatusEvent.Status.SUCCESSFULLY_LOADED) {
            this.core.bgm.restart(e.getPlayer());
        }
    }

    @EventHandler
    public void onJoin(PlayerJoinEvent var1) {
        this.core.lobby.onJoin(var1.getPlayer());
    }

    @EventHandler
    public void onQuit(PlayerQuitEvent var1) {
        this.core.bgm.quit(var1.getPlayer());
        this.core.onQuit(var1.getPlayer());
    }

    @EventHandler(
        priority = EventPriority.HIGH
    )
    public void onInteract(PlayerInteractEvent var1) {
        Player var2 = var1.getPlayer();
        GameManager var3 = this.core.matchOf(var2);
        if (var1.getHand() != EquipmentSlot.HAND) {
            if (var3 != null || this.lobbyPlayer(var2)) {
                var1.setCancelled(true);
            }
        } else {
            Action var4 = var1.getAction();
            boolean var5 = var4 == Action.RIGHT_CLICK_AIR || var4 == Action.RIGHT_CLICK_BLOCK;
            String var6 = Ui.tagOf(var1.getItem(), this.core.uiKey);
            if (var3 == null) {
                if (var6 != null && var5) {
                    var1.setCancelled(true);
                    this.core.lobby.action(var2, var6);
                } else {
                    if (this.lobbyPlayer(var2) && var4 == Action.RIGHT_CLICK_BLOCK) {
                        var1.setCancelled(true);
                    }
                }
            } else if (var3.inMatch(var2)) {
                if (var5) {
                    var1.setCancelled(true);
                    if ("surrender".equals(var6)) {
                        var3.surrender(var2);
                        return;
                    }

                    if (var3.kingTeam(var2) == null || var3.activeUnits.contains(var2.getUniqueId())) {
                        return;
                    }

                    String var7 = var3.cardIdOf(var1.getItem());
                    if (var7 == null) {
                        return;
                    }

                    var3.kingUseCard(var2, var2.getInventory().getHeldItemSlot());
                } else if (var4 == Action.LEFT_CLICK_BLOCK) {
                    var1.setCancelled(true);
                }
            }
        }
    }

    @EventHandler
    public void onInteractEntity(PlayerInteractEntityEvent var1) {
        String var2 = this.core.lobby.clickAction(var1.getRightClicked());
        if (var2 != null && !this.core.inGame(var1.getPlayer())) {
            var1.setCancelled(true);
            this.core.lobby.action(var1.getPlayer(), var2);
        }
    }

    @EventHandler
    public void onSwing(PlayerAnimationEvent var1) {
        if (var1.getAnimationType() == PlayerAnimationType.ARM_SWING) {
            Player var2 = var1.getPlayer();
            GameManager var3 = this.core.matchOf(var2);
            if (var3 != null && var3.phase == GameManager.Phase.PLAYING && var3.activeUnits.contains(var2.getUniqueId())) {
                var3.battle.playerSwing(var2);
            }
        }
    }

    @EventHandler(
        priority = EventPriority.HIGH
    )
    public void onMove(PlayerMoveEvent var1) {
        Player var2 = var1.getPlayer();
        Location var3 = var1.getFrom();
        Location var4 = var1.getTo();
        if (var4 != null) {
            GameManager var5 = this.core.matchOf(var2);
            if (var5 == null) {
                if (this.lobbyPlayer(var2)
                    && this.core.lobby.origin != null
                    && var4.getWorld() == this.core.lobby.origin.getWorld()
                    && var4.getY() < this.core.lobby.origin.getY() - 30.0) {
                    var1.setTo(this.core.lobby.spawn());
                }
            } else if (var5.inMatch(var2)) {
                if (!var5.test.freeMove || !var5.test.isAdmin(var2.getUniqueId()) || var5.activeUnits.contains(var2.getUniqueId())) {
                    GameTeam var6 = var5.kingTeam(var2);
                    if (var6 == null || var5.activeUnits.contains(var2.getUniqueId())) {
                        Combatant var15 = var5.battle.unitOf(var2.getUniqueId());
                        if (var15 != null) {
                            boolean var8 = var3.getX() != var4.getX() || var3.getZ() != var4.getZ() || var3.getY() != var4.getY();
                            if (var8) {
                                if (var5.battle.frozen(var15)) {
                                    var1.setTo(keepLook(var3, var4));
                                } else {
                                    Arena var9 = var5.arena;
                                    if (!var9.inField(var4)) {
                                        var1.setTo(keepLook(var3, var4));
                                    } else {
                                        int var10 = var9.tileX(var4.getX());
                                        int var11 = var9.tileZ(var4.getZ());
                                        if (!var15.air && var9.isRiverRow(var11) && !var9.onBridge(var4.getX())) {
                                            if (var15.card.riverJump) {
                                                int var16 = var4.getZ() > var3.getZ() ? 1 : (var4.getZ() < var3.getZ() ? -1 : var15.team.dir);
                                                Location var13 = var4.clone();
                                                var13.setZ(var16 > 0 ? var9.riverMaxZ() + 0.6 : var9.riverMinZ() - 0.6);
                                                var13.setY(var9.floorY + 1);
                                                var1.setTo(var13);
                                                var2.getWorld()
                                                    .playSound(
                                                        var13, var15.card.id.equals("hog_rider") ? "entity.pig.ambient" : "entity.horse.jump", 1.0F, 0.8F
                                                    );
                                                var5.models.anim(var2, "jump");
                                            } else {
                                                var1.setTo(keepLook(var3, var4));
                                            }
                                        } else {
                                            if (var15.air) {
                                                double var12 = var9.floorY + 1 + var5.airHeight;
                                                if (Math.abs(var4.getY() - var12) > 0.5) {
                                                    Location var14 = var4.clone();
                                                    var14.setY(var12);
                                                    var1.setTo(var14);
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    } else if (var5.phase == GameManager.Phase.PLAYING && var5.battle != null && var5.battle.inTopView(var2)) {
                        // 탑뷰: 자리 고정, 고개만 돌릴 수 있음
                        Location tv = var5.battle.topViewLoc(var6.color);
                        if (Math.abs(var4.getX() - tv.getX()) > 0.01 || Math.abs(var4.getY() - tv.getY()) > 0.01 || Math.abs(var4.getZ() - tv.getZ()) > 0.01) {
                            var1.setTo(keepLook(tv, var4));
                        }

                        if (!var2.isFlying()) {
                            var2.setAllowFlight(true);
                            var2.setFlying(true);
                        }
                    } else if (var5.kingFly && var5.phase == GameManager.Phase.PLAYING) {
                        Location var7 = var5.arena.clampKing(var4);
                        if (var7.getX() != var4.getX() || var7.getY() != var4.getY() || var7.getZ() != var4.getZ()) {
                            var1.setTo(var7);
                        }

                        if (!var2.isFlying()) {
                            var2.setAllowFlight(true);
                            var2.setFlying(true);
                        }
                    } else {
                        if (!var5.arena.inBalcony(var6.color, var4)) {
                            var1.setTo(keepLook(var3, var4));
                        }
                    }
                }
            }
        }
    }

    private static Location keepLook(Location var0, Location var1) {
        Location var2 = var0.clone();
        var2.setYaw(var1.getYaw());
        var2.setPitch(var1.getPitch());
        return var2;
    }

    @EventHandler
    public void onJump(PlayerJumpEvent var1) {
        GameManager var2 = this.core.matchOf(var1.getPlayer());
        if (var2 != null && var2.inMatch(var1.getPlayer()) && var2.kingTeam(var1.getPlayer()) == null) {
            var1.setCancelled(true);
        }
    }

    @EventHandler
    public void onSprint(PlayerToggleSprintEvent var1) {
        GameManager var2 = this.core.matchOf(var1.getPlayer());
        if (var1.isSprinting() && var2 != null && var2.activeUnits.contains(var1.getPlayer().getUniqueId())) {
            var1.setCancelled(true);
        }
    }

    @EventHandler
    public void onFood(FoodLevelChangeEvent var1) {
        if (var1.getEntity() instanceof Player var2 && (this.core.inGame(var2) || this.lobbyPlayer(var2))) {
            var1.setCancelled(true);
        }
    }

    @EventHandler(
        priority = EventPriority.HIGHEST
    )
    public void onDamage(EntityDamageEvent var1) {
        Entity var2 = var1.getEntity();
        if (this.core.matchOfEntity(var2) == null && this.core.lobby.clickAction(var2) == null) {
            if (var2 instanceof Player var3 && (this.core.inGame(var3) || this.lobbyPlayer(var3))) {
                var1.setCancelled(true);
            }
        } else {
            var1.setCancelled(true);
        }
    }

    @EventHandler(
        priority = EventPriority.HIGHEST
    )
    public void onDamageBy(EntityDamageByEntityEvent var1) {
        if (var1.getDamager() instanceof Player var2) {
            if (this.core.inGame(var2)) {
                var1.setCancelled(true);
            }

            String var4 = this.core.lobby.clickAction(var1.getEntity());
            if (var4 != null && !this.core.inGame(var2)) {
                var1.setCancelled(true);
                this.core.lobby.action(var2, var4);
            }
        }

        if (this.core.matchOfEntity(var1.getEntity()) != null) {
            var1.setCancelled(true);
        }
    }

    @EventHandler(
        priority = EventPriority.HIGHEST
    )
    public void onDeath(EntityDeathEvent var1) {
        LivingEntity var2 = var1.getEntity();
        if (!(var2 instanceof Player)) {
            boolean var3 = var2.getScoreboardTags().contains("clashmc") || this.core.matchOfEntity(var2) != null || this.core.lobby.clickAction(var2) != null;
            if (var3 && var1 instanceof Cancellable var4) {
                var4.setCancelled(true);
                if (var2 instanceof LivingEntity var5) {
                    var5.setHealth(Math.max(1.0, var5.getHealth()));
                }
            }
        }
    }

    @EventHandler
    public void onCombust(EntityCombustEvent var1) {
        if (this.core.matchOfEntity(var1.getEntity()) != null) {
            var1.setCancelled(true);
        }
    }

    @EventHandler
    public void onClick(InventoryClickEvent var1) {
        if (var1.getInventory().getHolder() instanceof Menus.Menu var4) {
            var1.setCancelled(true);
            if (var1.getWhoClicked() instanceof Player && var1.getClickedInventory() == var1.getInventory()) {
                var4.click(var1.getRawSlot(), var1.isShiftClick());
            }
        } else {
            if (var1.getWhoClicked() instanceof Player var2 && (this.core.inGame(var2) || this.lobbyPlayer(var2))) {
                var1.setCancelled(true);
            }
        }
    }

    @EventHandler
    public void onDrag(InventoryDragEvent var1) {
        if (var1.getInventory().getHolder() instanceof Menus.Menu) {
            var1.setCancelled(true);
        } else if (var1.getWhoClicked() instanceof Player var2 && (this.core.inGame(var2) || this.lobbyPlayer(var2))) {
            var1.setCancelled(true);
        }
    }

    @EventHandler
    public void onDrop(PlayerDropItemEvent var1) {
        if (this.core.inGame(var1.getPlayer()) || this.lobbyPlayer(var1.getPlayer())) {
            var1.setCancelled(true);
        }
    }

    @EventHandler
    public void onSwap(PlayerSwapHandItemsEvent var1) {
        Player var2 = var1.getPlayer();
        if (this.core.inGame(var2)) {
            var1.setCancelled(true);
            // 킹: F키로 탑뷰 전환
            GameManager gm = this.core.matchOf(var2);
            if (gm != null && gm.phase == GameManager.Phase.PLAYING && gm.battle != null && !gm.activeUnits.contains(var2.getUniqueId())) {
                GameTeam team = gm.kingTeam(var2);
                if (team != null) {
                    gm.battle.toggleTopView(var2, team);
                }
            }
        } else {
            if (this.lobbyPlayer(var2)) {
                var1.setCancelled(true);
                this.core.lobby.action(var2, "menu");
            }
        }
    }

    @EventHandler
    public void onBreak(BlockBreakEvent var1) {
        if (this.core.inGame(var1.getPlayer()) || this.lobbyPlayer(var1.getPlayer())) {
            var1.setCancelled(true);
        }
    }

    @EventHandler
    public void onPlace(BlockPlaceEvent var1) {
        if (this.core.inGame(var1.getPlayer()) || this.lobbyPlayer(var1.getPlayer())) {
            var1.setCancelled(true);
        }
    }

    @EventHandler(
        priority = EventPriority.HIGH
    )
    public void onChat(AsyncPlayerChatEvent var1) {
        Player var2 = var1.getPlayer();
        UUID var3 = var2.getUniqueId();
        GameManager var4 = null;

        for (GameManager var6 : new ArrayList<>(this.core.matches)) {
            if (var6.teamOf.containsKey(var3)) {
                var4 = var6;
                break;
            }
        }

        if (var4 == null) {
            Profile var15 = this.core.profiles.get(var3);
            var1.setFormat(Ranks.badge(var15.trophies) + " §f%1$s§7: §f%2$s");
        } else {
            TeamColor var14 = var4.teamOf.get(var3);
            GameTeam var16 = var14 == null ? null : var4.teams.get(var14);
            if (var16 != null) {
                boolean var7 = var3.equals(var16.king);
                boolean var8 = !var7 && !var4.activeUnits.contains(var3);
                if (var8 && var4.slowmode > 0.0) {
                    long var9 = System.currentTimeMillis();
                    Long var11 = var4.chatCooldown.get(var3);
                    long var12 = (long)(var4.slowmode * 1000.0);
                    if (var11 != null && var9 - var11 < var12) {
                        var1.setCancelled(true);
                        var2.sendMessage("§7슬로우모드: " + String.format("%.1f", (var12 - (var9 - var11)) / 1000.0) + "초 후 다시 보낼 수 있습니다.");
                        return;
                    }

                    var4.chatCooldown.put(var3, var9);
                }

                var1.getRecipients().removeIf(var1x -> !var16.members.contains(var1x.getUniqueId()));
                String var17 = var7 ? "§6[킹]" : (var8 ? "§7[대기]" : "§a[유닛]");
                var1.setFormat(var14.cc + "[팀] " + var17 + " §f%1$s§7: §f%2$s");
            }
        }
    }
}
