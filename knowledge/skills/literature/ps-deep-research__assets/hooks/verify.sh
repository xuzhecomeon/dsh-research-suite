#!/usr/bin/env bash
# deep-research dev-time verify (v2.7.1) — 单文件聚合 4 子命令
# 用法:
#   verify.sh scan <report.md> [--json]    # Phase 6 自动扫描(主 agent 不得改输出)
#   verify.sh preflight <report.md>         # Phase 0.5 declared vs ran 比对
#   verify.sh frontmatter <report.md>       # tier 阈值校验
#   verify.sh drift                         # 跨 skill 文件 tier 数字一致
#   verify.sh hook-tests                    # 7 fixture self-test
#   verify.sh all [report.md]               # 全跑 + 可选 report 扫描

set -u
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SUB="${1:-help}"; shift || true

num_ge(){ awk -v a="${1:-0}" -v b="${2:-0}" 'BEGIN{exit !((a+0) >= (b+0))}'; }
num_le(){ awk -v a="${1:-0}" -v b="${2:-0}" 'BEGIN{exit !((a+0) <= (b+0))}'; }

#############################################
# subcmd: scan  — Phase 6 报告级 hedge/vague/action_title/rebuttal/confab 扫描
#############################################
cmd_scan() {
  local REPORT="${1:-}"; local FORMAT="${2:-yaml}"
  [[ -z "$REPORT" || ! -f "$REPORT" ]] && { echo "scan: needs <report.md>" >&2; return 64; }

  # 词表 v2.7.1(依据 wordlists.md;新词必加 fixture)
  local HEDGE_RE='可能|或许|也许|视情况|看具体|大致|似乎|大概|应该是|估计|貌似|看起来|may |might |could |possibly|perhaps|arguably|probably|seems to|appears to|in some cases|it is likely'
  local VAGUE_RE='显著|大量|经常|较多|部分|大部分|许多|多数|一些|相对|相当|不少|significantly|many|considerable|often|relatively|somewhat|several|various|a lot of|a number of|fairly|quite'
  local WEAK_H2_RE='^## *(分析|现状|概述|介绍|讨论|局限|缺口|背景|内容|总结|结论|说明|信息|关于|其他|附录)( |$|与|和)'
  local REBUT_RE='Rebuttal|例外:|反方:|反对|但.*不成立|然而.*并非|尽管.*仍|critics argue|opponents claim|counter-argument'
  local CONFAB_RE='[0-9]+\.?[0-9]*[[:space:]]*(MB|GB|KB|TB|%|x|×|倍|ms|s |秒|分钟|min|hour|小时|天|day|month|月|year|年)'

  local H=$(grep -oE "$HEDGE_RE" "$REPORT" 2>/dev/null | wc -l | tr -d ' ')
  local V=$(grep -oE "$VAGUE_RE" "$REPORT" 2>/dev/null | wc -l | tr -d ' ')
  local TH=$(grep -cE '^## ' "$REPORT" || true)
  local WH=$(grep -cE "$WEAK_H2_RE" "$REPORT" || true)
  local AR; [[ "$TH" -gt 0 ]] && AR=$(awk "BEGIN{printf \"%.2f\",($TH-$WH)/$TH}") || AR="0.00"
  local RB=$(grep -oE "$REBUT_RE" "$REPORT" 2>/dev/null | wc -l | tr -d ' ')
  local CF=$(grep -oE "$CONFAB_RE" "$REPORT" 2>/dev/null | wc -l | tr -d ' ')
  local WC=$(awk '{gsub(/[^\x00-\x7F]/," & ")}{for(i=1;i<=NF;i++)c++}END{print c}' "$REPORT")

  if [[ "$FORMAT" == "--json" ]]; then
    printf '{"hedge_word_count":%s,"vague_quantifier_count":%s,"action_title_ratio":%s,"total_h2":%s,"weak_h2":%s,"rebuttal_count":%s,"confab_candidates":%s,"word_count":%s}\n' \
      "$H" "$V" "$AR" "$TH" "$WH" "$RB" "$CF" "$WC"
  else
    cat <<EOF
hedge_word_count: $H
vague_quantifier_count: $V
action_title_ratio: $AR
total_h2: $TH
weak_h2: $WH
rebuttal_count: $RB
confab_candidates: $CF
word_count: $WC
EOF
  fi
}

