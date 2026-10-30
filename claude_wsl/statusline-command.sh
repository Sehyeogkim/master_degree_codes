#!/usr/bin/env bash
# Claude Code status line — styled after shell PS1:
#   bold-green  user@host  :  bold-blue cwd  (git-branch)
# followed by: model · rate limits · token/cache info
#
# Self-contained: parses the status JSON with python3 (no jq dependency).
# python3 is located by absolute path so this works regardless of the PATH
# the status line is invoked under.

input=$(cat)

# --- Locate a python3 interpreter ---
PY=""
for cand in python3 /usr/bin/python3 /home/jeff/miniconda3/bin/python3 /usr/local/bin/python3; do
    if command -v "$cand" >/dev/null 2>&1; then PY="$cand"; break; fi
    [ -x "$cand" ] && { PY="$cand"; break; }
done

# --- Parse all JSON fields in one pass ---
# Emits one value per line (newline preserves empty fields, unlike tab which
# bash's `read` would collapse): cwd, model, five_pct, week_pct,
# total_input, total_output, cache_read, cache_write
fields=()
if [ -n "$PY" ]; then
    mapfile -t fields < <(printf '%s' "$input" | "$PY" -c '
import sys, json
try:
    d = json.load(sys.stdin)
except Exception:
    d = {}
def g(obj, *path, default=""):
    cur = obj
    for k in path:
        if not isinstance(cur, dict) or k not in cur or cur[k] is None:
            return default
        cur = cur[k]
    return cur
cwd   = g(d, "cwd") or g(d, "workspace", "current_dir")
model = g(d, "model", "display_name") or g(d, "model", "id") or "unknown"
five  = g(d, "rate_limits", "five_hour", "used_percentage")
week  = g(d, "rate_limits", "seven_day", "used_percentage")
ti    = g(d, "context_window", "total_input_tokens")
to    = g(d, "context_window", "total_output_tokens")
cr    = g(d, "context_window", "current_usage", "cache_read_input_tokens", default=0)
cw    = g(d, "context_window", "current_usage", "cache_creation_input_tokens", default=0)
for x in [cwd, model, five, week, ti, to, cr, cw]:
    print(x)
')
fi

cwd=${fields[0]}
model=${fields[1]:-unknown}
five_pct=${fields[2]}
week_pct=${fields[3]}
total_input=${fields[4]}
total_output=${fields[5]}
cache_read=${fields[6]:-0}
cache_write=${fields[7]:-0}
cache_total=$((cache_read + cache_write))

# Git branch — resolved from cwd at runtime
git_branch=""
if [ -n "$cwd" ]; then
    git_branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
fi

# --- Build output ---

# PS1 block: bold-green user@host : bold-blue cwd
printf "\033[01;32m%s@%s\033[0m" "$(whoami)" "$(hostname -s)"
printf ":"
if [ -n "$cwd" ]; then
    printf "\033[01;34m%s\033[0m" "$cwd"
fi

# Git branch  (green, in parens — mirrors common PS1 git extensions)
if [ -n "$git_branch" ]; then
    printf " \033[0;32m(%s)\033[0m" "$git_branch"
fi

# Model  (cyan bold, after a separator)
printf "  \033[1;36m%s\033[0m" "$model"

# Rate limits  (yellow; shown only when data is present)
rate_str=""
if [ -n "$five_pct" ]; then
    rate_str="5h:$(printf '%.0f' "$five_pct")%"
fi
if [ -n "$week_pct" ]; then
    [ -n "$rate_str" ] && rate_str="$rate_str "
    rate_str="${rate_str}7d:$(printf '%.0f' "$week_pct")%"
fi
if [ -n "$rate_str" ]; then
    printf "  \033[0;33mlimit:%s\033[0m" "$rate_str"
fi

# Total tokens  (white/dim; shown only after first message)
if [ -n "$total_input" ] && [ "$total_input" != "0" ]; then
    tok_str="in:${total_input}"
    if [ -n "$total_output" ] && [ "$total_output" != "0" ]; then
        tok_str="${tok_str} out:${total_output}"
    fi
    printf "  \033[0;37mtok(%s)\033[0m" "$tok_str"
fi

# Prompt cache  (magenta; shown only when non-zero)
if [ "$cache_total" -gt 0 ] 2>/dev/null; then
    printf "  \033[0;35mcache(+%s r%s)\033[0m" "$cache_write" "$cache_read"
fi

printf "\n"
