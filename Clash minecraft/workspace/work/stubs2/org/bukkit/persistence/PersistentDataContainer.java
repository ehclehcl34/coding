package org.bukkit.persistence;

public interface PersistentDataContainer {
    default java.lang.Object get(org.bukkit.NamespacedKey a0, org.bukkit.persistence.PersistentDataType a1) { return null; }
    default boolean has(org.bukkit.NamespacedKey a0, org.bukkit.persistence.PersistentDataType a1) { return false; }
    default void set(org.bukkit.NamespacedKey a0, org.bukkit.persistence.PersistentDataType a1, java.lang.Object a2) {  }
}
