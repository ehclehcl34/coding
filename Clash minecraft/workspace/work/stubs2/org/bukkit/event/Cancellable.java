package org.bukkit.event;

public interface Cancellable {
    default void setCancelled(boolean a0) {  }
}
