#!/usr/bin/env bash
# MyBrain installer
# 用法:
#   ./install.sh                     交互式，默认装到 ~/.claude
#   ./install.sh /path/to/vault      指定 vault 路径
#   TARGET=~/.codex ./install.sh     指定客户端 skills 目录

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_ROOT="${TARGET:-$HOME/.claude}"
SKILLS_DIR="$TARGET_ROOT/skills"
RULES_DIR="$TARGET_ROOT/rules/common"

info()  { printf '  %s\n' "$*"; }
ok()    { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn()  { printf '  \033[33m!\033[0m %s\n' "$*"; }
die()   { printf '  \033[31m✗\033[0m %s\n' "$*" >&2; exit 1; }

printf '\n  MyBrain 安装程序\n\n'

# ---------- 1. 确定 vault 路径 ----------
VAULT="${1:-}"
if [ -z "$VAULT" ]; then
  printf '  Obsidian vault 路径（例如 ~/vault 或 /path/to/vault）: '
  read -r VAULT
fi
[ -n "$VAULT" ] || die "vault 路径不能为空"

# 展开 ~
case "$VAULT" in
  "~"*) VAULT="$HOME${VAULT#\~}" ;;
esac

# 归一化：去掉尾部斜杠
VAULT="${VAULT%/}"
VAULT="${VAULT%\\\\}"

if [ -d "$VAULT" ]; then
  ok "vault 已存在: $VAULT"
else
  warn "vault 不存在: $VAULT"
  printf '  现在创建目录结构？[y/N] '
  read -r ans
  if [ "${ans:-N}" = "y" ] || [ "${ans:-N}" = "Y" ]; then
    mkdir -p "$VAULT"/{00_Inbox,01_Daily,02_Reports/周报,02_Reports/月报,03_Knowledge,04_Projects}
    ok "已创建 vault 目录结构"
  fi
fi

mkdir -p "$VAULT"/{00_Inbox,01_Daily/$(date +%Y-%m),02_Reports/周报,02_Reports/月报,03_Knowledge,04_Projects}

# ---------- 1b. 播种元数据文件 ----------
# _词表.md / _资产契约.md 是规则文件要读的元数据层。
# 只在不存在时播种，绝不覆盖用户已有的版本。
seed_meta() {
  local name="$1"
  local dst="$VAULT/$name"
  if [ -e "$dst" ]; then
    ok "$name 已存在，跳过"
  else
    cp "$REPO_DIR/templates/$name" "$dst"
    ok "已播种 $name（模板，按需修改）"
  fi
}
seed_meta "_词表.md"
seed_meta "_资产契约.md"

# ---------- 2. 检查依赖 ----------
command -v perl >/dev/null 2>&1 || die "需要 perl（用于替换路径占位符）"
mkdir -p "$SKILLS_DIR" "$RULES_DIR"

# ---------- 3. 安装 skill ----------
printf '\n  安装 skill 到 %s\n' "$SKILLS_DIR"
count=0
for src in "$REPO_DIR"/skills/*/; do
  name="$(basename "$src")"
  dst="$SKILLS_DIR/$name"

  if [ -e "$dst" ]; then
    backup="${dst}.bak.$(date +%Y%m%d-%H%M%S)"
    mv "$dst" "$backup"
    warn "已存在，备份到 $(basename "$backup")"
  fi

  mkdir -p "$dst"
  cp "$src/SKILL.md" "$dst/SKILL.md"
  MYBRAIN_VAULT="$VAULT" perl -pi -e 's/\{\{VAULT_PATH\}\}/$ENV{MYBRAIN_VAULT}/g' "$dst/SKILL.md"
  ok "$name"
  count=$((count + 1))
done

# ---------- 3b. 安装契约校验脚本 ----------
# vault_doctor.py 的 L1 基线按 vault 现状写入，装完那一刻即为「只增不减」的起点。
# 只放脚本，不自动跑 —— 跑不跑由人决定。
printf '\n  安装契约校验脚本到 %s/_scripts\n' "$VAULT"
mkdir -p "$VAULT/_scripts"

L1_COUNT="$(
  find "$VAULT/01_Daily" "$VAULT/02_Reports" "$VAULT/04_Projects" \
       -type f -name '*.md' 2>/dev/null | wc -l | tr -d ' '
)"
case "$L1_COUNT" in ''|*[!0-9]*) L1_COUNT=0 ;; esac

script_count=0
for src in "$REPO_DIR"/_scripts/*.py; do
  [ -e "$src" ] || continue
  name="$(basename "$src")"
  dst="$VAULT/_scripts/$name"

  if [ -e "$dst" ]; then
    backup="${dst}.bak.$(date +%Y%m%d-%H%M%S)"
    mv "$dst" "$backup"
    warn "$name 已存在，备份到 $(basename "$backup")"
  fi

  cp "$src" "$dst"
  MYBRAIN_L1="$L1_COUNT" perl -pi -e 's/\{\{L1_BASELINE\}\}/$ENV{MYBRAIN_L1}/g' "$dst"
  ok "$name"
  script_count=$((script_count + 1))
done

if [ "$script_count" -eq 0 ]; then
  warn "仓内没有 _scripts/*.py，跳过"
elif [ "$L1_COUNT" -eq 0 ]; then
  warn "L1 基线写入为 0（vault 里还没有 01_Daily/02_Reports/04_Projects？）——第 8 项检查将跳过"
else
  ok "L1 基线写入为 $L1_COUNT（日后只增不减）"
fi
info "跑法：cd \"$VAULT\" && python _scripts/vault_doctor.py"

# ---------- 4. 安装全局规则 ----------
printf '\n  安装全局规则到 %s\n' "$RULES_DIR"
rule_src="$REPO_DIR/rules/common/brain-capture.md"
rule_dst="$RULES_DIR/brain-capture.md"
if [ -e "$rule_dst" ]; then
  mv "$rule_dst" "${rule_dst}.bak.$(date +%Y%m%d-%H%M%S)"
  warn "已存在，已备份"
fi
cp "$rule_src" "$rule_dst"
MYBRAIN_VAULT="$VAULT" perl -pi -e 's/\{\{VAULT_PATH\}\}/$ENV{MYBRAIN_VAULT}/g' "$rule_dst"
ok "brain-capture.md"

# ---------- 5. 校验 ----------
printf '\n  校验\n'
leftover=$(grep -rl '{{VAULT_PATH}}\|{{L1_BASELINE}}' \
  "$SKILLS_DIR" "$rule_dst" "$VAULT/_scripts" 2>/dev/null || true)
if [ -n "$leftover" ]; then
  warn "以下文件仍有未替换的占位符："
  printf '    %s\n' $leftover
else
  ok "所有占位符已替换"
fi

missing_meta=""
for name in "_词表.md" "_资产契约.md"; do
  [ -e "$VAULT/$name" ] || missing_meta="$missing_meta $name"
done
if [ -n "$missing_meta" ]; then
  warn "vault 缺少元数据文件：$missing_meta"
  printf '    全局规则会去读它们。装完请手动补齐。\n'
else
  ok "元数据文件就位（_词表.md / _资产契约.md）"
fi

printf '\n  完成：%s 个 skill + 1 条全局规则 + %s 个校验脚本\n\n' "$count" "$script_count"
printf '  下一步：\n'
printf '    1. 在 agent 客户端里说「/start-my-day」试试\n'
printf '    2. 新的对话会自动触发知识捕获（每次会话最多 3 条）\n'
printf '    3. 随时用「/save-to-brain」手动做一次完整归档\n'
printf '    4. 体检：cd "%s" && python _scripts/vault_doctor.py\n\n' "$VAULT"
