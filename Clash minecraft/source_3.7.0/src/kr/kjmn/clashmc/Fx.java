package kr.kjmn.clashmc;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Random;
import java.util.Set;
import java.util.function.Consumer;
import java.util.function.Supplier;
import org.bukkit.Color;
import org.bukkit.Location;
import org.bukkit.Material;
import org.bukkit.Particle;
import org.bukkit.World;
import org.bukkit.Particle.DustOptions;
import org.bukkit.block.data.BlockData;
import org.bukkit.entity.ArmorStand;
import org.bukkit.entity.BlockDisplay;
import org.bukkit.entity.Display;
import org.bukkit.entity.Entity;
import org.bukkit.entity.ItemDisplay;
import org.bukkit.entity.TextDisplay;
import org.bukkit.entity.Display.Billboard;
import org.bukkit.entity.Display.Brightness;
import org.bukkit.inventory.ItemStack;
import org.bukkit.scheduler.BukkitRunnable;
import org.bukkit.util.Transformation;
import org.bukkit.util.Vector;
import org.joml.Quaternionf;
import org.joml.Vector3f;

final class Fx {
    private final GameManager gm;
    private final Set<Entity> spawned = new HashSet<>();
    private final List<BukkitRunnable> tasks = new ArrayList<>();

    Fx(GameManager var1) {
        this.gm = var1;
    }

    private World w() {
        return this.gm.arena.world;
    }

    private boolean playing() {
        return this.gm.phase == GameManager.Phase.PLAYING;
    }

    void shoot(Fx.Shot var1, Location var2, Supplier<Location> var3, Consumer<Location> var4) {
        this.shoot(var1, var2, var3, var4, null, null);
    }

    void shoot(final Fx.Shot var1, final Location var2, final Supplier<Location> var3, final Consumer<Location> var4, String var5, Color var6) {
        Location var7 = (Location)var3.get();
        if (var7 == null) {
            var4.accept(var2.clone());
        } else {
            final double var8 = Math.max(0.5, var2.distance(var7));
            final int var10 = Math.max(2, (int)Math.round(var8 / var1.speed * 20.0));
            final ArmorStand var11 = null;
            if (var5 != null && !var5.isEmpty() && this.gm.models.enabled()) {
                var11 = (ArmorStand)this.w().spawn(var2.clone(), ArmorStand.class);
                var11.addScoreboardTag("clashmc");
                var11.setInvisible(true);
                var11.setGravity(false);
                var11.setMarker(true);
                var11.setInvulnerable(true);
                var11.setPersistent(false);
                if (this.gm.models.apply(var11, var5, true, var6)) {
                    this.spawned.add(var11);
                } else {
                    var11.remove();
                    var11 = null;
                }
            }

            final Display var13 = var11 != null ? null : this.body(var1, var2);
            World var14 = this.w();
            this.muzzle(var1, var2);
            BukkitRunnable var15 = new BukkitRunnable() {
                int i = 0;
                Location last = var2.clone();
                float spin = 0.0F;

                public void run() {
                    if (!Fx.this.playing()) {
                        this.end();
                    } else {
                        this.i++;
                        Location var1x = (Location)var3.get();
                        if (var1x == null) {
                            var1x = this.last;
                        }

                        double var2x = Math.min(1.0, (double)this.i / var10);
                        Vector var4x = var1x.toVector().subtract(var2.toVector()).multiply(var2x);
                        Location var5x = var2.clone().add(var4x).add(0.0, Math.sin(Math.PI * var2x) * var8 * var1.arc, 0.0);
                        Vector var6x = var5x.toVector().subtract(this.last.toVector());
                        if (var6x.lengthSquared() > 1.0E-6) {
                            var5x.setDirection(var6x);
                        }

                        if (var11 != null && var11.isValid()) {
                            Location var7x = var5x.clone().add(0.0, -0.55, 0.0);
                            var7x.setPitch(0.0F);
                            var11.teleport(var7x);
                        }

                        if (var13 != null && var13.isValid()) {
                            var13.teleport(var5x);
                            if (var1 == Fx.Shot.BARREL || var1 == Fx.Shot.SNOWBALL || var1 == Fx.Shot.BOMB) {
                                this.spin = this.spin + (var1 == Fx.Shot.BOMB ? 0.35F : 0.55F);
                                Fx.spinBlock((BlockDisplay)var13, var1 == Fx.Shot.BARREL ? 1.1F : (var1 == Fx.Shot.SNOWBALL ? 1.5F : 0.42F), this.spin);
                            }
                        }

                        Fx.this.trail(var1, var5x);
                        if (var1 == Fx.Shot.BARREL || var1 == Fx.Shot.BIG_FIREBALL || var1 == Fx.Shot.SNOWBALL || var1 == Fx.Shot.ROCKET) {
                            Fx.this.marker(var1x, var1 == Fx.Shot.BARREL ? 1.6 : (var1 == Fx.Shot.SNOWBALL ? 2.2 : 2.4), 1.0 - var2x);
                        }

                        this.last = var5x;
                        if (this.i >= var10) {
                            this.end();
                            var4.accept(var1x.clone());
                        }
                    }
                }

                void end() {
                    this.cancel();
                    Fx.this.tasks.remove(this);
                    if (var13 != null) {
                        Fx.this.spawned.remove(var13);
                        var13.remove();
                    }

                    if (var11 != null) {
                        Fx.this.gm.models.remove(var11);
                        Fx.this.spawned.remove(var11);
                        var11.remove();
                    }
                }
            };
            this.tasks.add(var15);
            var15.runTaskTimer(this.gm.plugin, 0L, 1L);
            if (var1 == Fx.Shot.BARREL) {
                var14.playSound(var2, "entity.witch.throw", 1.0F, 0.6F);
            }

            if (var1 == Fx.Shot.BIG_FIREBALL) {
                var14.playSound(var2, "entity.blaze.shoot", 1.0F, 0.6F);
            }
        }
    }

