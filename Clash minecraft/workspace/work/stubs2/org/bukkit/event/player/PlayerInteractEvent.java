package org.bukkit.event.player;

public class PlayerInteractEvent {
    protected PlayerInteractEvent() {}
    public org.bukkit.event.block.Action getAction() { return null; }
    public org.bukkit.inventory.EquipmentSlot getHand() { return null; }
    public org.bukkit.inventory.ItemStack getItem() { return null; }
    public org.bukkit.entity.Player getPlayer() { return null; }
    public void setCancelled(boolean a0) {  }
}
