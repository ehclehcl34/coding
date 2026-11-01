package org.bukkit.scoreboard;

public interface Objective {
    default org.bukkit.scoreboard.Score getScore(java.lang.String a0) { return null; }
    default void setDisplaySlot(org.bukkit.scoreboard.DisplaySlot a0) {  }
}
