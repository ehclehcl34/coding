package kr.kjmn.clashmc;

import org.bukkit.Color;
import org.bukkit.Material;

public enum TeamColor {
    BLUE("파랑", "§9", Color.fromRGB(60, 90, 255), Material.BLUE_CONCRETE, 1),
    RED("빨강", "§c", Color.fromRGB(230, 50, 50), Material.RED_CONCRETE, -1);

    public final String ko;
    public final String cc;
    public final Color color;
    public final Material concrete;
    public final int dir;

    private TeamColor(String nullxx, String nullxxx, Color nullxxxx, Material nullxxxxx, int nullxxxxxx) {
        this.ko = nullxx;
        this.cc = nullxxx;
        this.color = nullxxxx;
        this.concrete = nullxxxxx;
        this.dir = nullxxxxxx;
    }

    public TeamColor other() {
        return this == BLUE ? RED : BLUE;
    }

    public String label() {
        return this.cc + this.ko;
    }
}
