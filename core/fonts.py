"""中文字体安装。

界面里的控件都用 ``(字体, 字号)`` 元组显式指定微软雅黑，但 tkinter 自带的
命名字体（菜单、消息框、Treeview 行、表头）走的是 Tk 默认值 —— 那些还是
西文字体，中文会由系统逐个字符回退，行高不统一。这里把它们统一改掉。

在 Tk 根窗口创建之后、构建界面之前调用一次即可。
"""

from __future__ import annotations

import logging

log = logging.getLogger(__name__)

#: 候选顺序：装了哪个用哪个。前三个都是微软雅黑家族。
CJK_FAMILIES = (
    "Microsoft YaHei UI",
    "Microsoft YaHei",
    "微软雅黑",
    "SimHei",
    "SimSun",
    "Segoe UI",
)

#: tkinter 内置命名字体，覆盖菜单 / 普通文字 / 文本域 / 表头 / 提示。
_NAMED_FONTS = (
    "TkDefaultFont",
    "TkTextFont",
    "TkMenuFont",
    "TkHeadingFont",
    "TkCaptionFont",
    "TkTooltipFont",
)


def pick_family(root) -> str:
    """返回本机第一个可用的中文字体族；都不可用时退回 Tk 默认。"""
    try:
        import tkinter.font as tkfont

        available = set(tkfont.families(root))
        for family in CJK_FAMILIES:
            if family in available:
                return family
    except Exception as exc:  # pragma: no cover - 仅在异常环境触发
        log.debug("字体探测失败：%s", exc)
    return "TkDefaultFont"


def install_default_fonts(root) -> str:
    """把 tkinter 命名字体统一成中文字体，返回实际使用的字体族。

    失败不影响启动：任何一步出错都只是回到 Tk 默认字体。
    """
    family = pick_family(root)
    if family == "TkDefaultFont":
        return family
    try:
        import tkinter.font as tkfont

        for name in _NAMED_FONTS:
            try:
                font = tkfont.nametofont(name)
                size = font.cget("size")
                font.configure(family=family)
                # 保持原有字号，只换字形。
                font.configure(size=size)
            except Exception:
                continue
    except Exception as exc:  # pragma: no cover
        log.debug("命名字体安装失败：%s", exc)
    return family
