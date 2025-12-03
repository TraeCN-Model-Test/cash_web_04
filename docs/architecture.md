# CashLog 项目架构文档

## 概述

CashLog 是一款轻量化本地记账/待办事项管理工具，采用分层架构设计，实现了业务逻辑、数据访问和用户界面的有效分离。本文档详细描述了项目的整体架构、各模块职责以及它们之间的交互关系。

## 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户界面层                               │
├─────────────────────┬─────────────────────┬─────────────────────┤
│     CLI命令行界面    │      REST API       │      未来扩展        │
│  (src/cashlog/cli)  │ (src/cashlog/rest)  │   (Web界面/移动端)    │
└─────────────────────┴─────────────────────┴─────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                         业务逻辑层                               │
├─────────────────────┬─────────────────────┬─────────────────────┤
│   交易管理服务      │   待办事项服务       │    报表生成服务      │
│(TransactionService)│   (TodoService)     │  (ReportService)    │
├─────────────────────┼─────────────────────┼─────────────────────┤
│                     │    数据管理服务      │                     │
│                     │   (DataService)     │                     │
└─────────────────────┴─────────────────────┴─────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                         数据访问层                               │
├─────────────────────┬─────────────────────┬─────────────────────┤
│   交易数据模型       │   待办事项数据模型   │    数据库配置         │
│  (Transaction)      │      (Todo)         │      (Database)      │
└─────────────────────┴─────────────────────┴─────────────────────┘
                                │
┌─────────────────────────────────────────────────────────────────┐
│                         数据存储层                               │
├─────────────────────────────────────────────────────────────────┤
│                    SQLite 数据库                               │
│                   (data/cashlog.db)                            │
└─────────────────────────────────────────────────────────────────┘
```

## 架构原则

### 1. 分层架构

CashLog 采用经典的分层架构模式，将系统划分为四个主要层次：

1. **用户界面层**：处理用户交互，包括CLI命令和REST API
2. **业务逻辑层**：实现核心业务规则和数据处理逻辑
3. **数据访问层**：定义数据模型和数据库交互
4. **数据存储层**：负责数据的持久化存储

### 2. 关注点分离

每个层次专注于特定的功能，减少层与层之间的耦合：

- 用户界面层不直接访问数据库，通过业务逻辑层处理数据
- 业务逻辑层不直接操作数据库，通过数据访问层进行数据操作
- 数据访问层专注于数据模型定义和数据库交互，不包含业务逻辑

### 3. 依赖注入

使用依赖注入模式管理组件之间的依赖关系，提高代码的可测试性和可维护性：

```python
# 示例：在API路由中注入服务依赖
@router.get("/todos", response_model=List[TodoResponse])
def get_todos(
    status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db)
):
    todo_service = TodoService(db)
    # ...
```

## 模块设计

### 1. 用户界面层

#### CLI模块 (`src/cashlog/cli`)

负责处理命令行界面，使用Click框架实现命令解析和用户交互：

- `main_cli.py`：主命令入口，定义全局选项和子命令
- `transaction_cli.py`：交易记录相关命令
- `todo_cli.py`：待办事项相关命令
- `report_cli.py`：报表生成相关命令
- `data_cli.py`：数据管理相关命令

设计特点：
- 命令分组管理，提高命令组织性
- 参数验证和错误处理
- 丰富的输出格式，支持表格和文本格式

#### REST API模块 (`src/cashlog/rest`)

提供RESTful API接口，使用FastAPI框架实现：

- `api.py`：API应用主入口，配置FastAPI应用
- `models.py`：API数据模型，定义请求和响应结构
- `routers/`：API路由模块
  - `todos.py`：待办事项相关API端点
  - `transactions.py`：交易记录相关API端点

设计特点：
- 自动生成OpenAPI文档
- 数据验证和序列化
- 统一的错误处理
- 支持查询参数和路径参数

### 2. 业务逻辑层

#### 服务模块 (`src/cashlog/services`)

实现核心业务逻辑，处理数据验证、业务规则和业务流程：

- `TransactionService`：交易记录业务逻辑
- `TodoService`：待办事项业务逻辑
- `ReportService`：报表生成业务逻辑
- `DataService`：数据备份和恢复业务逻辑

设计特点：
- 静态方法设计，便于调用和测试
- 完整的数据验证
- 事务管理，确保数据一致性
- 统一的错误处理机制

#### 服务层设计模式

```python
class TransactionService:
    @staticmethod
    def create_transaction(db: Session, amount: float, category: str, 
                         tags: Optional[str] = None, note: Optional[str] = None,
                         transaction_date: Optional[datetime] = None) -> Transaction:
        # 数据验证
        # 业务逻辑处理
        # 数据持久化
        pass
    
    @staticmethod
    def get_transactions(db: Session, month: Optional[str] = None,
                        category: Optional[str] = None, 
                        transaction_type: Optional[str] = None,
                        tags: Optional[str] = None) -> List[Transaction]:
        # 查询条件构建
        # 数据查询
        # 结果处理
        pass
```

### 3. 数据访问层

#### 数据模型模块 (`src/cashlog/models`)

定义数据模型和数据库配置，使用SQLAlchemy ORM：

- `db.py`：数据库连接配置和会话管理
- `transaction.py`：交易记录数据模型
- `todo.py`：待办事项数据模型

设计特点：
- 声明式模型定义
- 自动表创建
- 关系映射
- 索引优化

#### 数据模型设计模式

```python
class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    tags = Column(String(200))
    note = Column(String(500))
    transaction_date = Column(DateTime, default=datetime.utcnow)
    
    # 关系定义
    todos = relationship("Todo", back_populates="transaction")
