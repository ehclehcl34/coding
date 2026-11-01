package org.bukkit.entity;

public interface Interaction extends org.bukkit.entity.Entity {
    default boolean addScoreboardTag(java.lang.String a0) { return false; }
    default java.util.UUID getUniqueId() { return null; }
    default void setInteractionHeight(float a0) {  }
    default void setInteractionWidth(float a0) {  }
    default void setPersistent(boolean a0) {  }
}
