"""Generate compile-only stubs for external (Bukkit etc.) classes referenced by the jar bytecode."""
import re, os, sys, collections

W = os.path.dirname(os.path.abspath(__file__))
code = open(os.path.join(W, 'javap_c.txt'), encoding='utf-8', errors='replace').read()
hdr = open(os.path.join(W, 'javap_p.txt'), encoding='utf-8', errors='replace').read()
OUT = os.path.join(W, 'stubs')

def ext(n):  # external (needs stub)?
    return not (n.startswith('kr/') or n.startswith('java/') or n.startswith('javax/') or n.startswith('com/sun/') or n.startswith('jdk/') or n.startswith('['))

# kr class -> (super, [interfaces]) and declared method names
krsuper = {}
for m in re.finditer(r'^(?:[a-z ]*)(?:class|interface) (kr\.[\w.$]+)(?:<[^>]*>)?(?: extends ([\w.$<>,]+?))?(?: implements ([\w.$,<> ]+))? \{', hdr, re.M):
    c = m.group(1).replace('.', '/')
    sup = (m.group(2) or 'java.lang.Object').split('<')[0].replace('.', '/')
    itf = [x.strip().split('<')[0].replace('.', '/') for x in (m.group(3) or '').split(',') if x.strip()]
    krsuper[c] = (sup, itf)

classes = {}  # name -> dict(kind, methods{(name,desc,static)}, fields{(name,desc,static)}, ctors set)
def C(n):
    if n not in classes:
        classes[n] = dict(iface=False, cls=False, enum=False, methods=set(), fields=set(), ctors=set(), abstract=False)
    return classes[n]

def types_in(desc):
    return re.findall(r'L([\w/$]+);', desc)

def resolve_owner(owner):
    # method referenced on a kr subclass but declared in external super
    seen = set()
    while owner.startswith('kr/') and owner in krsuper and owner not in seen:
        seen.add(owner)
        sup, itf = krsuper[owner]
        if ext(sup):
            return sup
        owner = sup
    return owner

for line in code.splitlines():
    m = re.search(r'\b(invoke\w+|getstatic|putstatic|getfield|putfield|new|checkcast|instanceof|anewarray|ldc\w*)\s+#\d+(?:,\s*\d+)?\s+// (Method|InterfaceMethod|Field|class|String|) ?(.*)$', line)
    if not m:
        continue
    op, kind, rest = m.groups()
    if kind in ('Method', 'InterfaceMethod', 'Field'):
        mm = re.match(r'"?([\w/$\[;]+)"?\.("?[\w<>$]+"?):(.*)$', rest)
        if not mm:
            continue
        owner, name, desc = mm.group(1), mm.group(2).strip('"'), mm.group(3)
        if owner.startswith('kr/') and (name == '<init>' or kind == 'Field'):
            continue
        if owner.startswith('kr/'):
            # only care if method not declared in kr: approximate by resolving to external super for inherited calls
            r = resolve_owner(owner)
            if r == owner or not ext(r):
                for t in types_in(desc):
                    if ext(t): C(t)
                continue
            owner = r
        for t in types_in(desc):
            if ext(t): C(t)
        if not ext(owner):
            continue
        c = C(owner)
        if kind == 'InterfaceMethod':
            c['iface'] = True
        elif kind == 'Method' and op in ('invokevirtual', 'invokespecial'):
            c['cls'] = True
        static = op in ('invokestatic', 'getstatic', 'putstatic')
        if kind == 'Field':
            c['fields'].add((name, desc, static))
        elif name == '<init>':
            c['ctors'].add(desc)
            c['cls'] = True
        else:
            c['methods'].add((name, desc, static))
            if name in ('values', 'ordinal') and owner in ('org/bukkit/Material', 'org/bukkit/Particle', 'org/bukkit/entity/EntityType'):
                c['enum'] = True
    elif kind == 'class':
        t = rest.strip().strip('"')
        t = re.sub(r'^\[+L?', '', t).rstrip(';')
        if ext(t) and '/' in t:
            C(t)
            if op == 'new':
                C(t)['cls'] = True

