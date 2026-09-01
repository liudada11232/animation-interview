# -*- coding: utf-8 -*-
"""统一路径配置 —— 让所有脚本在任意目录可复现。

约定(按优先级)：
  1. 环境变量覆盖: ANIM_ASSETS(素材解压目录) / ANIM_PNG(转换后素材) / ANIM_OUT(输出根)
  2. 默认相对仓库根:
       - ASSETS = repo/../picture   (题目素材解压位置, 或你放素材的地方)
       - PNG    = repo/png          (convert_tga.py 的输出)
       - OUT    = repo              (outA/outB/... 输出到仓库根)

用法:  from paths import ASSETS, PNG, OUT_ROOT, data, out
"""
import os

# anim/ 的父目录 = 仓库根
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASSETS = os.environ.get("ANIM_ASSETS", os.path.join(REPO, "..", "picture"))
PNG = os.environ.get("ANIM_PNG", os.path.join(REPO, "png"))
OUT_ROOT = os.environ.get("ANIM_OUT", REPO)

def data(*parts):
    """转换后素材路径, 如 data('KTK_04_246B','成品','描原','A0001.png')"""
    return os.path.join(PNG, *parts)

def out(name):
    """输出目录, 如 out('outA')"""
    return os.path.join(OUT_ROOT, name)

def asset(*parts):
    """原始素材路径, 如 asset('KTK_04_246B','源文件','描原','A1.jpg')"""
    return os.path.join(ASSETS, *parts)

def _check(label, p):
    if not os.path.exists(p):
        print(f"[paths] 提示: {label} 不存在: {p}")
        print(f"[paths] 请设置环境变量 ANIM_ASSETS / ANIM_PNG, 或先运行 convert_tga.py")
    return p

_check("素材目录", ASSETS)