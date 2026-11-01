"""모델링 규격표 (1타일 = 3블록 = 48px). card: (배치 타일, 외형 타일)"""
SPEC = {
 # 건물
 'goblin_cage': (3, 2.5), 'tesla': (2, 1.5), 'cannon': (3, 2.2), 'bomb_tower': (3, 2.75), 'tombstone': (3, 2.3),
 'goblin_hut': (3, 2.5), 'barbarian_hut': (3, 2.5), 'x_bow': (1, 1.5), 'inferno_tower': (3, 2.5), 'elixir_collector': (3, 2.75),
 # 소형
 'archers': (1, 1), 'firecracker': (1, 1), 'skeletons': (1, 1), 'goblins': (1, 1), 'spear_goblins': (1, 1), 'bomber': (1, 1),
 'wall_breakers': (1, 1), 'princess': (1, 1), 'dart_goblin': (1, 1), 'musketeer': (1, 1), 'minions': (1, 1),
 'fire_spirit': (1, 1), 'ice_spirit': (1, 1), 'electro_spirit': (1, 1), 'heal_spirit': (1, 1), 'bandit': (1, 1), 'guards': (1, 1),
 # 인간형
 'barbarians': (1, 1.5), 'elite_barbarians': (1, 1.5), 'pekka': (2, 2.25), 'mini_pekka': (1, 1.5), 'witch': (1, 1.5),
 'night_witch': (1, 1.5), 'mother_witch': (1, 1.5), 'magic_archer': (1, 1.5), 'knight': (1, 1.5), 'wizard': (1, 1.5),
 'ice_wizard': (1, 1.5), 'electro_wizard': (1, 1.5), 'zappies': (1, 1.5), 'valkyrie': (1, 1.5), 'hunter': (1, 1.5),
 'miner': (1, 1.5), 'executioner': (1, 1.5), 'lumberjack': (1, 1.5),
 # 대형
 'golem': (3, 2.5), 'elixir_golem': (3, 3), 'ice_golem': (2, 2), 'goblin_brawler': (2, 2), 'mega_knight': (3, 3),
 'giant': (3, 3.15), 'giant_skeleton': (3, 3.15), 'royal_giant': (3, 3.15), 'bowler': (2, 2.25),
 # 비행
 'baby_dragon': (2, 1.7), 'electro_dragon': (2, 1.7), 'inferno_dragon': (2, 1.7), 'lava_hound': (2, 1.7),
 'flying_machine': (2, 1.5), 'balloon': (2, 2.25), 'sparky': (2, 2.1), 'skeleton_barrel': (2, 2), 'cannon_cart': (2, 1.5),
 # 기마
 'prince': (1, 1.25), 'dark_prince': (1, 1.25), 'hog_rider': (1, 1.25), 'ram_rider': (1, 1.25), 'royal_hogs': (1, 1.1),
}
# 같은 모델을 쓰는 카드 (표의 카드를 따라감)
SAME = {'skeleton_army': 'skeletons', 'goblin_barrel': 'goblins', 'goblin_gang': 'goblins', 'three_musketeers': 'musketeer',
        'minion_horde': 'minions', 'electro_giant': 'giant'}
# 표에 없는 모델: 주인 모델과 같은 배율
FOLLOW = {'clash_bat': 'clash_minion', 'clash_mega_minion': 'clash_minion', 'clash_cursed_hog': 'clash_royal_hog',
          'clash_golemite': 'clash_golem', 'clash_elixir_golemite': 'clash_elixir_golem', 'clash_elixir_blob': 'clash_elixir_golem',
          'clash_lava_pup': 'clash_lava_hound', 'clash_battle_ram': 'clash_barbarian', 'clash_cannon_cart_broken': 'clash_cannon_cart',
          'clash_boulder': 'clash_bowler', 'clash_executioner_axe': 'clash_executioner', 'clash_bomb': 'clash_giant_skeleton',
          'clash_goblin_barrel': 'clash_goblin'}
# 측정에서 빼는 무기 본 (창·칼 길이로 몸이 작아지지 않게, 앞뒤 깊이만)
WEAPON = ('lance','sword','spear','axe','blade','bow','staff','pick','hammer','club','weapon','gun','musket','mace','wand','pole',
          'rifle','cane','broom','trident','scythe','torch','dart','blowgun','sledge','cleaver','pennant','flag','arrow','spark','bolt','beam','flame')
