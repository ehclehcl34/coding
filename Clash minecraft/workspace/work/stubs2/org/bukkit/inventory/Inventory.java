package org.bukkit.inventory;

public interface Inventory {
    default void clear() {  }
    default org.bukkit.inventory.InventoryHolder getHolder() { return null; }
    default int getSize() { return 0; }
    default void setItem(int a0, org.bukkit.inventory.ItemStack a1) {  }
}
