"""全库契约体检 —— 把 _资产契约.md 的不变量变成可执行检查。

用法（在本脚本所在 vault 的根目录跑）：
    python _scripts/vault_doctor.py
    python _scripts/vault_doctor.py --md     额外写 _scripts/_doctor_report.md

只读。不改任何笔记。exit 1 = 有违规。

检查项：
  1. 每篇恰好 1 个 type/，且值在 _词表.md 内
  2. sum(type) == md 总数（排除 _scripts/*.md 工具产物）
  3. source: 可解析；标出字面量占位
  4. tags 全在受控词表内
  5. wikilink 有效性
  6. MOC/索引登记完整性
  7. 孤儿（0 入链）
  8. L1 基线只增不减

L1_BASELINE 由 install.sh 在安装时按你的 vault 现状写入，之后只增不减。

口径说明（踩过的坑，勿改）：
  - 只解析 frontmatter 块。正文里的 `type/xxx` 之类是示例文本，不是标签。
  - `_scripts/*.md` 是脚本产物，无 frontmatter，按契约豁免。
  - 围栏代码块与行内反引号里的 `[[...]]` 不算链接。
  - 别名可写成 `[[路径\\|别名]]`，切 `|` 前要先剥 `\\`。
"""
import re, os, sys, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

SKIP_DIRS = ('.obsidian', '.trash', '_backup', '.claude', '.claudian',
             '.vault-scripts', 'node_modules')
TOOL_OUT_DIR = '_scripts'          # 该目录下的 .md 是工具产物，豁免
L1_BASELINE = {{L1_BASELINE}}      # install.sh 写入；0 = 不检查
NAV_NAMES = {'_MOC', '_索引', '_INBOX', '_词表', '_资产契约'}

if not os.path.exists('_词表.md'):
    sys.exit('找不到 _词表.md —— 请在 vault 根目录跑，或先用 install.sh 播种元数据文件。')

# ---------- 读受控词表 ----------
vocab = set()
with open('_词表.md', encoding='utf-8') as f:
    for line in f:
        if not line.lstrip().startswith('|'):
            continue
        for tok in re.findall(r'`([^`]+)`', line):
            tok = tok.strip()
            if not tok or '.' in tok or '<' in tok or '#' in tok:
                continue
            if tok[0].isdigit() or '-' == tok[0] and not tok.startswith('type/'):
                continue
            if tok.endswith('/'):      # 裸命名空间 `type/` 不是 tag
                continue
            vocab.add(tok)
VALID_TYPE = {t for t in vocab if t.startswith('type/')}

# ---------- 收集笔记 ----------
notes = {}          # path -> text
exempt = set()      # _scripts/ 下工具产物
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for fn in files:
        if not fn.endswith('.md'):
            continue
        p = os.path.join(root, fn).replace('\\', '/').lstrip('./')
        if p.startswith(TOOL_OUT_DIR + '/'):
            exempt.add(p)
            continue
        notes[p] = open(p, encoding='utf-8').read()

basenames = {os.path.splitext(os.path.basename(p))[0] for p in notes}
# wikilink 也能指向附件（png/webp/pdf…），Obsidian 照样解析，别误判成断链
attach = set()
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for fn in files:
        if not fn.endswith('.md'):
            attach.add(os.path.splitext(fn)[0])
resolve = basenames | attach
errors, warns = [], []

# leaf -> 真实 basename。链接可带扩展名也可不带，两种都要认。
# 注意：不能用 splitext 去归一化文件名本身 —— 形如 `v1.2.0-发布说明` 的名字里带点，
# splitext 会在最后一个点切开，把 `0-发布说明` 误当成扩展名，进而误判成孤儿。
resolve_map = {}
for name in resolve:
    resolve_map.setdefault(name, name)
    if '.' in name:
        resolve_map.setdefault(name.rsplit('.', 1)[0], name)


def lookup(leaf):
    return resolve_map.get(leaf) or resolve_map.get(leaf.rsplit('.', 1)[0])


def parse_fm(text):
    """只取开头 frontmatter 块；返回 (存在?, 文本)。"""
    if not text.startswith('---'):
        return False, ''
    m = re.search(r'^---\s*$', text[3:], re.M)
    if not m:
        return False, ''
    return True, text[3:3 + m.start()]


type_of, tags_of, src_of = {}, {}, {}
for p, text in sorted(notes.items()):
    has_fm, fm = parse_fm(text)
    if not has_fm:
        errors.append(f'[1] 无 frontmatter: {p}')
        type_of[p] = []
        tags_of[p] = []
        src_of[p] = None
        continue
    type_of[p] = re.findall(r'^\s*-\s*(type/\S+)', fm, re.M)
    tags_of[p] = re.findall(r'^\s*-\s*(\S+)\s*$', fm, re.M)
    m = re.search(r'^source:\s*(.+?)\s*$', fm, re.M)
    src_of[p] = m.group(1).strip().strip('"\'') if m else None

