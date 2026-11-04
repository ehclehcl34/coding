package kr.kjmn.clashmc;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import org.bukkit.Bukkit;
import org.bukkit.Material;
import org.bukkit.entity.Player;
import org.bukkit.inventory.Inventory;
import org.bukkit.inventory.InventoryHolder;
import org.bukkit.inventory.ItemStack;
import org.bukkit.inventory.meta.ItemMeta;

final class Menus {
    private Menus() {
    }

    static String avg(Clash var0, List<String> var1) {
        int var2 = 0;
        int var3 = 0;

        for (String var5 : var1) {
            CardDef var6 = var0.cards.get(var5);
            if (var6 != null) {
                var2 += var6.elixir;
                var3++;
            }
        }

        return var3 == 0 ? "-" : String.format("%.1f", (double)var2 / var3);
    }

    static final class AiMenu extends Menus.Menu {
        AiMenu(Clash var1, Player var2) {
            super(var1, var2);
        }

        @Override
        String title() {
            return Ui.title('\ue107', "AI 대전 - 난이도");
        }

        @Override
        void render() {
            Room var1 = this.core.roomOf.get(this.viewer.getUniqueId());
            String var2 = var1 == null ? "§7혼자 출전 (유닛은 전부 AI)" : "§7방 인원 " + var1.members.size() + "명이 한 팀으로 출전";
            this.panel(1, 0, 3, 2, "§a§l쉬움", List.of("§7봇이 느리고 무작위로 둡니다", var2, "", "§e클릭: 시작"), Material.WOODEN_SWORD, var1x -> this.go(Bot.Level.EASY));
            this.panel(1, 3, 3, 5, "§e§l보통", List.of("§7위협에 반응하고 스펠을 노립니다", var2, "", "§e클릭: 시작"), Material.IRON_SWORD, var1x -> this.go(Bot.Level.NORMAL));
            this.panel(1, 6, 3, 8, "§c§l어려움", List.of("§7엘릭서를 모아 한 라인 몰아치기", var2, "", "§e클릭: 시작"), Material.DIAMOND_SWORD, var1x -> this.go(Bot.Level.HARD));
            this.set(49, Ui.icon("assault", Material.DIAMOND_SWORD, "§c§l돌격전 §7(미니게임)",
                "§740 엘릭서 안에서 유닛 카드만 골라 (중복 가능)",
                "§7양쪽 군대가 한꺼번에 돌격!",
                "§7마지막까지 유닛이 남은 팀 승리 · 타워 없음",
                var2,
                "",
                "§e클릭: 봇과 돌격전"), var1x -> {
                this.viewer.closeInventory();
                this.core.startAi(this.viewer, Bot.Level.NORMAL, true);
            });
            this.backButton(45, () -> new Menus.MainMenu(this.core, this.viewer).open());
        }

        private void go(Bot.Level var1) {
            this.viewer.closeInventory();
            this.core.startAi(this.viewer, var1);
        }
    }

    static final class DeckListMenu extends Menus.Menu {
        private final List<String> matchDeck;
        private final GameManager match;
        private static final int[] SLOTS = {10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34};

        DeckListMenu(Clash c, Player p, List<String> matchDeck, GameManager match) {
            super(c, p);
            this.matchDeck = matchDeck;
            this.match = match;
        }

        @Override
        String title() {
            return Ui.title('\ue101', "덱 불러오기");
        }

        @Override
        void render() {
            Profile pr = this.core.profiles.get(this.viewer);
            List<String> cur = this.matchDeck != null ? this.matchDeck : pr.deck();
            for (int i = 0; i < Profile.DECK_SLOTS && i < SLOTS.length; i++) {
                int idx = i;
                List<String> d = pr.decks.get(i);
                boolean on = this.matchDeck == null && pr.activeDeck == i;
                List<String> lore = new ArrayList<>();
                lore.add("§7" + d.size() + "/8장 §8| §d평균 엘릭서 §f" + Menus.avg(this.core, d));
                for (String id : d) {
                    CardDef cd = this.core.cards.get(id);
                    lore.add("§8- §f" + (cd == null ? id : cd.name) + (cd == null ? "" : " §d" + cd.elixir));
                }
                lore.add("");
                if (on) {
                    lore.add("§a사용 중");
                } else {
                    lore.add(d.isEmpty() ? "§8비어 있음" : (this.matchDeck != null ? "§e클릭: 이번 판 덱으로 불러오기" : "§e클릭: 이 덱 사용"));
                }
                lore.add("§bShift+클릭: 지금 덱을 이 칸에 저장");
                ItemStack it = Ui.icon(on ? "deck_tab_on" : "deck_tab", on ? Material.LIME_DYE : (d.isEmpty() ? Material.GRAY_DYE : Material.LIGHT_BLUE_DYE),
                    (on ? "§a§l" : "§f") + "덱 " + (i + 1), lore);
                it.setAmount(i + 1);
                this.set(SLOTS[i], Ui.glow(it, on), shift -> {
                    if (shift) {
                        if (pr.decks.get(idx) != cur) {
                            pr.decks.get(idx).clear();
                            pr.decks.get(idx).addAll(cur);
                        }
                        pr.dirty = true;
                        this.viewer.playSound(this.viewer.getLocation(), "entity.experience_orb.pickup", 0.6F, 1.4F);
                        this.viewer.sendActionBar("§a덱 " + (idx + 1) + " 에 저장했습니다");
                        this.open();
                        return;
                    }
                    if (this.matchDeck != null) {
                        if (pr.decks.get(idx).isEmpty()) {
                            return;
                        }
                        this.matchDeck.clear();
                        for (String id : pr.decks.get(idx)) {
                            if (this.matchDeck.size() < 8 && !this.matchDeck.contains(id) && this.core.cards.get(id) != null) {
                                this.matchDeck.add(id);
                            }
                        }
                    } else {
                        pr.activeDeck = idx;
                        pr.dirty = true;
                    }
                    new Menus.DeckMenu(this.core, this.viewer, this.matchDeck, this.match).open();
                });
            }
            this.backButton(45, () -> new Menus.DeckMenu(this.core, this.viewer, this.matchDeck, this.match).open());
        }
    }

    static final class DeckMenu extends Menus.Menu {
        private final List<String> matchDeck;
        private final GameManager match;
        private int page;
        private static final int PER_PAGE = 27;
        /** 플레이어별 정렬 방식 (true: 희귀도순) */
        private static final java.util.Map<java.util.UUID, Boolean> SORT_RARITY = new java.util.HashMap<>();

        DeckMenu(Clash var1, Player var2, List<String> var3, GameManager var4) {
            super(var1, var2);
            this.matchDeck = var3;
            this.match = var4;
        }

        List<String> deck() {
            return this.matchDeck != null ? this.matchDeck : this.core.profiles.get(this.viewer).deck();
        }