for c, (sup, itf) in krsuper.items():
    for t in [sup] + itf:
        if ext(t):
            C(t)
            if t == sup:
                C(t)['cls'] = True
            else:
                C(t)['iface'] = True

# Known kinds / hierarchy
ENUMS = {'org/bukkit/Material', 'org/bukkit/Particle', 'org/bukkit/entity/EntityType', 'org/bukkit/boss/BarColor',
         'org/bukkit/boss/BarStyle', 'org/bukkit/GameMode', 'org/bukkit/attribute/Attribute', 'org/bukkit/event/block/Action',
         'org/bukkit/inventory/EquipmentSlot', 'org/bukkit/entity/Display$Billboard', 'org/bukkit/inventory/ItemFlag',
         'org/bukkit/scoreboard/DisplaySlot', 'org/bukkit/event/inventory/ClickType', 'org/bukkit/event/inventory/InventoryAction',
         'org/bukkit/event/player/PlayerResourcePackStatusEvent$Status', 'org/bukkit/event/entity/EntityDamageEvent$DamageCause',
         'org/bukkit/event/entity/CreatureSpawnEvent$SpawnReason', 'org/bukkit/SoundCategory', 'org/bukkit/event/EventPriority',
         'org/bukkit/entity/TextDisplay$TextAlignment', 'org/bukkit/scoreboard/Team$Option', 'org/bukkit/scoreboard/Team$OptionStatus',
         'org/bukkit/event/player/PlayerTeleportEvent$TeleportCause', 'org/bukkit/inventory/meta/trim/TrimMaterial',
         'org/bukkit/persistence/PersistentDataType$PrimitivePersistentDataType', 'org/bukkit/entity/ItemDisplay$ItemDisplayTransform',
         'org/bukkit/scoreboard/Criteria', 'org/bukkit/block/BlockFace', 'org/bukkit/event/inventory/InventoryType',
         'org/bukkit/WeatherType', 'org/bukkit/Difficulty', 'org/bukkit/GameRule', 'org/bukkit/entity/Pose', 'org/bukkit/FluidCollisionMode'}
CLASSES = {'org/bukkit/Location', 'org/bukkit/Bukkit', 'org/bukkit/Color', 'org/bukkit/util/Vector', 'org/bukkit/inventory/ItemStack',
           'org/bukkit/scheduler/BukkitRunnable', 'org/bukkit/plugin/java/JavaPlugin', 'org/bukkit/Particle$DustOptions',
           'org/bukkit/Particle$DustTransition', 'org/bukkit/util/Transformation', 'org/bukkit/util/RayTraceResult',
           'org/bukkit/NamespacedKey', 'org/bukkit/ChatColor', 'org/bukkit/configuration/file/YamlConfiguration',
           'org/bukkit/configuration/file/FileConfiguration', 'org/bukkit/configuration/MemorySection', 'org/bukkit/WorldCreator',
           'org/bukkit/event/Event', 'org/bukkit/util/BoundingBox', 'org/joml/Vector3f', 'org/joml/Quaternionf', 'org/joml/AxisAngle4f',
           'org/joml/Matrix4f', 'net/md_5/bungee/api/chat/TextComponent', 'net/md_5/bungee/api/chat/ClickEvent',
           'net/md_5/bungee/api/chat/HoverEvent', 'net/md_5/bungee/api/chat/BaseComponent', 'net/md_5/bungee/api/chat/ComponentBuilder',
           'net/md_5/bungee/api/chat/hover/content/Text', 'org/bukkit/event/player/PlayerEvent', 'org/bukkit/event/entity/EntityEvent',
           'org/bukkit/event/block/BlockEvent', 'org/bukkit/event/inventory/InventoryEvent', 'org/bukkit/event/inventory/InventoryInteractEvent',
           'org/bukkit/plugin/PluginBase', 'org/bukkit/command/Command', 'org/bukkit/command/PluginCommand', 'org/bukkit/FireworkEffect', 'org/bukkit/FireworkEffect$Builder',
           'org/bukkit/potion/PotionEffect', 'org/bukkit/inventory/meta/components/CustomModelDataComponent'}
