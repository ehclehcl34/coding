package kr.kjmn.clashmc;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.ItemStack;

/** 스트리머 모드 · 관전 GUI */
final class StreamerMenus {
    static final char BG_STREAMER = '';
    static final char BG_SPECTATE = '';
    static final char BG_ADMIN = '';

    private StreamerMenus() {
    }

    private static String onOff(boolean b) {
        return b ? "§a● 켜짐" : "§7○ 꺼짐";
    }

    /** /스트리머 를 그냥 쳤을 때 */
    static void openFor(Clash core, Player p) {
        if (core.streamers.streamers.containsKey(p.getUniqueId())) {
            new StreamerMenu(core, p).open();
        } else if (p.hasPermission("clash.admin")) {
            new AdminMenu(core, p).open();
        } else {
            p.sendMessage("§c관리자가 지정한 스트리머만 쓸 수 있습니다.");
        }
    }

    // ------------------------------------------------------------ 스트리머 설정
    static final class StreamerMenu extends Menus.Menu {
        StreamerMenu(Clash core, Player viewer) {
            super(core, viewer);
        }

        @Override
        String title() {
            Streamers.Opt o = this.core.streamers.streamers.get(this.viewer.getUniqueId());
            return Ui.title(BG_STREAMER, "스트리머 모드" + (o != null && o.on ? " §c● LIVE" : ""));
        }

        private void toggle(int slot, int r0, int c0, int r1, int c1, String id, Material mat, String name, boolean state, List<String> lore, Runnable act) {
            List<String> l = new ArrayList<>(lore);
            l.add("");
            l.add("§f지금: " + onOff(state));
            l.add("§e클릭: " + (state ? "끄기" : "켜기"));
            this.panel(r0, c0, r1, c1, name, l, mat, x -> {
                act.run();
                this.refresh();
            });
            this.set(slot, Ui.glow(Ui.icon(id, mat, name, l), state), x -> {
                act.run();
                this.refresh();
            });
        }

        @Override
        void render() {
            Streamers st = this.core.streamers;
            Streamers.Opt o = st.streamers.get(this.viewer.getUniqueId());
            if (o == null) {
                this.viewer.closeInventory();
                return;
            }

            this.toggle(10, 0, 0, 2, 2, o.on ? "live_on" : "live_off", Material.REDSTONE_TORCH, "§c§l스트리머 모드", o.on,
                List.of("§7켜면: LIVE 표시 · F3 좌표 숨김", "§7방 코드 · 대기열 인원 숨김", "§7매칭 랜덤 지연 · 내 경기 관전 차단"),
                () -> st.setOn(this.viewer, !o.on));
            this.toggle(13, 0, 3, 2, 5, o.whisperBlock ? "whisper_on" : "whisper_off", Material.WRITABLE_BOOK, "§d§l귓속말 · 초대 차단", o.whisperBlock,
                List.of("§7스트리머 모드일 때", "§7다른 사람의 귓속말 / 친선전 방 초대를 막음"),
                () -> st.setOption(this.viewer, "whisper"));
            this.toggle(16, 0, 6, 2, 8, o.filter ? "filter_on" : "filter_off", Material.SHIELD, "§6§l욕설 · 링크 가리기", o.filter,
                List.of("§7스트리머 모드일 때 내 화면 채팅에서", "§7욕설은 ***, 링크·IP 는 [링크] 로 가림"),
                () -> st.setOption(this.viewer, "filter"));
            this.toggle(28, 3, 0, 4, 2, o.chatOff ? "chat_hidden" : "chat_shown", Material.OAK_SIGN, "§9§l전체채팅 끄기", o.chatOff,
                List.of("§7스트리머 모드일 때 다른 사람 전체채팅을 안 보이게", "§7(팀 채팅 · 게임 메시지는 보임)"),
                () -> st.setOption(this.viewer, "chat"));

            List<String> sl = List.of("§7지금 진행 중인 경기를 골라 관전", "", "§e클릭: 관전 목록 열기");
            this.panel(3, 3, 4, 5, "§3§l관전 목록", sl, Material.ENDER_EYE, x -> new SpectateMenu(this.core, this.viewer).open());
            this.set(31, Ui.icon("spectate", Material.ENDER_EYE, "§3§l관전 목록", sl), x -> new SpectateMenu(this.core, this.viewer).open());

            List<String> help = List.of(
                "§f/스트리머 §7- 이 메뉴",
                "§f/관전 §7- 관전 목록",
                "§7경기 중 §e!§7로 시작하면 전체 채팅",
                "§7스트리머 모드가 켜진 사람이 있는 경기는",
                "§7아무도 관전할 수 없습니다"
            );
            this.panel(3, 6, 4, 8, "§f§l도움말", help, Material.BOOK, null);
            this.set(34, Ui.icon("info", Material.BOOK, "§f§l도움말", help), null);

            this.backButton(45, () -> new Menus.MainMenu(this.core, this.viewer).open());
            if (this.viewer.hasPermission("clash.admin")) {
                this.set(49, Ui.icon("streamer", Material.NAME_TAG, "§d§l스트리머 관리 §7(관리자)", "§7스트리머 지정 / 해제 · 전체 관전 켜고 끄기"),
                    x -> new AdminMenu(this.core, this.viewer).open());
            }

            this.set(53, Ui.icon("close", Material.BARRIER, "§c닫기"), x -> this.viewer.closeInventory());
        }
    }