        @Override
        String title() {
            Profile var1 = this.core.profiles.get(this.viewer);
            return Ui.title(
                '\ue101', this.match != null ? "이번 판 덱 (" + this.deck().size() + "/8)" : "덱 " + (var1.activeDeck + 1) + " (" + this.deck().size() + "/8)"
            );
        }

        @Override
        void render() {
            List<String> var1 = this.deck();
            Profile var2 = this.core.profiles.get(this.viewer);

            for (int var3 = 0; var3 < 8; var3++) {
                if (var3 < var1.size()) {
                    CardDef var4 = this.core.cards.get(var1.get(var3));
                    ItemStack var5 = this.core.cardItem(var4, false, false);
                    String var6 = (String)var1.get(var3);
                    this.set(var3, lore(var5, "§c클릭: 덱에서 빼기"), var2x -> {
                        this.deck().remove(var6);
                        this.dirty();
                        this.reopen();
                    });
                } else {
                    this.set(var3, Ui.icon("slot_empty", Material.LIGHT_GRAY_STAINED_GLASS_PANE, "§7빈 칸", "§7아래 카드를 눌러 넣기"), null);
                }
            }

            int var14 = 0;

            for (String var17 : var1) {
                CardDef var18 = this.core.cards.get(var17);
                if (var18 != null) {
                    var14 += var18.elixir;
                }
            }

            double var16 = var1.isEmpty() ? 0.0 : (double)var14 / var1.size();
            ItemStack var19 = Ui.icon(
                "elixir",
                Material.AMETHYST_SHARD,
                "§d평균 엘릭서 §f" + (var1.isEmpty() ? "-" : String.format("%.1f", var16)),
                "§7" + var1.size() + "/8장",
                var16 >= 4.3 ? "§c무거운 덱" : (var16 > 0.0 && var16 <= 3.0 ? "§a빠른 사이클 덱" : "§7균형 잡힌 덱")
            );
            var19.setAmount(Math.max(1, (int)Math.round(var16)));
            this.set(8, var19, null);
            ArrayList<CardDef> var7 = new ArrayList<>();

            for (CardDef var9 : this.core.cards.values()) {
                if (this.core.usable(var9)) {
                    var7.add(var9);
                }
            }

            boolean byRarity = SORT_RARITY.getOrDefault(this.viewer.getUniqueId(), false);
            if (byRarity) {
                var7.sort(Comparator.<CardDef>comparingInt(var0 -> var0.rarity).thenComparingInt(var0 -> var0.elixir).thenComparing(var0 -> var0.name));
            } else {
                var7.sort(Comparator.<CardDef>comparingInt(var0 -> var0.elixir).thenComparingInt(var0 -> var0.rarity).thenComparing(var0 -> var0.name));
            }
            int var20 = Math.max(1, (var7.size() + 27 - 1) / 27);
            this.page = Math.max(0, Math.min(this.page, var20 - 1));
            int var21 = 9;

            for (CardDef var11 : var7.subList(this.page * 27, Math.min(var7.size(), (this.page + 1) * 27))) {
                if (var21 >= 36) {
                    break;
                }

                boolean var12 = var1.contains(var11.id);
                ItemStack var13 = this.core.cardItem(var11, false, var12);
                lore(var13, var12 ? "§a✔ 덱에 있음 §7(클릭: 빼기)" : (var1.size() >= 8 ? "§c덱이 가득 참" : "§e클릭: 덱에 넣기"));
                this.set(var21++, var13, var2x -> {
                    if (this.deck().contains(var11.id)) {
                        this.deck().remove(var11.id);
                    } else {
                        if (this.deck().size() >= 8) {
                            this.viewer.playSound(this.viewer.getLocation(), "block.note_block.bass", 1.0F, 0.6F);
                            return;
                        }

                        this.deck().add(var11.id);
                    }

                    this.dirty();
                    this.reopen();
                });
            }

            this.set(36, Ui.icon("deck", Material.BOOK, "§b§l덱 불러오기",
                this.match == null ? "§7저장된 덱 " + Profile.DECK_SLOTS + "개 중 골라 쓰기" : "§7저장된 덱을 이번 판 덱으로",
                "§e클릭: 덱 목록 열기"), var1x -> new Menus.DeckListMenu(this.core, this.viewer, this.matchDeck, this.match).open());
            if (this.match == null) {
                int cur = var2.activeDeck;
                this.set(37, Ui.icon("page_prev", Material.ARROW, "§e◀ 이전 덱", "§7지금: 덱 " + (cur + 1)), var1x -> {
                    var2.activeDeck = (cur + Profile.DECK_SLOTS - 1) % Profile.DECK_SLOTS;
                    var2.dirty = true;
                    this.reopen();
                });
                this.set(38, Ui.icon("page_next", Material.ARROW, "§e다음 덱 ▶", "§7지금: 덱 " + (cur + 1)), var1x -> {
                    var2.activeDeck = (cur + 1) % Profile.DECK_SLOTS;
                    var2.dirty = true;
                    this.reopen();
                });
            }

            this.set(46, Ui.glow(Ui.icon("elixir", Material.AMETHYST_SHARD, (byRarity ? "§7" : "§d§l✔ ") + "엘릭서순 정렬", "§7엘릭서 낮은 카드부터"), !byRarity), var1x -> {
                SORT_RARITY.put(this.viewer.getUniqueId(), false);
                this.page = 0;
                this.reopen();
            });
            this.set(47, Ui.glow(Ui.icon("trophy", Material.GOLD_INGOT, (byRarity ? "§6§l✔ " : "§7") + "희귀도순 정렬", "§7일반 → 레어 → 에픽 → 전설"), byRarity), var1x -> {
                SORT_RARITY.put(this.viewer.getUniqueId(), true);
                this.page = 0;
                this.reopen();
            });
            this.set(42, Ui.icon("random", Material.ENDER_PEARL, "§b랜덤 채우기", "§7빈 칸을 무작위 카드로"), var1x -> {
                ArrayList<String> var2x = new ArrayList<>();

                for (CardDef var4x : this.core.cards.values()) {
                    if (this.core.usable(var4x)) {
                        var2x.add(var4x.id);
                    }
                }

                Collections.shuffle(var2x);

                for (String var6x : var2x) {
                    if (this.deck().size() < 8 && !this.deck().contains(var6x)) {
                        this.deck().add(var6x);
                    }
                }

                this.dirty();
                this.reopen();
            });
            this.set(43, Ui.icon("clear", Material.LAVA_BUCKET, "§c전부 빼기"), var1x -> {
                this.deck().clear();
                this.dirty();
                this.reopen();
            });
            if (var20 > 1) {
                String var23 = "§7" + (this.page + 1) + " / " + var20 + " 쪽";
                if (this.page > 0) {
                    this.set(48, Ui.icon("page_prev", Material.ARROW, "§e◀ 이전 카드", var23), var1x -> {
                        this.page--;
                        this.reopen();
                    });
                }

                if (this.page < var20 - 1) {
                    this.set(50, Ui.icon("page_next", Material.ARROW, "§e다음 카드 ▶", var23), var1x -> {
                        this.page++;
                        this.reopen();
                    });
                }
            }

            this.backButton(45, () -> {
                if (this.match == null) {
                    new Menus.MainMenu(this.core, this.viewer).open();
                } else {
                    this.viewer.closeInventory();
                }
            });
            boolean var24 = var1.size() == 8;
            if (this.match != null) {
                this.set(
                    53,
                    Ui.icon(
                        var24 ? "confirm" : "confirm_off",
                        var24 ? Material.EMERALD_BLOCK : Material.REDSTONE_BLOCK,
                        var24 ? "§a§l이 덱으로 출전" : "§c8장을 채워야 출전 (" + var1.size() + "/8)",
                        "§7제한 시간이 지나면 빈 칸은 자동으로 채워집니다"
                    ),
                    var1x -> {
                        if (this.deck().size() == 8) {
                            this.match.confirmDeck(this.viewer);
                        }
                    }
                );
            } else {
                this.set(
                    53,
                    Ui.icon(
                        var24 ? "confirm" : "confirm_off",
                        var24 ? Material.EMERALD_BLOCK : Material.REDSTONE_BLOCK,
                        var24 ? "§a§l저장됨" : "§e" + var1.size() + "/8장",
                        "§7변경 사항은 자동 저장됩니다",
                        "§7랭크전 / 친선전 / AI 대전에 이 덱을 사용"
                    ),
                    var1x -> this.viewer.closeInventory()
                );
            }
        }