SUPER = {
    'org/bukkit/entity/Entity': ['org/bukkit/command/CommandSender', 'org/bukkit/persistence/PersistentDataHolder'],
    'org/bukkit/command/CommandSender': [],
    'org/bukkit/entity/LivingEntity': ['org/bukkit/entity/Entity', 'org/bukkit/entity/Damageable', 'org/bukkit/attribute/Attributable'],
    'org/bukkit/entity/Damageable': ['org/bukkit/entity/Entity'],
    'org/bukkit/entity/HumanEntity': ['org/bukkit/entity/LivingEntity', 'org/bukkit/inventory/InventoryHolder'],
    'org/bukkit/entity/Player': ['org/bukkit/entity/HumanEntity', 'org/bukkit/OfflinePlayer'],
    'org/bukkit/entity/Mob': ['org/bukkit/entity/LivingEntity'],
    'org/bukkit/entity/ArmorStand': ['org/bukkit/entity/LivingEntity'],
    'org/bukkit/entity/Interaction': ['org/bukkit/entity/Entity'],
    'org/bukkit/entity/Display': ['org/bukkit/entity/Entity'],
    'org/bukkit/entity/BlockDisplay': ['org/bukkit/entity/Display'],
    'org/bukkit/entity/ItemDisplay': ['org/bukkit/entity/Display'],
    'org/bukkit/entity/TextDisplay': ['org/bukkit/entity/Display'],
    'org/bukkit/entity/Item': ['org/bukkit/entity/Entity'],
    'org/bukkit/entity/Firework': ['org/bukkit/entity/Entity'],
    'org/bukkit/entity/FallingBlock': ['org/bukkit/entity/Entity'],
    'org/bukkit/entity/Ageable': ['org/bukkit/entity/Mob'],
    'org/bukkit/entity/Zombie': ['org/bukkit/entity/Ageable'],
    'org/bukkit/entity/Slime': ['org/bukkit/entity/Mob'],
    'org/bukkit/World': ['org/bukkit/plugin/messaging/PluginMessageRecipient'],
    'org/bukkit/block/Block': [],
    'org/bukkit/inventory/PlayerInventory': ['org/bukkit/inventory/Inventory'],
    'org/bukkit/inventory/meta/SkullMeta': ['org/bukkit/inventory/meta/ItemMeta'],
    'org/bukkit/inventory/meta/LeatherArmorMeta': ['org/bukkit/inventory/meta/ItemMeta'],
    'org/bukkit/inventory/meta/FireworkMeta': ['org/bukkit/inventory/meta/ItemMeta'],
    'org/bukkit/inventory/meta/ItemMeta': ['org/bukkit/persistence/PersistentDataHolder'],
    'org/bukkit/plugin/Plugin': ['org/bukkit/command/TabExecutor'],
    'org/bukkit/command/TabExecutor': ['org/bukkit/command/CommandExecutor', 'org/bukkit/command/TabCompleter'],
    'org/bukkit/command/PluginCommand': ['org/bukkit/command/Command'],
    'org/bukkit/plugin/PluginBase': ['org/bukkit/plugin/Plugin'],
    'org/bukkit/plugin/java/JavaPlugin': ['org/bukkit/plugin/PluginBase'],
    'org/bukkit/configuration/file/YamlConfiguration': ['org/bukkit/configuration/file/FileConfiguration'],
    'org/bukkit/configuration/file/FileConfiguration': ['org/bukkit/configuration/ConfigurationSection'],
    'org/bukkit/configuration/MemorySection': ['org/bukkit/configuration/ConfigurationSection'],
    'org/bukkit/block/data/type/Light': ['org/bukkit/block/data/BlockData'],
    'org/bukkit/scheduler/BukkitRunnable': ['java/lang/Runnable'],
    'org/bukkit/event/player/PlayerEvent': ['org/bukkit/event/Event'],
    'org/bukkit/event/entity/EntityEvent': ['org/bukkit/event/Event'],
    'org/bukkit/event/block/BlockEvent': ['org/bukkit/event/Event'],
    'org/bukkit/event/inventory/InventoryEvent': ['org/bukkit/event/Event'],
    'org/bukkit/event/inventory/InventoryInteractEvent': ['org/bukkit/event/inventory/InventoryEvent'],
    'org/bukkit/event/inventory/InventoryClickEvent': ['org/bukkit/event/inventory/InventoryInteractEvent'],
    'org/bukkit/event/inventory/InventoryDragEvent': ['org/bukkit/event/inventory/InventoryInteractEvent'],
    'org/bukkit/event/entity/EntityDamageEvent': ['org/bukkit/event/entity/EntityEvent'],
    'org/bukkit/event/entity/EntityDamageByEntityEvent': ['org/bukkit/event/entity/EntityDamageEvent'],
}
for k in SUPER:
    C(k)
    for s_ in SUPER[k]:
        if ext(s_): C(s_)