    // ------------------------------------------------------------ 관전 목록
    static final class SpectateMenu extends Menus.Menu {
        int page;

        SpectateMenu(Clash core, Player viewer) {
            super(core, viewer);
        }

        @Override
        String title() {
            return Ui.title(BG_SPECTATE, "관전");
        }

        private static String names(GameTeam t) {
            if (t == null || t.members.isEmpty()) {
                return "§8-";
            }

            StringBuilder sb = new StringBuilder();
            for (UUID id : t.members) {
                if (sb.length() > 0) {
                    sb.append("§7, ");
                }

                sb.append(id.equals(t.king) ? "§6♚" : "§f").append(GameManager.nameOf(id));
            }

            return sb.toString();
        }

        @Override
        void render() {
            Streamers st = this.core.streamers;
            boolean admin = this.viewer.hasPermission("clash.admin");
            List<GameManager> list = new ArrayList<>();
            for (GameManager gm : this.core.matches) {
                if (gm.mode != GameManager.Mode.TEST && (gm.phase == GameManager.Phase.DECK || gm.phase == GameManager.Phase.PLAYING)) {
                    list.add(gm);
                }
            }

            int pages = Math.max(1, (list.size() + 35) / 36);
            this.page = Math.max(0, Math.min(this.page, pages - 1));
            if (!st.spectateEnabled) {
                this.set(22, Ui.icon("spectate_off", Material.BARRIER, "§c지금은 관전이 꺼져 있습니다", "§7관리자가 관전을 막아 두었습니다"), null);
            } else if (list.isEmpty()) {
                this.set(22, Ui.icon("info", Material.PAPER, "§7진행 중인 경기가 없습니다"), null);
            } else {
                int slot = 9;
                for (GameManager gm : list.subList(this.page * 36, Math.min(list.size(), (this.page + 1) * 36))) {
                    boolean live = st.liveMatch(gm);
                    GameTeam blue = gm.teams.get(TeamColor.BLUE);
                    GameTeam red = gm.teams.get(TeamColor.RED);
                    List<String> lore = new ArrayList<>();
                    lore.add("§7" + gm.modeName() + (gm.assault ? " §c(돌격전)" : "") + " §8· §7" + (gm.phase == GameManager.Phase.DECK ? "덱 고르는 중" : "경기 중"));
                    lore.add("§9파랑 §f" + (blue == null ? 0 : blue.crowns) + " §7: §c" + (red == null ? 0 : red.crowns) + " 빨강");
                    lore.add("§9파랑: " + names(blue));
                    lore.add("§c빨강: " + names(red));
                    lore.add("");
                    ItemStack it;
                    if (live) {
                        lore.add("§c스트리머 경기라 관전할 수 없습니다");
                        it = Ui.icon("lock", Material.IRON_BARS, "§c경기 #" + gm.id + " §8(관전 불가)", lore);
                    } else {
                        lore.add("§e클릭: 관전하기");
                        it = Ui.icon(gm.assault ? "assault" : "play", Material.IRON_SWORD, "§f경기 #" + gm.id, lore);
                    }

                    this.set(slot++, it, x -> {
                        if (st.liveMatch(gm)) {
                            this.viewer.sendMessage("§c스트리머 경기는 관전할 수 없습니다.");
                            this.refresh();
                        } else {
                            this.viewer.closeInventory();
                            st.spectateMatch(this.viewer, gm, null);
                        }
                    });
                }
            }

            this.backButton(45, () -> new Menus.MainMenu(this.core, this.viewer).open());
            if (admin) {
                boolean on = st.spectateEnabled;
                this.set(47, Ui.icon(on ? "spectate" : "spectate_off", on ? Material.ENDER_EYE : Material.ENDER_PEARL, "§b§l전체 관전 " + onOff(on), "§7관리자 전용 · 서버 전체 관전을 켜고 끔", "§e클릭: " + (on ? "끄기" : "켜기")), x -> {
                    st.setSpectateEnabled(this.viewer, !st.spectateEnabled);
                    this.refresh();
                });
            }

            if (st.spectating(this.viewer)) {
                this.set(49, Ui.icon("leave", Material.OAK_DOOR, "§c§l관전 나가기", "§7로비로 돌아갑니다"), x -> {
                    this.viewer.closeInventory();
                    st.stopSpectate(this.viewer, "§7관전을 그만뒀습니다.");
                });
            } else {
                this.set(49, Ui.icon("info", Material.PAPER, "§f관전 방법", "§7경기를 클릭하면 그 경기장으로 이동", "§7나가기: §f/관전 나가기 §7또는 §f/clash leave"), null);
            }

            if (pages > 1) {
                this.set(51, Ui.icon("page_next", Material.ARROW, "§e다음 ▶", "§7" + (this.page + 1) + " / " + pages), x -> {
                    this.page = (this.page + 1) % pages;
                    this.refresh();
                });
            }

            this.set(53, Ui.icon("close", Material.BARRIER, "§c닫기"), x -> this.viewer.closeInventory());
        }
    }