        private void dirty() {
            this.core.profiles.get(this.viewer).dirty = true;
        }

        private void reopen() {
            this.open();
        }

        private static ItemStack lore(ItemStack var0, String var1) {
            ItemMeta var2 = var0.getItemMeta();
            if (var2 == null) {
                return var0;
            } else {
                ArrayList var3 = var2.getLore() == null ? new ArrayList() : new ArrayList(var2.getLore());
                if (!var3.isEmpty()) {
                    var3.remove(var3.size() - 1);
                }

                var3.add(var1);
                var2.setLore(var3);
                var0.setItemMeta(var2);
                return var0;
            }
        }
    }

    /** 관리자: 유저가 쓸 수 있는 카드 켜기/끄기 (/clash cards) */
    static final class CardAdminMenu extends Menus.Menu {
        private int page;

        CardAdminMenu(Clash var1, Player var2) {
            super(var1, var2);
        }

        private List<CardDef> list() {
            ArrayList<CardDef> l = new ArrayList<>();
            for (CardDef c : this.core.cards.values()) {
                if (c.deckable) {
                    l.add(c);
                }
            }
            l.sort(Comparator.<CardDef>comparingInt(c -> c.elixir).thenComparingInt(c -> c.rarity).thenComparing(c -> c.name));
            return l;
        }

        @Override
        String title() {
            int on = 0;
            List<CardDef> l = this.list();
            for (CardDef c : l) {
                if (this.core.usable(c)) on++;
            }
            return "§8카드 관리 (사용 " + on + "/" + l.size() + ")";
        }

        @Override
        void render() {
            List<CardDef> l = this.list();
            int pages = Math.max(1, (l.size() + 44) / 45);
            this.page = Math.max(0, Math.min(this.page, pages - 1));
            int slot = 0;
            for (CardDef c : l.subList(this.page * 45, Math.min(l.size(), (this.page + 1) * 45))) {
                boolean on = this.core.usable(c);
                ItemStack it = this.core.cardItem(c, false, !on);
                ItemMeta m = it.getItemMeta();
                if (m != null) {
                    m.setDisplayName((on ? "§a✔ " : "§c✘ ") + c.name + " §8(" + c.id + ")");
                    ArrayList<String> lore = m.getLore() == null ? new ArrayList<>() : new ArrayList<>(m.getLore());
                    if (!lore.isEmpty()) lore.remove(lore.size() - 1);
                    lore.add(on ? "§a사용 가능 §7(클릭: 끄기)" : "§c사용 불가 §7(클릭: 켜기)");
                    m.setLore(lore);
                    it.setItemMeta(m);
                }
                this.set(slot++, Ui.glow(it, on), x -> {
                    this.core.setCardEnabled(c.id, !this.core.usable(c));
                    this.open();
                });
            }
            if (this.page > 0) {
                this.set(45, Ui.icon("page_prev", Material.ARROW, "§e◀ 이전", "§7" + (this.page + 1) + " / " + pages), x -> {
                    this.page--;
                    this.open();
                });
            }
            this.set(48, Ui.icon("confirm", Material.EMERALD_BLOCK, "§a전부 켜기"), x -> {
                for (CardDef c : l) this.core.disabledCards.remove(c.id);
                this.core.saveDisabledCards();
                this.open();
            });
            this.set(49, Ui.icon("close", Material.BARRIER, "§7닫기", "§7변경은 바로 저장 (plugins/ClashMC/cards.yml)", "§7진행 중인 경기 덱에는 다음 판부터 적용"), x -> this.viewer.closeInventory());
            this.set(50, Ui.icon("clear", Material.REDSTONE_BLOCK, "§c전부 끄기"), x -> {
                for (CardDef c : l) this.core.disabledCards.add(c.id);
                this.core.saveDisabledCards();
                this.open();
            });
            if (this.page < pages - 1) {
                this.set(53, Ui.icon("page_next", Material.ARROW, "§e다음 ▶", "§7" + (this.page + 1) + " / " + pages), x -> {
                    this.page++;
                    this.open();
                });
            }
        }
    }

    static final class LeaderboardMenu extends Menus.Menu {
        LeaderboardMenu(Clash var1, Player var2) {
            super(var1, var2);
        }

        @Override
        String title() {
            return Ui.title('\ue105', "랭킹 TOP 21");
        }

        @Override
        void render() {
            List var1 = this.core.profiles.top(21);
            int[] var2 = new int[]{4, 12, 14, 19, 20, 21, 22, 23, 24, 25, 28, 29, 30, 31, 32, 33, 34, 37, 38, 39, 40};

            for (int var3 = 0; var3 < var1.size() && var3 < var2.length; var3++) {
                Profile var4 = (Profile)var1.get(var3);
                this.set(
                    var2[var3],
                    Ui.head(
                        var4.id,
                        (var3 == 0 ? "§6§l① " : (var3 == 1 ? "§7§l② " : (var3 == 2 ? "§c§l③ " : "§f" + (var3 + 1) + ". "))) + "§f" + var4.name,
                        List.of(
                            Ranks.label(var4.trophies),
                            "§6\ud83c\udfc6 " + var4.trophies,
                            "§7승 " + var4.wins + " · 패 " + var4.losses + " (" + var4.winRate() + ")"
                        )
                    ),
                    null
                );
            }

            Profile var5 = this.core.profiles.get(this.viewer);
            int var6 = this.core.profiles.rankOf(this.viewer.getUniqueId());
            this.set(
                49,
                Ui.head(
                    this.viewer.getUniqueId(),
                    "§e나: " + (var6 > 0 ? var6 + "위" : "순위 없음"),
                    List.of(Ranks.label(var5.trophies), "§6\ud83c\udfc6 " + var5.trophies)
                ),
                null
            );
            this.backButton(45, () -> new Menus.MainMenu(this.core, this.viewer).open());
        }
    }

