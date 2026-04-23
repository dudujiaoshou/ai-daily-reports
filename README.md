# 🤖 AI Daily Reports

> AI行业每日/晚报自动生成项目

## 📋 内容

每日自动生成AI行业报告，包含：

| 模块 | 内容 |
|------|------|
| **全球AI动态** | 模型发布、融资事件、政策动向 |
| **中国创业分析** | 融资数据、细分赛道、新兴公司 |
| **上海活动** | 线下活动、沙龙、Meetup |

## ⏰ 执行时间

- 🌅 **早报**: 每天 10:00 (北京时间)
- 🌙 **晚报**: 每天 18:00 (北京时间)

## 🔧 配置

需要在 GitHub Secrets 中配置以下变量：

| Secret | 说明 |
|--------|------|
| `SERVERCHAN_SCKEY` | [Server酱](https://sc.ftqq.com) SCKEY，用于微信推送 |
| `OPENAI_API_KEY` | OpenAI API Key，用于AI内容生成 |

## 📊 最新报告

报告自动提交到本仓库的 `main` 分支。

---

*由 GitHub Actions 自动调度生成*
