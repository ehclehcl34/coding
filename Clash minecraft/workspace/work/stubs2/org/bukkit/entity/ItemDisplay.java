package org.bukkit.entity;

public interface ItemDisplay extends org.bukkit.entity.Display {
    default boolean addScoreboardTag(java.lang.String a0) { return false; }
    default void setBillboard(org.bukkit.entity.Display.Billboard a0) {  }
    default void setBrightness(org.bukkit.entity.Display.Brightness a0) {  }
    default void setItemStack(org.bukkit.inventory.ItemStack a0) {  }
    default void setTransformation(org.bukkit.util.Transformation a0) {  }
}
