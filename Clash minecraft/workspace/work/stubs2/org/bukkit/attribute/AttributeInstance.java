package org.bukkit.attribute;

public interface AttributeInstance {
    default double getBaseValue() { return 0; }
    default void setBaseValue(double a0) {  }
}
