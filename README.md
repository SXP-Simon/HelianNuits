# 夜之向日葵 - HelianNuits

基于 MkDocs Material ，支持自动化归档、分类和 RSS 订阅。

## 🌻 项目特色

- **自动化管理**：文章自动归档、分类，无需手动维护
- **多语言支持**：中文/英文双语支持
- **现代化 UI**：基于 Material Design 的美观界面
- **响应式设计**：完美适配各种设备

## 📁 项目结构

```
HelianNuits/
├── docs/                    # 文档目录
│   ├── blog/               # 博客相关
│   │   ├── posts/          # 博客文章（手动添加）
│   │   ├── index.md        # 博客首页（自动生成）
│   │   ├── archive.md      # 时间归档（自动生成）
│   │   └── categories.md   # 分类页面（自动生成）
│   ├── assets/             # 静态资源
│   ├── stylesheets/        # 自定义样式
│   ├── javascripts/        # 自定义脚本
│   ├── index.md           # 网站首页
│   └── about.md           # 关于页面
├── material/               # Material 主题覆盖
├── .github/workflows/      # GitHub Actions 配置
├── mkdocs.yml             # MkDocs 配置文件
├── requirements.txt        # Python 依赖
└── README.md              # 项目说明
```

### 3. 发布新文章

1. 在 `docs/blog/posts/` 目录下创建新的 Markdown 文件
2. 添加 Front Matter：

```markdown
---
title: Front Matter 模板
author: Helian Nuits
description: 这里是一个 Front Matter 示例
date: 2025-07-01
categories:
  - 技术分享
tags:
  - 模板
  - 示例
---

# ... 文章内容
```

3. 保存文件，系统会自动更新首页、归档和分类页面

### 4. 部署

```bash
# 构建网站
mkdocs build

# 部署到 GitHub Pages（需要配置）
mkdocs gh-deploy
```

## 🔧 配置说明

### 主要插件

- **mkdocs-material**: 主题和核心功能
- **mkdocs-blog-plugin**: 博客功能
- **mkdocs-static-i18n**: 多语言支持
- **mkdocs-rss-plugin**: RSS 订阅
- **mkdocs-minify-plugin**: 代码压缩

### 自定义功能

- **自动化归档**: 通过 `hooks.py` 自动生成归档和分类页面

## 📝 写作指南

### 文章格式

- 文件位置：`docs/blog/posts/`
- 文件格式：Markdown (.md)
- 编码：UTF-8

### Front Matter 字段

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| title | string | 是 | 文章标题 |
| date | string | 是 | 发布日期 (YYYY-MM-DD) |
| categories | array | 否 | 分类列表 |
| tags | array | 否 | 标签列表 |
| description | string | 否 | 文章描述 |
| author | string | 否 | 作者名称 |

### 支持的 Markdown 扩展

- 数学公式 (MathJax)
- 代码高亮
- 表格
- 任务列表
- 表情符号
- 警告框
- 标签页

## 🌐 在线访问

- **网站**: https://sxp-simon.github.io/HelianNuits/

---

> 此曲为一切不合时宜者而作。