package org.bukkit.entity;

public interface Player extends org.bukkit.entity.HumanEntity, org.bukkit.OfflinePlayer {
    default void playSound(org.bukkit.entity.Entity a0, java.lang.String a1, org.bukkit.SoundCategory a2, float a3, float a4) {  }
    default void stopSound(java.lang.String a0, org.bukkit.SoundCategory a1) {  }
    default void addResourcePack(java.util.UUID a0, java.lang.String a1, byte[] a2, java.lang.String a3, boolean a4) {  }
    default void closeInventory() {  }
    default boolean getAllowFlight() { return false; }
    default org.bukkit.Location getEyeLocation() { return null; }
    default int getFoodLevel() { return 0; }
    default org.bukkit.GameMode getGameMode() { return null; }
    default org.bukkit.inventory.PlayerInventory getInventory() { return null; }
    default org.bukkit.Location getLocation() { return null; }
    default java.lang.String getName() { return null; }
    default org.bukkit.block.Block getTargetBlockExact(int a0) { return null; }
    default java.util.UUID getUniqueId() { return null; }
    default java.net.InetSocketAddress getVirtualHost() { return null; }
    default float getWalkSpeed() { return 0; }
    default org.bukkit.World getWorld() { return null; }
    default boolean hasPermission(java.lang.String a0) { return false; }
    default boolean isFlying() { return false; }
    default boolean isOnline() { return false; }
    default org.bukkit.inventory.InventoryView openInventory(org.bukkit.inventory.Inventory a0) { return null; }
    default void playSound(org.bukkit.Location a0, java.lang.String a1, float a2, float a3) {  }
    default void sendActionBar(java.lang.String a0) {  }
    default void sendMessage(java.lang.String a0) {  }
    default void sendTitle(java.lang.String a0, java.lang.String a1, int a2, int a3, int a4) {  }
    default void setAllowFlight(boolean a0) {  }
    default void setExp(float a0) {  }
    default void setFireTicks(int a0) {  }
    default void setFlySpeed(float a0) {  }
    default void setFlying(boolean a0) {  }
    default void setFoodLevel(int a0) {  }
    default void setGameMode(org.bukkit.GameMode a0) {  }
    default void setHealth(double a0) {  }
    default void setLevel(int a0) {  }
    default void setSaturation(float a0) {  }
    default void setScoreboard(org.bukkit.scoreboard.Scoreboard a0) {  }
    default void setVelocity(org.bukkit.util.Vector a0) {  }
    default void setWalkSpeed(float a0) {  }
    default void spawnParticle(org.bukkit.Particle a0, double a1, double a2, double a3, int a4, double a5, double a6, double a7, double a8, java.lang.Object a9) {  }
    default org.bukkit.entity.Player.Spigot spigot() { return null; }
    default boolean teleport(org.bukkit.Location a0) { return false; }
    default void showEntity(org.bukkit.plugin.Plugin a0, org.bukkit.entity.Entity a1) {  }
    default void setPlayerListName(java.lang.String a0) {  }
    default java.lang.String getDisplayName() { return null; }
    public static class Spigot {
        protected Spigot() {}
        public void sendMessage(net.md_5.bungee.api.ChatMessageType a0, net.md_5.bungee.api.chat.BaseComponent[] a1) {  }
        public void sendMessage(net.md_5.bungee.api.chat.BaseComponent[] a0) {  }
    }
}
