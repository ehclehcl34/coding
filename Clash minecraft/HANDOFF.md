# ClashMC 작업 인수인계 (새 세션용)

Minecraft 클래시 로얄 플러그인 ClashMC (BetterModel 모델). 현재 버전 3.7.0.
사용자에게는 **짧은 한국어**로 답할 것.

## 이 레포 구조
- `plugin/`, `models/base/`, `source_3.7.0/` : 마지막 배포본 (3.7.0-b10281351)
- `workspace/work/` : 빌드 작업 폴더 전체 (자바 소스 `dec/`, 모델 원본 `newmodels2`/`newmodels3`, 스크립트)
- `workspace/scratch_root/` : work 위 폴더에 있던 공용 파이썬 모듈 (animlib, bbrender 등)

## 새 세션에서 빌드 환경 복구
스크립트들이 예전 경로를 하드코딩하고 있어서 그 경로로 복사해서 쓴다:
```bash
OLD=/tmp/claude-0/-home-user/a75908a7-8974-5998-8a40-4328f255db88/scratchpad
mkdir -p $OLD $OLD/zip
cp -r "Clash minecraft/workspace/work" $OLD/work
cp "Clash minecraft/workspace/scratch_root/"*.py $OLD/
cd $OLD/work
```
(Java 17+ 과 python3, Pillow 필요)

## 빌드
- jar만 (플러그인 코드만 바뀜): `bash build370.sh` → `ClashMC-3.7.0.jar` 결과 (출력에 BUILD FAILED 없으면 OK)
- 모델까지 전체:
  ```bash
  (bash pack370.sh && python3 gen_heights.py pkg370/ClashMC_v3.7.0/models/base dec/kr/kjmn/clashmc/ModelHeights.java && bash build370.sh && bash pack370.sh) > /tmp/p.log 2>&1
  grep -c "BUILD FAILED" /tmp/p.log   # 0 이면 OK
  python3 prev_final.py               # 모델 미리보기 png (preview_final/)
  bash pack370.sh                     # zip: /home/user/ClashMC_v3.7.0.zip
  ```
- 전달 규칙: 플러그인만 바뀌면 jar만, 모델 바뀌면 zip(+필요시 미리보기 이미지)
- 작업 끝나면 이 레포 `Clash minecraft/` 도 갱신해서 푸시 (plugin/, models/, source, workspace/work 의 바뀐 파일)

## 핵심 지식
- `build370.sh`: `dec/kr/kjmn/clashmc/*.java` 중 Bot/Fx/TestMode/Profiles/Ui 제외하고 컴파일, 나머지는 `ClashMC-3.6.0.jar` 것 사용. plugin.yml 버전 `3.7.0-b<날짜>` 자동.
- 모델 크기: `spec_factors.json` (factor, tweak=누적 배율). 수정: `factor*=m, tweak*=m`. 타워는 제외.
- 모델 원본 우선순위: newmodels3 > newmodels2 > pkg360 원본.
- 아레나 54x96 블록, 1타일 = 3블록 (`CardDef.TILE = 3.0`), 강 z = minZ+45..51. 프린세스 타워 3x3타일, 킹 4x4.
- 거리 계산: `Battle.edgeDist` (히트박스 끝↔끝). 적 인식 거리 = 각 카드 사거리 (`pickTarget`에서 `nearest(..., card.range, ...)`). config `sight-range`는 안 씀.
- 사용 가능 카드: `Clash.usable()`, `/clash cards` GUI (plugins/ClashMC/cards.yml 의 disabled). AI, 로비 쇼케이스도 usable 카드만 (로비는 건물 제외).
- HP바 높이: `ModelHeights.java` (gen_heights.py 로 생성).
- 로비: `dec/clash_lobby.schem` (`/clash lobby repaste`), 원본 백업 `lobby_preroof.schem`.
- 공중 유닛 높이 `air-height: 7`. 라바하운드 죽으면 펍 퍼지며 등장 (`Battle.burstSpawn`).
- 서버 적용 안 된다고 하면: 서버 완전 종료 → ClashMC jar 하나만 남기기 → 예전 clash_*.bbmodel 삭제 후 교체 → `/bettermodel reload` → 재접속. `/version ClashMC` 로 빌드 번호 확인.

## 최근 상태
마지막 요청(적 인식 거리 = 사거리, 발키리 x0.9)까지 반영된 빌드 전달 완료. 인게임 테스트는 사용자가 함.
