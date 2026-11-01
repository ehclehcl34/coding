package org.bukkit.scoreboard;

public interface ScoreboardManager {
    default org.bukkit.scoreboard.Scoreboard getNewScoreboard() { return null; }
}
