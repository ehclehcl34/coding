package org.bukkit.event.inventory;

public class InventoryClickEvent extends org.bukkit.event.inventory.InventoryInteractEvent {
    protected InventoryClickEvent() {}
    public org.bukkit.inventory.Inventory getClickedInventory() { return null; }
    public org.bukkit.inventory.Inventory getInventory() { return null; }
    public int getRawSlot() { return 0; }
    public org.bukkit.entity.HumanEntity getWhoClicked() { return null; }
    public boolean isShiftClick() { return false; }
    public void setCancelled(boolean a0) {  }
}