for n_ in CLASSES | ENUMS:
    pass

def jt(t):  # internal name -> java source name
    return t.replace('/', '.').replace('$', '.')

def parse_desc(d):
    out = []; i = 0
    while i < len(d):
        a = 0
        while d[i] == '[':
            a += 1; i += 1
        ch = d[i]
        if ch == 'L':
            j = d.index(';', i); base = jt(d[i+1:j]); i = j + 1
        else:
            base = {'Z': 'boolean', 'B': 'byte', 'C': 'char', 'S': 'short', 'I': 'int', 'J': 'long', 'F': 'float', 'D': 'double', 'V': 'void'}[ch]; i += 1
        out.append(base + '[]' * a)
    return out

def msig(desc):
    m = re.match(r'\((.*)\)(.*)', desc)
    return parse_desc(m.group(1)), parse_desc(m.group(2))[0]

def dflt(t):
    if t == 'void': return ''
    if t == 'boolean': return 'return false;'
    if t in ('byte', 'char', 'short', 'int', 'long', 'float', 'double'): return 'return 0;'
    return 'return null;'

EXTRA_CONST = {'org/bukkit/Material': ['PACKED_ICE', 'MAGMA_BLOCK', 'BLUE_ICE', 'SNOW_BLOCK', 'LIME_CONCRETE', 'ORANGE_CONCRETE', 'RED_STAINED_GLASS', 'YELLOW_CONCRETE', 'LIME_STAINED_GLASS', 'RED_CONCRETE', 'OAK_PLANKS', 'TNT', 'IRON_BLOCK', 'OAK_LOG', 'JUKEBOX', 'NOTE_BLOCK', 'COBBLESTONE'], 'org/bukkit/Particle': ['HAPPY_VILLAGER', 'HEART', 'EXPLOSION_EMITTER', 'FLASH', 'SMOKE']}

# overrides for generics (filled after compile errors)
GEN = {}
gpath = os.path.join(W, 'generics.txt')
if os.path.exists(gpath):
    for line in open(gpath, encoding='utf-8'):
        line = line.strip()
        if not line or line.startswith('#'): continue
        key, val = line.split('=>', 1)
        GEN[key.strip()] = val.strip()

def kind_of(n):
    c = classes[n]
    if n in ENUMS or c['enum']: return 'enum'
    if n in CLASSES: return 'class'
    if c['iface'] and not c['ctors']: return 'interface'
    if c['cls'] and n not in SUPER: return 'class'
    if n.endswith('Event') or n.endswith('Event$Status'): return 'class'
    return 'interface'

# group nested
outers = collections.defaultdict(list)
for n in classes:
    outers[n.split('$')[0]].append(n)