    /** 돌격전 군대 고르기: 클릭 = 1장 넣기, Shift+클릭 = 1장 빼기 (같은 카드 여러 장 가능) */
    static final class AssaultMenu extends Menus.Menu {
        private final List<String> army;
        private final GameManager match;
        private int page;
        private int armyPage;

        AssaultMenu(Clash c, Player p, List<String> army, GameManager match) {
            super(c, p);
            this.army = army;
            this.match = match;
        }

        @Override
        String title() {
            return Ui.title('', "돌격전 군대 " + Assault.cost(this.core, this.army) + "/" + this.match.as.budget + " 엘릭서");
        }

        private static ItemStack add(ItemStack it, List<String> lines) {
            ItemMeta m = it.getItemMeta();
            if (m != null) {
                List<String> l = m.getLore() == null ? new ArrayList<>() : new ArrayList<>(m.getLore());
                l.addAll(lines);
                m.setLore(l);
                it.setItemMeta(m);
            }
            return it;
        }

        private boolean editable() {
            if (this.match.phase != GameManager.Phase.DECK) {
                this.viewer.closeInventory();
                return false;
            }
            return true;
        }

        private void deny(String why) {
            this.viewer.playSound(this.viewer.getLocation(), "block.note_block.bass", 1.0F, 0.6F);
            this.viewer.sendActionBar("§c" + why);
        }

        @Override
        void render() {
            Assault as = this.match.as;
            Map<String, Integer> cnt = new java.util.LinkedHashMap<>();
            for (String id : this.army) {
                cnt.merge(id, 1, Integer::sum);
            }

            // 윗줄: 지금 군대 (카드별 장수). 종류 제한 없음, 8종류 넘으면 ◀ ▶ 로 넘겨 봄
            List<Map.Entry<String, Integer>> kinds = new ArrayList<>(cnt.entrySet());
            boolean more = kinds.size() > 8;
            int per = more ? 6 : 8;
            int armyPages = Math.max(1, (kinds.size() + per - 1) / per);
            this.armyPage = Math.max(0, Math.min(this.armyPage, armyPages - 1));
            int slot = more ? 1 : 0;
            if (more) {
                this.set(0, Ui.icon("page_prev", Material.ARROW, "§e◀ 군대 앞쪽", "§7" + (this.armyPage + 1) + " / " + armyPages + " · " + kinds.size() + "종류"), x -> {
                    this.armyPage = (this.armyPage + armyPages - 1) % armyPages;
                    this.open();
                });
                this.set(7, Ui.icon("page_next", Material.ARROW, "§e군대 뒤쪽 ▶", "§7" + (this.armyPage + 1) + " / " + armyPages + " · " + kinds.size() + "종류"), x -> {
                    this.armyPage = (this.armyPage + 1) % armyPages;
                    this.open();
                });
            }
            int last = more ? 7 : 8;
            for (Map.Entry<String, Integer> e : kinds.subList(Math.min(kinds.size(), this.armyPage * per), Math.min(kinds.size(), (this.armyPage + 1) * per))) {
                if (slot >= last) {
                    break;
                }
                CardDef cd = this.core.cards.get(e.getKey());
                if (cd == null) {
                    continue;
                }
                String id = e.getKey();
                ItemStack it = add(this.core.cardItem(cd, false, false), List.of("§a군대에 " + e.getValue() + "장", "§c클릭: 1장 빼기"));
                it.setAmount(Math.max(1, Math.min(64, e.getValue())));
                this.set(slot++, it, sh -> {
                    if (this.editable()) {
                        this.army.remove(id);
                        this.open();
                    }
                });
            }
            for (; slot < last; slot++) {
                this.set(slot, Ui.icon("slot_empty", Material.LIGHT_GRAY_STAINED_GLASS_PANE, "§7빈 칸", "§7아래 유닛 카드를 눌러 넣기"), null);
            }

            int cost = Assault.cost(this.core, this.army);
            int units = Assault.unitCount(this.core, this.army);
            List<String> info = new ArrayList<>();
            info.add("§7남은 엘릭서 §d" + (as.budget - cost));
            info.add("§7유닛 §f" + units + "/" + as.maxUnits + "마리 §8(렉 방지 상한)");
            info.add("§7카드 " + this.army.size() + "장 · " + cnt.size() + "종류");
            if (cnt.size() > 8) {
                info.add("");
                for (Map.Entry<String, Integer> e : cnt.entrySet()) {
                    CardDef cd = this.core.cards.get(e.getKey());
                    info.add("§8- §f" + (cd == null ? e.getKey() : cd.name) + " §7×" + e.getValue());
                }
            }
            ItemStack el = Ui.icon("elixir", Material.AMETHYST_SHARD, "§d엘릭서 §f" + cost + " §7/ " + as.budget, info);
            el.setAmount(Math.max(1, Math.min(64, as.budget - cost)));
            this.set(8, el, null);

            // 유닛 카드 목록 (마법·건물 제외)
            List<CardDef> pool = new ArrayList<>();
            for (CardDef c : this.core.cards.values()) {
                if (Assault.allowed(this.core, c)) {
                    pool.add(c);
                }
            }
            pool.sort(Comparator.<CardDef>comparingInt(c -> c.elixir).thenComparingInt(c -> c.rarity).thenComparing(c -> c.name));
            int pages = Math.max(1, (pool.size() + 26) / 27);
            this.page = Math.max(0, Math.min(this.page, pages - 1));
            int s = 9;
            for (CardDef cd : pool.subList(this.page * 27, Math.min(pool.size(), (this.page + 1) * 27))) {
                int n = cnt.getOrDefault(cd.id, 0);
                String why = as.cantAdd(this.army, cd);
                List<String> lines = new ArrayList<>();
                lines.add("§7유닛 " + Assault.units(this.core, cd) + "마리");
                if (n > 0) {
                    lines.add("§a✔ 군대에 " + n + "장");
                }
                lines.add(why == null ? "§e클릭: 1장 넣기" : "§c" + why);
                if (n > 0) {
                    lines.add("§bShift+클릭: 1장 빼기");
                }
                ItemStack it = add(this.core.cardItem(cd, false, why != null && n == 0), lines);
                it.setAmount(Math.max(1, Math.min(64, n)));
                this.set(s++, Ui.glow(it, n > 0), shift -> {
                    if (!this.editable()) {
                        return;
                    }
                    if (shift) {
                        if (this.army.remove(cd.id)) {
                            this.open();
                        }
                        return;
                    }
                    String w = as.cantAdd(this.army, cd);
                    if (w != null) {
                        this.deny(w);
                        return;
                    }
                    this.army.add(cd.id);
                    this.open();
                });
            }

            if (pages > 1) {
                String pg = "§7" + (this.page + 1) + " / " + pages + " 쪽";
                if (this.page > 0) {
                    this.set(48, Ui.icon("page_prev", Material.ARROW, "§e◀ 이전 카드", pg), x -> {
                        this.page--;
                        this.open();
                    });
                }
                if (this.page < pages - 1) {
                    this.set(50, Ui.icon("page_next", Material.ARROW, "§e다음 카드 ▶", pg), x -> {
                        this.page++;
                        this.open();
                    });
                }
            }

            this.set(42, Ui.icon("random", Material.ENDER_PEARL, "§b랜덤 채우기", "§7남은 엘릭서를 무작위 유닛으로"), x -> {
                if (this.editable()) {
                    as.fillRandom(this.army);
                    this.open();
                }
            });
            this.set(43, Ui.icon("clear", Material.LAVA_BUCKET, "§c전부 빼기"), x -> {
                if (this.editable()) {
                    this.army.clear();
                    this.open();
                }
            });
            this.set(45, Ui.icon("close", Material.BARRIER, "§7닫기", "§7/clash deck 으로 다시 열기"), x -> this.viewer.closeInventory());
            boolean ok = !this.army.isEmpty();
            this.set(53, Ui.icon(ok ? "confirm" : "confirm_off", ok ? Material.EMERALD_BLOCK : Material.REDSTONE_BLOCK,
                ok ? "§a§l이 군대로 출전" : "§c유닛을 넣어 주세요",
                "§7클릭 = 넣기 · Shift+클릭 = 빼기",
                "§7시간이 지나면 남은 엘릭서는 자동으로 채워집니다"), x -> {
                if (ok && this.editable()) {
                    this.match.confirmDeck(this.viewer);
                }
            });
        }
    }


