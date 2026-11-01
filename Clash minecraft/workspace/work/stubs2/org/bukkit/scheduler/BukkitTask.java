package org.bukkit.scheduler;

public interface BukkitTask {
    default void cancel() {  }
    default boolean isCancelled() { return false; }
}