#############################################
# subcmd: preflight — Phase 0.5 declared 与 phase_X ran 比对
#############################################
cmd_preflight() {
  local REPORT="${1:-}"
  [[ -z "$REPORT" || ! -f "$REPORT" ]] && { echo "preflight: needs <report.md>" >&2; return 64; }
  local FM=$(awk '/^---$/{c++;if(c==2)exit;next} c==1' "$REPORT")
  [[ -z "$FM" ]] && { echo "Error: no frontmatter" >&2; return 1; }
  local DECLARED=$(echo "$FM" | awk '
    /^pre_flight:/ {pf=1;next}
    pf && /^[a-z]/ {pf=0}
    pf && /predicted_phases:/ {pp=1;next}
    pp && /^  [a-z]/ {pp=0}
    pp && /will_run/ {gsub(/^ +- /,"",$0);gsub(/:.*/,"",$0);print $0}')
  local SKIPPED=""
  for p in $DECLARED; do
    local ran=$(echo "$FM" | grep -E "^  ${p}:" | head -1 | awk -F: '{print $2}' | tr -d ' ')
    [[ "$ran" == "skipped" || "$ran" == "no" || "$ran" == "fail" || -z "$ran" ]] && SKIPPED+=" $p"
  done
  if [[ -n "$SKIPPED" ]]; then
    echo "preflight: FAIL"; echo "skipped_declared:$SKIPPED"; return 1
  fi
  echo "preflight: PASS"
}

#############################################
# subcmd: frontmatter — tier 阈值校验(a_tier_ratio / vendor_blog / dissent / word_count)
#############################################
_fm_get() {
  echo "$FM" | grep -E "^[[:space:]]*$1:" | head -1 | sed -E "s/^[[:space:]]*$1:[[:space:]]*//" | sed 's/#.*//' | tr -d '"' | tr -d "'" | xargs
}

cmd_frontmatter() {
  local REPORT="${1:-}"
  [[ -z "$REPORT" || ! -f "$REPORT" ]] && { echo "frontmatter: needs <report.md>" >&2; return 64; }
  FM=$(awk '/^---$/{c++;if(c==2)exit;next} c==1' "$REPORT")
  local TIER=$(_fm_get declared_tier); local WC=$(_fm_get word_count); local AT=$(_fm_get a_tier_ratio)
  local VR=$(_fm_get vendor_blog_ratio); local DS=$(_fm_get dissent_queries_run); local DG=$(_fm_get degraded)
  [[ -z "$AT" ]] && AT=-1; [[ -z "$VR" ]] && VR=-1; [[ -z "$DS" ]] && DS=0; [[ -z "$WC" ]] && WC=0
  local F=0 TAGS=""
  _assert(){ if eval "$2"; then echo "  ✅ $1"; else echo "  ❌ $1 (tag:$3)"; F=$((F+1)); TAGS+=" $3"; fi; }
  alias assert=_assert 2>/dev/null
  # use _assert directly
  echo "=== Frontmatter Audit: $TIER ==="
  case "$TIER" in
    deep|museum)
      _assert "字数 ≥5000" "[[ \"$WC\" -ge 5000 ]]" "[under-length]"
      _assert "A-tier ≥0.20" "num_ge \"$AT\" 0.20" "[a-tier-low]"
      _assert "vendor blog ≤0.40" "num_ge \"$VR\" 0 && num_le \"$VR\" 0.40" "[vendor-overrun]"
      _assert "反方 ≥2" "[[ \"$DS\" -ge 2 ]]" "[dissent-missing]" ;;
    standard)
      _assert "字数 ≥2500" "[[ \"$WC\" -ge 2500 ]]" "[under-length]"
      _assert "A-tier ≥0.10" "num_ge \"$AT\" 0.10" "[a-tier-low]"
      _assert "反方 ≥1" "[[ \"$DS\" -ge 1 ]]" "[dissent-missing]" ;;
    fast) _assert "字数 ≥1000" "[[ \"$WC\" -ge 1000 ]]" "[under-length]" ;;
  esac
  [[ "$F" -gt 0 ]] && { echo "frontmatter: FAIL ($F);tags:$TAGS"; return 1; }
  echo "frontmatter: PASS"
}

#############################################
# subcmd: drift — 跨 skill 文件 tier 硬约束一致性
#############################################
_drift_check() {
  local desc="$1" file="$2" pat="$3" min="$4"
  local g=$(grep -cE "$pat" "$SK/$file" 2>/dev/null|tr -d '[:space:]'); [[ -z "$g" ]] && g=0
  if [[ "$g" -lt "$min" ]]; then echo "❌ $desc — $file expects ≥$min of /$pat/, got $g"; D=$((D+1)); else echo "✅ $desc — $file"; fi
}

cmd_drift() {
  SK="${SKILL_DIR:-$HOME/.claude/skills/deep-research}"
  [[ ! -d "$SK" ]] && { echo "Error: $SK not found" >&2; return 66; }
  D=0
  echo "=== Doc-drift check (v5.0: SKILL.md 是单一权威源) ==="
  _drift_check "deep spawn ≥4" "SKILL.md" 'researcher.*≥ *4|spawn ≥4' 1
  _drift_check "deep extract ≥15" "SKILL.md" '≥15' 1
  _drift_check "字数 5000-12000" "SKILL.md" '5000-12000' 1
  _drift_check "字数 5000-12000" "REPORT_TEMPLATES.md" '5000-12000' 1
  _drift_check "A-tier 占比" "SKILL.md" 'A-tier.*占比|A-tier.*≥' 1
  _drift_check "vendor blog 上限" "SKILL.md" 'vendor.*≤|vendor blog' 1
  _drift_check "Phase 5 QA 合并" "SKILL.md" 'Phase 5 QA|QA sub-agent' 1
  _drift_check "反方搜索" "SKILL.md" '反方 query|找反方|反方搜索' 1
  _drift_check "PLAYBOOK 仍引 SKILL 权威" "PLAYBOOK.md" 'SKILL.md.*为准|SKILL.md' 1
  [[ "$D" -gt 0 ]] && { echo "drift: FAIL ($D)"; return 1; }
  echo "drift: PASS (跨文件一致)"
}

