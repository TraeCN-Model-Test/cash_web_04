# CashLog - 轻量化本地记账/待办CLI工具

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

CashLog 是一款轻量化本地记账/待办事项管理工具，专为个人财务管理设计。所有数据存储在本地SQLite数据库中，确保数据隐私和安全性。

## ✨ 主要功能

### 📊 交易管理
- **添加交易记录**：支持收入和支出记录，可添加分类、标签和备注
- **查看交易列表**：支持按月份、分类、标签和交易类型筛选
- **灵活的查询**：组合多种条件进行精确查询

### 📝 待办事项管理
- **任务管理**：添加、更新状态、查看待办事项
- **状态跟踪**：支持待办、进行中、已完成、已取消四种状态
- **智能筛选**：按状态、分类、截止时间筛选任务

### 📈 多维度报表
- **时间维度**：支持日、周、月、季度及自定义时间段报表
- **分类筛选**：可按一个或多个分类生成报表
- **自定义字段**：可指定展示的字段内容
- **环比计算**：支持与上一周期对比分析
- **多格式输出**：支持纯文本和Markdown格式输出

### 💾 数据管理
- **数据备份**：支持自定义路径和强制覆盖选项
- **数据恢复**：支持从备份文件恢复，恢复前可自动备份当前数据
- **数据安全**：所有操作都有确认机制，防止误操作

### 🌐 REST API
- **待办事项API**：提供完整的待办事项CRUD操作
- **交易记录API**：提供交易记录的查询和管理功能
- **筛选和分页**：支持多条件筛选和分页查询
- **API文档**：自动生成的OpenAPI文档

## 🚀 快速开始

### 环境要求

- Python 3.10+
- 推荐使用 uv 作为包管理工具

### 安装步骤

1. 克隆项目
```bash
git clone <repository-url>
cd cash_web_04
```

2. 安装依赖
```bash
uv sync
```

3. 初始化数据库（首次运行自动完成）
```bash
uv run python main.py --help
```

## 📖 使用指南

### 基本命令

```bash
# 查看帮助
uv run python main.py --help

# 查看版本
uv run python main.py --version
```

### 交易管理

#### 添加交易记录
```bash
# 添加收入
uv run python main.py transaction add -a 5000.00 -c 工资 -t 收入,月度 -n "12月份工资"

# 添加支出
uv run python main.py transaction add -a -150.00 -c 餐饮 -t 日常,午餐 -n "工作日午餐"

# 带时间的交易（可选，默认为当前时间）
uv run python main.py transaction add -a 200.00 -c 交通 -t 地铁 -n "上下班地铁费" -d "2024-12-01 08:30:00"
```

#### 查看交易记录
```bash
# 列出所有交易
uv run python main.py transaction list

# 按月份筛选
uv run python main.py transaction list -m 2024-12

# 按分类筛选
uv run python main.py transaction list -c 餐饮

# 按交易类型筛选
uv run python main.py transaction list --type income
uv run python main.py transaction list --type expense

# 组合筛选
uv run python main.py transaction list -m 2024-12 -c 餐饮 -t 午餐
```

### 待办事项管理

#### 添加待办事项
```bash
# 添加带截止时间的待办事项
uv run python main.py todo add -c "完成项目报告" -C 工作 -t 重要,紧急 -d "2024-12-10 18:00:00"

# 添加无截止时间的待办事项
uv run python main.py todo add -c "学习Python新特性" -C 学习 -t 自我提升
```

#### 更新待办状态
```bash
# 更新为进行中
uv run python main.py todo update-status 1 doing

# 更新为已完成
uv run python main.py todo update-status 1 done
```

#### 查看待办事项
```bash
# 列出所有待办事项
uv run python main.py todo list

# 按状态筛选
uv run python main.py todo list -s todo      # 只显示待办
uv run python main.py todo list -s doing    # 只显示进行中
uv run python main.py todo list -s done     # 只显示已完成

# 按分类筛选
uv run python main.py todo list -c 工作

# 按截止时间筛选
uv run python main.py todo list --before 2024-12-31
uv run python main.py todo list --after 2024-12-01
```

### 报表功能

#### 生成多维度报表
```bash
# 生成日报表
uv run python main.py report generate --daily

# 生成周报表
uv run python main.py report generate --weekly

# 生成月度报表（默认）
uv run python main.py report generate --monthly

# 生成季度报表
uv run python main.py report generate --quarterly

# 生成自定义时间段报表
uv run python main.py report generate --start 2024-12-01 --end 2024-12-31

# 按分类筛选生成报表
uv run python main.py report generate --category 餐饮,交通

# 指定展示字段
uv run python main.py report generate --fields 金额,分类,笔数

# 输出为Markdown格式
uv run python main.py report generate --monthly --format markdown
```

#### 兼容旧接口
```bash
# 生成当前月报表
uv run python main.py report monthly

# 生成指定月份报表
uv run python main.py report monthly -m 2024-12
```

### 数据管理

#### 数据备份
```bash
# 使用默认路径备份
uv run python main.py data backup

# 指定备份路径
uv run python main.py data backup -o ~/cashlog_backup.db

# 强制覆盖已存在的备份文件
uv run python main.py data backup -o ~/cashlog_backup.db -f
```

