package kr.kjmn.clashmc;

import com.sun.net.httpserver.HttpServer;
import java.io.File;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.file.Files;
import java.security.MessageDigest;
import java.util.logging.Logger;
import org.bukkit.Bukkit;
import org.bukkit.configuration.file.FileConfiguration;
import org.bukkit.entity.Player;

final class PackHost {
    static final String FILE = "ClashMC_UI_pack.zip";
    private final ClashPlugin plugin;
    private final Logger log;
    private HttpServer server;
    private byte[] data;
    private final java.util.LinkedHashMap<String, byte[]> versions = new java.util.LinkedHashMap<>();
    String sha1 = "";
    private int port;
    private String address = "";

    PackHost(ClashPlugin var1) {
        this.plugin = var1;
        this.log = var1.getLogger();
    }

    boolean running() {
        return this.server != null && this.data != null;
    }

    void start() {
        this.stop();
        FileConfiguration var1 = this.plugin.getConfig();
        if (var1.getBoolean("ui.pack-host.enabled", true)) {
            this.port = var1.getInt("ui.pack-host.port", 8165);
            this.address = var1.getString("ui.pack-host.address", "");

            try {
                File var2 = new File(this.plugin.getDataFolder(), "ClashMC_UI_pack.zip");
                byte[] var3 = null;

                try (InputStream var4 = this.plugin.getResource("ClashMC_UI_pack.zip")) {
                    if (var4 != null) {
                        var3 = var4.readAllBytes();
                    }
                }

                if (var3 != null && (!var2.exists() || !hex(sha(Files.readAllBytes(var2.toPath()))).equals(hex(sha(var3))))) {
                    this.plugin.getDataFolder().mkdirs();
                    Files.write(var2.toPath(), var3);
                    this.log.info("UI 리소스팩 최신 버전으로 교체: " + var2.getName());
                }

                if (!var2.exists()) {
                    this.log.warning("UI 리소스팩 파일 없음 (ClashMC_UI_pack.zip) - 자동 배포 꺼짐");
                    return;
                }

                byte[] ui = Files.readAllBytes(var2.toPath());
                this.data = ui;
                // BetterModel 등 다른 리소스팩과 합쳐서 하나로 보냄 (UI 팩이 우선)
                if (var1.getBoolean("ui.merge-pack.enabled", true)) {
                    java.util.List<java.util.Map<String, byte[]>> packs = new java.util.ArrayList<>();
                    java.util.List<String> used = new java.util.ArrayList<>();
                    for (Object src : var1.getList("ui.merge-pack.sources", java.util.Arrays.asList("plugins/BetterModel/build.zip"))) {
                        File f = new File(String.valueOf(src));
                        try {
                            java.util.Map<String, byte[]> m = PackMerge.read(f);
                            if (m != null && !m.isEmpty()) {
                                packs.add(m);
                                used.add(f.getPath() + " (" + m.size() + "개)");
                            }
                        } catch (Exception ex) {
                            this.log.warning("리소스팩 읽기 실패 (" + f.getPath() + "): " + ex);
                        }
                    }

                    if (!packs.isEmpty()) {
                        packs.add(PackMerge.read(ui));
                        this.data = PackMerge.merge(packs);
                        Files.write(new File(this.plugin.getDataFolder(), "ClashMC_merged_pack.zip").toPath(), this.data);
                        this.log.info("리소스팩 병합: " + String.join(", ", used) + " + UI 팩 → ClashMC_merged_pack.zip (" + this.data.length / 1024 + "KB)");
                    } else {
                        this.log.info("병합할 리소스팩 없음 (ui.merge-pack.sources) → UI 팩만 배포");
                    }
                }

                this.sha1 = hex(sha(this.data));
                // 이번 세션에 만든 버전들 보관 (재시작 전 server.properties 가 예전 sha1 을 보내도 받을 수 있게)
                this.versions.put(this.sha1.substring(0, 8), this.data);
                while (this.versions.size() > 4) {
                    this.versions.remove(this.versions.keySet().iterator().next());
                }

                this.server = HttpServer.create(new InetSocketAddress(this.port), 0);
                this.server.createContext("/clashmc_ui.zip", var1x -> {
                    byte[] var2x = this.data;
                    String q = var1x.getRequestURI().getQuery();
                    if (q != null && q.startsWith("v=")) {
                        byte[] old = this.versions.get(q.substring(2, Math.min(q.length(), 10)));
                        if (old != null) {
                            var2x = old;
                        }
                    }

                    var1x.getResponseHeaders().add("Content-Type", "application/zip");
                    var1x.sendResponseHeaders(200, var2x.length);

                    try (OutputStream var3x = var1x.getResponseBody()) {
                        var3x.write(var2x);
                    }
                });
                this.server.setExecutor(null);
                this.server.start();
                this.log.info("UI 리소스팩 자동 배포 중: 포트 " + this.port + ", sha1 " + this.sha1);
                this.syncServerProperties(var1);
            } catch (Throwable var9) {
                this.log.warning("UI 리소스팩 자동 배포 실패 (포트 " + this.port + "): " + var9 + " → config ui.pack-host 확인");
                this.stop();
            }
        }
    }

