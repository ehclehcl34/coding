package org.bukkit.event.entity;

public class EntityDamageByEntityEvent extends org.bukkit.event.entity.EntityDamageEvent {
    protected EntityDamageByEntityEvent() {}
    public org.bukkit.entity.Entity getDamager() { return null; }
    public org.bukkit.entity.Entity getEntity() { return null; }
    public void setCancelled(boolean a0) {  }
}