    static final class MainMenu extends Menus.Menu {
        MainMenu(Clash var1, Player var2) {
            super(var1, var2);
        }

        @Override
        String title() {
            return Ui.title('\ue100', "클래시 마크");
        }

        @Override
        void render() {
            Profile var1 = this.core.profiles.get(this.viewer);
            boolean var2 = this.core.queued(this.viewer.getUniqueId());
            this.panel(
                0,
                0,
                2,
                2,
                "§a§lAI 대전",
                List.of("§7봇 킹과 1:1 (친선전 방이면 방 인원 전원 협동)", "§7트로피 변동 없음", "", "§e클릭: 난이도 선택"),
                Material.IRON_SWORD,
                var1x -> new Menus.AiMenu(this.core, this.viewer).open()
            );
            this.panel(
                0,
                3,
                2,
                5,
                var2 ? "§c§l랭크전 매칭 취소" : "§6§l랭크전",
                List.of(
                    "§7비슷한 트로피끼리 2~10명 자동 매칭",
                    "§7승리 시 트로피 획득 · 패배 시 §c킹§7이 더 많이 잃음",
                    (this.core.streamers.live(this.viewer) ? "§7대기 §8비공개" : "§7대기 §f" + this.core.rankedQueue.size() + "명") + " §8· §7빈 경기장 §f" + this.core.arenas.freeCount(),
                    "",
                    var2 ? "§c클릭: 매칭 취소" : "§e클릭: 매칭 시작"
                ),
                Material.GOLDEN_SWORD,
                var2x -> {
                    this.viewer.closeInventory();
                    if (var2) {
                        this.core.leaveRanked(this.viewer);
                    } else {
                        this.core.joinRanked(this.viewer);
                    }
                }
            );
            this.panel(
                0,
                6,
                2,
                8,
                "§b§l친선전",
                List.of("§7방을 만들고 친구를 초대", "§7짝수 인원(2~10)이면 랜덤 팀 대결", "§7트로피 변동 없음", "", "§e클릭: 방 메뉴"),
                Material.CAKE,
                var1x -> new Menus.RoomMenu(this.core, this.viewer).open()
            );
            this.panel(
                3,
                0,
                4,
                2,
                "§b§l덱 편집",
                List.of("§7덱 3칸 · 8장씩", "§7현재 덱 평균 엘릭서 §d" + Menus.avg(this.core, var1.deck())),
                Material.BOOK,
                var1x -> new Menus.DeckMenu(this.core, this.viewer, null, null).open()
            );
            this.panel(3, 3, 4, 5, "§d§l스킨", List.of("§7유닛 / 타워 스킨 변경"), Material.ARMOR_STAND, var1x -> new Menus.SkinListMenu(this.core, this.viewer).open());
            this.panel(
                3,
                6,
                4,
                8,
                "§6§l프로필",
                List.of(Ranks.label(var1.trophies), "§6\ud83c\udfc6 " + var1.trophies, "§7승 " + var1.wins + " · 패 " + var1.losses),
                Material.NAME_TAG,
                var1x -> new Menus.ProfileMenu(this.core, this.viewer).open()
            );
            this.panel(5, 0, 5, 2, "§e§l랭킹", List.of("§7서버 TOP 21"), Material.GOLD_BLOCK, var1x -> new Menus.LeaderboardMenu(this.core, this.viewer).open());
            this.set(49, Ui.icon("trophy", Material.GOLD_INGOT, Ranks.label(var1.trophies), "§6\ud83c\udfc6 §f" + var1.trophies, "§7최고 " + var1.best), null);
            this.set(53, Ui.icon("close", Material.BARRIER, "§c닫기"), var1x -> this.viewer.closeInventory());
            boolean bgmOn = !this.core.bgm.muted.contains(this.viewer.getUniqueId());
            this.set(
                51,
                Ui.icon(bgmOn ? "music_on" : "music_off", bgmOn ? Material.JUKEBOX : Material.NOTE_BLOCK, bgmOn ? "§a♫ 배경음악 켜짐" : "§7♫ 배경음악 꺼짐", "§e클릭: " + (bgmOn ? "끄기" : "켜기"), "§8(/clash bgm)"),
                var1x -> {
                    this.core.bgm.toggle(this.viewer);
                    this.refresh();
                }
            );
            this.set(50, Ui.icon("spectate", Material.ENDER_EYE, "§3§l관전", "§7진행 중인 경기 관전", "§e클릭: 관전 목록 §8(/관전)"),
                var1x -> new StreamerMenus.SpectateMenu(this.core, this.viewer).open());
            boolean isStreamer = this.core.streamers.streamers.containsKey(this.viewer.getUniqueId());
            if (isStreamer || this.viewer.hasPermission("clash.admin")) {
                boolean live = this.core.streamers.live(this.viewer);
                this.set(52, Ui.icon(isStreamer ? (live ? "live_on" : "live_off") : "streamer", Material.REDSTONE_TORCH,
                        isStreamer ? "§c§l스트리머 모드 " + (live ? "§a켜짐" : "§7꺼짐") : "§d§l스트리머 관리",
                        isStreamer ? "§7방송용 설정 메뉴" : "§7스트리머 지정 / 해제 (관리자)", "§e클릭: 열기 §8(/스트리머)"),
                    var1x -> StreamerMenus.openFor(this.core, this.viewer));
            }
        }
    }

