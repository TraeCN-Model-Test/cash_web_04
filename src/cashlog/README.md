# CashLog 核心模块

CashLog 是一个轻量化本地记账/待办事项管理工具的核心模块，采用分层架构设计。

## 📁 目录结构

```
src/cashlog/
├── api/                 # API层 - REST API接口
│   ├── routers/         # API路由模块
│   │   ├── todo.py      # 待办事项API路由
│   │   └── transaction.py # 交易记录API路由
│   └── main.py          # FastAPI应用入口
├── cli/                 # CLI层 - 命令行接口
│   ├── data_cli.py      # 数据管理命令
│   ├── main_cli.py      # 主命令接口
│   ├── report_cli.py    # 报表命令
│   ├── todo_cli.py      # 待办事项命令
│   └── transaction_cli.py # 交易命令
├── models/              # 数据模型层 - 数据库模型定义
│   ├── db.py            # 数据库配置
│   ├── schemas.py       # API响应模型
│   ├── todo.py          # 待办事项数据模型
│   └── transaction.py   # 交易记录数据模型
├── services/            # 业务逻辑层 - 核心业务逻辑
│   ├── data_service.py  # 数据管理服务
│   ├── report_service.py # 报表服务
│   ├── todo_service.py  # 待办事项服务
│   └── transaction_service.py # 交易服务
└── utils/               # 工具层 - 通用工具函数
    └── formatter.py     # 格式化工具
```

## 🏗️ 架构设计

CashLog 采用分层架构模式，各层职责明确：

- **API层**: 提供RESTful API接口，基于FastAPI，处理HTTP请求和响应
- **CLI层**: 提供命令行接口，基于Click，实现用户交互
- **数据模型层**: 定义数据模型和数据库结构，基于SQLAlchemy，处理数据持久化
- **业务逻辑层**: 实现核心业务逻辑，处理数据操作和业务规则
- **工具层**: 提供通用工具函数和辅助功能，如格式化输出

## 🔄 数据流

```
用户请求 → API/CLI层 → Services层 → Models层 → 数据库
    ↑                                    ↓
    ←────────── 响应数据 ←─────────────────
```

## 📋 核心功能

- 交易管理：添加、查询交易记录，支持多种筛选条件
- 待办事项管理：添加、更新状态、查询待办事项
- 报表生成：多维度报表（日、周、月、季度、自定义时间段）
- 数据管理：数据备份和恢复

## 🔧 开发规范

- 遵循PEP 8 Python代码规范
- 使用类型注解提高代码可读性
- 编写清晰的文档字符串
- 每个服务类都应有对应的单元测试

## 📚 相关文档

- [项目根文档](../../../README.md) - 项目整体介绍和使用指南
- [API接口文档](./api/README.md) - REST API详细说明
- [测试文档](../../../tests/README.md) - 测试指南和说明
- [脚本工具文档](../../../scripts/README.md) - 脚本使用说明