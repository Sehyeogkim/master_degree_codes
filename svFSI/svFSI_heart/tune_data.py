import re
import math
from itertools import islice
from typing import List, Tuple, Optional

STAR_RUN_RE = re.compile(r"\*+")

def _safe_float(s: str) -> float:
    s = s.strip()
    if (not s) or ("*" in s):
        return 0.0
    s = s.replace("D", "E").replace("d", "E")
    try:
        return float(s)
    except ValueError:
        return 0.0

def _looks_parseable_field(seg: str) -> bool:
    seg = seg.strip()
    if not seg:
        return True
    if "*" in seg:
        return True
    try:
        float(seg.replace("D", "E").replace("d", "E"))
        return True
    except ValueError:
        return False

def _best_offset_for_width(line: str, width: int, ncols: int) -> Tuple[int, int]:
    # offset을 0..width-1까지 시험해서 "숫자/별표로 잘 해석되는 칸"이 최대가 되는 offset 선택
    best_score = -10**9
    best_offset = 0
    max_offset = min(width, max(1, len(line)))
    for off in range(max_offset):
        score = 0
        for i in range(ncols):
            seg = line[off + i * width : off + (i + 1) * width]
            if not seg:
                score -= 2
                continue
            if _looks_parseable_field(seg):
                score += 1
            else:
                score -= 3
        if score > best_score:
            best_score = score
            best_offset = off
    return best_offset, best_score

def _split_fixed_width(line: str, width: int, ncols: int) -> List[str]:
    off, _ = _best_offset_for_width(line, width, ncols)
    need_len = off + ncols * width
    if len(line) < need_len:
        line = line.ljust(need_len)
    return [line[off + i * width : off + (i + 1) * width] for i in range(ncols)]

def _detect_width(probe_lines: List[str], ncols: int) -> int:
    # 1) 별표 run 길이들의 gcd로 폭 추정 (가장 강력)
    star_lengths = []
    for ln in probe_lines:
        for m in STAR_RUN_RE.finditer(ln):
            star_lengths.append(len(m.group()))
    if star_lengths:
        g = 0
        for L in star_lengths:
            g = math.gcd(g, L)
        # 너무 작은 gcd면(예: 2) 의미 없으니 스코어링으로 넘어감
        if 10 <= g <= 40:
            return g

    # 2) 폭 후보(10~40)를 스코어링해서 선택
    cand = [ln.rstrip("\n") for ln in probe_lines if ln.strip()]
    if not cand:
        return 14  # fallback

    best_w, best_avg = 14, -1e9
    for w in range(10, 41):
        total = 0
        cnt = 0
        for ln in cand[:200]:
            _, sc = _best_offset_for_width(ln, w, ncols)
            total += sc
            cnt += 1
        avg = total / max(cnt, 1)
        if avg > best_avg:
            best_avg = avg
            best_w = w
    return best_w

def clean_fortran_star_file(
    in_path: str,
    out_path: str,
    ncols: int = 15,
    width: Optional[int] = None,
    probe_nlines: int = 2000,
    out_float_fmt: str = "{:.6E}",
) -> None:
    # 1) 폭 자동 추정용 probe
    with open(in_path, "r", encoding="utf-8", errors="replace") as f:
        probe = list(islice(f, probe_nlines))

    if width is None:
        width = _detect_width(probe, ncols)

    # 2) 본 처리(스트리밍)
    with open(in_path, "r", encoding="utf-8", errors="replace") as fin, \
         open(out_path, "w", encoding="utf-8") as fout:

        for raw in fin:
            line = raw.rstrip("\n")
            if not line.strip():
                fout.write("\n")
                continue

            # 먼저 공백 split이 정상적으로 15개면 그걸 사용
            parts = line.split()
            if len(parts) == ncols and all(("*" in p) or _looks_parseable_field(p) for p in parts):
                vals = [0.0 if "*" in p else _safe_float(p) for p in parts]
            else:
                # 망가진 줄은 fixed-width로 복구
                segs = _split_fixed_width(line, width, ncols)
                vals = [_safe_float(s) for s in segs]

            fout.write(" ".join(out_float_fmt.format(v) for v in vals) + "\n")

if __name__ == "__main__":
    # 사용 예시:
    #   python fix_fortran_output.py input.dat output_clean.dat
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="원본 Fortran 출력 파일")
    ap.add_argument("output", help="정리된 출력 파일")
    ap.add_argument("--ncols", type=int, default=15, help="컬럼 개수 (기본 15)")
    ap.add_argument("--width", type=int, default=None, help="고정 폭을 알고 있으면 지정(예: 14). 미지정 시 자동 추정")
    args = ap.parse_args()

    clean_fortran_star_file(args.input, args.output, ncols=args.ncols, width=args.width)
