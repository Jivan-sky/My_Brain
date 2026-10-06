"""全库 wikilink 有效性检查。

用法（在本脚本所在 vault 的根目录跑）：
    python _scripts/check_links.py

判定规则：
- `[[目标]]` / `[[目标|别名]]` / `[[路径/目标#锚点|别名]]` 取「路径最后一段」
- 纯锚点链接 `[[#小节]]` 视为页内跳转，跳过
- 围栏代码块与行内反引号里的 `[[...]]` 是示例文本，不算链接

目标分三类判：
1. 显式带 `.md` → 查 `.md` 文件名集合（Obsidian 允许 `[[Note.md]]`，与裸名等价）
2. 显式带媒体扩展名（`![[x.png]]` 这类嵌入 / 附件）→ 查媒体附件集合
3. 其余（裸名）→ 查 `.md` 文件名集合

⚠️ 判扩展名**必须显式比对后缀字符串，不能用 `os.path.splitext`**：文件名里可以合法地
带点（形如 `v1.2.0-发布说明`），`splitext` 会在最后一个点切开，把 `0-发布说明` 误当扩展名。
"""
import re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

# 媒体 / 附件扩展名白名单（小写比对）。带这些后缀的 wikilink 目标按「附件存在性」判，
# 不再要求它是一篇 .md 笔记。
MEDIA_EXT = {
    '.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.svg', '.ico',
    '.pdf', '.canvas',
    '.mp3', '.wav', '.m4a', '.ogg', '.flac',
    '.mp4', '.mov', '.webm', '.mkv', '.avi',
}

allmd = set()
allmedia = set()
for root, dirs, files in os.walk('.'):
    if '.obsidian' in root or '.trash' in root:
        continue
    for f in files:
        low = f.lower()
        if low.endswith('.md'):
            allmd.add(os.path.splitext(f)[0])
            continue
        for ext in MEDIA_EXT:
            if low.endswith(ext):
                allmedia.add(f)
                break

broken = []
nlink = 0
for root, dirs, files in os.walk('.'):
    if '.obsidian' in root or '.trash' in root:
        continue
    for f in files:
        if not f.endswith('.md'):
            continue
        p = os.path.join(root, f)
        txt = open(p, encoding='utf-8').read()
        txt = re.sub(r'^```.*?^```', '', txt, flags=re.S | re.M)   # 围栏代码块
        txt = re.sub(r'`[^`\n]*`', '', txt)                        # 行内反引号
        for m in re.findall(r'\[\[([^\]]+?)\]\]', txt):
            raw = m.split('|')[0].strip().rstrip('\\').strip()
            if raw.startswith('#'):          # 页内锚点
                continue
            tgt = raw.split('#')[0].strip()
            if not tgt:
                continue
            nlink += 1
            base = tgt.split('/')[-1]
            low = base.lower()

            if low.endswith('.md'):                       # 类别 1：显式 .md
                ok = base[:-3] in allmd
            elif any(low.endswith(e) for e in MEDIA_EXT):  # 类别 2：媒体附件
                ok = base in allmedia
            else:                                         # 类别 3：裸名
                ok = base in allmd

            if not ok:
                broken.append((p, tgt))

print(f'库内 md 笔记：{len(allmd)}')
print(f'库内媒体附件：{len(allmedia)}')
print(f'扫描 wikilink：{nlink}')
print(f'失效链接：{len(broken)}')
for p, t in broken:
    print(f'  MISSING  {p}  ->  {t}')
sys.exit(1 if broken else 0)
