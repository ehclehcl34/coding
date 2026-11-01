package org.bukkit.entity;

public interface BlockDisplay extends org.bukkit.entity.Display {
    default boolean addScoreboardTag(java.lang.String a0) { return false; }
    default org.bukkit.Location getLocation() { return null; }
    default org.bukkit.util.Transformation getTransformation() { return null; }
    default boolean isValid() { return false; }
    default void remove() {  }
    default void setBlock(org.bukkit.block.data.BlockData a0) {  }
    default void setBrightness(org.bukkit.entity.Display.Brightness a0) {  }
    default void setInterpolationDelay(int a0) {  }
    default void setInterpolationDuration(int a0) {  }
    default void setPersistent(boolean a0) {  }
    default void setTeleportDuration(int a0) {  }
    default void setTransformation(org.bukkit.util.Transformation a0) {  }
    default void setViewRange(float a0) {  }
    default boolean teleport(org.bukkit.Location a0) { return false; }
}
