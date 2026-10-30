# 파이프라인 리팩터: 3 Processes + 3 Functions

## Context (왜 하는가)

현재 `pipeline/`는 `select_stocks.py`·`run_live_report.py` 두 스크립트에 **날짜가 하드코딩**돼 있고, 종목선정·엔진가동·보고서생성 로직이 한 파일에 뒤섞여 있다. 매주 상수를 손으로 바꿔야 하고, 실시간 5분 갱신을 자동화할 수 없다.

목표: 로직을 **재사용 가능한 3 함수**로 쪼개고, 그 위에 **3 process 드라이버**를 올려 (1) 임의 종목·기간 단발 보고서, (2) 과거 주 종목선정+검증, (3) 실시간 5분 갱신을 모두 같은 코어로 돌린다. 엔진(`engines/engine281/*`)은 **손대지 않는다**.

보고서 HTML은 이미 `run_live_report.py`가 100% 순수 파이썬으로(내러티브까지 엔진 이벤트에서 결정론적으로) 생성 중 → **function3는 순수 코드로 만든다** (LLM/스킬 불필요). `chart_example_template` 스킬은 "큐레이션된 설명용 일회성 워크스루" 전용으로 유지 — 자동 파이프라인과 용도가 겹치지 않는다.

## 확정된 설계 결정

- **Process 1 시간입력 = 기간 지정.** `(code, start, end)` → 기간을 주(월~금) 단위로 쪼개 **주별 섹션** 렌더 (각 주 F0=직전 금 종가, 금요일 강제청산 따로). walkthrough 스타일 자동화.
- **Process 3 = cron** (while 루프 아님). 상태 없는 독립 틱, 자가복구.
- **구현 순서 = function부터 하나씩** (func1 → func2 → func3 → processes), 각 단계 검증 후 진행.
- **"섹션" = (종목, 주) 1단위.** build_report는 섹션 리스트를 렌더. P1은 주별 섹션(한 종목), P2/P3는 종목별 섹션(한 주).
- OUT 경로 표준 = `report/live/live-281-thisweek.html` (낡은 상수 `report/live-...` 수정).
- `_top5.json`에 `name` 필드 추가(가산적) — 5분 틱마다 screener 재조회 회피.
- 실시간 데이터 = tvDatafeed 메인 + yfinance fallback (기존 `data_source.bars_5m` 그대로).

## 파일 구조 (전부 `pipeline/` 아래, 엔진 불변)

```
data_source.py     (불변)  bars_5m(code,start,end)->(bars,src) · f0_close(code,fri,fallback)->(px,src)
weekcal.py         (신규)  순수 날짜 계산, I/O·네트워크 없음
function1.py       (신규)  select_stocks()      — 종목 고르기
function2.py       (신규)  run_engine()         — 엔진 가동 (default engine281)
function3.py       (신규)  build_report() + week_chart + narrative + skeleton — 보고서(순수코드)
process1.py        (신규)  (종목,기간) → 주별 f2 → f3 → 1 html   (원자 단위)
process2.py        (신규)  f1 → 종목별 f2 → f3 병합 → 1 html      (과거 확인)
process3.py        (신규)  --mode select|update                  (실시간, cron 진입점)
select_stocks.py   (shim)  function1에 옛 하드코딩 월요일 위임
run_live_report.py (shim)  process2/process3 update에 위임 (CLI 보존)
```

## 함수 시그니처

### weekcal.py — 순수 날짜
```python
to_monday(d) -> date                 # date|"YYYY-MM-DD"; 월요일 아니면 그 주 월요일로 snap
week_bounds(monday) -> (start, end)  # end = monday+5d(토), bars_5m용 반열림 [start,end)
prior_week(monday) -> (prior_mon, prior_fri, dl_start, dl_end)
    # prior_mon=mon-7d, prior_fri=mon-3d, dl_start=prior_mon-2d, dl_end=prior_fri+2d
weeks_in_range(start, end) -> [monday_str, ...]   # 기간에 걸치는 모든 주의 월요일
```

