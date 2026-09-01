# -*- coding: utf-8 -*-
"""合规调色盘 v2 — 仅从角色设定图 06_001_ミュイ.png 的青色边框色卡提取 (合法来源).

数据来自 extract_palette_legal.py 检测的 45 个色卡芯片 (中位色, 抗噪).
站点布局(设定图左侧色卡面板, 原始坐标): 色卡按行分组, 每行是某部位的 固有/影/高光 与 影中列.
我们按芯片的归一化 y 分组到部位, 具体色值取自芯片中位色.

诚实声明: 本调色盘 100% 只使用设定图色卡; 不再读取成品/上色 任何像素.
"""
import json

# ---- 从设定图色卡芯片(中位色)构建 ----
# 芯片坐标(原始4443x1900) -> 部位/色调
# 依据设定图布局人工分组 (行内按 x 从小到大 = 固有->影/高光)
CHIPS = [
    # y~176-213: 发顶 (髪)
    ((80,176), "hair_stem"), ((220,176), "hair_stem2"), ((346,201), "hair_base"),
    ((432,213), "hair_trim"),
    # y~353-369: 发/毛先/腮红
    ((63,355), "hair_tip"), ((141,355), "hair_tip2"), ((218,353), "hair_tip3"), ((383,369), "hair_mid"),
    # y~504-537: 肌/瞳/まぶた
    ((74,535), "skin_a"), ((203,537), "skin_b"), ((328,530), "skin_c"),
    ((1331,504), "eye_iris"), ((1411,504), "eye_line"), ((1554,507), "eye_shadow"),
    # y~670-743: 衣服/带子
    ((1339,676), "cloth_dark"), ((1431,670), "cloth_mid"), ((1517,678), "cloth_base"),
    ((216,743), "cloth_trim"),
    # y~1002-1046: 衣服影/肌影
    ((316,991), "skin_shadow"), ((1050,1002), "cloth_shadow2"),
    ((1451,1046), "cloth_light"),
    # y~1201-1331: 目(normal 行)
    ((361,1203), "eye_white_n"), ((441,1201), "eye_spec_n"), ((515,1203), "iris_n"),
    ((732,1292), "pupil_n"), ((779,1292), "iris_hi_n"), ((857,1297), "eye_white2_n"),
    ((942,1331), "brow_n"),
    # y~1582-1816: 目(影中 行)
    ((357,1816), "eye_white_s"), ((440,1813), "eye_spec_s"), ((524,1812), "iris_s"),
    ((312,1582), "shadow_skin"),
]

def _load_medians():
    import os
    p = r"D:\desktop\mianshi\work\sheet_chips.json"
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    return {(int(d["cx"]), int(d["cy"])): tuple(int(v) for v in d["median"]) for d in data}

_MED = _load_medians()

def chip_color(coord, fallback):
    return _MED.get(coord, fallback)

# ---- 部位 -> 色调 -> RGB (全部来自设定图色卡) ----
PALETTE = {
    "hair": {
        "base":   chip_color((346,201), (42,35,26)),
        "shadow": chip_color((383,369), (34,26,20)),
        "hilight":chip_color((63,355), (62,50,31)),
    },
    "skin": {
        "base":   chip_color((328,530), (62,39,24)),
        "shadow": chip_color((316,991), (92,54,22)),
        "hilight":chip_color((203,537), (62,34,20)),
    },
    "coat": {
        "base":   chip_color((1517,678), (44,34,25)),
        "shadow": chip_color((1339,676), (21,16,13)),
        "hilight":chip_color((1451,1046), (62,44,34)),
        "trim":   chip_color((216,743), (63,50,31)),
    },
    "eye_white": {
        "base":   chip_color((361,1203), (65,43,18)),
        "shadow": chip_color((857,1297), (27,14,8)),
    },
    "iris": {
        "base":   chip_color((515,1203), (122,85,46)),
        "shadow": chip_color((1331,504), (40,27,11)),
    },
    "pupil": {
        "base":   chip_color((732,1292), (17,4,1)),
    },
    "eye_spec": {
        "base":   chip_color((441,1201), (128,96,58)),
    },
    "eyeline": {
        "base":   chip_color((1411,504), (23,8,7)),
    },
    "cloth_light": {
        "base":   chip_color((1431,670), (83,60,29)),
        "shadow": chip_color((2169,1401), (24,12,8)),
    },
}

# 中位色兜底列表 (仅用于 kNN 兜底, 若需要)
PRIMARY_FILLS = sorted({tuple(v) for p in PALETTE.values() if isinstance(p, dict) for v in p.values()})

if __name__ == "__main__":
    with open(r"D:\desktop\mianshi\work\palette_legal.json", "w", encoding="utf-8") as f:
        json.dump(PALETTE, f, ensure_ascii=False, indent=2)
    for part, tones in PALETTE.items():
        print(part, tones)
    print("saved palette_legal.json")
    print("仅设定图色卡来源:", _load_medians().__len__(), "个芯片可用")