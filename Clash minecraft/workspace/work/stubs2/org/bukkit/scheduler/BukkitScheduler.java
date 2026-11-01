package org.bukkit.scheduler;

public interface BukkitScheduler {
    default org.bukkit.scheduler.BukkitTask runTaskLater(org.bukkit.plugin.Plugin a0, java.lang.Runnable a1, long a2) { return null; }
    default org.bukkit.scheduler.BukkitTask runTaskTimer(org.bukkit.plugin.Plugin a0, java.lang.Runnable a1, long a2, long a3) { return null; }
}
