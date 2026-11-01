package org.bukkit.boss;

public interface BossBar {
    default void addPlayer(org.bukkit.entity.Player a0) {  }
    default void removeAll() {  }
    default void removePlayer(org.bukkit.entity.Player a0) {  }
    default void setColor(org.bukkit.boss.BarColor a0) {  }
    default void setProgress(double a0) {  }
    default void setTitle(java.lang.String a0) {  }
}
