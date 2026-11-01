package org.bukkit;

public interface World extends org.bukkit.plugin.messaging.PluginMessageRecipient {
    default <T extends org.bukkit.entity.Entity> java.util.Collection<T> getEntitiesByClass(java.lang.Class<T> a0) { return null; }
    default java.util.List<org.bukkit.entity.Player> getPlayers() { return null; }
    default org.bukkit.block.Block getBlockAt(int a0, int a1, int a2) { return null; }
    default java.lang.String getName() { return null; }
    default org.bukkit.Location getSpawnLocation() { return null; }
    default boolean isChunkLoaded(int a0, int a1) { return false; }
    default void playSound(org.bukkit.Location a0, java.lang.String a1, float a2, float a3) {  }
    default org.bukkit.util.RayTraceResult rayTraceEntities(org.bukkit.Location a0, org.bukkit.util.Vector a1, double a2, double a3, java.util.function.Predicate<? super org.bukkit.entity.Entity> a4) { return null; }
    default org.bukkit.entity.Entity spawn(org.bukkit.Location a0, java.lang.Class a1) { return null; }
    default org.bukkit.entity.Entity spawnEntity(org.bukkit.Location a0, org.bukkit.entity.EntityType a1) { return null; }
    default void spawnParticle(org.bukkit.Particle a0, double a1, double a2, double a3, int a4, double a5, double a6, double a7, double a8) {  }
    default void spawnParticle(org.bukkit.Particle a0, double a1, double a2, double a3, int a4, double a5, double a6, double a7, double a8, java.lang.Object a9) {  }
    default void spawnParticle(org.bukkit.Particle a0, org.bukkit.Location a1, int a2) {  }
    default void spawnParticle(org.bukkit.Particle a0, org.bukkit.Location a1, int a2, double a3, double a4, double a5, double a6) {  }
    default void spawnParticle(org.bukkit.Particle a0, org.bukkit.Location a1, int a2, double a3, double a4, double a5, double a6, java.lang.Object a7) {  }
}