### function1.py — 종목 고르기
```python
select_stocks(target_monday, cap_min=500_000_000_000, top_change=20, top_value=5,
              with_names=False, out_path=None) -> list[dict]
# target_monday 직전 주(prior_week)로: 시총≥cap_min → 주간변동율 상승 Top_change → 거래대금 Top_value
# F0 = f0_close(code, prior_fri, fallback=yf 금종가)
# 반환 [{code, chg, val, fri_close(=F0), mon_open [, name]}]; out_path 주면 json 저장
# = 기존 select_stocks.main()에서 상수 4개를 weekcal.prior_week()로 치환 + I/O를 out_path 게이트
```

### function2.py — 엔진 가동
```python
run_engine(code, start, end, F0, capital=10_000_000.0, strat=STRAT281, engine_run=run) -> dict | None
# bars_5m(code,start,end) → engine_run(bars, F0, capital, **strat)
# 반환 {code, F0, bars, events, ctx, source, nbar}; 5분봉 없으면 None
# 엔진/전략 주입 가능 → 다른 엔진도 function2 수정 없이 plug-in
```

### function3.py — 보고서 (순수·오프라인·결정론)
```python
week_chart(bars, events, ctx, reentry) -> str          # run_live_report에서 그대로 이전
narrative(name, code, sel, ctx, events, stamp) -> str   # STAMP 전역 → stamp 파라미터
build_report(sections, meta) -> str                     # 파일 쓰기 없음, 문자열 반환
# sections: [{code, name, label, sel, bars, events, ctx, source}]  (label = h2 제목: P1은 "주", P2/3은 종목명)
# meta: {title, stamp, live:bool, subtitle, intro:bool, refresh:int|None}
#   live=True  → '🔴 LIVE' h1 + ⚠️진행중 disclaimer;  False → 평문 title
#   intro=True → legend_block + 선정규칙 + 요약 table (P2/P3);  P1은 False(린) 가능
#   refresh=N & live → <meta http-equiv=refresh content=N> 주입 (historical은 None → 기존과 byte-동일)
#   ◆ 미청산 마커는 플래그 불필요 — week_chart가 "데이터 종료" in e.reason 으로 자동 판정
```
name 조회(screener)는 function3에서 **제거**, 드라이버가 1회 수행 → function3 네트워크-free.

## Process 드라이버 (얇은 조립, 모든 I/O 담당)

```python
# process1.py — 원자 단위: 종목 + 기간 → 주별 섹션 → 1 html
process1(code, start, end, *, strat=STRAT281, live=False, out_path=None) -> html
  for m in weeks_in_range(start, end):
     ws, we = week_bounds(m); _, pf, *_ = prior_week(m); F0,_ = f0_close(code, pf)
     sec = run_engine(code, ws, we, F0, strat=strat)
     if sec: sec.update(name=resolve_name(code), label=f"{m} 주", sel={...}); sections.append(sec)
  build_report(sections, meta={title:f"281 · {name}({code})", stamp:now, live, intro:False, refresh:None})

# process2.py — 과거 확인: f1 → 종목별 f2(=process1 엔진스텝) → f3 병합 → 1 html
process2(target_monday, *, out_path, strat=STRAT281) -> html
  top = select_stocks(target_monday, with_names=True)
  ws, we = week_bounds(target_monday)
  for sel in top:
     sec = run_engine(sel["code"], ws, we, sel["fri_close"], strat=strat)
     if sec: sec.update(name=sel.get("name") or resolve_name(sel["code"]), label=name, sel=sel); sections.append(sec)
  build_report(sections, meta={title:"281 과거주 확인", stamp:f"{target_monday} 마감", live:False, intro:True, refresh:None})

# process3.py — 실시간, cron 진입점 (--mode select|update)
select (주말): next_mon = --monday or 다음주 월; select_stocks(next_mon, with_names=True, out_path=TOP5)
               + TOP5에 monday 저장({"monday":..., "stocks":[...]})
update (평일 틱): TOP5 로드; ws,we = week_bounds(monday); 종목별 run_engine;
               build_report(sections, meta={title:"LIVE 281 이번 주", stamp:now, live:True, intro:True, refresh:300});
               OUT 매번 동일 경로 덮어쓰기
```

