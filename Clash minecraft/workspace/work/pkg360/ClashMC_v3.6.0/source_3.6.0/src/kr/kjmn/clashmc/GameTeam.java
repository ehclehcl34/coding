package kr.kjmn.clashmc;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.LinkedList;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;
import org.bukkit.scoreboard.Scoreboard;

public final class GameTeam {
    public final TeamColor color;
    public final Set<UUID> members = ConcurrentHashMap.newKeySet();
    public UUID king;
    public final LinkedList<UUID> queue = new LinkedList<>();
    public double elixir;
    public final List<String> deck = new ArrayList<>();
    public final String[] hand = new String[4];
    public final Deque<String> pending = new ArrayDeque<>();
    public boolean deckReady;
    public int crowns;
    public Scoreboard board;
    public final List<String> boardLines = new ArrayList<>();
    public long alertUntil;
    public int alertNeed;
    public int handMask = -1;
    public String lastPlayed;
    public boolean surrenderShown;

    public GameTeam(TeamColor var1) {
        this.color = var1;
    }

    public Player kingPlayer() {
        return this.king == null ? null : Bukkit.getPlayer(this.king);
    }

    public UUID pollQueue() {
        while (!this.queue.isEmpty()) {
            UUID var1 = this.queue.pollFirst();
            if (Bukkit.getPlayer(var1) != null && this.members.contains(var1)) {
                return var1;
            }
        }

        return null;
    }

    public int queuePos(UUID var1) {
        int var2 = this.queue.indexOf(var1);
        return var2 < 0 ? -1 : var2 + 1;
    }
}