    /** 고정 팩 id: server.properties 의 resource-pack-id 와 플러그인이 보내는 팩이 같은 id → 새 팩이 덮어씀 */
    static final java.util.UUID PACK_ID = java.util.UUID.nameUUIDFromBytes("clashmc-pack".getBytes(java.nio.charset.StandardCharsets.UTF_8));

    /** 고정 주소 (config address → server.properties 의 server-ip). 없으면 null */
    String fixedUrl() {
        String host = this.address;
        if (host == null || host.isEmpty()) {
            host = Bukkit.getIp();
        }

        return host != null && !host.isEmpty() && this.sha1.length() >= 8 ? "http://" + host + ":" + this.port + "/clashmc_ui.zip?v=" + this.sha1.substring(0, 8) : null;
    }

    /**
     * server.properties 에 합친 팩 주소·sha1·id 를 적어둠 → 다음 재시작부터 접속 로딩 화면에서 바로 적용,
     * 같은 버전이면 클라이언트가 다시 안 받음 (캐시). 값이 같으면 파일 안 건드림
     */
    private void syncServerProperties(FileConfiguration cfg) {
        if (!cfg.getBoolean("ui.pack-host.server-properties", true)) {
            return;
        }

        String url = this.fixedUrl();
        if (url == null) {
            this.log.info("server.properties 리소스팩 자동 등록 건너뜀: 고정 주소 없음 → config ui.pack-host.address 에 서버 주소(예: play.myserver.kr)를 넣으면 접속할 때 로딩 화면에서 바로 적용됨");
            return;
        }

        try {
            File f = new File("server.properties");
            if (!f.isFile()) {
                return;
            }

            java.util.List<String> lines = Files.readAllLines(f.toPath(), java.nio.charset.StandardCharsets.ISO_8859_1);
            java.util.Map<String, String> want = new java.util.LinkedHashMap<>();
            want.put("resource-pack", url.replace(":", "\\:").replace("=", "\\="));
            want.put("resource-pack-sha1", this.sha1);
            want.put("resource-pack-id", PACK_ID.toString());
            boolean changed = false;
            java.util.Set<String> seen = new java.util.HashSet<>();
            for (int i = 0; i < lines.size(); i++) {
                String ln = lines.get(i);
                int eq = ln.indexOf('=');
                if (eq <= 0 || ln.startsWith("#")) {
                    continue;
                }

                String key = ln.substring(0, eq).trim();
                if (want.containsKey(key)) {
                    seen.add(key);
                    String nl = key + "=" + want.get(key);
                    if (!nl.equals(ln)) {
                        lines.set(i, nl);
                        changed = true;
                    }
                }
            }

            for (java.util.Map.Entry<String, String> e : want.entrySet()) {
                if (!seen.contains(e.getKey())) {
                    lines.add(e.getKey() + "=" + e.getValue());
                    changed = true;
                }
            }

            if (changed) {
                Files.write(f.toPath(), lines, java.nio.charset.StandardCharsets.ISO_8859_1);
                this.log.info("server.properties 에 리소스팩 등록 (sha1 " + this.sha1.substring(0, 8) + ") → 다음 재시작부터 접속 로딩 화면에서 바로 적용");
            }
        } catch (Exception ex) {
            this.log.warning("server.properties 리소스팩 등록 실패: " + ex);
        }
    }

    void stop() {
        if (this.server != null) {
            try {
                this.server.stop(0);
            } catch (Throwable var2) {
            }

            this.server = null;
        }
    }

    String urlFor(Player var1) {
        if (!this.running()) {
            return null;
        } else {
            String var2 = this.address;
            if (var2 == null || var2.isEmpty()) {
                try {
                    InetSocketAddress var3 = var1.getVirtualHost();
                    if (var3 != null) {
                        var2 = var3.getHostString();
                    }
                } catch (Throwable var4) {
                }
            }

            if (var2 == null || var2.isEmpty()) {
                var2 = Bukkit.getIp();
            }

            return var2 != null && !var2.isEmpty() ? "http://" + var2 + ":" + this.port + "/clashmc_ui.zip?v=" + this.sha1.substring(0, 8) : null;
        }
    }

    private static byte[] sha(byte[] var0) throws Exception {
        return MessageDigest.getInstance("SHA-1").digest(var0);
    }

    private static String hex(byte[] var0) {
        StringBuilder var1 = new StringBuilder();

        for (byte var5 : var0) {
            var1.append(String.format("%02x", var5));
        }

        return var1.toString();
    }
}