    private Display body(Fx.Shot var1, Location var2) {
        World var3 = this.w();
        switch (var1) {
            case ARROW:
            case BOLT:
                return this.block(
                    var2,
                    Material.STRIPPED_OAK_LOG.createBlockData(),
                    var1 == Fx.Shot.BOLT ? new Vector3f(0.09F, 0.09F, 1.3F) : new Vector3f(0.06F, 0.06F, 0.8F)
                );
            case BULLET:
                return this.block(var2, Material.IRON_BLOCK.createBlockData(), new Vector3f(0.09F, 0.09F, 0.3F));
            case FIREBALL:
            case BIG_FIREBALL:
                ItemDisplay var8 = (ItemDisplay)var3.spawn(var2, ItemDisplay.class);
                var8.addScoreboardTag("clashmc");
                var8.setItemStack(new ItemStack(Material.FIRE_CHARGE));
                var8.setBillboard(Billboard.CENTER);
                float var5 = var1 == Fx.Shot.BIG_FIREBALL ? 2.4F : 0.9F;
                var8.setTransformation(new Transformation(new Vector3f(), new Quaternionf(), new Vector3f(var5, var5, var5), new Quaternionf()));
                var8.setBrightness(new Brightness(15, 15));
                this.common(var8);
                return var8;
            case CANNONBALL:
                return this.block(var2, Material.COAL_BLOCK.createBlockData(), new Vector3f(0.42F, 0.42F, 0.42F));
            case GOOP:
                return this.block(var2, Material.AMETHYST_BLOCK.createBlockData(), new Vector3f(0.28F, 0.28F, 0.28F));
            case BARREL:
                BlockDisplay var7 = (BlockDisplay)var3.spawn(var2, BlockDisplay.class);
                var7.addScoreboardTag("clashmc");
                var7.setBlock(Material.BARREL.createBlockData());
                this.common(var7);
                spinBlock(var7, 1.1F, 0.0F);
                return var7;
            case SPEAR:
                return this.block(var2, Material.STRIPPED_SPRUCE_LOG.createBlockData(), new Vector3f(0.07F, 0.07F, 1.3F));
            case BOMB:
                BlockDisplay var6 = (BlockDisplay)var3.spawn(var2, BlockDisplay.class);
                var6.addScoreboardTag("clashmc");
                var6.setBlock(Material.COAL_BLOCK.createBlockData());
                this.common(var6);
                spinBlock(var6, 0.42F, 0.0F);
                return var6;
            case SNOWBALL:
                BlockDisplay var4 = (BlockDisplay)var3.spawn(var2, BlockDisplay.class);
                var4.addScoreboardTag("clashmc");
                var4.setBlock(Material.SNOW_BLOCK.createBlockData());
                var4.setBrightness(new Brightness(15, 15));
                this.common(var4);
                spinBlock(var4, 1.5F, 0.0F);
                return var4;
            case ROCKET:
                return this.block(var2, Material.RED_CONCRETE.createBlockData(), new Vector3f(0.45F, 0.45F, 1.6F));
            default:
                return null;
        }
    }

    private BlockDisplay block(Location var1, BlockData var2, Vector3f var3) {
        BlockDisplay var4 = (BlockDisplay)this.w().spawn(var1, BlockDisplay.class);
        var4.addScoreboardTag("clashmc");
        var4.setBlock(var2);
        var4.setTransformation(new Transformation(new Vector3f(-var3.x / 2.0F, -var3.y / 2.0F, -var3.z / 2.0F), new Quaternionf(), var3, new Quaternionf()));
        var4.setBrightness(new Brightness(15, 15));
        this.common(var4);
        return var4;
    }

    private void common(Display var1) {
        var1.setPersistent(false);
        var1.setTeleportDuration(1);
        var1.setInterpolationDelay(0);
        var1.setInterpolationDuration(1);
        var1.setViewRange(1.5F);
        this.spawned.add(var1);
    }

    private static void spinBlock(BlockDisplay var0, float var1, float var2) {
        float var3 = var1 / 2.0F;
        float var4 = (float)(var3 * Math.cos(var2) - var3 * Math.sin(var2));
        float var5 = (float)(var3 * Math.sin(var2) + var3 * Math.cos(var2));
        var0.setInterpolationDelay(0);
        var0.setInterpolationDuration(1);
        var0.setTransformation(
            new Transformation(new Vector3f(-var3, -var4, -var5), new Quaternionf().rotateX(var2), new Vector3f(var1, var1, var1), new Quaternionf())
        );
    }

    private void muzzle(Fx.Shot var1, Location var2) {
        World var3 = this.w();
        switch (var1) {
            case ARROW:
                var3.playSound(var2, "entity.arrow.shoot", 0.7F, 1.2F);
                break;
            case BOLT:
                var3.playSound(var2, "item.crossbow.shoot", 0.8F, 1.1F);
                break;
            case BULLET:
                var3.spawnParticle(Particle.FLASH, var2, 1, 0.0, 0.0, 0.0, 0.0);
                var3.spawnParticle(Particle.LARGE_SMOKE, var2, 4, 0.1, 0.1, 0.1, 0.02);
                var3.playSound(var2, "entity.generic.explode", 0.35F, 1.9F);
                var3.playSound(var2, "item.crossbow.shoot", 0.8F, 0.7F);
                break;
            case FIREBALL:
                var3.playSound(var2, "entity.blaze.shoot", 0.6F, 1.3F);
                break;
            case CANNONBALL:
                var3.spawnParticle(Particle.EXPLOSION, var2, 1, 0.0, 0.0, 0.0, 0.0);
                var3.spawnParticle(Particle.LARGE_SMOKE, var2, 8, 0.2, 0.2, 0.2, 0.03);
                var3.playSound(var2, "entity.generic.explode", 0.6F, 1.5F);
                break;
            case GOOP:
                var3.playSound(var2, "entity.slime.squish_small", 0.8F, 1.4F);
            case BIG_FIREBALL:
            case BARREL:
            default:
                break;
            case SPEAR:
                var3.playSound(var2, "entity.arrow.shoot", 0.8F, 0.7F);
                break;
            case BOMB:
                var3.playSound(var2, "entity.tnt.primed", 0.6F, 1.6F);
                break;
            case SNOWBALL:
                var3.playSound(var2, "entity.snowball.throw", 1.0F, 0.5F);
                break;
            case ROCKET:
                var3.playSound(var2, "entity.firework_rocket.launch", 1.0F, 0.5F);
                var3.playSound(var2, "entity.blaze.shoot", 0.8F, 0.5F);
        }
    }