# 규격 적용 후 추가 조정 (배율, 또는 ('h', 기준모델, 배수) = 기준 모델 높이 x 배수에 맞춤)
ADJUST = {
 'clash_knight': 0.75,
 'clash_wizard': ('h', 'clash_musketeer', 1.1),
 'clash_prince': ('h', 'clash_pekka', 1.0), 'clash_dark_prince': ('h', 'clash_pekka', 1.0),
 'clash_x_bow': 2.0 * 0.8, 'clash_tesla': 2.25 * 0.85, 'clash_baby_dragon': ('m', 'clash_inferno_dragon', 1.0),
 'clash_valkyrie': ('h', 'clash_wizard', 1.0), 'clash_archer': ('h', 'clash_musketeer', 1.0),
 'clash_lava_hound': 1.7,
 'clash_hog_rider': ('h', 'clash_dark_prince', 0.85), 'clash_ram_rider': ('h', 'clash_hog_rider', 1.0),
 'clash_skeletons': ('h', 'clash_musketeer', 1.0),
 'clash_witch': ('h', 'clash_wizard', 1.0), 'clash_night_witch': ('h', 'clash_wizard', 1.0), 'clash_mother_witch': ('h', 'clash_wizard', 1.0), 'clash_electro_wizard': ('h', 'clash_wizard', 1.0), 'clash_ice_wizard': ('h', 'clash_wizard', 1.0), 'clash_lumberjack': ('h', 'clash_wizard', 1.0), 'clash_executioner': ('h', 'clash_wizard', 1.0), 'clash_miner': ('h', 'clash_wizard', 1.0), 'clash_barbarian': ('h', 'clash_wizard', 1.0), 'clash_elite_barbarian': ('h', 'clash_wizard', 1.0), 'clash_magic_archer': ('h', 'clash_wizard', 1.0),
 'clash_barbarian_hut': ('m', 'clash_goblin_hut', 1.0), 'clash_goblin_cage': ('m', 'clash_goblin_hut', 1.0), 'clash_tombstone': ('m', 'clash_goblin_hut', 1.0),
 'clash_wall_breaker': ('h', 'clash_skeletons', 1.0), 'clash_bomber': ('h', 'clash_skeletons', 1.0), 'clash_fire_spirit': ('h', 'clash_heal_spirit', 1.0), 'clash_ice_spirit': ('h', 'clash_heal_spirit', 1.0), 'clash_electro_spirit': ('h', 'clash_heal_spirit', 1.0), 'clash_cursed_hog': ('h', 'clash_heal_spirit', 1.0), 'clash_royal_hog': ('h', 'clash_heal_spirit', 1.0), 'clash_dart_goblin': ('h', 'clash_goblin', 1.0),
 'clash_golemite': 2.0, 'clash_elixir_golemite': 2.0, 'clash_zappies': 0.7, 'clash_bandit': ('h', 'clash_wizard', 1.0),
 'clash_cannon_cart': ('m', 'clash_cannon', 1.0), 'clash_flying_machine': ('m', 'clash_electro_dragon', 1.0),
 'clash_fire_spirit@2': 2.0 * 0.5 * 1.15 * 3.9 / 3.36, 'clash_lava_pup': 3.4, 'clash_elixir_blob': 3.0,  # 라바 펍: 라바 하운드 현재 배율(1.97) x2 / 기본 1.16
 'clash_hunter': ('h', 'clash_barbarian', 1.0), 'clash_miner@2': ('w', 'clash_barbarian', 1.0),
 'clash_dart_goblin@2': ('w', 'clash_goblin', 1.0),
 'clash_witch@2': 1.2, 'clash_mother_witch@2': 1.2, 'clash_night_witch@2': ('h', 'clash_witch', 1.0), 'clash_bandit@2': 0.7,
 'clash_princess': 0.7, 'clash_miner@3': 0.9 * 0.9 * 0.95, 'clash_magic_archer@2': 1.15,
 'clash_royal_hog@2': ('m', 'clash_cursed_hog', 1.0),
 'clash_bomber@2': 0.9, 'clash_goblin_brawler': ('m', 'clash_ice_golem', 1.0),
 'clash_mega_knight': 1.1, 'clash_pekka': 1.15, 'clash_mini_pekka': 0.9,
}

# 타워: 모델 이름 → 외형 블록 (킹 4x4타일, 프린세스 3x3타일)
TOWERS = {'clash_king': 12.0, 'clash_princess_tower': 9.0}
TOWER_FOLLOW = {'clash_princess_top': 'clash_princess_tower'}

# 옆으로만 늘리기 (X, Z 배율) - 균일 배율 다음에 적용
WIDEN = {'clash_miner': (1.25, 1.15), 'clash_fire_spirit': (2.5 / 2.27, 1.0)}
