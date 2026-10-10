# LLM API Cost & Capability Monitor

一个用于跟踪大模型 API 定价与能力数据的投研工具。

## 项目目标
- 自动采集主流大模型 API 定价
- 对比模型能力与调用成本
- 生成性价比排名与可视化仪表盘
- 支持定期报告导出

## Day 1 进展
- [x] 项目初始化
- [x] 从 LiteLLM 公开 JSON 采集定价数据
- [x] 创建 .gitignore
- [ ] 数据标准化与单位换算
- [ ] 能力榜单采集
- [ ] 可视化仪表盘

## 技术栈
- Python 3.11+
- requests
- pandas
- Git

## 如何运行
```bash
pip install requests pandas
python collect_litellm.py