    private void trail(Fx.Shot var1, Location var2) {
        World var3 = this.w();
        switch (var1) {
            case ARROW:
            case BOLT:
                var3.spawnParticle(Particle.CRIT, var2, 1, 0.0, 0.0, 0.0, 0.0);
                break;
            case BULLET:
                var3.spawnParticle(Particle.SMOKE, var2, 1, 0.0, 0.0, 0.0, 0.0);
                break;
            case FIREBALL:
                var3.spawnParticle(Particle.FLAME, var2, 3, 0.08, 0.08, 0.08, 0.01);
                break;
            case CANNONBALL:
                var3.spawnParticle(Particle.SMOKE, var2, 2, 0.05, 0.05, 0.05, 0.005);
                break;
            case GOOP:
                var3.spawnParticle(Particle.DUST, var2, 2, 0.05, 0.05, 0.05, 0.0, new DustOptions(Color.fromRGB(150, 70, 220), 1.0F));
                break;
            case BIG_FIREBALL:
                var3.spawnParticle(Particle.FLAME, var2, 10, 0.4, 0.4, 0.4, 0.02);
                var3.spawnParticle(Particle.LARGE_SMOKE, var2, 2, 0.3, 0.3, 0.3, 0.01);
                var3.spawnParticle(Particle.LAVA, var2, 1, 0.2, 0.2, 0.2, 0.0);
                break;
            case BARREL:
                var3.spawnParticle(Particle.CLOUD, var2, 1, 0.1, 0.1, 0.1, 0.01);
                break;
            case SPEAR:
                var3.spawnParticle(Particle.CRIT, var2, 1, 0.0, 0.0, 0.0, 0.0);
                break;
            case BOMB:
                var3.spawnParticle(Particle.SMOKE, var2.clone().add(0.0, 0.3, 0.0), 1, 0.0, 0.0, 0.0, 0.0);
                var3.spawnParticle(Particle.FLAME, var2.clone().add(0.0, 0.3, 0.0), 1, 0.0, 0.0, 0.0, 0.0);
                break;
            case SNOWBALL:
                var3.spawnParticle(Particle.SNOWFLAKE, var2, 6, 0.5, 0.5, 0.5, 0.01);
                break;
            case ROCKET:
                var3.spawnParticle(Particle.FLAME, var2, 6, 0.12, 0.12, 0.12, 0.02);
                var3.spawnParticle(Particle.LARGE_SMOKE, var2, 3, 0.15, 0.15, 0.15, 0.01);
        }
    }

    void marker(Location var1, double var2, double var4) {
        DustOptions var6 = new DustOptions(Color.fromRGB(30, 30, 30), 1.3F);
        double var7 = var2 * (0.4 + 0.6 * Math.max(0.0, var4));
        byte var9 = 14;

        for (int var10 = 0; var10 < var9; var10++) {
            double var11 = (Math.PI * 2) * var10 / var9 + var4 * 3.0;
            this.w()
                .spawnParticle(
                    Particle.DUST,
                    var1.getX() + Math.cos(var11) * var7,
                    this.gm.arena.floorY + 1.08,
                    var1.getZ() + Math.sin(var11) * var7,
                    1,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    var6
                );
        }
    }

    void impact(Fx.Shot var1, Location var2, double var3) {
        World var5 = this.w();
        switch (var1) {
            case ARROW:
            case BOLT:
                var5.playSound(var2, "entity.arrow.hit", 0.7F, 1.1F);
                var5.spawnParticle(Particle.CRIT, var2, 6, 0.2, 0.2, 0.2, 0.2);
                break;
            case BULLET:
                var5.playSound(var2, "entity.player.attack.crit", 0.7F, 1.4F);
                var5.spawnParticle(Particle.CRIT, var2, 8, 0.15, 0.15, 0.15, 0.3);
                var5.spawnParticle(Particle.SMOKE, var2, 3, 0.1, 0.1, 0.1, 0.01);
                break;
            case FIREBALL:
                var5.playSound(var2, "entity.generic.burn", 0.7F, 1.2F);
                var5.spawnParticle(Particle.FLAME, var2, 25, var3 / 2.0, 0.3, var3 / 2.0, 0.03);
                var5.spawnParticle(Particle.LARGE_SMOKE, var2, 4, var3 / 3.0, 0.2, var3 / 3.0, 0.01);
                this.ring(var2, var3, Color.fromRGB(255, 130, 30));
                break;
            case CANNONBALL:
                var5.playSound(var2, "entity.generic.explode", 0.5F, 1.3F);
                var5.spawnParticle(Particle.EXPLOSION, var2, 1, 0.0, 0.0, 0.0, 0.0);
                var5.spawnParticle(Particle.BLOCK, var2, 20, 0.4, 0.2, 0.4, 0.0, Material.DIRT.createBlockData());
                break;
            case GOOP:
                var5.playSound(var2, "entity.slime.squish", 0.6F, 1.6F);
                var5.spawnParticle(Particle.DUST, var2, 12, 0.25, 0.25, 0.25, 0.0, new DustOptions(Color.fromRGB(150, 70, 220), 1.2F));
                break;
            case BIG_FIREBALL:
                var5.playSound(var2, "entity.generic.explode", 1.2F, 0.9F);
                var5.playSound(var2, "entity.blaze.hurt", 0.6F, 0.6F);
                var5.spawnParticle(Particle.EXPLOSION_EMITTER, var2.clone().add(0.0, 0.5, 0.0), 1);
                var5.spawnParticle(Particle.FLAME, var2, 120, var3 / 2.0, 0.5, var3 / 2.0, 0.08);
                var5.spawnParticle(Particle.LAVA, var2, 15, var3 / 3.0, 0.2, var3 / 3.0, 0.0);
                this.ring(var2, var3, Color.fromRGB(255, 110, 20));
                break;
            case BARREL:
                var5.playSound(var2, "entity.zombie.break_wooden_door", 0.9F, 1.3F);
                var5.playSound(var2, "block.barrel.open", 1.0F, 0.7F);
                var5.spawnParticle(Particle.BLOCK, var2.clone().add(0.0, 0.6, 0.0), 60, 0.6, 0.5, 0.6, 0.0, Material.BARREL.createBlockData());
                var5.spawnParticle(Particle.POOF, var2, 20, 0.6, 0.3, 0.6, 0.03);
                break;
            case SPEAR:
                var5.playSound(var2, "entity.arrow.hit", 0.7F, 0.8F);
                var5.spawnParticle(Particle.CRIT, var2, 6, 0.2, 0.2, 0.2, 0.2);
                break;
            case BOMB:
                var5.playSound(var2, "entity.generic.explode", 0.6F, 1.4F);
                var5.spawnParticle(Particle.EXPLOSION, var2, 1, 0.0, 0.0, 0.0, 0.0);
                var5.spawnParticle(Particle.LARGE_SMOKE, var2, 8, var3 / 3.0, 0.2, var3 / 3.0, 0.02);
                this.ring(var2, Math.max(1.0, var3), Color.fromRGB(255, 150, 40));
                break;
            case SNOWBALL:
                var5.playSound(var2, "block.snow.break", 1.2F, 0.6F);
                var5.playSound(var2, "entity.player.hurt_freeze", 0.8F, 1.1F);
                var5.spawnParticle(Particle.SNOWFLAKE, var2.clone().add(0.0, 0.5, 0.0), 80, var3 / 2.0, 0.5, var3 / 2.0, 0.05);
                var5.spawnParticle(Particle.BLOCK, var2.clone().add(0.0, 0.5, 0.0), 50, var3 / 2.0, 0.4, var3 / 2.0, 0.0, Material.SNOW_BLOCK.createBlockData());
                this.ring(var2, var3, Color.fromRGB(235, 245, 255));
                break;
            case ROCKET:
                var5.playSound(var2, "entity.generic.explode", 1.4F, 0.7F);
                var5.playSound(var2, "entity.firework_rocket.large_blast", 1.0F, 0.6F);
                var5.spawnParticle(Particle.EXPLOSION_EMITTER, var2.clone().add(0.0, 0.5, 0.0), 1);
                var5.spawnParticle(Particle.FLAME, var2, 90, var3 / 2.0, 0.5, var3 / 2.0, 0.1);
                var5.spawnParticle(Particle.LARGE_SMOKE, var2, 30, var3 / 2.0, 0.6, var3 / 2.0, 0.03);
                this.ring(var2, var3, Color.fromRGB(255, 70, 30));
        }
    }

