package org.bukkit.scoreboard;

public interface Scoreboard {
    default org.bukkit.scoreboard.Objective getObjective(java.lang.String a0) { return null; }
    default org.bukkit.scoreboard.Objective registerNewObjective(java.lang.String a0, java.lang.String a1, java.lang.String a2) { return null; }
    default void resetScores(java.lang.String a0) {  }
}