    abstract static class Menu implements InventoryHolder {
        final Clash core;
        final Player viewer;
        Inventory inv;
        final Map<Integer, Consumer<Boolean>> actions = new HashMap<>();

        Menu(Clash var1, Player var2) {
            this.core = var1;
            this.viewer = var2;
        }

        abstract String title();

        abstract void render();

        int rows() {
            return 6;
        }

        public Inventory getInventory() {
            return this.inv;
        }

        void open() {
            this.inv = Bukkit.createInventory(this, this.rows() * 9, this.title());
            this.refresh();
            this.viewer.openInventory(this.inv);
        }

        void refresh() {
            this.inv.clear();
            this.actions.clear();
            this.render();
        }

        void set(int var1, ItemStack var2, Consumer<Boolean> var3) {
            if (var1 >= 0 && var1 < this.inv.getSize()) {
                this.inv.setItem(var1, var2);
                if (var3 != null) {
                    this.actions.put(var1, var3);
                }
            }
        }

        void panel(int var1, int var2, int var3, int var4, String var5, List<String> var6, Material var7, Consumer<Boolean> var8) {
            int var9 = (var1 + var3) / 2;
            int var10 = (var2 + var4) / 2;

            for (int var11 = var1; var11 <= var3; var11++) {
                for (int var12 = var2; var12 <= var4; var12++) {
                    boolean var13 = var11 == var9 && var12 == var10;
                    ItemStack var14 = Glyphs.pack
                        ? Ui.blank(var5, var6, var7)
                        : (var13 ? Ui.icon("blank", var7, var5, var6) : Ui.icon("blank", Material.GRAY_STAINED_GLASS_PANE, var5, var6));
                    this.set(var11 * 9 + var12, var14, var8);
                }
            }
        }

        void click(int var1, boolean var2) {
            Consumer var3 = this.actions.get(var1);
            if (var3 != null) {
                this.viewer.playSound(this.viewer.getLocation(), "ui.button.click", 0.5F, 1.3F);
                var3.accept(var2);
            }
        }

        void backButton(int var1, Runnable var2) {
            this.set(var1, Ui.icon("back", Material.ARROW, "§7◀ 뒤로"), var1x -> var2.run());
        }
    }

    static final class ProfileMenu extends Menus.Menu {
        ProfileMenu(Clash var1, Player var2) {
            super(var1, var2);
        }

        @Override
        String title() {
            return Ui.title('\ue104', this.viewer.getName() + " 님의 프로필");
        }

        @Override
        void render() {
            Profile var1 = this.core.profiles.get(this.viewer);
            Ranks.Tier var2 = Ranks.tier(var1.trophies);
            Ranks.Tier var3 = Ranks.next(var1.trophies);
            int var4 = Ranks.TIERS.indexOf(var2);
            this.set(
                4,
                Ui.head(
                    this.viewer.getUniqueId(),
                    "§f§l" + this.viewer.getName(),
                    List.of(
                        Ranks.label(var1.trophies),
                        "§7서버 순위 §f"
                            + (this.core.profiles.rankOf(this.viewer.getUniqueId()) > 0 ? this.core.profiles.rankOf(this.viewer.getUniqueId()) + "위" : "-")
                    )
                ),
                null
            );
            ArrayList var5 = new ArrayList();
            var5.add("§6\ud83c\udfc6 §f" + var1.trophies + " §7(최고 " + var1.best + ")");
            if (var3 != null) {
                double var6 = (double)(var1.trophies - var2.min()) / (var3.min() - var2.min());
                var5.add(Ui.bar(var6, 20, var2.color(), "§8") + " §7" + (int)(var6 * 100.0) + "%");
                var5.add("§7다음 티어 " + var3.color() + var3.name() + " §7까지 " + (var3.min() - var1.trophies) + "\ud83c\udfc6");
            } else {
                var5.add("§6최고 티어!");
            }

            this.set(13, Ui.icon("tier_" + var4, Material.GOLD_INGOT, Ranks.label(var1.trophies), var5), null);
            this.set(
                19,
                Ui.icon("stat_wins", Material.LIME_DYE, "§a승리 §f" + var1.wins, "§7패배 " + var1.losses + " · 무승부 " + var1.draws, "§7승률 " + var1.winRate()),
                null
            );
            this.set(21, Ui.icon("stat_ranked", Material.GOLDEN_SWORD, "§6랭크전", "§a" + var1.rankedWins + "승 §c" + var1.rankedLosses + "패"), null);
            this.set(23, Ui.icon("stat_ai", Material.IRON_SWORD, "§aAI 대전 승리 §f" + var1.aiWins, "§b친선전 승리 §f" + var1.friendlyWins), null);
            this.set(
                25,
                Ui.icon(
                    "stat_king",
                    Material.GOLDEN_HELMET,
                    "§6킹으로 출전 §f" + var1.kingGames + "판",
                    "§7연승 " + (var1.streak > 0 ? "§a" + var1.streak : "§70") + " §8· §7최근 " + (var1.streak < 0 ? "§c" + -var1.streak + "연패" : "")
                ),
                null
            );

            for (int var9 = 0; var9 < Ranks.TIERS.size() && var9 < 9; var9++) {
                Ranks.Tier var7 = Ranks.TIERS.get(var9);
                boolean var8 = var1.best >= var7.min();
                this.set(
                    36 + var9,
                    Ui.icon(
                        "tier_" + var9 + (var8 ? "" : "_off"),
                        var8 ? Material.GOLD_NUGGET : Material.GRAY_DYE,
                        var7.color() + var7.name(),
                        "§7" + var7.min() + "\ud83c\udfc6 이상",
                        var8 ? "§a달성" : "§8미달성",
                        var9 == var4 ? "§e◀ 현재" : ""
                    ),
                    null
                );
            }

            this.backButton(45, () -> new Menus.MainMenu(this.core, this.viewer).open());
            this.set(53, Ui.icon("leaderboard", Material.GOLD_BLOCK, "§e랭킹 보기"), var1x -> new Menus.LeaderboardMenu(this.core, this.viewer).open());
        }
    }

    static final class RoomListMenu extends Menus.Menu {
        RoomListMenu(Clash var1, Player var2) {
            super(var1, var2);
        }

        @Override
        String title() {
            return Ui.title('\ue108', "참가할 방");
        }