    List<BlockDisplay> floorDisc(Location var1, double var2, Material var4, float var5) {
        ArrayList var6 = new ArrayList();
        int var7 = Math.max(8, (int)Math.round(var2 * 4.0));
        double var8 = 2.0 * var2 / var7;
        double var10 = this.gm.arena.floorY + 1 + var5;
        BlockData var12 = var4.createBlockData();

        for (int var13 = 0; var13 < var7; var13++) {
            double var14 = -var2 + var13 * var8;
            double var16 = var14 + var8 / 2.0;
            double var18 = Math.sqrt(Math.max(0.0, var2 * var2 - var16 * var16));
            if (!(var18 < 0.05)) {
                Location var20 = new Location(var1.getWorld(), var1.getX() - var18, var10, var1.getZ() + var14);
                BlockDisplay var21 = (BlockDisplay)this.w().spawn(var20, BlockDisplay.class);
                var21.addScoreboardTag("clashmc");
                var21.setBlock(var12);
                var21.setTransformation(
                    new Transformation(new Vector3f(), new Quaternionf(), new Vector3f((float)(var18 * 2.0), 0.03F, (float)var8), new Quaternionf())
                );
                var21.setBrightness(new Brightness(15, 15));
                var21.setPersistent(false);
                var21.setViewRange(2.0F);
                this.spawned.add(var21);
                var6.add(var21);
            }
        }

        return var6;
    }

    void fadeDisc(List<BlockDisplay> var1) {
        for (BlockDisplay var3 : var1) {
            if (var3.isValid()) {
                Transformation var4 = var3.getTransformation();
                var3.setInterpolationDelay(0);
                var3.setInterpolationDuration(6);
                var3.setTransformation(
                    new Transformation(
                        new Vector3f(var4.getScale().x * 0.5F, 0.0F, var4.getScale().z * 0.5F),
                        new Quaternionf(),
                        new Vector3f(0.01F, 0.01F, 0.01F),
                        new Quaternionf()
                    )
                );
            }
        }

        this.later(7L, () -> {
            for (BlockDisplay var3x : var1) {
                this.spawned.remove(var3x);
                var3x.remove();
            }
        });
    }

    void edge(Location var1, double var2, Color var4) {
        DustOptions var5 = new DustOptions(var4, 1.9F);
        DustOptions var6 = new DustOptions(var4, 1.1F);
        double var7 = this.gm.arena.floorY + 1.12;
        int var9 = Math.max(24, (int)(var2 * 12.0));

        for (int var10 = 0; var10 < var9; var10++) {
            double var11 = (Math.PI * 2) * var10 / var9;
            this.w()
                .spawnParticle(Particle.DUST, var1.getX() + Math.cos(var11) * var2, var7, var1.getZ() + Math.sin(var11) * var2, 1, 0.0, 0.0, 0.0, 0.0, var5);
            if (var10 % 2 == 0) {
                this.w()
                    .spawnParticle(
                        Particle.DUST,
                        var1.getX() + Math.cos(var11) * (var2 - 0.3),
                        var7,
                        var1.getZ() + Math.sin(var11) * (var2 - 0.3),
                        1,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        var6
                    );
            }
        }

        for (int var15 = 0; var15 < 8; var15++) {
            double var16 = (Math.PI * 2) * var15 / 8.0;

            for (double var13 = 0.3; var13 <= 0.9; var13 += 0.3) {
                this.w()
                    .spawnParticle(
                        Particle.DUST, var1.getX() + Math.cos(var16) * var2, var7 + var13, var1.getZ() + Math.sin(var16) * var2, 1, 0.0, 0.0, 0.0, 0.0, var6
                    );
            }
        }
    }

    void spellArea(final Location var1, final double var2, final Color var4, Material var5, final int var6) {
        final List var7 = this.floorDisc(var1, var2, var5, 0.02F);
        BukkitRunnable var8 = new BukkitRunnable() {
            int i = 0;

            public void run() {
                if (Fx.this.playing() && this.i <= var6) {
                    double var1x = this.i < 5 ? var2 * (0.3 + 0.7 * this.i / 5.0) : var2;
                    if (this.i % 2 == 0) {
                        Fx.this.edge(var1, var1x, var4);
                    }

                    this.i++;
                } else {
                    this.cancel();
                    Fx.this.tasks.remove(this);
                    Fx.this.fadeDisc(var7);
                }
            }
        };
        this.tasks.add(var8);
        var8.runTaskTimer(this.gm.plugin, 0L, 1L);
    }