#############################################
# subcmd: hook-tests — 7 fixture self-test
#############################################
_cmp_min(){ if num_ge "$2" "$3"; then echo "  ✅ $1=$2 ≥ $3"; PASS=$((PASS+1)); else echo "  ❌ $1=$2 < $3"; FAIL=$((FAIL+1)); fi; }
_cmp_max(){ if num_le "$2" "$3"; then echo "  ✅ $1=$2 ≤ $3"; PASS=$((PASS+1)); else echo "  ❌ $1=$2 > $3"; FAIL=$((FAIL+1)); fi; }

cmd_hook_tests() {
  local FX="$SCRIPT_DIR/../hook-tests/fixtures"
  PASS=0; FAIL=0
  echo "=== Hook self-test ==="
  local fixtures=("$FX"/*.md)
  if [[ ! -d "$FX" || ! -e "${fixtures[0]}" ]]; then
    echo "hook-tests: missing fixtures in $FX" >&2
    return 1
  fi
  for f in "${fixtures[@]}"; do
    local n=$(basename "$f" .md); echo "▶ $n"
    local out=$(cmd_scan "$f")
    local h=$(echo "$out"|awk '/hedge_word_count:/{print $2}')
    local v=$(echo "$out"|awk '/vague_quantifier_count:/{print $2}')
    local a=$(echo "$out"|awk '/action_title_ratio:/{print $2}')
    local r=$(echo "$out"|awk '/rebuttal_count:/{print $2}')
    local c=$(echo "$out"|awk '/confab_candidates:/{print $2}')
    case "$n" in
      01_clean_report) _cmp_max hedge "$h" 0; _cmp_max vague "$v" 0; _cmp_min action "$a" 0.70; _cmp_min rebuttal "$r" 2 ;;
      02_hedge_heavy)  _cmp_min hedge "$h" 15 ;;
      03_vague_heavy)  _cmp_min vague "$v" 15 ;;
      04_no_action_title) _cmp_max action "$a" 0.10 ;;
      05_confab_numbers)  _cmp_min confab "$c" 12 ;;
      06_preflight_skip) cmd_preflight "$f" >/dev/null && { echo "  ❌ should FAIL"; FAIL=$((FAIL+1)); } || { echo "  ✅ preflight correctly FAILed"; PASS=$((PASS+1)); } ;;
      07_preflight_clean) cmd_preflight "$f" >/dev/null && { echo "  ✅ preflight PASS"; PASS=$((PASS+1)); } || { echo "  ❌ should PASS"; FAIL=$((FAIL+1)); } ;;
      R03_retrospective) echo "  (info-only fixture: scan=$h hedge/$v vague/$a action/$r rebuttal)"; PASS=$((PASS+1)) ;;
    esac
  done
  echo "Pass: $PASS  Fail: $FAIL"
  [[ "$FAIL" -gt 0 ]] && return 1 || return 0
}

#############################################
# subcmd: all — 一键全跑(可选 report)
#############################################
cmd_all() {
  local REPORT="${1:-}"
  local rc=0
  echo "## 1 Hook self-test"; cmd_hook_tests || rc=1; echo
  echo "## 2 Doc-drift"; cmd_drift || rc=1; echo
  if [[ -n "$REPORT" && -f "$REPORT" ]]; then
    echo "## 3 Report: $REPORT"
    echo "### scan"; cmd_scan "$REPORT" || rc=1
    echo "### preflight"; cmd_preflight "$REPORT" || rc=1
    echo "### frontmatter"; cmd_frontmatter "$REPORT" || rc=1
  fi
  [[ "$rc" -eq 0 ]] && echo "✅ ALL PASS" || echo "❌ FAIL (rc=$rc)"
  return $rc
}

case "$SUB" in
  scan) cmd_scan "$@" ;;
  preflight) cmd_preflight "$@" ;;
  frontmatter) cmd_frontmatter "$@" ;;
  drift) cmd_drift ;;
  hook-tests) cmd_hook_tests ;;
  all) cmd_all "$@" ;;
  *) cat <<EOF
Usage: verify.sh <subcmd> [args]
  scan <report.md> [--json]   Phase 6 报告级扫描
  preflight <report.md>        Phase 0.5 declared vs ran
  frontmatter <report.md>      tier 阈值校验
  drift                        跨 skill 文件一致性
  hook-tests                   7 fixture self-test
  all [report.md]              一键全跑
EOF
    [[ "$SUB" == "help" || "$SUB" == "-h" || "$SUB" == "--help" ]] && exit 0 || exit 64 ;;
esac
