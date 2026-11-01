# ClashMC model brief (BetterModel .bbmodel via bbgen2)

Project: a Clash Royale-style Minecraft minigame plugin. Units and buildings are BetterModel models
(Blockbench .bbmodel files) that we generate in Python with our own generator `bbgen2.py`.

## Paths
- WORK = /tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad/work
- Generator and renderer: WORK/pkg340/ClashMC_v3.4.0/source/model_tools/bbgen2.py and bbrender.py.
  Do NOT import kit.py: it depends on a missing module.
- **Reference script to copy the style from: WORK/models_new.py.** It is self-contained (cb helper,
  loop helper, common_tail for spawn/hit/death, the export loop with sculpt/fit/check). Read it fully
  first. WORK/lava_hound_v2.py is another detailed example.
- Existing finished models to look at for scale and style: WORK/pkg342/ClashMC_v3.4.2/models/base/*.bbmodel
  (for example clash_mini_pekka, clash_musketeer, clash_electro_wizard, clash_prince, clash_goblin,
  clash_cannon, clash_goblin_hut, clash_tombstone, clash_golem, clash_golemite, clash_bat, clash_skeletons, clash_barbarian).
  Render a couple with bbrender to see the quality bar.
- Write output models to WORK/newmodels2/<model_name>.bbmodel and previews to WORK/newmodels2/preview_<name>.png.
- Put your generator script at WORK/<your script name>.py. Run it like models_new.py:
  `python3 WORK/models_xx.py WORK/pkg340/ClashMC_v3.4.0/source/model_tools WORK/newmodels2`
- Only touch your own model files and script. Other agents are writing other models in the same folder at the same time.

## Conventions (must follow)
- Units: pixels, 16 px = 1 block. Front faces north (-Z). Origin = centre of the feet.
- Model name = `clash_<id>`.
- Animations, by these exact names. bbgen2 renames `spawn` → `deploy` on export, which is intended.
  - Troops: `idle` (loop), `walk` (loop), `attack` (once), `spawn` (once, about 0.5 s), `hit` (once, about 0.3 s), `death` (hold).
  - Buildings: `idle` (loop), `attack` (once), `spawn` (once), `hit` (once), `death` (hold). No walk.
  - **Every model needs an `idle` loop.** It is the fallback animation and prevents frozen poses.
  - The attack animation should read clearly from a distance (wind-up, then strike or recoil). Its length should be
    about the unit's hit speed or shorter (usually 0.5 to 1.0 s).
- Team colour: bones whose name contains `tc_` are tinted with the team colour (red or blue) in game.
  Give the team-coloured cloth or trim pieces a light base colour (#efefef, 'cloth') inside a bone named
  `tc_<something>` (for example tc_cape, tc_band). Every model should have some visible team-coloured part.
- Call `m.hitbox(w, h)` with the hitbox size in blocks that I give below.
- Then follow the same export loop as models_new.py: `m.sculpt(); m.fit(48); m.check(48); m.export(...)`.
  Report the cube count and any `bad` result from check. Keep each model around or under 250 cubes.
- Buildings with a rotating turret (x_bow, bomb_tower, cannon_cart_broken): the root must have two
  sub-trees. One is a bone named `base` whose descendants are all named `base_...` (static part). The other
  is a bone named `top` whose descendants are all named `top_...` (the part that turns to aim).
  Team-colour bones inside them are then named for example `top_tc_band` or `base_tc_flag`.
  The game spawns the model twice: once with `top*` hidden (base) and once with `base*` hidden (turret).
  Pivot the `top` bone at the turret's rotation centre (x=0, z=0).
- Original designs only: evoke the role and silhouette, not a copy of Supercell's art. The existing models
  say "role-readable, not based on any existing game's characters". Keep a chunky, colourful, stylised
  Minecraft-meets-Clash look with good detail (decals for faces, trim, cracks, rivets).

## Quality check
Render each model with bbrender (see models_new.py and WORK/card_icons.py for render usage, for example
`render(doc, 400, cam=(0.6,0.5,-1.0))` and `sample(doc, anim, t)` for poses). Look at the PNGs with the
Read tool. Make at least one sheet per model with the idle pose plus 2 or 3 attack and walk frames
(bbrender's `render(..., pose=sample(doc,'attack',t))`; check its signature). Fix anything that looks broken:
floating parts, parts clipping through the body, or a pose that doesn't read.

## Report back
For each model: file path, cube count, hitbox, the animation list with lengths, bone names that matter
(muzzle or hand bone for projectile origin if any), and the preview path. Keep the report short.
