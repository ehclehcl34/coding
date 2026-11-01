package org.bukkit.entity;

public interface Display extends org.bukkit.entity.Entity {
    default boolean isValid() { return false; }
    default void remove() {  }
    default void setInterpolationDelay(int a0) {  }
    default void setInterpolationDuration(int a0) {  }
    default void setPersistent(boolean a0) {  }
    default void setTeleportDuration(int a0) {  }
    default void setViewRange(float a0) {  }
    default boolean teleport(org.bukkit.Location a0) { return false; }
    default void setGlowColorOverride(org.bukkit.Color a0) {  }
    public enum Billboard {
        CENTER, FIXED;
    }
    public static class Brightness {
        public Brightness(int a0, int a1) {}
        protected Brightness() {}
    }
}
