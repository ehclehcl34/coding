package org.bukkit.entity;

public interface Ageable extends org.bukkit.entity.Mob {
    default void setAdult() {  }
    default void setBaby() {  }
}
