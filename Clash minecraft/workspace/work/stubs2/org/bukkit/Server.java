package org.bukkit;

public interface Server {
    default org.bukkit.plugin.PluginManager getPluginManager() { return null; }
}
