"""中文界面显示映射。

内部取值（模式、置信度、外观、配色方案名）一律保持英文原值，因为设置文件、
经济档次的控制器和历史记录都以这些字符串作为键。本模块只负责在 UI 层做
英文原值 ⇄ 中文显示名 的双向转换，避免翻译污染持久化数据。
"""

from __future__ import annotations

# ---------------------------------------------------------------- 外观模式
APPEARANCE_ZH: dict[str, str] = {
    "System": "跟随系统",
    "Light": "浅色",
    "Dark": "深色",
}

# ---------------------------------------------------------------- 配色方案
PALETTE_ZH: dict[str, str] = {
    "Default Dark": "默认·深色",
    "Default Light": "默认·浅色",
    "PoE2 — Witch (Necro Purple)": "流放2·女巫（死灵紫）",
    "PoE2 — Mercenary (Crimson)": "流放2·佣兵（绯红）",
    "PoE2 — Sorceress (Ice)": "流放2·法师（寒冰）",
    "PoE2 — Monk (Jade)": "流放2·武僧（青玉）",
    "PoE2 — Druid (Forest)": "流放2·德鲁伊（森林）",
    "PoE2 — Warrior (Bronze)": "流放2·战士（青铜）",
    "PoE2 — Huntress (Steel)": "流放2·女猎手（钢铁）",
    "Solarized Dark": "Solarized 深色",
    "Nord": "Nord 北境",
    "Dracula": "Dracula 暗夜",
    "Cyberpunk Neon": "赛博霓虹",
    "High Contrast": "高对比度",
}

# ---------------------------------------------------------------- 经济档次模式
MODE_ZH: dict[str, str] = {
    "Off": "关闭",
    "Preview Only": "仅预览",
    "Apply Economy Tier Visuals": "应用经济档次视觉",
    "Apply Economy Tier Visuals Plus Chance Base Boost": "应用经济档次视觉＋机会石基底提升",
    "Restore Previous Visuals": "恢复上一次视觉",
}

# ---------------------------------------------------------------- 置信度
CONF_ZH: dict[str, str] = {
    "low": "低",
    "medium": "中",
    "high": "高",
}

# ---------------------------------------------------------------- 稀有度
RARITY_ZH: dict[str, str] = {
    "Normal": "普通",
    "Magic": "魔法",
    "Rare": "稀有",
    "Unique": "传奇",
}

# ---------------------------------------------------------------- 音效类型
SOUND_TYPE_ZH: dict[str, str] = {
    "Custom": "自定义",
    "Play": "内置音效",
    "None": "无音效",
}

# ---------------------------------------------------------------- 显隐
VISIBILITY_ZH: dict[str, str] = {
    "Show": "显示",
    "Hide": "隐藏",
}

# ---------------------------------------------------------------- 价值档次
TIER_ZH: dict[str, str] = {
    "Mythic": "神话",
    "Top": "顶级",
    "High": "高档",
    "Mid": "中档",
    "Low": "低档",
    "Junk": "垃圾",
    "Hidden": "隐藏",
}


def _reverse(table: dict[str, str]) -> dict[str, str]:
    """中文显示名 -> 英文原值（同值多条时保留第一个）。"""
    out: dict[str, str] = {}
    for k, v in table.items():
        out.setdefault(v, k)
    return out


_APPEARANCE_EN = _reverse(APPEARANCE_ZH)
_PALETTE_EN = _reverse(PALETTE_ZH)
_MODE_EN = _reverse(MODE_ZH)
_CONF_EN = _reverse(CONF_ZH)


def appearance_label(value: str) -> str:
    return APPEARANCE_ZH.get(value, value)


def appearance_value(label: str) -> str:
    return _APPEARANCE_EN.get(label, label)


def palette_label(value: str) -> str:
    return PALETTE_ZH.get(value, value)


def palette_value(label: str) -> str:
    return _PALETTE_EN.get(label, label)


def mode_label(value: str) -> str:
    return MODE_ZH.get(value, value)


def mode_value(label: str) -> str:
    return _MODE_EN.get(label, label)


def conf_label(value: str) -> str:
    return CONF_ZH.get(value, value)


def conf_value(label: str) -> str:
    return _CONF_EN.get(label, label)


def rarity_label(value: str) -> str:
    return RARITY_ZH.get(value, value)


def sound_type_label(value: str) -> str:
    return SOUND_TYPE_ZH.get(value, value)


def visibility_label(value: str) -> str:
    return VISIBILITY_ZH.get(value, value)


def tier_label(value: str) -> str:
    return TIER_ZH.get(value, value)


def rarity_display(text: str) -> str:
    """把 `Unique, Rare` 这类逗号分隔的稀有度串整体转成中文。"""
    text = (text or "").strip()
    if not text:
        return text
    if text == "Any rarity":
        return "任意稀有度"
    return ", ".join(RARITY_ZH.get(part.strip(), part.strip()) for part in text.split(","))


def visibility_word_label(value: str) -> str:
    return VISIBILITY_ZH.get(value, value)


# ---------------------------------------------------------------- 风险等级
RISK_ZH: dict[str, str] = {
    "High": "高",
    "Medium": "中",
    "Low": "低",
}


def risk_label(value: str) -> str:
    return RISK_ZH.get(value, value)
