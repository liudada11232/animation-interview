# 动画智能制作笔试题 · 交付代码

三道工序（描原 / 中割 / 上色）的传统计算机视觉实现 + 严格评测。题目：KTK_04_246B（主）+ KTK_05_140（进阶）。

## 环境
- Python 3.12，依赖见 `requirements.txt`（numpy / scipy / opencv-python / Pillow）
- 无 GPU、无 API、无训练成本，全部离线跑
- 安装：`pip install -r requirements.txt`

## 数据准备
题目素材（`2026.07.13.zip`）**不在本仓库**（避免公开泄露考题）。复现需要：
1. 解压素材包到任意目录（如 `D:\path\to\assets`，含 `KTK_04_246B/`、`KTK_05_140/`）
2. 设置环境变量 `ANIM_ASSETS` 指向素材目录；`ANIM_PNG` 指向转换后素材目录（默认仓库下 `png/`）；`ANIM_OUT` 指向输出目录（默认仓库根）
3. 转换素材：`python anim/convert_tga.py <素材目录> <ANIM_PNG>`

```bash
# 示例 (Windows PowerShell)
$env:ANIM_ASSETS="D:\path\to\assets"
$env:ANIM_PNG="D:\path\to\png"
$env:ANIM_OUT="D:\path\to\outputs"
python anim/convert_tga.py $env:ANIM_ASSETS $env:ANIM_PNG
```

## 运行（在 anim/ 目录下）
```bash
cd anim
python taskA_trace.py    # 题A 描原 -> outA/
python taskB_inbet.py    # 题B 中割 -> outB/
python taskC_color.py    # 题C 上色 -> outC/
python final_evalA.py    # 题A 评测
python evalB.py          # 题B 评测
python evalC.py          # 题C 评测
# 进阶
python taskA_ktk05.py / taskB_ktk05.py / taskC_ktk05.py
```

> 路径配置见 `anim/paths.py`：支持环境变量覆盖，也支持相对仓库根的默认值，保证任意目录可复现。

## 目录
```
anim/           全部算法与评测脚本（paths.py 统一路径）
figures/        输入|输出|参考答案 对比图（3张）
outA/ outB/ outC/    主镜头三道工序输出（PNG）
outA5/ outB5/ outC5/ 进阶镜头输出
palette*.json   调色盘（palette_legal.json 为合规版本，仅取自设定图色卡）
report.md       提交报告（2-4页）
```

## 运行成本
- 单帧处理：上色 <1s，描原 1-3s，光流插值 1-3min/帧
- 全套（主镜头三道工序 + 评测）：普通笔记本约 10-20 分钟
- 零 API 调用、零 GPU 费用

## 合规声明
- 调色盘 100% 来自角色设定图色卡；成品/参考答案只用于评测脚本
- 主流程算法脚本不含读取成品的代码；历史违规版本已改名 `*_LEAKED_UNUSED.py` 存档