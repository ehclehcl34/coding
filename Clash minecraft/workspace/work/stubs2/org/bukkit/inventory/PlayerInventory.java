package org.bukkit.inventory;

public interface PlayerInventory extends org.bukkit.inventory.Inventory {
    default org.bukkit.inventory.ItemStack getItem(int a0) { return null; }
    default void clear() {  }
    default int getHeldItemSlot() { return 0; }
    default org.bukkit.inventory.ItemStack getItemInMainHand() { return null; }
    default void setHeldItemSlot(int a0) {  }
    default void setHelmet(org.bukkit.inventory.ItemStack a0) {  }
    default void setItem(int a0, org.bukkit.inventory.ItemStack a1) {  }
}
