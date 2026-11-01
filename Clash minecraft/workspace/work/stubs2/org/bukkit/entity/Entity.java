package org.bukkit.entity;

public interface Entity extends org.bukkit.command.CommandSender, org.bukkit.persistence.PersistentDataHolder {
    default org.bukkit.Location getLocation() { return null; }
    default java.util.Set getScoreboardTags() { return null; }
    default java.util.UUID getUniqueId() { return null; }
    default boolean isValid() { return false; }
    default void remove() {  }
    default void setCustomName(java.lang.String a0) {  }
    default void setCustomNameVisible(boolean a0) {  }
    default org.bukkit.util.Vector getVelocity() { return null; }
    default void setGlowing(boolean a0) {  }
    default void setVisibleByDefault(boolean a0) {  }
}