    void telegraph(final Location var1, final double var2, final Color var4, final int var5) {
        BukkitRunnable var6 = new BukkitRunnable() {
            int i = 0;

            public void run() {
                if (Fx.this.playing() && this.i++ <= var5) {
                    if (this.i % 4 < 2) {
                        Fx.this.edge(var1, var2, var4);
                    }
                } else {
                    this.cancel();
                    Fx.this.tasks.remove(this);
                }
            }
        };
        this.tasks.add(var6);
        var6.runTaskTimer(this.gm.plugin, 0L, 1L);
    }

    void ring(Location var1, double var2, Color var4) {
        DustOptions var5 = new DustOptions(var4, 1.4F);
        int var6 = Math.max(16, (int)(var2 * 10.0));

        for (int var7 = 0; var7 < var6; var7++) {
            double var8 = (Math.PI * 2) * var7 / var6;
            this.w()
                .spawnParticle(
                    Particle.DUST,
                    var1.getX() + Math.cos(var8) * var2,
                    this.gm.arena.floorY + 1.15,
                    var1.getZ() + Math.sin(var8) * var2,
                    1,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    var5
                );
        }
    }

    void melee(CardDef var1, Location var2, Location var3) {
        World var4 = this.w();
        Location var5 = var3.clone().add(0.0, 1.0, 0.0);
        Location var6 = var2.clone().add(var3.toVector().subtract(var2.toVector()).multiply(0.6)).add(0.0, 1.1, 0.0);
        String var7 = var1.id;
        switch (var7) {
            case "giant":
                var4.playSound(var3, "entity.iron_golem.attack", 1.0F, 0.6F);
                var4.playSound(var3, "entity.generic.explode", 0.35F, 1.7F);
                var4.spawnParticle(Particle.BLOCK, var3.clone().add(0.0, 0.2, 0.0), 30, 0.6, 0.1, 0.6, 0.0, Material.GRASS_BLOCK.createBlockData());
                var4.spawnParticle(Particle.EXPLOSION, var5, 1, 0.0, 0.0, 0.0, 0.0);
                break;
            case "hog_rider":
                var4.playSound(var3, "entity.hoglin.attack", 1.0F, 1.0F);
                var4.playSound(var3, "entity.player.attack.strong", 0.8F, 0.8F);
                var4.spawnParticle(Particle.CRIT, var5, 14, 0.3, 0.3, 0.3, 0.3);
                break;
            case "goblins":
            case "goblin_barrel":
                var4.playSound(var3, "entity.player.attack.weak", 0.8F, 1.7F);
                var4.spawnParticle(Particle.CRIT, var5, 5, 0.2, 0.2, 0.2, 0.2);
                break;
            case "skeleton_barrel":
                var4.playSound(var3, "entity.skeleton.hurt", 0.4F, 1.8F);
                var4.playSound(var3, "entity.player.attack.weak", 0.7F, 1.4F);
                var4.spawnParticle(Particle.CRIT, var5, 5, 0.2, 0.2, 0.2, 0.2);
                break;
            case "miner":
                var4.playSound(var3, "block.stone.break", 0.8F, 1.3F);
                var4.playSound(var3, "entity.player.attack.strong", 0.6F, 1.2F);
                var4.spawnParticle(Particle.BLOCK, var5, 12, 0.2, 0.2, 0.2, 0.0, Material.STONE_BRICKS.createBlockData());
                break;
            default:
                var4.playSound(var3, "entity.player.attack.sweep", 0.9F, 1.0F);
                var4.playSound(var3, "entity.player.attack.strong", 0.5F, 1.1F);
                var4.spawnParticle(Particle.SWEEP_ATTACK, var6, 1, 0.0, 0.0, 0.0, 0.0);
                var4.spawnParticle(Particle.CRIT, var5, 6, 0.25, 0.25, 0.25, 0.2);
        }
    }

    void lightning(Location var1, Location var2, boolean var3) {
        World var4 = this.w();
        Vector var5 = var2.toVector().subtract(var1.toVector());
        double var6 = var5.length();
        if (!(var6 < 0.1)) {
            int var8 = Math.max(3, (int)(var6 * 2.0));
            Location var9 = var1.clone();
            Random var10 = this.gm.rng;

            for (int var11 = 1; var11 <= var8; var11++) {
                double var12 = (double)var11 / var8;
                Location var14 = var1.clone().add(var5.clone().multiply(var12));
                if (var11 < var8) {
                    var14.add((var10.nextDouble() - 0.5) * 0.6, (var10.nextDouble() - 0.5) * 0.6, (var10.nextDouble() - 0.5) * 0.6);
                }

                Vector var15 = var14.toVector().subtract(var9.toVector());
                double var16 = var15.length();

                for (double var18 = 0.0; var18 < var16; var18 += 0.2) {
                    Location var20 = var9.clone().add(var15.clone().multiply(var18 / var16));
                    var4.spawnParticle(Particle.ELECTRIC_SPARK, var20, 1, 0.0, 0.0, 0.0, 0.0);
                    var4.spawnParticle(Particle.END_ROD, var20, 0, 0.0, 0.0, 0.0, 0.0);
                }

                var9 = var14;
            }

            var4.spawnParticle(Particle.FLASH, var2, 1, 0.0, 0.0, 0.0, 0.0);
            if (var3) {
                var4.playSound(var2, "entity.lightning_bolt.impact", 0.5F, 1.8F);
            }
        }
    }

    void zapStrike(Location var1, double var2) {
        World var4 = this.w();
        Location var5 = var1.clone().add(0.0, 9.0, 0.0);
        this.lightning(var5, var1.clone().add(0.0, 0.2, 0.0), false);

        for (int var6 = 0; var6 < 3; var6++) {
            double var7 = this.gm.rng.nextDouble() * Math.PI * 2.0;
            this.lightning(var1.clone().add(0.0, 0.6, 0.0), var1.clone().add(Math.cos(var7) * var2, 0.2, Math.sin(var7) * var2), false);
        }

        this.ring(var1, var2, Color.fromRGB(120, 200, 255));
        var4.spawnParticle(Particle.ELECTRIC_SPARK, var1.clone().add(0.0, 1.0, 0.0), 80, var2 / 2.0, 0.8, var2 / 2.0, 0.2);
        var4.playSound(var1, "entity.lightning_bolt.thunder", 0.4F, 1.9F);
        var4.playSound(var1, "entity.lightning_bolt.impact", 1.0F, 1.4F);
    }

