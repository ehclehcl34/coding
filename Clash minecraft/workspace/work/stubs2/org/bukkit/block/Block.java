package org.bukkit.block;

public interface Block {
    default org.bukkit.Location getLocation() { return null; }
    default int getX() { return 0; }
    default int getZ() { return 0; }
    default void setType(org.bukkit.Material a0) {  }
}
