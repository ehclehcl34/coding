package org.bukkit.event.player;

public class PlayerResourcePackStatusEvent {
    protected PlayerResourcePackStatusEvent() {}
    public org.bukkit.entity.Player getPlayer() { return null; }
    public Status getStatus() { return null; }
    public static enum Status { SUCCESSFULLY_LOADED, DECLINED, FAILED_DOWNLOAD, ACCEPTED, DOWNLOADED, INVALID_URL, FAILED_RELOAD, DISCARDED }
}
