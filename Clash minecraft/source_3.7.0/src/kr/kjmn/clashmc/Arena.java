package kr.kjmn.clashmc;

import org.bukkit.Location;
import org.bukkit.World;

public final class Arena {
    public static final int TILE = 3;
    public static final int TW = 18;
    public static final int TL = 32;
    public static final int HX = 27;
    public static final int HZ = 48;
    public final World world;
    public final int px;
    public final int py;
    public final int pz;
    public final int minX;
    public final int minZ;
    public final int floorY;
    public static final int BALCONY_Y = 16;

    public Arena(World var1, int var2, int var3, int var4) {
        this.world = var1;
        this.px = var2;
        this.py = var3;
        this.pz = var4;
        this.minX = var2 - 27;
        this.minZ = var4 - 48;
        this.floorY = var3 - 1;
    }

    public int tileX(double var1) {
        return (int)Math.floor((var1 - this.minX) / 3.0);
    }

    public int tileZ(double var1) {
        return (int)Math.floor((var1 - this.minZ) / 3.0);
    }

    public boolean inField(int var1, int var2) {
        return var1 >= 0 && var1 < 18 && var2 >= 0 && var2 < 32;
    }

    public boolean inField(Location var1) {
        return this.inField(this.tileX(var1.getX()), this.tileZ(var1.getZ()));
    }

    public boolean isRiverRow(int var1) {
        return var1 == 15 || var1 == 16;
    }

    public boolean isBridgeCol(int var1) {
        return var1 >= 2 && var1 <= 4 || var1 >= 13 && var1 <= 15;
    }

    public TeamColor sideOf(int var1) {
        return var1 <= 14 ? TeamColor.BLUE : (var1 >= 17 ? TeamColor.RED : null);
    }

    public Location tileCenter(int var1, int var2) {
        return new Location(this.world, this.minX + var1 * 3 + 1.5, this.floorY + 1, this.minZ + var2 * 3 + 1.5);
    }

    public double centerX() {
        return this.minX + 27;
    }

    public double riverMinZ() {
        return this.minZ + 45.0;
    }

    public double riverMaxZ() {
        return this.minZ + 51.0;
    }

    public double bridgeX(boolean var1) {
        return this.minX + (var1 ? 3.5 : 14.5) * 3.0;
    }

    /** 다리 반폭 (블록). 상판 7블록 (흙길 가운데 맞춤) + 양쪽 난간 */
    public double bridgeHalf() {
        return 3.5;
    }

    /** x 좌표가 다리 폭 안인지 (블록 단위) */
    public boolean onBridge(double var1) {
        double var3 = this.bridgeHalf();
        return Math.abs(var1 - this.bridgeX(true)) <= var3 || Math.abs(var1 - this.bridgeX(false)) <= var3;
    }

    public int princessTx(boolean var1) {
        return var1 ? 2 : 13;
    }

    public int princessTz(TeamColor var1) {
        return var1 == TeamColor.BLUE ? 5 : 24;
    }

    public int kingTx() {
        return 7;
    }

    public int kingTz(TeamColor var1) {
        return var1 == TeamColor.BLUE ? 1 : 27;
    }

    public Location princessCenter(TeamColor var1, boolean var2) {
        return new Location(this.world, this.minX + this.princessTx(var2) * 3 + 4.5, this.floorY + 1, this.minZ + this.princessTz(var1) * 3 + 4.5);
    }

    public Location kingCenter(TeamColor var1) {
        return new Location(this.world, this.minX + this.kingTx() * 3 + 6.0, this.floorY + 1, this.minZ + this.kingTz(var1) * 3 + 6.0);
    }

    public Location balcony(TeamColor var1) {
        Location var2 = new Location(this.world, this.px + 0.0, this.py + 16, var1 == TeamColor.BLUE ? this.pz - 57.0 : this.pz + 57.0);
        var2.setYaw(var1 == TeamColor.BLUE ? 0.0F : 180.0F);
        var2.setPitch(35.0F);
        return var2;
    }

    public boolean inBalcony(TeamColor var1, Location var2) {
        double var3 = var2.getX() - this.px;
        double var5 = var2.getZ() - this.pz;
        double var7 = var2.getY() - this.py;
        boolean var9 = var1 == TeamColor.BLUE ? var5 >= -60.0 && var5 < -54.0 : var5 >= 54.0 && var5 < 60.0;
        return var3 >= -7.0 && var3 < 7.0 && var9 && var7 >= 14.0 && var7 <= 22.0;
    }

    public Location spectate(TeamColor var1) {
        Location var2 = new Location(this.world, this.px + 0.5, this.py + 30, var1 == TeamColor.BLUE ? this.pz - 24.0 : this.pz + 24.0);
        var2.setYaw(var1 == TeamColor.BLUE ? 0.0F : 180.0F);
        var2.setPitch(45.0F);
        return var2;
    }

    public Location overview() {
        Location var1 = new Location(this.world, this.px + 0.5, this.py + 44, this.pz + 0.5);
        var1.setPitch(90.0F);
        return var1;
    }

    public boolean tileInRect(int var1, int var2, int var3, int var4, int var5) {
        return var1 >= var3 && var1 < var3 + var5 && var2 >= var4 && var2 < var4 + var5;
    }

    public Location clampKing(Location var1) {
        Location var2 = var1.clone();
        double var3 = this.minX - 8;
        double var5 = this.minX + 54 + 8;
        double var7 = this.minZ - 16;
        double var9 = this.minZ + 96 + 16;
        var2.setX(Math.max(var3, Math.min(var5, var2.getX())));
        var2.setZ(Math.max(var7, Math.min(var9, var2.getZ())));
        var2.setY(Math.max(this.floorY + 3.0, Math.min(this.floorY + 40.0, var2.getY())));
        return var2;
    }
}
