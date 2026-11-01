package org.bukkit.plugin;

public interface PluginManager {
    default org.bukkit.plugin.Plugin getPlugin(java.lang.String a0) { return null; }
    default void registerEvents(org.bukkit.event.Listener a0, org.bukkit.plugin.Plugin a1) {  }
}
