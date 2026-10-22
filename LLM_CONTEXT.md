# LLM 上下文日志

给接手这个项目的任何 LLM 的现成简报。先读这里，再读 `CLAUDE.md`（协作偏好），
然后进代码。下面的**会话记录**按时间倒序，记录最近做过的事；再往下的第 1–10 节是
更早的快照，除非后加的会话记录明确推翻了某条，否则仍然成立。

---

## 会话记录（最新在上）

### 2026-10-22 — 界面全中文化 + 中文字体 + 中文文档

**目标：** 界面全部改成简体中文，术语用国服（WeGame）说法；不做中英切换；过滤器
文件本身一个字符都不翻。

**状态：** 分支 `feat/zh-cn-ui`，PR
[#2](https://github.com/panyanyu/poe2-filter-sound-studio/pull/2) 已推送，
**尚未合并**。`py_compile` 全量通过；**没有做 GUI 启动验证**（本机两套 Python 都
没装 `customtkinter`），需要用户本地跑 `run.bat` 确认。

**新增：**
- `core/zh.py` —— 显示名 ⇄ 内部英文值的映射层。里面是几张表（外观模式、配色、
  经济档次模式、置信度、稀有度、音效类型、显隐、价值档次、风险等级）加
  `*_label()` / `*_value()` 双向函数。**设计要点：内部值永远是英文**，因为
  `settings.json`、`operation history`、配色查找都以这些字符串为键；中文只活在
  显示层。
- `core/fonts.py` —— `install_default_fonts(root)`，把 tkinter 命名字体
  （`TkDefaultFont`、`TkTextFont`、`TkMenuFont`、`TkHeadingFont` 等）统一成
  微软雅黑，按 `Microsoft YaHei UI → Microsoft YaHei → 微软雅黑 → SimHei →
  SimSun → Segoe UI` 的顺序探测。

**改动：**
- 主窗口、`ui/` 全部对话框、`features/smart_merge_ui.py` 的界面文案全部中文化：
  菜单、页签、工具栏分簇、表格列头与单元格、右键菜单、状态栏、提示/确认/报错弹窗，
  以及 `HOW_TO_USE_TEXT`（使用说明）和 About / 设置页的长文案。
- 所有字体字面量：`("Segoe UI Semibold", N)` → `("Microsoft YaHei UI", N, "bold")`，
  `"Segoe UI"` / `"Arial"` → `"Microsoft YaHei UI"`。等宽字体保留
  `Consolas` / `Courier`（原始过滤器视图需要等宽）。
- `features/visibility_manager.py`：`SMART_GROUPS` 标签改成中文（通货、引路石/地图、
  传奇、技能宝石、装备、药剂/咒符、符文/灵魂核心/神像、其他），`smart_group_for()`
  的返回值同步改。**这些标签只用于分组显示，不参与文件写入。**
- `ui/visibility_manager_tab.py`：三个筛选下拉框的取值与判断条件一起改成中文
  （`全部` / `当前显示` / `当前隐藏` / `全部章节` / `全部分组`）；表格行的显隐词、
  风险等级、稀有度走 `core/zh.py` 映射。
- `ui/economy_tier_ui.py`、`ui/tier_sound_dialog.py`：模式与置信度下拉框显示中文，
  `Mode(...)` 构造前用 `mode_value()` / `conf_value()` 转回英文。
- `main.py`：`_tree_heading_text`（表格列名）、`_TIER_SORT_RANK`（加中文键）、
  `tier_label`、`rarity_display`、`sound_type_label` 接入；经济档次/主题/外观三个
  下拉框改成「显示中文、回调里映射回英文」。
- `README.md`、`docs/economy_tier_visuals.md`、`docs/development_roadmap.md`、
  `LLM_CONTEXT.md`（本文件）全部改写为中文。

**给下一个 LLM 的坑：**
- 新增界面文案时，**纯显示的**直接写中文；**会参与逻辑判断的**（枚举、下拉框选中值、
  写进设置或文件的东西）必须走 `core/zh.py` 的 `*_label` / `*_value`，否则会把中文
  写进 `settings.json`、操作历史或 `.filter`，后果是设置失效或过滤器被游戏拒绝。
- 过滤器语法关键词（`Show`/`Hide`/`Rarity`/`BaseType`/`PlayAlertSound`/
  `CustomAlertSound`/`SetTextColor`/`PlayEffect`/`MinimapIcon`）**永远保持英文**。
- 表格里 `stype` 的取值 `Custom`/`Play`/`None` 是逻辑键，只在渲染时翻译成
  自定义/内置音效/无音效。
- 中文替换是用脚本按“精确字面量”批量做的，只匹配 `text=` / `label=` / `title(` /
  `title=` / `placeholder_text=` / `_set_status(` / `messagebox` 这些位置，所以列 id、
  字体名、色值、正则片段都没被误伤。以后再做类似批量替换，务必保持这个约束。

### 2026-06-21 — 物品显隐页签

**目标：** 给新手一个页签，把每个规则块在**显示**（物品能掉在地上）和**隐藏**之间
切换，不用手改过滤器文本。硬性不变式：改显隐只重写块首行的 `Show`/`Hide` 这个词，
条件、音效、颜色、`PlayEffect`、`MinimapIcon`、注释、换行符全部保留。

**状态：** 代码在 `feature/item-visibility-tab` 分支，PR #10（旧仓库
`xtheredshirtx/poe2-filter-sound-studio`），**已合并**。

**新增：**
- [features/visibility_manager.py](features/visibility_manager.py) —— 全部核心逻辑，
  不含界面：
  - `iter_filter_blocks(lines)` —— **共享的** Show/Hide 块边界遍历器（生成
    `RawBlock`）。它跟踪每行的 `# [[NNNN]]` / `#  [NNNN]` 章节与子章节标记，
    因此“夹在块体与下一个块首行之间的章节注释”会归属到**后一个**块。每个块的
    `raw_lines` 会裁掉尾部空行和章节标记。**以后做任何遍历块的工具都复用它。**
  - `VisibilityBlockView` —— 表格的一行（起止行号、当前/目标显隐、分类/子章节、
    稀有度、类别、基底、物品等级、堆叠数量、音效/特效/小地图摘要、上下文、
    `raw_lines`、风险等级、风险原因、`stable_key`）。
  - `VisibilityChange` / `ApplyResult` 数据类。
  - `header_word()` / `rewrite_header_word()` —— 纯首行替换，保留缩进、行尾注释
    和精确换行符（`\n`/`\r\n`/`\r`/无）。
  - `assess_risk()` —— 高/中/低。复用 `visual_emphasis.classify_block` 的档次 +
    价值关键词扫描（通货、引路石、地图、传奇、宝石、符文、灵魂核心、神像、裂隙、
    远征、首领、神圣石、崇高石、魔镜…）+ 结构检查（`PlayEffect`/`MinimapIcon`、
    字号 ≥ 40、既无 Class 也无 BaseType = 过宽泛/高风险）。
  - `smart_group_for()` + `SMART_GROUPS` —— 粗略分组，供「分组」下拉使用。
  - `VisibilityManager` —— 持有 `blocks`，绑定应用**同一个** `lines` 列表对象。
    待应用改动只存在各视图的 `desired_visibility` 上，`apply()` 才落地。`apply()`
    的顺序：逐行确认目标行仍以 Show/Hide 开头（漂移的行跳过，绝不写坏）→
    `make_backup(label="visibility")` → 就地重写首行 → `save_filter_file(create_backup=False)`
    → `rebuild()`。
- [ui/visibility_manager_tab.py](ui/visibility_manager_tab.py) —— 表格 + 控制栏 +
  右键菜单 + 批量操作 + 复核对话框（列出计划改动、Show→Hide/Hide→Show 计数、
  高风险数量、文件路径、备份位置，以及“隐藏贵重物品 / 一次隐藏 ≥15 块”的警告）。
- [tests/test_visibility.py](tests/test_visibility.py) —— 17 个测试，覆盖单行替换、
  各类内容保留、只对选中生效、撤销不写盘、过滤器只读、风险标记、章节注释解析、
  无 BaseType、多 BaseType、首行漂移跳过。

**已知坑：**
- 管理器**就地**改 `app.lines`（同一个对象），所以应用后编辑器页签立刻能看到变化；
  界面随后还会调 `app.refresh_filter_data()` 全量刷新。
- “改哪一行”的唯一依据始终是文件里的 `start_line`。`stable_key`（不含 Show/Hide 词，
  不同于 `user_overrides.block_signature`）只用于身份匹配，绝不用来定位编辑目标。
- `刷新`、`撤销未保存的改动` 以及任何重新加载都会**丢弃**待应用改动（从磁盘重建）——
  这是刻意的，行为可预期优先于聪明。

---

## 1. 这个项目是什么

**POE2 Filter Sound Studio** —— 一个 Windows 桌面应用（CustomTkinter），用来编辑
《流放之路 2》的 `.filter` 文件。最初的功能是音效替换 / 音量调整 / 分类浏览，之后
在上面叠了一层视觉工具和安全工具。

- 入口：[main.py](main.py) —— `FilterSoundEditor` 类。
- 解析核心：[core/parser.py](core/parser.py) → `FilterParser` + 音效/颜色/章节正则。
- 块模型：[core/data_models.py](core/data_models.py) → `FilterBlock`。
- 设置持久化：[core/settings.py](core/settings.py) → `AppSettings` +
  `%APPDATA%/POE2FilterSoundEditor/settings.json`。
- 文件 IO：[core/file_operations.py](core/file_operations.py) →
  `load_filter_file`、`save_filter_file`（tmp + 原子替换）、`make_backup`
  （带时间戳 + 轮转）。
- 中文显示映射：[core/zh.py](core/zh.py)；中文字体：[core/fonts.py](core/fonts.py)。

## 2. 按构建顺序的功能

### 2.1 过滤器兼容性检查
更新或换用别人的过滤器时，检测未知/改名的指令并给出自动修复。

- [core/compatibility.py](core/compatibility.py) —— `FilterCompatibilityChecker`、
  `MigrationRulesEngine`、`CompatibilityReport`、`CompatibilityIssue`。校验 POE2 指令集、
  RGB 范围、音量范围、Show/Hide 之外的孤立动作。
- [data/migration_rules.json](data/migration_rules.json) —— 用户可编辑的规则表，
  schema 写在文件自己的 `_rule_schema` 里。四种规则动作：`command`、`regex`、
  `allow`、`remove`。
- [ui/compatibility_dialog.py](ui/compatibility_dialog.py) —— 模态对话框，逐条显示问题、
  可选是否修复、全选可修复、编辑规则文件。
- 接进两条加载路径 + 手动 `过滤器健康 → 检查过滤器兼容性…`。
- 设置项：`AppSettings.auto_check_compatibility`（默认 `True`）。

### 2.2 加载时自动快照
每次加载都在任何工具改动之前先留一份干净备份。

- `make_backup` 增加 `label`（`_load_` 与 `_backup_` 各自轮转）和 `skip_if_identical`
  （同一文件重复加载不会堆副本）；修了同一秒内命名冲突（`-2`、`-3` 结尾）。
- 设置项：`AppSettings.auto_backup_on_load`（默认 `True`）。
- 备份落在过滤器旁的 `<过滤器名>_backups/`。

### 2.3 视觉工具 —— 强化 + 随机化
让贵重物品更扎眼，也能把整张过滤器随机成一套新观感，同时**不改变哪些物品会显示**。

- [features/visual_emphasis.py](features/visual_emphasis.py)：
  `ValueTier`（MYTHIC > TOP > HIGH > MID > LOW > JUNK，另有 HIDDEN 哨兵）、
  `classify_block()`（顺序读 Hide 首行 → `$tier->tN` 标签 → 章节关键词）、
  `BlockStyle`（字段全可选，只写设置过的）、`iter_blocks()`、
  `apply_style_to_block()`、`EmphasisStyler`、`RandomizerStyler`（带种子，15 套配色）。
- 只碰 `SetTextColor`、`SetBorderColor`、`SetBackgroundColor`、`SetFontSize`、
  `PlayEffect`、`MinimapIcon`。绝不碰 Show/Hide、条件、音效。Hide 块整体跳过。

### 2.4 JSON 预设
- [data/visual_presets.json](data/visual_presets.json)（首次点“编辑”时生成）。
  加载器很宽容：缺字段回退到代码默认，坏配色静默丢弃，文件不存在就全用默认。
  文件内 `_notes` 自带 schema 说明（列出合法颜色名和小地图形状）。

### 2.5 视觉工具对话框
- [ui/visual_tools_dialog.py](ui/visual_tools_dialog.py) —— 两个页签（按档次强化、
  随机视觉），顶部共用工具栏（编辑预设文件 / 重新载入）。两个页签都是先预览再提交；
  随机化可填种子以复现；档次色块可点击进入档次详情对话框。

### 2.6 每个过滤器的用户覆盖
- [core/user_overrides.py](core/user_overrides.py) —— 侧车文件
  `<过滤器>.filterstudio.json`，两层覆盖：`tier_presets`（这个过滤器里某档次长什么样）
  与 `block_overrides`（按稳定签名索引，可改档次或钉死样式）。
- `block_signature(block_lines)` = `Show | rarity=Unique | base=heavy belt`，
  由 Show/Hide 词 + Rarity + 排序后的 Class + 排序后的 BaseType 组成，扛得住行序调整、
  样式变化和注释。
- 解析优先级（高到低）：块样式覆盖 → 块档次覆盖 → 档次预设覆盖 → 代码默认。

### 2.7 应用内档次详情对话框
- [ui/tier_detail_dialog.py](ui/tier_detail_dialog.py) —— 点档次色块打开。含实时
  预览（原生 `tk.Frame`，颜色按游戏里那样直接上色）、文字/边框/背景三行取色、
  字号滑杆、PlayEffect（None + 11 色 + 临时勾选）、MinimapIcon（大小/颜色/形状）、
  块列表右键「移动到某档次」/「移回自动判定档次」、恢复默认 / 移除档次覆盖。
  改动即存侧车文件，关闭时回调父对话框重新规划。

### 2.8 应用日志
- [core/app_logging.py](core/app_logging.py) —— `init_logging()`、`get_logger()`、
  `get_log_path()`、`log_section()`、`shutdown()`。`RotatingFileHandler`（5 MB × 3）。
  写到 `%APPDATA%/POE2FilterSoundEditor/app_debug.log`，在仓库之外，不可能被误提交。
  钩住 `sys.excepthook` 和 `tk.Tk.report_callback_exception`；帮助菜单提供
  “打开调试日志 / 打开日志目录”。

### 2.9 冲突感知的兼容性检查
- `CompatibilityIssue` 增加 `has_user_override` 与 `override_summary`；检查器接收
  `overrides=` 并算出被自定义块的行范围。对话框里冲突项显示琥珀色行、`⚠` 前缀、
  默认**不勾选**修复，且不参与“全选可修复”。

---

## 3. 持久化模型

| 内容 | 位置 | 作用域 |
|------|------|--------|
| 应用设置（主题、FFmpeg、自动加载等） | `%APPDATA%/POE2FilterSoundEditor/settings.json` | 每用户每机器 |
| 迁移规则 | `<app>/data/migration_rules.json` | 每份安装，所有过滤器共享 |
| 视觉预设（档次样式 + 随机配色） | `<app>/data/visual_presets.json` | 每份安装 |
| 每过滤器覆盖（档次自定义 + 块重分配） | `<过滤器目录>/<名>.filterstudio.json` | 每过滤器 |
| 备份 | `<过滤器目录>/<名>_backups/` | 每过滤器 |
| 调试日志 | `%APPDATA%/POE2FilterSoundEditor/app_debug.log` | 每用户每机器 |
| 经济档次操作历史 | 用户配置目录 | 每用户（供“恢复”用） |

`visual_presets.json` 是**默认层**，`<过滤器>.filterstudio.json` 是**覆盖层**。
遍历顺序：默认 → 档次预设覆盖 → 块样式覆盖。

## 4. 加载一个过滤器时的数据流

```
用户选文件
  └─ load_filter()
      ├─ load_filter_file() → self.lines
      ├─ _snapshot_on_load()
      │    └─ make_backup(label="load", skip_if_identical=True)
      ├─ refresh_filter_data()  [原解析器，填充界面]
      └─ if auto_check_compatibility:
            _run_compatibility_check(auto=True)
              ├─ load_overrides(filter_path)  [用于冲突标记]
              ├─ FilterCompatibilityChecker(engine, overrides=...)
              ├─ checker.check(self.lines)
              └─ 有问题就弹兼容性对话框
```

打开 `视觉与档次 → 按档次强化` 时：

```
open_visual_tools()
  └─ _VisualToolsDialog
       ├─ load_visual_presets(presets_path)   [默认层]
       ├─ load_overrides(filter_path)         [用户层]
       ├─ EmphasisStyler(presets=..., overrides=...).plan(lines)
       └─ 渲染色块（可点击）
             └─ 点击：open_tier_detail(tier, plan, presets, overrides)
                  └─ 保存：save_overrides(filter_path, overrides)
                  └─ 关闭回调：重载并重新规划父对话框
```

## 5. 关键架构决策

1. **块签名是稳定身份，不是位置。** 能扛住重新导入、重排、改注释；但条件一变就是
   另一个块（语义上正确）。
2. **JSON 加载器一律宽容。** 坏字段只告警并丢弃该条，绝不因为一个 typo 崩掉加载。
3. **跨模块用延迟 import 破循环依赖。** 新增跨模块钩子时沿用这个模式。
4. **所有写入走 `os.replace` 原子替换。** 写到一半崩溃也不会截断过滤器。
5. **备份失败不能阻断加载。** `_snapshot_on_load` 吞掉异常，只在状态栏提示。
6. **视觉工具只改样式。** Show/Hide、物品条件、音效指令是禁区，这是硬不变式。
7. **冲突默认不应用。** 兼容性修复若会碰到用户自定义过的块，默认不勾选，必须显式选择
   才放弃自定义。
8. **中文只在显示层。** 内部值（枚举、模式、配色名、置信度）保持英文，见 `core/zh.py`。

## 6. 已知限制 / 坑

- **块边界。** `iter_blocks` 从一条 Show/Hide 给到下一个，包含尾部空行和（属于下一个
  块的）章节注释。`apply_style_to_block` 的插入点会跳过这两者。新增“尾部内容重写”
  逻辑时必须复刻这个跳过。
- **`POE2 Custom Sound Filter.exe`** 是旧的打包产物；`build_exe.bat` 重新打包，
  构建号在 `version.txt`。
- **颜色/形状集合** 在 `features/visual_emphasis.py`：`POE2_NAMED_COLORS`（11）、
  `POE2_MINIMAP_SHAPES`（12）。GGG 新增时要同步更新这些常量**和**
  `data/visual_presets.json` 加载器里的校验集合。
- **档次判定关键词** `_SECTION_KEYWORDS` 是首个命中即返回的子串匹配，顺序敏感；
  假设使用 NeverSink 的章节命名习惯。
- **Windows 控制台打不出 Unicode 箭头**（cp1252）。测试里用 ASCII；应用本身没问题，
  Tk 原生支持 Unicode。
- **本机没装 `customtkinter`**，所以本仓库的历史改动大多只有 `py_compile` 级别的验证，
  没有 GUI 冒烟测试。

## 7. 后续工作（按大致的优先级）

1. **`migration_rules.json` 的应用内规则编辑器**（现在只能从对话框打开文件）。
2. **兼容性修复的冲突解决界面**：加个 before/after diff 视图。
3. **多档次批量重分配**：“把所有含某 BaseType 的块移到顶级”这类查询式批处理。
4. **预览模式与保存分离**：现在点应用就落盘，改成“只在保存时提交”的图层式实验。
5. **导出/分享自定义**：把覆盖 + 视觉预设打成一个可导入的包。
6. **档次详情对话框里的块级样式选择器**（`BlockOverride.style` 已经打通，只差界面）。
7. **更聪明的价值启发式**：把现有字号、是否已有 `PlayEffect`/`MinimapIcon`、
   堆叠数量阈值也纳入判定。
8. **主编辑器里的实时预览**：把选中的样式画到表格行上。
9. **自动化测试**：`block_signature` 稳定性、`apply_style_to_block` 插入边界、
   `_compute_override_ranges`、迁移规则解析顺序。

## 8. 验证命令

```powershell
# 全量编译
python -m py_compile main.py core/*.py features/*.py ui/*.py economy_tier/*.py

# 兼容性引擎冒烟
python -c "from core.compatibility import FilterCompatibilityChecker, MigrationRulesEngine; print(len(MigrationRulesEngine().rules))"

# 视觉强化冒烟
python -c "from features.visual_emphasis import EmphasisStyler, apply_changes; lines=['Show\n','\tRarity Unique\n']; print(apply_changes(lines, EmphasisStyler().plan(lines)))"

# 中文映射往返
python -c "from core.zh import mode_label, mode_value, conf_label, conf_value; assert mode_value(mode_label('Preview Only'))=='Preview Only'; assert conf_value(conf_label('high'))=='high'; print('ok')"

# 跑测试（需先装 pytest）
python -m pytest -q
```

## 9. 协作偏好（`CLAUDE.md` 的浓缩版）

- 用户不直接操作 git/GitHub。搭完一段工作就提交、推送、开或更新 PR，不用每次问。
- 新工作一律走**特性分支**，绝不在 `main` 上直接改。
- 破坏性操作（force-push、重写历史、删分支、合并 PR）先确认。
- `gh` CLI 已安装并登录为 `panyanyu`；`origin` =
  `https://github.com/panyanyu/poe2-filter-sound-studio`。
- 提交身份：`pyy <704508940@qq.com>`（仓库级已设置）。
- 推送若报 `CONNECT tunnel failed, response 502`，是沙箱代理的问题，改用
  `git -c http.proxy=http://127.0.0.1:7897 push`。

---

*上下文日志结束。最后更新：2026-10-22（界面中文化 + 中文字体 + 中文文档）。*
