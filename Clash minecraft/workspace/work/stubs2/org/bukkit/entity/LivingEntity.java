package org.bukkit.entity;

public interface LivingEntity extends org.bukkit.entity.Entity, org.bukkit.entity.Damageable, org.bukkit.attribute.Attributable {
    default boolean addPotionEffect(org.bukkit.potion.PotionEffect a0) { return false; }
    default boolean removePotionEffect(org.bukkit.potion.PotionEffectType a0) { return false; }
    default boolean addScoreboardTag(java.lang.String a0) { return false; }
    default org.bukkit.attribute.AttributeInstance getAttribute(org.bukkit.attribute.Attribute a0) { return null; }
    default org.bukkit.inventory.EntityEquipment getEquipment() { return null; }
    default double getHealth() { return 0; }
    default double getHeight() { return 0; }
    default org.bukkit.Location getLocation() { return null; }
    default java.util.List<org.bukkit.entity.Entity> getPassengers() { return null; }
    default java.util.UUID getUniqueId() { return null; }
    default boolean isValid() { return false; }
    default boolean leaveVehicle() { return false; }
    default void playHurtAnimation(float a0) {  }
    default void remove() {  }
    default void setAI(boolean a0) {  }
    default void setCanPickupItems(boolean a0) {  }
    default void setCollidable(boolean a0) {  }
    default void setCustomNameVisible(boolean a0) {  }
    default void setGravity(boolean a0) {  }
    default void setHealth(double a0) {  }
    default void setInvisible(boolean a0) {  }
    default void setPersistent(boolean a0) {  }
    default void setRemoveWhenFarAway(boolean a0) {  }
    default void setSilent(boolean a0) {  }
    default boolean teleport(org.bukkit.Location a0) { return false; }
}