    void beam(Location var1, Location var2, Particle var3, DustOptions var4) {
        Vector var5 = var2.toVector().subtract(var1.toVector());
        double var6 = var5.length();
        if (!(var6 < 0.1)) {
            var5.multiply(1.0 / var6);

            for (double var8 = 0.0; var8 < var6; var8 += 0.3) {
                Location var10 = var1.clone().add(var5.clone().multiply(var8));
                if (var4 != null) {
                    this.w().spawnParticle(Particle.DUST, var10, 1, 0.02, 0.02, 0.02, 0.0, var4);
                } else {
                    this.w().spawnParticle(var3, var10, 1, 0.0, 0.0, 0.0, 0.0);
                }
            }
        }
    }

    void rollingLog(Location var1, int var2, double var3, double var5, String var7, Color var8, Consumer<Location> var9) {
        this.rollingLog(var1, var2, var3, var5, var7, var8, var9, null, Material.OAK_LOG);
    }

    void rollingLog(
        final Location var1,
        final int var2,
        double var3,
        final double var5,
        String var7,
        Color var8,
        final Consumer<Location> var9,
        final Consumer<Location> var10,
        final Material var11
    ) {
        final ArmorStand var12 = null;
        if (var7 != null && !var7.isEmpty() && this.gm.models.enabled()) {
            Location var13 = var1.clone();
            var13.setYaw(var2 > 0 ? 0.0F : 180.0F);
            var13.setPitch(0.0F);
            var12 = (ArmorStand)this.w().spawn(var13, ArmorStand.class);
            var12.addScoreboardTag("clashmc");
            var12.setInvisible(true);
            var12.setGravity(false);
            var12.setMarker(true);
            var12.setInvulnerable(true);
            var12.setPersistent(false);
            if (this.gm.models.apply(var12, var7, true, var8)) {
                this.spawned.add(var12);
            } else {
                var12.remove();
                var12 = null;
            }
        }

        final BlockDisplay var14;
        if (var12 == null) {
            var14 = (BlockDisplay)this.w().spawn(var1.clone().add(0.0, 0.5, 0.0), BlockDisplay.class);
            var14.addScoreboardTag("clashmc");
            var14.setBlock(Material.OAK_LOG.createBlockData("[axis=x]"));
            this.common(var14);
        } else {
            var14 = null;
        }

        final float var15 = (float)var3;
        this.w().playSound(var1, "block.wood.place", 1.0F, 0.6F);
        this.w().playSound(var1, "entity.zombie.attack_wooden_door", 0.7F, 0.6F);
        this.w().spawnParticle(Particle.BLOCK, var1.clone().add(0.0, 0.4, 0.0), 30, var15 / 3.0F, 0.2, 0.4, 0.0, Material.DIRT.createBlockData());
        BukkitRunnable var16 = new BukkitRunnable() {
            double traveled = 0.0;
            float ang = 0.0F;

            public void run() {
                Object var1x = var12 != null ? var12 : var14;
                if (Fx.this.playing() && !(this.traveled >= var5) && var1x != null && var1x.isValid()) {
                    this.traveled = Math.min(var5, this.traveled + 0.4);
                    Location var7x = var1.clone().add(0.0, 0.0, var2 * this.traveled);
                    if (var12 != null) {
                        Location var8x = var7x.clone();
                        var8x.setYaw(var2 > 0 ? 0.0F : 180.0F);
                        var8x.setPitch(0.0F);
                        var12.teleport(var8x);
                    } else {
                        this.ang = this.ang + 0.55F * var2;
                        var14.teleport(var7x.clone().add(0.0, 0.5, 0.0));
                        float var9x = 0.5F;
                        float var4 = 0.5F;
                        float var5x = (float)(var9x * Math.cos(this.ang) - var4 * Math.sin(this.ang));
                        float var6 = (float)(var9x * Math.sin(this.ang) + var4 * Math.cos(this.ang));
                        var14.setInterpolationDelay(0);
                        var14.setInterpolationDuration(1);
                        var14.setTransformation(
                            new Transformation(
                                new Vector3f(-var15 / 2.0F, -var5x, -var6),
                                new Quaternionf().rotateX(this.ang),
                                new Vector3f(var15, 1.0F, 1.0F),
                                new Quaternionf()
                            )
                        );
                    }

                    Fx.this.w()
                        .spawnParticle(
                            Particle.BLOCK, var7x.clone().add(0.0, 0.1, -var2 * 0.5), 8, var15 / 3.0F, 0.05, 0.15, 0.0, Material.GRASS_BLOCK.createBlockData()
                        );
                    if ((int)(this.traveled / 0.4) % 2 == 0) {
                        Fx.this.w()
                            .spawnParticle(
                                Particle.BLOCK, var7x.clone().add(0.0, 0.1, -var2 * 0.6), 4, var15 / 3.0F, 0.05, 0.1, 0.0, Material.DIRT.createBlockData()
                            );
                    }

                    if ((int)(this.traveled / 0.4) % 3 == 0) {
                        Fx.this.w().playSound(var7x, "block.wood.step", 0.9F, 0.6F);
                    }

                    var9.accept(var7x);
                } else {
                    this.cancel();
                    Fx.this.tasks.remove(this);
                    if (var1x != null) {
                        Location var2x = var1x.getLocation();
                        Fx.this.w().spawnParticle(Particle.BLOCK, var2x.clone().add(0.0, 0.6, 0.0), 50, var15 / 3.0F, 0.4, 0.4, 0.0, var11.createBlockData());
                        Fx.this.w().spawnParticle(Particle.POOF, var2x.clone().add(0.0, 0.6, 0.0), 12, var15 / 3.0F, 0.3, 0.3, 0.02);
                        Fx.this.w().playSound(var2x, "block.wood.break", 1.0F, 0.8F);
                        if (var12 != null) {
                            Fx.this.gm.models.remove(var12);
                        }

                        Fx.this.spawned.remove(var1x);
                        var1x.remove();
                        if (var10 != null && Fx.this.playing()) {
                            Location var3x = var2x.clone();
                            var3x.setY(var1.getY());
                            var10.accept(var3x);
                        }
                    }
                }
            }
        };
        this.tasks.add(var16);
        var16.runTaskTimer(this.gm.plugin, 0L, 1L);
    }

