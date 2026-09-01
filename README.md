# 复现说明（README）

## 环境
- Python 3.12，依赖见 `requirements.txt`
- 无需 GPU、无需 API，全部离线运行，零金钱成本

## 目录结构
```
anim/            全部算法与评测脚本
png/             素材库（tga 已转 png，与源库一一对应）
outA/ outB/ outC/    主镜头三题输出
outA5/ outB5/ outC5/ 进阶镜头输出
figures/         输入|输出|参考答案 对比图
report.md        提交报告
```

## 复现步骤（在 anim/ 目录下运行）
```bash
pip install -r requirements.txt

python convert_tga.py      # 素材 tga -> png（首次）
python taskA_trace.py      # 题A 描原 -> outA/
python taskB_inbet.py      # 题B 中割 -> outB/
python taskC_color.py      # 题C 上色 -> outC/
python evalA.py | evalB.py | evalC.py   # 评测
# 进阶
python taskA_ktk05.py / taskB_ktk05.py / taskC_ktk05.py
```

## 运行成本
- 单帧处理：上色 <1s，描原 1-3s，光流插值 1-3min/帧
- 全套（主镜头三题 + 评测）：普通笔记本约 10-20 分钟
- 无 API 调用、无 GPU 费用

## 合规说明
- 调色盘 100% 来自角色设定图色卡（`palette_legal.json`），成品/参考答案只用于评测脚本
- 主流程算法脚本不含读取成品的代码；历史违规版本已改名 `*_LEAKED_UNUSED.py` 存档