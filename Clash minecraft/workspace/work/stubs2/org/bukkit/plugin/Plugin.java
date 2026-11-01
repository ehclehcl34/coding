package org.bukkit.plugin;

public interface Plugin extends org.bukkit.command.TabExecutor {
    default boolean isEnabled() { return false; }
}
