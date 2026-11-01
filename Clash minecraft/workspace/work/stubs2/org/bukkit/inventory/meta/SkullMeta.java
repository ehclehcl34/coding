package org.bukkit.inventory.meta;

public interface SkullMeta extends org.bukkit.inventory.meta.ItemMeta {
    default boolean setOwningPlayer(org.bukkit.OfflinePlayer a0) { return false; }
}