        @Override
        void render() {
            int var1 = 9;

            for (Room var3 : this.core.rooms.values()) {
                if (var1 >= 45) {
                    break;
                }

                if (var3.openToAll || var3.invited.contains(this.viewer.getUniqueId())) {
                    this.set(
                        var1++,
                        Ui.head(
                            var3.host,
                            "§b방 " + var3.code + " §7- " + GameManager.nameOf(var3.host),
                            List.of("§7인원 " + var3.members.size() + "/10", var3.match != null ? "§c경기 중" : "§e클릭: 참가", var3.openToAll ? "§a공개" : "§d초대받음")
                        ),
                        var2 -> {
                            this.viewer.closeInventory();
                            this.core.joinRoom(this.viewer, var3.code);
                        }
                    );
                }
            }

            if (var1 == 9) {
                this.set(22, Ui.icon("info", Material.PAPER, "§7참가할 수 있는 방이 없습니다", "§7친구에게 초대를 받거나 방을 만드세요"), null);
            }

            this.backButton(45, () -> new Menus.RoomMenu(this.core, this.viewer).open());
        }
    }

    static final class RoomMenu extends Menus.Menu {
        RoomMenu(Clash var1, Player var2) {
            super(var1, var2);
        }

        @Override
        String title() {
            Room var1 = this.core.roomOf.get(this.viewer.getUniqueId());
            return var1 == null ? Ui.title('\ue109', "친선전") : Ui.title('\ue106', "친선전 방 " + (this.core.streamers.live(this.viewer) ? "" : var1.code + " ") + "(" + var1.members.size() + "/10)");
        }

        @Override
        void render() {
            Room var1 = this.core.roomOf.get(this.viewer.getUniqueId());
            if (var1 == null) {
                this.panel(1, 1, 3, 3, "§b§l방 만들기", List.of("§7방을 만들고 친구를 초대하세요", "", "§e클릭"), Material.CAKE, var1x -> {
                    this.core.createRoom(this.viewer);
                    this.open();
                });
                this.panel(
                    1,
                    5,
                    3,
                    7,
                    "§f§l방 목록",
                    List.of("§7초대받았거나 공개된 방", "", "§e클릭"),
                    Material.BOOKSHELF,
                    var1x -> new Menus.RoomListMenu(this.core, this.viewer).open()
                );
                this.backButton(45, () -> new Menus.MainMenu(this.core, this.viewer).open());
            } else {
                boolean var2 = var1.host.equals(this.viewer.getUniqueId());
                int var3 = 0;

                for (UUID var5 : var1.members) {
                    if (var3 >= 10) {
                        break;
                    }

                    Player var6 = Bukkit.getPlayer(var5);
                    Profile var7 = this.core.profiles.get(var5);
                    ArrayList var8 = new ArrayList<>(List.of(Ranks.label(var7.trophies), "§6\ud83c\udfc6 " + var7.trophies, var6 == null ? "§c오프라인" : "§a온라인"));
                    if (var2 && !var5.equals(this.viewer.getUniqueId())) {
                        var8.add("§cShift+클릭: 추방");
                    }

                    int var9 = var3 < 5 ? 11 + var3 : 20 + (var3 - 5);
                    String var10 = var7.name;
                    this.set(var9, Ui.head(var5, (var5.equals(var1.host) ? "§6♔ " : "§f") + var7.name, var8), var3x -> {
                        if (var3x && var2) {
                            this.core.kick(this.viewer, var10);
                            this.refresh();
                        }
                    });
                    var3++;
                }

                int var11 = var1.online();
                boolean var12 = var11 >= 2 && var11 % 2 == 0;
                this.set(37, Ui.icon("invite", Material.WRITABLE_BOOK, "§a친구 초대", "§7클릭하면 채팅창에 명령어가 입력됩니다"), var1x -> {
                    this.viewer.closeInventory();
                    Ui.suggest(this.viewer, "§b[친선전] §f여기를 눌러 초대할 닉네임을 입력하세요 §7(/clash room invite <닉네임>)", "/clash room invite ");
                });
                if (var2) {
                    this.set(
                        38,
                        Ui.icon(
                            var1.openToAll ? "room_open" : "room_closed",
                            var1.openToAll ? Material.OAK_DOOR : Material.IRON_DOOR,
                            var1.openToAll ? "§a공개 방" : "§7초대 전용",
                            "§e클릭: 전환"
                        ),
                        var2x -> {
                            var1.openToAll = !var1.openToAll;
                            this.refresh();
                        }
                    );
                    this.set(39, Ui.icon("clock", Material.CLOCK, "§f경기 시간 §e" + var1.matchSeconds / 60 + "분", "§e클릭: 2분 / 3분 / 4분"), var2x -> {
                        var1.matchSeconds = var1.matchSeconds >= 240 ? 120 : var1.matchSeconds + 60;
                        this.refresh();
                    });
                    this.set(
                        41,
                        Ui.icon(
                            var12 ? "start" : "start_off",
                            var12 ? Material.EMERALD_BLOCK : Material.REDSTONE_BLOCK,
                            var12 ? "§a§l친선전 시작" : "§c짝수 인원 필요 (" + var11 + "명)",
                            "§7랜덤 팀 / 랜덤 킹",
                            "§7트로피 변동 없음"
                        ),
                        var1x -> {
                            this.viewer.closeInventory();
                            this.core.startFriendly(this.viewer);
                        }
                    );
                    this.set(
                        42, Ui.icon("ai", Material.IRON_SWORD, "§a§lAI 대전으로 시작", "§7방 인원 전원 vs 봇"), var1x -> new Menus.AiMenu(this.core, this.viewer).open()
                    );
                    this.set(43, Ui.icon("assault", Material.DIAMOND_SWORD, var12 ? "§c§l돌격전으로 시작" : "§c돌격전: 짝수 인원 필요 (" + var11 + "명)",
                        "§7랜덤 팀 · 40 엘릭서 군대 대결", "§7마지막까지 유닛이 남은 팀 승리"), var1x -> {
                        this.viewer.closeInventory();
                        this.core.startFriendly(this.viewer, true);
                    });
                } else {
                    this.set(41, Ui.icon("start_off", Material.CLOCK, "§7방장이 시작하기를 기다리는 중..."), null);
                }

                this.set(45, Ui.icon("leave", Material.DARK_OAK_DOOR, "§c방 나가기"), var1x -> {
                    this.core.leaveRoom(this.viewer);
                    this.viewer.closeInventory();
                    this.core.lobby.giveHotbar(this.viewer);
                });
                this.set(53, Ui.icon("close", Material.BARRIER, "§7닫기"), var1x -> this.viewer.closeInventory());
            }
        }
    }

    static final class SkinListMenu extends Menus.Menu {
        SkinListMenu(Clash var1, Player var2) {
            super(var1, var2);
        }

        @Override
        String title() {
            return Ui.title('\ue102', "스킨");
        }