```

### 4. 工具模块

#### 格式化工具 (`src/cashlog/utils`)

提供通用的格式化和输出功能：

- `Formatter`：数据格式化工具类
  - 表格格式化
  - 数据格式化
  - 消息打印

设计特点：
- 静态方法设计
- 支持多种输出格式
- 使用Rich库美化输出

## 数据流

### 1. CLI命令执行流程

```
用户输入命令
    ↓
CLI命令解析 (main_cli.py)
    ↓
参数验证
    ↓
调用业务服务 (services/*.py)
    ↓
数据模型操作 (models/*.py)
    ↓
数据库操作 (SQLite)
    ↓
结果格式化 (utils/formatter.py)
    ↓
输出结果
```

### 2. REST API请求流程

```
客户端请求
    ↓
API路由处理 (routers/*.py)
    ↓
参数验证 (models.py)
    ↓
调用业务服务 (services/*.py)
    ↓
数据模型操作 (models/*.py)
    ↓
数据库操作 (SQLite)
    ↓
响应序列化 (models.py)
    ↓
返回响应
```

## 数据库设计

### 1. 表结构

#### 交易记录表 (transactions)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY | 主键 |
| amount | Float | NOT NULL | 交易金额 |
| category | String(50) | NOT NULL | 交易分类 |
| tags | String(200) | | 交易标签 |
| note | String(500) | | 备注信息 |
| transaction_date | DateTime | DEFAULT NOW | 交易时间 |

#### 待办事项表 (todos)

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | Integer | PRIMARY KEY | 主键 |
| content | String(200) | NOT NULL | 待办内容 |
| category | String(50) | | 分类 |
| tags | String(200) | | 标签 |
| status | String(20) | DEFAULT 'todo' | 状态 |
| due_date | DateTime | | 截止时间 |
| created_at | DateTime | DEFAULT NOW | 创建时间 |
| updated_at | DateTime | DEFAULT NOW | 更新时间 |
| transaction_id | Integer | FOREIGN KEY | 关联交易ID |

### 2. 索引设计

- 交易记录表：
  - `idx_transaction_date`：交易时间索引
  - `idx_category`：分类索引
  - `idx_amount`：金额索引

- 待办事项表：
  - `idx_status`：状态索引
  - `idx_due_date`：截止时间索引
  - `idx_category`：分类索引
  - `idx_transaction_id`：交易ID索引

## 安全设计

### 1. 数据安全

- 所有数据存储在本地SQLite数据库中，不涉及网络传输
- 数据备份和恢复操作需要用户确认
- 敏感操作（如数据恢复）前自动创建备份

### 2. 输入验证

- 所有用户输入都经过严格验证
- 防止SQL注入攻击（使用ORM参数化查询）
- 金额格式验证
- 日期格式验证

### 3. 错误处理

- 统一的异常处理机制
- 详细的错误日志记录
- 用户友好的错误提示

## 扩展性设计

### 1. 模块化设计

各模块之间松耦合，便于独立开发和测试：
- 新增功能只需添加相应的服务类和CLI命令
- 新增数据模型只需扩展models模块
- 新增API端点只需添加新的路由文件

### 2. 配置管理

- 数据库路径可配置
- 备份路径可配置
- 日志级别可配置

### 3. 插件机制

预留插件接口，支持未来功能扩展：
- 自定义报表格式
- 自定义数据验证规则
- 自定义输出格式

## 性能优化

### 1. 数据库优化

- 合理设计索引
- 使用连接池管理数据库连接
- 批量操作优化

### 2. 内存管理

- 使用生成器处理大量数据
- 及时释放数据库会话
- 避免不必要的数据加载

### 3. 查询优化

- 使用SQLAlchemy查询优化
- 避免N+1查询问题
- 合理使用缓存

## 测试策略

### 1. 测试分层

- 单元测试：测试各模块的独立功能
- 集成测试：测试模块间的交互
- 端到端测试：测试完整的功能流程

### 2. 测试工具

- pytest：测试框架
- unittest.mock：模拟对象
- 内存数据库：隔离测试环境

### 3. 测试覆盖

- 业务逻辑测试
- API接口测试
- CLI命令测试
- 数据模型测试

## 部署架构

### 1. 本地部署

- 单机部署，所有组件运行在同一台机器上
- 数据存储在本地文件系统
- 支持命令行和API两种访问方式

### 2. 容器化部署

- 支持Docker容器化部署
- 数据持久化到挂载卷
- 环境变量配置

## 未来扩展方向

### 1. 多用户支持

- 用户认证和授权
- 数据隔离
- 权限管理

### 2. 数据同步

- 云端同步
- 多设备同步
- 冲突解决

### 3. 高级分析

- 数据可视化
- 趋势分析
- 预测模型

### 4. 移动端支持

- 移动应用
- 离线支持
- 数据同步

## 总结

CashLog项目采用分层架构设计，实现了业务逻辑、数据访问和用户界面的有效分离。通过模块化设计和松耦合架构，项目具有良好的可维护性、可扩展性和可测试性。未来可以根据需求逐步扩展功能，支持更多用户场景。