    void tunnel(final Location var1, final Location var2, double var3, final Runnable var5) {
        double var6 = var1.distance(var2);
        final int var8 = 10 + (int)Math.round(var6 / var3 * 20.0);
        final BlockData var9 = Material.DIRT.createBlockData();
        final BlockData var10 = Material.COARSE_DIRT.createBlockData();
        final BlockData var11 = Material.ROOTED_DIRT.createBlockData();
        final BlockData var12 = Material.GRASS_BLOCK.createBlockData();
        final double var13 = this.gm.arena.floorY + 1;
        final BlockDisplay var15 = (BlockDisplay)this.w().spawn(new Location(this.w(), var1.getX(), var13, var1.getZ()), BlockDisplay.class);
        final BlockDisplay var16 = (BlockDisplay)this.w().spawn(new Location(this.w(), var1.getX(), var13, var1.getZ()), BlockDisplay.class);

        for (BlockDisplay var20 : new BlockDisplay[]{var15, var16}) {
            var20.addScoreboardTag("clashmc");
            var20.setBlock(var20 == var15 ? var10 : var11);
            this.common(var20);
            var20.setTeleportDuration(2);
        }

        var15.setTransformation(new Transformation(new Vector3f(-0.75F, -0.25F, -0.75F), new Quaternionf(), new Vector3f(1.5F, 0.5F, 1.5F), new Quaternionf()));
        var16.setTransformation(
            new Transformation(new Vector3f(-0.42F, 0.1F, -0.42F), new Quaternionf().rotateY(0.6F), new Vector3f(0.84F, 0.4F, 0.84F), new Quaternionf())
        );
        final ArrayList var21 = new ArrayList();
        this.w().playSound(var1, "block.rooted_dirt.break", 1.0F, 0.7F);
        this.w().spawnParticle(Particle.BLOCK, var1.clone().add(0.0, 0.3, 0.0), 40, 0.5, 0.3, 0.5, 0.15, var9);
        BukkitRunnable var22 = new BukkitRunnable() {
            int i = 0;

            public void run() {
                if (!Fx.this.playing()) {
                    this.cancel();
                    Fx.this.tasks.remove(this);
                    this.cleanup();
                } else {
                    this.i++;
                    double var1x = Math.min(1.0, (double)this.i / var8);
                    Location var3x = var1.clone().add(var2.toVector().subtract(var1.toVector()).multiply(var1x));
                    var3x.setY(var13);
                    double var4 = Math.abs(Math.sin(this.i * 0.9)) * 0.12;
                    var15.teleport(var3x.clone().add(0.0, var4 * 0.5, 0.0));
                    var16.teleport(var3x.clone().add(0.0, var4, 0.0));
                    Fx.this.w().spawnParticle(Particle.BLOCK, var3x.clone().add(0.0, 0.35, 0.0), 10, 0.35, 0.15, 0.35, 0.12, var9);
                    Fx.this.w().spawnParticle(Particle.BLOCK, var3x.clone().add(0.0, 0.1, 0.0), 5, 0.6, 0.02, 0.6, 0.0, var12);
                    if (this.i % 2 == 0) {
                        Fx.this.w().spawnParticle(Particle.BLOCK, var3x.clone().add(0.0, 0.5, 0.0), 3, 0.25, 0.2, 0.25, 0.25, var10);
                    }

                    if (this.i % 3 == 0) {
                        Fx.this.w().spawnParticle(Particle.POOF, var3x.clone().add(0.0, 0.25, 0.0), 2, 0.3, 0.05, 0.3, 0.01);
                    }

                    if (this.i % 4 == 0) {
                        Fx.this.w().spawnParticle(Particle.CAMPFIRE_COSY_SMOKE, var3x.clone().add(0.0, 0.2, 0.0), 1, 0.2, 0.0, 0.2, 0.005);
                    }

                    if (this.i % 3 == 0) {
                        BlockDisplay var6x = (BlockDisplay)Fx.this.w().spawn(new Location(Fx.this.w(), var3x.getX(), var13, var3x.getZ()), BlockDisplay.class);
                        var6x.addScoreboardTag("clashmc");
                        var6x.setBlock(this.i % 6 == 0 ? var10 : var9);
                        float var7 = 0.7F + (float)(Fx.this.gm.rng.nextDouble() * 0.3);
                        var6x.setTransformation(
                            new Transformation(
                                new Vector3f(-var7 / 2.0F, -0.02F, -var7 / 2.0F),
                                new Quaternionf().rotateY((float)(Fx.this.gm.rng.nextDouble() * 1.5)),
                                new Vector3f(var7, 0.08F, var7),
                                new Quaternionf()
                            )
                        );
                        Fx.this.common(var6x);
                        var21.add(var6x);
                        Fx.this.later(30L, () -> {
                            Fx.this.spawned.remove(var6);
                            var6.remove();
                            var21.remove(var6);
                        });
                    }

                    if (this.i % 4 == 0) {
                        Fx.this.w().playSound(var3x, "block.gravel.break", 0.7F, 0.7F + (float)Fx.this.gm.rng.nextDouble() * 0.3F);
                    }

                    if (this.i % 7 == 0) {
                        Fx.this.w().playSound(var3x, "block.rooted_dirt.step", 0.8F, 0.6F);
                    }

                    if (this.i >= var8) {
                        this.cancel();
                        Fx.this.tasks.remove(this);
                        this.cleanup();
                        Location var12x = new Location(Fx.this.w(), var2.getX(), var13, var2.getZ());
                        Fx.this.w().spawnParticle(Particle.BLOCK, var12x.clone().add(0.0, 0.4, 0.0), 90, 0.7, 0.3, 0.7, 0.35, var9);
                        Fx.this.w().spawnParticle(Particle.BLOCK, var12x.clone().add(0.0, 0.6, 0.0), 30, 0.5, 0.5, 0.5, 0.4, var10);
                        Fx.this.w().spawnParticle(Particle.BLOCK, var12x.clone().add(0.0, 0.2, 0.0), 25, 1.0, 0.05, 1.0, 0.1, var12);
                        Fx.this.w().spawnParticle(Particle.POOF, var12x.clone().add(0.0, 0.5, 0.0), 14, 0.6, 0.3, 0.6, 0.04);
                        Fx.this.w().spawnParticle(Particle.CAMPFIRE_COSY_SMOKE, var12x.clone().add(0.0, 0.3, 0.0), 4, 0.5, 0.1, 0.5, 0.01);
                        Fx.this.w().playSound(var12x, "block.rooted_dirt.break", 1.2F, 0.7F);
                        Fx.this.w().playSound(var12x, "entity.zombie.break_wooden_door", 0.5F, 0.6F);
                        ArrayList var13x = new ArrayList();

                        for (int var8x = 0; var8x < 6; var8x++) {
                            double var9x = (Math.PI * 2) * var8x / 6.0;
                            BlockDisplay var11x = (BlockDisplay)Fx.this.w()
                                .spawn(
                                    new Location(Fx.this.w(), var12x.getX() + Math.cos(var9x) * 0.85, var13, var12x.getZ() + Math.sin(var9x) * 0.85),
                                    BlockDisplay.class
                                );
                            var11x.addScoreboardTag("clashmc");
                            var11x.setBlock(var8x % 2 == 0 ? var10 : var11);
                            var11x.setTransformation(
                                new Transformation(
                                    new Vector3f(-0.3F, -0.1F, -0.3F),
                                    new Quaternionf().rotateY((float)var9x).rotateX(0.35F),
                                    new Vector3f(0.6F, 0.35F, 0.6F),
                                    new Quaternionf()
                                )
                            );
                            Fx.this.common(var11x);
                            var13x.add(var11x);
                        }

                        Fx.this.later(40L, () -> {
                            for (BlockDisplay var3xx : var13x) {
                                Fx.this.spawned.remove(var3xx);
                                var3xx.remove();
                            }
                        });
                        var5.run();
                    }
                }
            }

            void cleanup() {
                for (BlockDisplay var4 : new BlockDisplay[]{var15, var16}) {
                    Fx.this.spawned.remove(var4);
                    var4.remove();
                }
            }
        };
        this.tasks.add(var22);
        var22.runTaskTimer(this.gm.plugin, 0L, 1L);
    }