#### 数据恢复
```bash
# 从备份文件恢复（恢复前自动备份当前数据）
uv run python main.py data restore -i ~/cashlog_backup.db

# 跳过确认直接恢复
uv run python main.py data restore -i ~/cashlog_backup.db -y

# 跳过确认且不备份当前数据直接恢复
uv run python main.py data restore -i ~/cashlog_backup.db -y -b False
```

### REST API

#### 启动API服务器
```bash
# 启动API服务器（默认端口8000）
uv run python src/cashlog/rest/api.py

# 自定义端口
uv run python src/cashlog/rest/api.py --port 8080
```

#### API端点
```bash
# 待办事项API
GET    /todos              # 获取待办事项列表
GET    /todos/{todo_id}    # 获取特定待办事项
POST   /todos              # 创建待办事项
PUT    /todos/{todo_id}    # 更新待办事项
DELETE /todos/{todo_id}    # 删除待办事项

# 交易记录API
GET    /transactions              # 获取交易记录列表
GET    /transactions/{trans_id}   # 获取特定交易记录
POST   /transactions              # 创建交易记录
PUT    /transactions/{trans_id}   # 更新交易记录
DELETE /transactions/{trans_id}   # 删除交易记录
```

## 🧪 测试

项目包含完整的测试套件，可运行以下命令进行测试：

```bash
# 运行所有单元测试
uv run pytest

# 运行完整功能测试（包含测试数据）
./scripts/run_integration_tests.sh

# 添加交易测试数据
./scripts/setup_transaction_test_data.sh

# 添加待办事项测试数据
./scripts/setup_todo_test_data.sh
```

## 📁 项目结构

```
cash_web_04/
├── src/cashlog/           # 源代码目录
│   ├── cli/              # 命令行接口
│   │   ├── data_cli.py   # 数据管理命令
│   │   ├── main_cli.py   # 主命令接口
│   │   ├── report_cli.py  # 报表命令
│   │   ├── todo_cli.py    # 待办事项命令
│   │   └── transaction_cli.py # 交易命令
│   ├── models/           # 数据模型
│   │   ├── db.py         # 数据库配置
│   │   ├── todo.py       # 待办事项模型
│   │   └── transaction.py # 交易模型
│   ├── rest/             # REST API
│   │   ├── api.py        # API主入口
│   │   ├── models.py     # API数据模型
│   │   └── routers/      # API路由
│   │       ├── todos.py  # 待办事项路由
│   │       └── transactions.py # 交易记录路由
│   ├── services/         # 业务逻辑服务
│   │   ├── data_service.py # 数据管理服务
│   │   ├── report_service.py # 报表服务
│   │   ├── todo_service.py # 待办事项服务
│   │   └── transaction_service.py # 交易服务
│   └── utils/            # 工具函数
│       └── formatter.py  # 格式化工具
├── tests/                # 单元测试
│   ├── test_backup_restore_cli.py            # 备份恢复CLI命令测试
│   ├── test_backup_restore_service.py        # 备份恢复服务功能测试
│   ├── test_cli_utilities.py                 # CLI工具类测试基类
│   ├── test_report_generation_cli.py         # 报表生成CLI命令测试
│   ├── test_report_generation_service.py     # 报表生成服务功能测试
│   ├── test_rest_api.py                      # REST API接口测试
│   ├── test_todo_cli.py                      # 待办事项CLI命令测试
│   ├── test_todo_service.py                  # 待办事项服务功能测试
│   ├── test_transaction_cli.py               # 交易记录CLI命令测试
│   └── test_transaction_service.py           # 交易记录服务功能测试
├── scripts/              # 脚本工具
│   ├── setup_transaction_test_data.sh  # 添加交易测试数据
│   ├── setup_todo_test_data.sh # 添加待办事项测试数据
│   ├── test_backup_restore_error_cases.sh # 备份恢复错误测试
│   ├── test_backup_restore_workflow.sh # 备份恢复正常测试
│   ├── run_integration_tests.sh  # 运行完整测试
│   └── test_transaction_todo_association.sh # 交易与待办关联测试
├── data/                 # 数据存储目录
│   ├── backups/          # 备份文件目录
│   └── cashlog.db        # 主数据库文件
├── main.py               # 程序入口
├── pyproject.toml        # 项目配置
└── README.md             # 项目说明
```

## 🛠️ 开发

### 技术栈

- **语言**: Python 3.10+
- **CLI框架**: Click
- **数据库**: SQLAlchemy + SQLite
- **终端输出**: Rich
- **测试框架**: Pytest
- **API框架**: FastAPI
- **API文档**: OpenAPI/Swagger

### 本地开发

1. 安装开发依赖
```bash
uv sync --dev
```

2. 运行测试
```bash
uv run pytest
```

3. 代码格式化
```bash
uv run black src/ tests/
```

4. 启动API服务器（开发模式）
```bash
uv run uvicorn src.cashlog.rest.api:app --reload
```

### 项目文档

项目包含核心文档，位于以下位置：

- [src/cashlog/README.md](src/cashlog/README.md) - 核心模块概述
- [src/cashlog/api/README.md](src/cashlog/api/README.md) - REST API文档
- [scripts/README.md](scripts/README.md) - 脚本工具文档
- [tests/README.md](tests/README.md) - 测试文档

## 📄 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

如有问题或建议，请通过 Issue 联系我们。