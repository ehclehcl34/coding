package kr.kjmn.clashmc;

import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.Set;
import java.util.UUID;
import org.bukkit.Bukkit;
import org.bukkit.entity.Player;

final class Room {
    final String code;
    UUID host;
    final Set<UUID> members = new LinkedHashSet<>();
    final Set<UUID> invited = new HashSet<>();
    GameManager match;
    int matchSeconds = 180;
    boolean openToAll;

    Room(String var1, UUID var2) {
        this.code = var1;
        this.host = var2;
        this.members.add(var2);
    }

    int online() {
        int var1 = 0;

        for (UUID var3 : this.members) {
            if (Bukkit.getPlayer(var3) != null) {
                var1++;
            }
        }

        return var1;
    }

    void broadcast(String var1) {
        for (UUID var3 : this.members) {
            Player var4 = Bukkit.getPlayer(var3);
            if (var4 != null) {
                boolean hide = Streamers.instance != null && Streamers.instance.live(var3);
                var4.sendMessage("§8[§b친선전" + (hide ? "" : " " + this.code) + "§8] §r" + var1);
            }
        }
    }
}
