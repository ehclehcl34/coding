package kr.kjmn.clashmc;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import java.util.zip.ZipOutputStream;

/** 리소스팩 여러 개를 하나로 합침 (뒤에 오는 팩이 우선, 같은 JSON 은 목록·객체를 합침) */
final class PackMerge {
    private PackMerge() {
    }

    /** zip 파일이면 그대로, 폴더면 안의 파일을 읽음. 없으면 null */
    static Map<String, byte[]> read(File f) throws Exception {
        Map<String, byte[]> out = new LinkedHashMap<>();
        if (f.isFile()) {
            try (ZipInputStream in = new ZipInputStream(new ByteArrayInputStream(Files.readAllBytes(f.toPath())))) {
                ZipEntry e;
                while ((e = in.getNextEntry()) != null) {
                    if (!e.isDirectory()) {
                        out.put(norm(e.getName()), in.readAllBytes());
                    }
                }
            }
        } else if (f.isDirectory()) {
            String base = f.toPath().toAbsolutePath().normalize().toString();
            for (File c : walk(f)) {
                String rel = c.toPath().toAbsolutePath().normalize().toString().substring(base.length()).replace('\\', '/');
                out.put(norm(rel), Files.readAllBytes(c.toPath()));
            }
        } else {
            return null;
        }

        return out;
    }

    static Map<String, byte[]> read(byte[] zip) throws Exception {
        Map<String, byte[]> out = new LinkedHashMap<>();
        try (ZipInputStream in = new ZipInputStream(new ByteArrayInputStream(zip))) {
            ZipEntry e;
            while ((e = in.getNextEntry()) != null) {
                if (!e.isDirectory()) {
                    out.put(norm(e.getName()), in.readAllBytes());
                }
            }
        }

        return out;
    }

    private static List<File> walk(File dir) {
        List<File> out = new java.util.ArrayList<>();
        File[] kids = dir.listFiles();
        if (kids != null) {
            for (File k : kids) {
                if (k.isDirectory()) {
                    out.addAll(walk(k));
                } else {
                    out.add(k);
                }
            }
        }

        return out;
    }

    private static String norm(String n) {
        String s = n.replace('\\', '/');
        while (s.startsWith("/")) {
            s = s.substring(1);
        }

        return s;
    }

    /** packs: 낮은 우선순위 → 높은 우선순위 순서 */
    static byte[] merge(List<Map<String, byte[]>> packs) throws Exception {
        Map<String, byte[]> out = new LinkedHashMap<>();
        for (Map<String, byte[]> p : packs) {
            for (Map.Entry<String, byte[]> e : p.entrySet()) {
                String name = e.getKey();
                byte[] prev = out.get(name);
                if (prev != null && (name.endsWith(".json") || name.endsWith(".mcmeta"))) {
                    byte[] merged = mergeJson(prev, e.getValue());
                    out.put(name, merged != null ? merged : e.getValue());
                } else {
                    out.put(name, e.getValue());
                }
            }
        }

        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        try (ZipOutputStream zos = new ZipOutputStream(bos)) {
            for (Map.Entry<String, byte[]> e : out.entrySet()) {
                ZipEntry ze = new ZipEntry(e.getKey());
                ze.setTime(0L);           // 내용이 같으면 sha1 도 같게
                zos.putNextEntry(ze);
                zos.write(e.getValue());
                zos.closeEntry();
            }
        }

        return bos.toByteArray();
    }

    private static byte[] mergeJson(byte[] a, byte[] b) {
        try {
            JsonElement ja = JsonParser.parseString(strip(new String(a, StandardCharsets.UTF_8)));
            JsonElement jb = JsonParser.parseString(strip(new String(b, StandardCharsets.UTF_8)));
            if (!ja.isJsonObject() || !jb.isJsonObject()) {
                return null;
            }

            JsonObject m = mergeObj(ja.getAsJsonObject(), jb.getAsJsonObject());
            return m.toString().getBytes(StandardCharsets.UTF_8);
        } catch (Throwable t) {
            return null;
        }
    }

    private static String strip(String s) {
        return !s.isEmpty() && s.charAt(0) == '﻿' ? s.substring(1) : s;
    }

    /** a 에 b 를 합침: 목록은 이어붙임(중복 제거), 객체는 재귀, 숫자는 큰 값(pack_format), 나머지는 b 우선 */
    private static JsonObject mergeObj(JsonObject a, JsonObject b) {
        JsonObject out = new JsonObject();
        for (Map.Entry<String, JsonElement> e : a.entrySet()) {
            out.add(e.getKey(), e.getValue());
        }

        for (Map.Entry<String, JsonElement> e : b.entrySet()) {
            String k = e.getKey();
            JsonElement vb = e.getValue();
            JsonElement va = out.get(k);
            if (va == null) {
                out.add(k, vb);
            } else if (va.isJsonArray() && vb.isJsonArray()) {
                JsonArray arr = new JsonArray();
                Set<String> seen = new HashSet<>();
                for (JsonElement x : va.getAsJsonArray()) {
                    if (seen.add(x.toString())) {
                        arr.add(x);
                    }
                }

                for (JsonElement x : vb.getAsJsonArray()) {
                    if (seen.add(x.toString())) {
                        arr.add(x);
                    }
                }

                out.add(k, arr);
            } else if (va.isJsonObject() && vb.isJsonObject()) {
                out.add(k, mergeObj(va.getAsJsonObject(), vb.getAsJsonObject()));
            } else if (va.isJsonPrimitive() && vb.isJsonPrimitive() && va.getAsJsonPrimitive().isNumber() && vb.getAsJsonPrimitive().isNumber()) {
                out.add(k, va.getAsDouble() >= vb.getAsDouble() ? va : vb);
            } else {
                out.add(k, vb);
            }
        }

        return out;
    }
}
