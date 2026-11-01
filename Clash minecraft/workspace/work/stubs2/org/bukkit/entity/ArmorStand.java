package org.bukkit.entity;

public interface ArmorStand extends org.bukkit.entity.LivingEntity {
    default boolean addScoreboardTag(java.lang.String a0) { return false; }
    default org.bukkit.inventory.EntityEquipment getEquipment() { return null; }
    default org.bukkit.Location getLocation() { return null; }
    default java.util.UUID getUniqueId() { return null; }
    default boolean isValid() { return false; }
    default void remove() {  }
    default void setBasePlate(boolean a0) {  }
    default void setCustomNameVisible(boolean a0) {  }
    default void setGravity(boolean a0) {  }
    default void setInvisible(boolean a0) {  }
    default void setInvulnerable(boolean a0) {  }
    default void setMarker(boolean a0) {  }
    default void setPersistent(boolean a0) {  }
    default void setSmall(boolean a0) {  }
    default boolean teleport(org.bukkit.Location a0) { return false; }
}
