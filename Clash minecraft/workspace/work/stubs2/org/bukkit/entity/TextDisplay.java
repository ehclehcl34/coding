package org.bukkit.entity;

public interface TextDisplay extends org.bukkit.entity.Display {
    default java.lang.String getText() { return null; }
    default boolean addScoreboardTag(java.lang.String a0) { return false; }
    default boolean isValid() { return false; }
    default void remove() {  }
    default void setBackgroundColor(org.bukkit.Color a0) {  }
    default void setBillboard(org.bukkit.entity.Display.Billboard a0) {  }
    default void setBrightness(org.bukkit.entity.Display.Brightness a0) {  }
    default void setLineWidth(int a0) {  }
    default void setPersistent(boolean a0) {  }
    default void setSeeThrough(boolean a0) {  }
    default void setShadowed(boolean a0) {  }
    default void setTeleportDuration(int a0) {  }
    default void setText(java.lang.String a0) {  }
    default void setTextOpacity(byte a0) {  }
    default void setTransformation(org.bukkit.util.Transformation a0) {  }
    default void setViewRange(float a0) {  }
    default boolean teleport(org.bukkit.Location a0) { return false; }
}