**실시간 "차트가 옆으로 늘어난다"의 원리:** update는 파일을 버전화하지 않는다. `bars_5m`가 월요일→now를 가져오고 `week_chart`의 `W=max(940, n*8+90)`가 봉 수에 비례 → 매 재생성마다 캔들이 늘고 SVG가 넓어짐(자동). `<meta refresh 300>`이 열린 브라우저를 5분 틱에 맞춰 새로고침.

**cron 등록:**
```cron
0 18 * * 6         python3 /home/jeff/bullet281/pipeline/process3.py --mode select
*/5 9-15 * * 1-5   python3 /home/jeff/bullet281/pipeline/process3.py --mode update
```
`now()`는 오직 stamp(표시)용으로만 진입 — 데이터 윈도우는 `week_bounds`로 고정.

## 구현 순서 (단계별 검증)

1. **weekcal.py** — 날짜 계산. 단위 확인(prior_week/weeks_in_range 출력 print).
2. **function1.py** + `select_stocks.py` shim — `select_stocks("2026-07-06", with_names=True)` → `_top5.json` 스키마·값 확인.
3. **function2.py** — 한 종목 `run_engine` → events/ctx/weekly_return 확인.
4. **function3.py** — week_chart/narrative/skeleton **그대로 이전**(STAMP→param, refresh opt-in만). **골든 diff**: 기존 `_top5.json`+고정 stamp로 build_report → `report/live/live-281-thisweek.html`와 byte-비교(마지막 진행중 봉 제외).
5. **process1/2/3.py** 조립 + `run_live_report.py` shim.
6. **문서 갱신**: `.claude/workflows/live-weekly-pipeline.md`(상수→파라미터, tvDatafeed 데이터표 정정), `readme.md`(파일맵), `claude.md` 필요시.

## Verification (end-to-end)

1. **골든 렌더 diff** — 기존 `_top5.json` 고정 입력 + `stamp="2026-07-09 목 ~14:00"`, refresh=None → 기존 live html과 **byte-동일** 기대(진행중 마지막 봉은 네트워크 변동 → 캐시 후 diff 또는 tail 제외).
2. **Process1 스모크** — `process1("005930", "2026-06-29", "2026-07-06")` → 주별 섹션 2개, 차트/마커/내러티브 확인.
3. **Process2 과거주** — `process2("2026-06-29", out_path=scratch)` → 완료된 주: `T/S` 마커(◆ 아님), 금 15:15 청산, 요약표.
4. **Process3 dry-run** — `process3.py --mode update` 1회 → 같은 OUT 덮어씀·`<meta refresh 300>`·🔴 LIVE·◆ 확인; 2회째 파일이 새로 생기지 않고 더 넓어지는지.
5. **Process3 select** — `--mode select --monday <다음주 월>` → `_top5.json`에 name + monday 저장 확인.

## 핵심 참조 파일
- `pipeline/run_live_report.py` — week_chart/narrative/skeleton 원본(그대로 보존), 하드코딩 CUR_*/STAMP
- `pipeline/select_stocks.py` — function1 원본, 상수→weekcal.prior_week
- `pipeline/data_source.py` — bars_5m/f0_close (end 반열림·700봉 fetch 의미)
- `engines/engine281/chart.py` — Chart/Candle/legend_block/색상상수 (week_chart 의존)
- `engines/engine281/engine.py`·`strategy281.py` — run()/STRAT281 (불변, 참조만)
- `.claude/workflows/live-weekly-pipeline.md` — 갱신 대상(+ 낡은 데이터소스표 정정)
