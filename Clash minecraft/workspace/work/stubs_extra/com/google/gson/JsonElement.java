package com.google.gson;
public abstract class JsonElement {
    public boolean isJsonObject() { return false; }
    public boolean isJsonArray() { return false; }
    public boolean isJsonPrimitive() { return false; }
    public JsonObject getAsJsonObject() { return null; }
    public JsonArray getAsJsonArray() { return null; }
    public JsonPrimitive getAsJsonPrimitive() { return null; }
    public double getAsDouble() { return 0; }
}