# ---------- 1. type/ ----------
for p in notes:
    if p in exempt:
        continue
    base = os.path.splitext(os.path.basename(p))[0]
    want = 'type/moc' if base in NAV_NAMES else None
    n = len(type_of[p])
    if not type_of[p]:
        continue                      # 已在无 frontmatter 里报过
    if want:
        if type_of[p] != [want]:
            warns.append(f'[1] 导航文件 type 应为 {want}，实际 {type_of[p]}: {p}')
    elif n != 1:
        errors.append(f'[1] type/ 数量 = {n}（应恰好 1）: {p} -> {type_of[p]}')
    for t in type_of[p]:
        if t not in VALID_TYPE:
            errors.append(f'[1] type 不在词表: {p} -> {t}')

# ---------- 2. sum(type) == md 总数 ----------
cnt = collections.Counter(t for p in notes for t in type_of[p])
total = len(notes)
sumt = sum(cnt.values())
if sumt != total:
    errors.append(f'[2] sum(type) = {sumt}，md 总数 = {total}，差 {total - sumt}')

# ---------- 3. source ----------
for p, s in src_of.items():
    if s is None:
        continue
    if not s.startswith('[['):
        continue
    tgt = s.strip('[]').split('|')[0].split('#')[0].strip().rstrip('\\')
    if not tgt:
        continue
    if '待确认' in tgt:
        warns.append(f'[3] source 是占位符: {p} -> {s}')
    elif not lookup(tgt.split('/')[-1]):
        errors.append(f'[3] source 指向不存在的笔记: {p} -> {s}')

# ---------- 4. tags 词表 ----------
for p, ts in tags_of.items():
    for t in ts:
        if t not in vocab and not t.startswith('type/'):
            warns.append(f'[4] tag 不在词表: {p} -> {t}')

# ---------- 5. wikilink ----------
inbound = collections.Counter()
broken = []
for p, text in sorted(notes.items()):
    body = re.sub(r'^```.*?^```', '', text, flags=re.S | re.M)
    body = re.sub(r'`[^`\n]*`', '', body)
    for m in re.findall(r'\[\[([^\]]+?)\]\]', body):
        raw = m.split('|')[0].strip().rstrip('\\').strip()
        if raw.startswith('#'):
            continue
        tgt = raw.split('#')[0].strip()
        if not tgt:
            continue
        leaf = tgt.split('/')[-1]
        hit = lookup(leaf)
        if hit:
            inbound[hit] += 1
        else:
            broken.append((p, tgt))
for p, t in broken:
    errors.append(f'[5] 失效链接: {p} -> {t}')

# ---------- 6. MOC 登记 ----------
registered = set()
for p in notes:
    if os.path.splitext(os.path.basename(p))[0] in NAV_NAMES:
        for tgt in re.findall(r'\[\[([^\]]+?)\]\]', notes[p]):
            registered.add(tgt.split('|')[0].split('#')[0].strip().rstrip('\\').split('/')[-1])
# 只查 knowledge：知识桶的规范索引就是 MOC。
# 项目文档由自己的 项目档案/项目全貌/README 索引，没进顶层 MOC 不算问题；
# 真孤立的情况由检查 7 兜住。
for p in sorted(notes):
    if type_of[p] == ['type/knowledge']:
        base = os.path.splitext(os.path.basename(p))[0]
        if base not in registered:
            warns.append(f'[6] 未登记进任何 MOC/索引: {p}')

# ---------- 7. 孤儿 ----------
for p in sorted(notes):
    base = os.path.splitext(os.path.basename(p))[0]
    if base in NAV_NAMES:
        continue
    if inbound[base] == 0:
        warns.append(f'[7] 孤儿（0 入链）: {p}')

# ---------- 8. L1 基线 ----------
l1 = sum(1 for p in notes if p.split('/')[0] in ('01_Daily', '02_Reports', '04_Projects'))
if L1_BASELINE and l1 < L1_BASELINE:
    errors.append(f'[8] L1 记录 {l1} < 基线 {L1_BASELINE}（只增不减）')

# ---------- 输出 ----------
lines = []
lines.append('# vault_doctor 体检报告')
lines.append('')
lines.append(f'- 笔记总数：{total}（另有 `_scripts/` 工具产物 {len(exempt)} 篇，按契约豁免）')
lines.append(f'- `sum(type)`：{sumt}')
lines.append(f'- L1 记录数：{l1}（基线 {L1_BASELINE or "未设"}）')
lines.append(f'- 受控词表解析出 tag：{len(vocab)} 个，其中 type/ {len(VALID_TYPE)} 个')
lines.append(f'- **错误 {len(errors)} · 告警 {len(warns)}**')
lines.append('')
lines.append('## 分桶实测')
lines.append('')
lines.append('| type | 篇数 |')
lines.append('|---|---:|')
for t, c in sorted(cnt.items()):
    lines.append(f'| `{t}` | {c} |')
lines.append('')
for title, items in (('## 错误', errors), ('## 告警', warns)):
    lines.append(title + f'（{len(items)}）')
    lines.append('')
    if items:
        lines.extend('- ' + e for e in items)
    else:
        lines.append('无')
    lines.append('')

out = '\n'.join(lines)
print(out)
if '--md' in sys.argv:
    with open('_scripts/_doctor_report.md', 'w', encoding='utf-8', newline='') as f:
        f.write(out)
    print('已写 _scripts/_doctor_report.md')
sys.exit(1 if errors else 0)
