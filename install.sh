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
  printf '  Obsidian vault 路径（例如 D:\\Obsidian_database 或 ~/vault）: '
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
leftover=$(grep -rl '{{VAULT_PATH}}' "$SKILLS_DIR" "$rule_dst" 2>/dev/null || true)
if [ -n "$leftover" ]; then
  warn "以下文件仍有未替换的占位符："
  printf '    %s\n' $leftover
else
  ok "所有占位符已替换"
fi

printf '\n  完成：%s 个 skill + 1 条全局规则\n\n' "$count"
printf '  下一步：\n'
printf '    1. 在 agent 客户端里说「/start-my-day」试试\n'
printf '    2. 新的对话会自动触发知识捕获（每次会话最多 3 条）\n'
printf '    3. 随时用「/save-to-brain」手动做一次完整归档\n\n'
