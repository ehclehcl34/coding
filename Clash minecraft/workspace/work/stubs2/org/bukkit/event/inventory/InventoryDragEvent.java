package org.bukkit.event.inventory;

public class InventoryDragEvent extends org.bukkit.event.inventory.InventoryInteractEvent {
    protected InventoryDragEvent() {}
    public org.bukkit.inventory.Inventory getInventory() { return null; }
    public org.bukkit.entity.HumanEntity getWhoClicked() { return null; }
    public void setCancelled(boolean a0) {  }
}
