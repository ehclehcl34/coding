package org.bukkit.configuration;

public interface ConfigurationSection {
    default boolean isSet(java.lang.String a0) { return false; }
    default java.lang.Object get(java.lang.String a0) { return null; }
    default void set(java.lang.String a0, java.lang.Object a1) {  }
    default boolean getBoolean(java.lang.String a0, boolean a1) { return false; }
    default org.bukkit.configuration.ConfigurationSection getConfigurationSection(java.lang.String a0) { return null; }
    default double getDouble(java.lang.String a0, double a1) { return 0; }
    default int getInt(java.lang.String a0) { return 0; }
    default int getInt(java.lang.String a0, int a1) { return 0; }
    default java.util.Set<java.lang.String> getKeys(boolean a0) { return null; }
    default java.util.List<?> getList(java.lang.String a0, java.util.List<?> a1) { return null; }
    default java.lang.String getString(java.lang.String a0) { return null; }
    default java.lang.String getString(java.lang.String a0, java.lang.String a1) { return null; }
}
