#!/bin/bash
# 3.7.0 빌드: 바뀐 클래스 컴파일 → 3.4.2 jar 에 덮어쓰기 → 검증
set -e
W=/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad/work
Z=/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad/zip
cd $W
D=dec/kr/kjmn/clashmc
rm -rf stubcls3 && mkdir stubcls3 && javac -nowarn -d stubcls3 $(find stubs2 stubs_extra -name '*.java') 2>&1 | grep -A2 error || true
rm -rf out14 && mkdir out14
SRC=$(ls $D/*.java | grep -v -E "/(Bot|Fx|TestMode|Profiles|Ui)\.java$")
javac -Xmaxerrs 100 -nowarn -encoding UTF-8 -cp stubcls3:$W/ClashMC-3.6.0.jar -d out14 $SRC 2>&1 | grep -v JAVA_TOOL | grep -v '^Note' | tee /tmp/javac370.log || true
if grep -q 'error' /tmp/javac370.log; then echo 'BUILD FAILED (compile errors)'; exit 1; fi
ls out14/kr/kjmn/clashmc | wc -l
V=$W/verify370; rm -rf $V && mkdir -p $V && cd $V && unzip -q $W/ClashMC-3.6.0.jar
cp -r $W/out14/kr/kjmn/clashmc/* $V/kr/kjmn/clashmc/
cp $W/dec/config.yml $V/config.yml
cp $W/arena_350.schem $V/clash_arena.schem
cp $W/dec/clash_lobby.schem $V/clash_lobby.schem
sed -i "s/^version: .*/version: 3.7.0-b$(date +%m%d%H%M)/" $V/plugin.yml
sed -i 's/usage: \/clash \[menu|ranked|ai|room|deck|skin|profile|top|ff|leave|status\]/usage: \/clash [menu|ranked|ai|room|deck|skin|profile|top|ff|leave|status|bgm]/' $V/plugin.yml
# 스트리머 모드 / 관전 명령어
python3 - "$V/plugin.yml" <<'PYEOF'
import sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
if '스트리머:' not in s:
    s = s.replace('permissions:', '  스트리머:\n    description: 스트리머 모드 (관리자가 지정한 스트리머만)\n    aliases: [streamer]\n  관전:\n    description: 경기 관전\n    aliases: [spectate]\npermissions:', 1)
open(p, 'w', encoding='utf-8').write(s)
PYEOF
if [ -f $W/ClashMC_UI_pack_370.zip ]; then cp $W/ClashMC_UI_pack_370.zip $V/ClashMC_UI_pack.zip; fi
rm -f $W/ClashMC-3.7.0.jar
cd $V && zip -q -X -r $W/ClashMC-3.7.0.jar META-INF $(ls | grep -v META-INF)
cd $W
java -Xverify:all -cp $W/vchk:$V:$W/stubcls3:$W/lib/gson.jar V8 2>&1 | grep -v JAVA_TOOL
ext(){ grep -oE '(invoke\w+|getstatic|getfield|putfield|putstatic) +#[0-9]+(, +[0-9]+)? +// (Method|InterfaceMethod|Field) [a-z][^ ]*/[^ ]+' | sed -E 's/ +#[0-9]+(, +[0-9]+)? +\/\/ / /' | grep -v ' kr/\| java/' | sort -u; }
javap -c -p $(find out14 -name '*.class') 2>/dev/null | ext > new_refs15.txt
echo "--- new external refs vs 3.4.2 build:"; comm -23 new_refs15.txt new_refs14.txt | grep -E 'org/bukkit|com/|net/' || true
