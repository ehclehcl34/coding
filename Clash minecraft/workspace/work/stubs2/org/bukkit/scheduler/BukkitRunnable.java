package org.bukkit.scheduler;

public abstract class BukkitRunnable implements java.lang.Runnable {
    public BukkitRunnable() {}
    public void cancel() {  }
    public org.bukkit.scheduler.BukkitTask runTaskLater(org.bukkit.plugin.Plugin a0, long a1) { return null; }
    public org.bukkit.scheduler.BukkitTask runTaskTimer(org.bukkit.plugin.Plugin a0, long a1, long a2) { return null; }
    public abstract void run();
}