    void encase(Location var1, double var2, double var4, int var6) {
        BlockDisplay var7 = (BlockDisplay)this.w().spawn(var1.clone(), BlockDisplay.class);
        var7.addScoreboardTag("clashmc");
        var7.setBlock(Material.ICE.createBlockData());
        float var8 = (float)(var2 + 0.25);
        float var9 = (float)(var4 + 0.2);
        var7.setTransformation(
            new Transformation(new Vector3f(-var8 / 2.0F, 0.0F, -var8 / 2.0F), new Quaternionf(), new Vector3f(var8, var9, var8), new Quaternionf())
        );
        this.common(var7);
        this.later(
            var6,
            () -> {
                if (var7.isValid()) {
                    this.w()
                        .spawnParticle(
                            Particle.BLOCK,
                            var7.getLocation().add(0.0, var9 / 2.0F, 0.0),
                            20,
                            var8 / 3.0F,
                            var9 / 3.0F,
                            var8 / 3.0F,
                            0.0,
                            Material.ICE.createBlockData()
                        );
                }

                this.spawned.remove(var7);
                var7.remove();
            }
        );
    }

    void damageNumber(Location var1, double var2, boolean var4, boolean var5) {
        if (this.gm.damageNumbers) {
            final Location var6 = var1.clone().add((this.gm.rng.nextDouble() - 0.5) * 0.6, 0.0, (this.gm.rng.nextDouble() - 0.5) * 0.6);
            final TextDisplay var7 = (TextDisplay)this.w().spawn(var6, TextDisplay.class);
            var7.addScoreboardTag("clashmc");
            var7.setText((var4 ? "§e" : (var5 ? "§6" : "§f")) + "§l-" + (int)Math.round(var2));
            var7.setBillboard(Billboard.CENTER);
            var7.setBackgroundColor(Color.fromARGB(0, 0, 0, 0));
            var7.setShadowed(true);
            float var8 = var4 ? 1.3F : 0.9F;
            var7.setTransformation(new Transformation(new Vector3f(), new Quaternionf(), new Vector3f(var8, var8, var8), new Quaternionf()));
            this.common(var7);
            var7.setTeleportDuration(3);
            BukkitRunnable var9 = new BukkitRunnable() {
                int i = 0;

                public void run() {
                    this.i++;
                    if (var7.isValid() && this.i <= 14) {
                        var7.teleport(var6.clone().add(0.0, this.i * 0.07, 0.0));
                        if (this.i > 7) {
                            var7.setTextOpacity((byte)Math.max(40, 255 - (this.i - 7) * 30));
                        }
                    } else {
                        this.cancel();
                        Fx.this.tasks.remove(this);
                        Fx.this.spawned.remove(var7);
                        var7.remove();
                    }
                }
            };
            this.tasks.add(var9);
            var9.runTaskTimer(this.gm.plugin, 1L, 1L);
        }
    }

    void later(long var1, final Runnable var3) {
        BukkitRunnable var4 = new BukkitRunnable() {
            public void run() {
                Fx.this.tasks.remove(this);
                var3.run();
            }
        };
        this.tasks.add(var4);
        var4.runTaskLater(this.gm.plugin, var1);
    }

    void track(Entity var1) {
        this.spawned.add(var1);
    }

    void untrack(Entity var1) {
        this.spawned.remove(var1);
    }

    void clear() {
        for (BukkitRunnable var2 : new ArrayList<>(this.tasks)) {
            try {
                var2.cancel();
            } catch (IllegalStateException var4) {
            }
        }

        this.tasks.clear();

        for (Entity var6 : new ArrayList<>(this.spawned)) {
            var6.remove();
        }

        this.spawned.clear();
    }

    static enum Shot {
        ARROW(26.0, 0.08),
        BOLT(30.0, 0.04),
        BULLET(48.0, 0.0),
        FIREBALL(16.0, 0.12),
        CANNONBALL(22.0, 0.1),
        GOOP(18.0, 0.06),
        BIG_FIREBALL(18.0, 0.3),
        BARREL(15.0, 0.35),
        SPEAR(24.0, 0.08),
        BOMB(12.0, 0.45),
        SNOWBALL(16.0, 0.22),
        ROCKET(13.0, 0.18);

        final double speed;
        final double arc;

        private Shot(double nullxx, double nullxxx) {
            this.speed = nullxx;
            this.arc = nullxxx;
        }
    }
}