    // ------------------------------------------------------------ 스트리머 관리 (관리자)
    static final class AdminMenu extends Menus.Menu {
        int page;

        AdminMenu(Clash core, Player viewer) {
            super(core, viewer);
        }

        @Override
        String title() {
            return Ui.title(BG_ADMIN, "스트리머 관리 §8(" + this.core.streamers.streamers.size() + "명)");
        }

        @Override
        void render() {
            if (!this.viewer.hasPermission("clash.admin")) {
                this.viewer.closeInventory();
                return;
            }

            Streamers st = this.core.streamers;
            // 지정된 스트리머 먼저, 그다음 접속 중인 나머지
            Map<UUID, String> all = new LinkedHashMap<>();
            for (Map.Entry<UUID, Streamers.Opt> e : st.streamers.entrySet()) {
                all.put(e.getKey(), e.getValue().name);
            }

            for (Player op : Bukkit.getOnlinePlayers()) {
                all.putIfAbsent(op.getUniqueId(), op.getName());
            }

            List<Map.Entry<UUID, String>> list = new ArrayList<>(all.entrySet());
            int pages = Math.max(1, (list.size() + 35) / 36);
            this.page = Math.max(0, Math.min(this.page, pages - 1));
            int slot = 9;
            for (Map.Entry<UUID, String> e : list.subList(this.page * 36, Math.min(list.size(), (this.page + 1) * 36))) {
                UUID id = e.getKey();
                Streamers.Opt o = st.streamers.get(id);
                boolean online = Bukkit.getPlayer(id) != null;
                List<String> lore = new ArrayList<>();
                if (o != null) {
                    lore.add("§d● 스트리머 §7(모드 " + (o.on ? "§c켜짐" : "§7꺼짐") + "§7)");
                    lore.add(online ? "§a접속 중" : "§8오프라인");
                    lore.add("");
                    lore.add("§c클릭: 스트리머 지정 해제");
                } else {
                    lore.add("§7일반 플레이어");
                    lore.add("");
                    lore.add("§e클릭: 스트리머로 지정");
                }

                ItemStack head = Ui.head(id, (o != null ? "§d§l" : "§f") + e.getValue(), lore);
                this.set(slot++, Ui.glow(head, o != null), x -> {
                    if (st.streamers.containsKey(id)) {
                        st.undesignate(this.viewer, id);
                    } else {
                        st.designate(this.viewer, id, e.getValue());
                    }

                    this.refresh();
                });
            }

            this.backButton(45, () -> {
                if (st.streamers.containsKey(this.viewer.getUniqueId())) {
                    new StreamerMenu(this.core, this.viewer).open();
                } else {
                    new Menus.MainMenu(this.core, this.viewer).open();
                }
            });

            if (pages > 1) {
                this.set(47, Ui.icon("page_prev", Material.ARROW, "§e◀ 이전", "§7" + (this.page + 1) + " / " + pages), x -> {
                    this.page = (this.page - 1 + pages) % pages;
                    this.refresh();
                });
                this.set(51, Ui.icon("page_next", Material.ARROW, "§e다음 ▶", "§7" + (this.page + 1) + " / " + pages), x -> {
                    this.page = (this.page + 1) % pages;
                    this.refresh();
                });
            }

            boolean on = st.spectateEnabled;
            this.set(49, Ui.icon(on ? "spectate" : "spectate_off", on ? Material.ENDER_EYE : Material.ENDER_PEARL, "§b§l전체 관전 " + onOff(on), "§7서버 전체 관전을 켜고 끔", "§7(스트리머 경기는 항상 관전 불가)", "§e클릭: " + (on ? "끄기" : "켜기")), x -> {
                st.setSpectateEnabled(this.viewer, !st.spectateEnabled);
                this.refresh();
            });
            this.set(53, Ui.icon("close", Material.BARRIER, "§c닫기"), x -> this.viewer.closeInventory());
        }
    }
}
