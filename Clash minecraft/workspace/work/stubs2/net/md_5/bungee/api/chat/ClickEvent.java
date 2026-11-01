package net.md_5.bungee.api.chat;

public class ClickEvent {
    public ClickEvent(net.md_5.bungee.api.chat.ClickEvent.Action a0, java.lang.String a1) {}
    protected ClickEvent() {}
    public interface Action {
        net.md_5.bungee.api.chat.ClickEvent.Action RUN_COMMAND = null;
        net.md_5.bungee.api.chat.ClickEvent.Action SUGGEST_COMMAND = null;
    }
}