def gen_body(n, k, indent):
    c = classes[n]; ind = ' ' * indent; L = []
    simple = n.split('/')[-1].split('$')[-1]
    if k == 'enum':
        consts = sorted({f for f, d, s in c['fields'] if s and d == 'L%s;' % n} | set(EXTRA_CONST.get(n, [])))
        L.append(ind + '    ' + (', '.join(consts) if consts else 'STUB_CONST') + ';')
    for f, d, s in sorted(c['fields']):
        if k == 'enum' and s and d == 'L%s;' % n: continue
        t = parse_desc(d)[0]
        if k == 'interface':
            L.append(ind + '    %s %s = %s;' % (t, f, dflt(t).replace('return ', '').rstrip(';') or 'null'))
        else:
            L.append(ind + '    public %s%s %s;' % ('static ' if s else '', t, f))
    if k == 'class':
        has_noarg = False
        for d in sorted(c['ctors']):
            ps, _ = msig(d)
            if not ps: has_noarg = True
            L.append(ind + '    public %s(%s) {}' % (simple, ', '.join('%s a%d' % (p, i) for i, p in enumerate(ps))))
        if not has_noarg:
            L.append(ind + '    protected %s() {}' % simple)
    for name, d, s in sorted(c['methods']):
        if k == 'enum' and name in ('values', 'valueOf', 'ordinal', 'name', 'compareTo', 'equals', 'hashCode', 'toString', 'getDeclaringClass'): continue
        if name in ('equals', 'hashCode', 'toString', 'getClass', 'clone') and k == 'interface': continue
        ps, r = msig(d)
        key = '%s.%s%s' % (n, name, d)
        if key in GEN:
            L.append(ind + '    ' + GEN[key]); continue
        params = ', '.join('%s a%d' % (p, i) for i, p in enumerate(ps))
        if name == 'clone' and k == 'class':
            L.append(ind + '    public %s clone() { return null; }' % r); continue
        if k == 'interface':
            L.append(ind + '    %s%s %s(%s) { %s }' % ('static ' if s else 'default ', r, name, params, dflt(r)))
        else:
            L.append(ind + '    public %s%s %s(%s) { %s }' % ('static ' if s else '', r, name, params, dflt(r)))
    for key, val in GEN.items():
        if key.startswith(n + '.+'):
            L.append(ind + '    ' + val)
    return L

def header(n, k, nested):
    simple = n.split('/')[-1].split('$')[-1]
    sup = SUPER.get(n, [])
    mods = 'public ' + ('static ' if nested and k != 'interface' and k != 'enum' else '')
    if n == 'org/bukkit/scheduler/BukkitRunnable':
        return 'public abstract class BukkitRunnable implements java.lang.Runnable {'
    extends = ''
    gen = GEN.get(n + '.<class>', '')
    if k == 'interface':
        ext_ = [jt(s) for s in sup]
        if ext_: extends = ' extends ' + ', '.join(ext_)
    elif k == 'class':
        cl = [s for s in sup if kind_of(s) == 'class' if s in classes]
        it = [s for s in sup if s not in cl]
        if cl: extends += ' extends ' + jt(cl[0])
        if it: extends += ' implements ' + ', '.join(jt(s) for s in it)
    return '%s%s %s%s%s {' % (mods, k, simple, gen, extends)

os.makedirs(OUT, exist_ok=True)
for outer, members in outers.items():
    if outer not in classes:
        C(outer)
    k = kind_of(outer)
    pkg = '.'.join(outer.split('/')[:-1])
    L = ['package %s;' % pkg, '', header(outer, k, False)]
    L += gen_body(outer, k, 0)
    if outer == 'org/bukkit/scheduler/BukkitRunnable':
        L.append('    public abstract void run();')
    for n in sorted(members):
        if n == outer: continue
        nk = kind_of(n)
        L.append('    ' + header(n, nk, True))
        L += gen_body(n, nk, 4)
        L.append('    }')
    L.append('}')
    p = os.path.join(OUT, outer + '.java')
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8').write('\n'.join(L) + '\n')
print(len(classes), 'classes')
