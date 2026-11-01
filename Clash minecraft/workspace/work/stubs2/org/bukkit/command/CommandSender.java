package org.bukkit.command;

public interface CommandSender {
    default boolean hasPermission(java.lang.String a0) { return false; }
    default void sendMessage(java.lang.String a0) {  }
}