        @Override
        void render() {
            Profile var1 = this.core.profiles.get(this.viewer);
            int[] var2 = new int[]{2, 6};
            String[] var3 = new String[]{"princess", "king"};

            for (int var4 = 0; var4 < 2; var4++) {
                String var5 = var3[var4];
                Skins.Skin var6 = this.core.skins.selected(var1, var5);
                int var7 = 0;
                int var8 = this.core.skins.forTarget(var5).size();

                for (Skins.Skin var10 : this.core.skins.forTarget(var5)) {
                    if (this.core.skins.owns(var1, var10)) {
                        var7++;
                    }
                }

                ItemStack var17 = Ui.icon(
                    var6 != null ? "skin_" + var6.id() : "tower_" + var5,
                    Material.STONE_BRICKS,
                    var4 == 0 ? "§b§l프린세스 타워" : "§6§l킹 타워",
                    "§7적용: §f" + (var6 == null ? "기본" : var6.name()),
                    "§7보유 " + var7 + "/" + var8,
                    "§e클릭: 스킨 선택"
                );
                this.set(var2[var4], var17, var2x -> new Menus.SkinPickMenu(this.core, this.viewer, var5).open());
            }

            if (this.core.skins.all.isEmpty()) {
                this.set(22, Ui.icon("info", Material.BOOK, "§e§l스킨 준비 중", "§7아직 등록된 스킨이 없어요", "§7곧 추가됩니다!"), null);
            }

            int var12 = 18;

            for (CardDef var14 : this.core.cards.values()) {
                if (!var14.isSpell()) {
                    List<Skins.Skin> var15 = this.core.skins.forTarget(var14.id);
                    if (!var15.isEmpty()) {
                        Skins.Skin var16 = this.core.skins.selected(var1, var14.id);
                        int var18 = 0;

                        for (Skins.Skin var11 : var15) {
                            if (this.core.skins.owns(var1, var11)) {
                                var18++;
                            }
                        }

                        ItemStack var20 = var16 != null
                            ? Ui.icon("skin_" + var16.id(), var14.icon, var14.name, List.of())
                            : this.core.cardItem(var14, false, false);
                        ItemMeta var21 = var20.getItemMeta();
                        if (var21 != null) {
                            var21.setDisplayName("§f§l" + var14.name);
                            var21.setLore(
                                List.of(
                                    "§7적용: §f" + (var16 == null ? "기본" : var16.rarityColor() + var16.name()),
                                    "§7보유 " + var18 + "/" + var15.size(),
                                    "§e클릭: 스킨 선택"
                                )
                            );
                            var20.setItemMeta(var21);
                        }

                        var20.setAmount(1);
                        this.set(var12++, var20, var2x -> new Menus.SkinPickMenu(this.core, this.viewer, var14.id).open());
                        if (var12 == 45) {
                            break;
                        }
                    }
                }
            }

            boolean orig = var1 != null && var1.originalSkins;
            ItemStack ov = Ui.icon(
                orig ? "skin_original" : "skin_original_off",
                orig ? Material.LIME_DYE : Material.GRAY_DYE,
                orig ? "§a§l원본 스킨으로 보기: 켜짐" : "§7§l원본 스킨으로 보기: 꺼짐",
                "§7켜면 모든 유닛 / 타워가",
                "§7기본 모습으로 보여요 §8(내 화면에만)",
                "",
                orig ? "§e클릭: 끄기" : "§e클릭: 켜기"
            );
            this.set(49, Ui.glow(ov, orig), var2x -> {
                if (var1 == null) {
                    return;
                }
                var1.originalSkins = !var1.originalSkins;
                var1.dirty = true;
                if (this.core.models != null) {
                    this.core.models.refreshViewer(this.viewer);
                }
                this.viewer.playSound(this.viewer.getLocation(), "ui.button.click", 0.6F, var1.originalSkins ? 1.4F : 0.9F);
                this.viewer.sendMessage(var1.originalSkins ? "§d[스킨] §f원본 스킨으로 보기 §a켜짐" : "§d[스킨] §f원본 스킨으로 보기 §7꺼짐");
                this.refresh();
            });
            this.backButton(45, () -> new Menus.MainMenu(this.core, this.viewer).open());
        }
    }

    static final class SkinPickMenu extends Menus.Menu {
        private final String target;

        SkinPickMenu(Clash var1, Player var2, String var3) {
            super(var1, var2);
            this.target = var3;
        }

        @Override
        String title() {
            CardDef var1 = this.core.cards.get(this.target);
            String var2 = var1 != null ? var1.name : (this.target.equals("king") ? "킹 타워" : "프린세스 타워");
            return Ui.title('\ue103', var2 + " 스킨");
        }

        @Override
        void render() {
            Profile var1 = this.core.profiles.get(this.viewer);
            Skins.Skin var2 = this.core.skins.selected(var1, this.target);
            ItemStack var3 = Ui.icon(
                this.core.cards.containsKey(this.target) ? "skin_default_" + this.target : "tower_" + this.target,
                Material.PAPER,
                "§f§l기본",
                var2 == null ? "§a✔ 사용 중" : "§e클릭: 기본으로"
            );
            this.set(20, Ui.glow(var3, var2 == null), var2x -> {
                var1.selected.remove(this.target);
                var1.dirty = true;
                this.refresh();
            });
            int[] var4 = new int[]{21, 22, 23, 24, 30, 31, 32, 33, 34};
            int var5 = 0;

            for (Skins.Skin var7 : this.core.skins.forTarget(this.target)) {
                if (var5 >= var4.length) {
                    break;
                }

                boolean var8 = this.core.skins.owns(var1, var7);
                boolean var9 = var2 != null && var2.id().equals(var7.id());
                ArrayList var10 = new ArrayList();
                var10.add(var7.rarityColor() + rarityKo(var7.rarity()));
                if (!var7.desc().isEmpty()) {
                    var10.add("§7" + var7.desc());
                }

                var10.add("");
                var10.add(var8 ? (var9 ? "§a✔ 사용 중" : "§e클릭: 적용") : "§c\ud83d\udd12 잠김 §7- " + this.core.skins.unlockText(var7));
                ItemStack var11 = Ui.icon(
                    "skin_" + var7.id() + (var8 ? "" : "_off"), var8 ? Material.LIME_DYE : Material.GRAY_DYE, var7.rarityColor() + "§l" + var7.name(), var10
                );
                this.set(var4[var5++], Ui.glow(var11, var9), var4x -> {
                    if (!var8) {
                        this.viewer.playSound(this.viewer.getLocation(), "block.note_block.bass", 1.0F, 0.6F);
                    } else {
                        var1.selected.put(this.target, var7.id());
                        var1.dirty = true;
                        this.viewer.playSound(this.viewer.getLocation(), "entity.player.levelup", 0.6F, 1.6F);
                        this.refresh();
                    }
                });
            }

            this.backButton(45, () -> new Menus.SkinListMenu(this.core, this.viewer).open());
        }

        static String rarityKo(String var0) {
            switch (var0) {
                case "rare":
                    return "레어";
                case "epic":
                    return "에픽";
                case "legendary":
                    return "전설";
                default:
                    return "일반";
            }
        }
    }
}
