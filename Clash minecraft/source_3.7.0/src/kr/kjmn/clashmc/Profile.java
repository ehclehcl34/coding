package kr.kjmn.clashmc;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.Map.Entry;
import org.bukkit.configuration.ConfigurationSection;
import org.bukkit.configuration.file.YamlConfiguration;

public final class Profile {
    public static final int DECK_SLOTS = 10;
    public final UUID id;
    public String name = "?";
    public int trophies;
    public int best;
    public int wins;
    public int losses;
    public int draws;
    public int rankedWins;
    public int rankedLosses;
    public int aiWins;
    public int friendlyWins;
    public int streak;
    public int kingGames;
    public boolean lastWasKing;
    public final List<List<String>> decks = new ArrayList<>();
    public int activeDeck;
    public final Set<String> skins = new LinkedHashSet<>();
    public final Map<String, String> selected = new HashMap<>();
    public boolean dirty;

    Profile(UUID var1) {
        this.id = var1;

        for (int var2 = 0; var2 < DECK_SLOTS; var2++) {
            this.decks.add(new ArrayList<>());
        }
    }

    public List<String> deck() {
        return this.decks.get(Math.max(0, Math.min(DECK_SLOTS - 1, this.activeDeck)));
    }

    public int games() {
        return this.wins + this.losses + this.draws;
    }

    public String winRate() {
        int var1 = this.wins + this.losses;
        return var1 == 0 ? "-" : Math.round(this.wins * 100.0 / var1) + "%";
    }

    void load(YamlConfiguration var1) {
        this.name = var1.getString("name", this.name);
        this.trophies = var1.getInt("trophies", 0);
        this.best = var1.getInt("best", this.trophies);
        this.wins = var1.getInt("wins");
        this.losses = var1.getInt("losses");
        this.draws = var1.getInt("draws");
        this.rankedWins = var1.getInt("ranked-wins");
        this.rankedLosses = var1.getInt("ranked-losses");
        this.aiWins = var1.getInt("ai-wins");
        this.friendlyWins = var1.getInt("friendly-wins");
        this.streak = var1.getInt("streak");
        this.kingGames = var1.getInt("king-games");
        this.lastWasKing = var1.getBoolean("last-king");
        this.activeDeck = var1.getInt("active-deck", 0);

        for (int var2 = 0; var2 < DECK_SLOTS; var2++) {
            this.decks.get(var2).clear();
            this.decks.get(var2).addAll(var1.getStringList("decks." + var2));
        }

        this.skins.clear();
        this.skins.addAll(var1.getStringList("skins"));
        this.selected.clear();
        ConfigurationSection var5 = var1.getConfigurationSection("selected");
        if (var5 != null) {
            for (String var4 : var5.getKeys(false)) {
                this.selected.put(var4, var5.getString(var4));
            }
        }
    }

    YamlConfiguration save() {
        YamlConfiguration var1 = new YamlConfiguration();
        var1.set("name", this.name);
        var1.set("trophies", this.trophies);
        var1.set("best", this.best);
        var1.set("wins", this.wins);
        var1.set("losses", this.losses);
        var1.set("draws", this.draws);
        var1.set("ranked-wins", this.rankedWins);
        var1.set("ranked-losses", this.rankedLosses);
        var1.set("ai-wins", this.aiWins);
        var1.set("friendly-wins", this.friendlyWins);
        var1.set("streak", this.streak);
        var1.set("king-games", this.kingGames);
        var1.set("last-king", this.lastWasKing);
        var1.set("active-deck", this.activeDeck);

        for (int var2 = 0; var2 < DECK_SLOTS; var2++) {
            var1.set("decks." + var2, new ArrayList<>(this.decks.get(var2)));
        }

        var1.set("skins", new ArrayList<>(this.skins));

        for (Entry var3 : this.selected.entrySet()) {
            var1.set("selected." + (String)var3.getKey(), var3.getValue());
        }

        return var1;
    }
}
