package org.bukkit.inventory.meta;

public interface ItemMeta extends org.bukkit.persistence.PersistentDataHolder {
    default java.util.List getLore() { return null; }
    default org.bukkit.persistence.PersistentDataContainer getPersistentDataContainer() { return null; }
    default void setDisplayName(java.lang.String a0) {  }
    default void setEnchantmentGlintOverride(java.lang.Boolean a0) {  }
    default void setItemModel(org.bukkit.NamespacedKey a0) {  }
    default void setLore(java.util.List a0) {  }
}
