# Tests 目录说明

## 概述

`tests` 目录包含 CashLog 项目的完整测试套件，用于验证系统各组件功能的正确性、稳定性和可靠性。测试覆盖了服务层、CLI 命令、API 接口以及数据备份恢复等核心功能，确保代码质量和系统健壮性。

## 目录结构

```
tests/
├── __init__.py                           # 测试包初始化文件
├── test_backup_restore_cli.py            # 备份恢复CLI命令测试
├── test_backup_restore_service.py        # 备份恢复服务功能测试
├── test_cli_utilities.py                 # CLI工具类测试基类
├── test_report_generation_cli.py         # 报表生成CLI命令测试
├── test_report_generation_service.py     # 报表生成服务功能测试
├── test_rest_api.py                      # REST API接口测试
├── test_todo_cli.py                      # 待办事项CLI命令测试
├── test_todo_service.py                  # 待办事项服务功能测试
├── test_transaction_cli.py               # 交易记录CLI命令测试
└── test_transaction_service.py           # 交易记录服务功能测试
```

## 测试架构

### 测试分层

1. **服务层测试** (`test_*_service.py`)
   - 测试业务逻辑的核心功能
   - 验证数据处理和业务规则
   - 使用内存 SQLite 数据库进行隔离测试

2. **CLI层测试** (`test_*_cli.py`)
   - 测试命令行界面的各种命令
   - 验证参数解析和用户交互
   - 使用模拟对象隔离外部依赖

3. **API层测试** (`test_rest_api.py`)
   - 测试 REST API 接口
   - 验证 HTTP 请求/响应处理
   - 使用 FastAPI 测试客户端

### 测试工具和框架

- **pytest**: 测试框架，提供测试运行、断言和夹具功能
- **unittest.mock**: 模拟对象，用于隔离外部依赖
- **click.testing**: CLI 测试工具，用于测试 Click 命令
- **fastapi.testclient**: API 测试工具，用于测试 FastAPI 应用
- **sqlalchemy**: 数据库测试，使用内存 SQLite 数据库

## 测试文件说明

### 1. 服务层测试

#### test_transaction_service.py - 交易服务测试

**测试内容**:
- 交易记录创建功能
- 交易数据验证（金额格式、必填字段等）
- 交易查询功能（按月份、分类、类型筛选）
- 交易更新和删除功能

**关键测试用例**:
```python
def test_create_transaction_success(db_session):
    """测试成功创建交易记录"""
    
def test_create_transaction_invalid_amount(db_session):
    """测试金额格式错误"""
    
def test_get_transactions_by_month(db_session):
    """测试按月份查询交易"""
```

#### test_todo_service.py - 待办事项服务测试

**测试内容**:
- 待办事项创建功能
- 待办数据验证（内容、分类、截止时间等）
- 待办事项状态更新
- 待办事项查询功能（按状态、分类、截止时间筛选）

**关键测试用例**:
```python
def test_create_todo_success(db_session):
    """测试成功创建待办事项"""
    
def test_update_todo_status_success(db_session):
    """测试成功更新待办事项状态"""
    
def test_get_todos_by_status(db_session):
    """测试按状态查询待办事项"""
```

#### test_report_generation_service.py - 报表生成服务测试

**测试内容**:
- 月度报表生成功能
- 报表数据准确性验证
- 不同时间维度报表（日、周、月、季度）
- 报表格式化（文本和Markdown格式）

**关键测试用例**:
```python
def test_generate_monthly_report(sample_transactions, db_session):
    """测试生成月度报表"""
    
def test_format_report_text(sample_transactions, db_session):
    """测试文本格式报表"""
    
def test_generate_report_daily(sample_transactions, db_session):
    """测试按日维度生成报表"""
```

#### test_backup_restore_service.py - 数据备份恢复服务测试

**测试内容**:
- 数据库备份功能
- 数据库恢复功能
- 备份文件验证
- 错误处理（文件不存在、无效数据库等）

**关键测试用例**:
```python
def test_create_backup_custom_path(db_session, test_db_dir):
    """测试使用自定义路径创建备份"""
    
def test_restore_backup_file_not_found(db_session, test_db_dir):
    """测试恢复不存在的备份文件"""
    
def test_is_valid_sqlite_db(mock_connect, test_db_dir):
    """测试SQLite数据库文件验证"""
```

### 2. CLI层测试

#### test_transaction_cli.py - 交易CLI测试

**测试内容**:
- 交易添加命令
- 交易列表查询命令
- 交易更新命令
- 交易关联解除命令
- 参数验证和错误处理

**关键测试用例**:
```python
def test_add_transaction_success(self):
    """测试成功添加交易记录"""
    
def test_list_transactions_with_filters(self):
    """测试带筛选条件列出交易记录"""
    
def test_unlink_transaction_success(self):
    """测试成功解除交易记录关联"""
```

#### test_todo_cli.py - 待办事项CLI测试

**测试内容**:
- 待办事项添加命令
- 待办事项列表查询命令
- 待办事项状态更新命令
- 待办事项删除命令
- 参数验证和错误处理

#### test_report_generation_cli.py - 报表生成CLI测试

**测试内容**:
- 报表生成命令
- 不同时间维度报表参数
- 报表格式参数
- 输出重定向功能

#### test_backup_restore_cli.py - 备份恢复CLI测试

**测试内容**:
- 数据备份命令
- 数据恢复命令
- 备份文件路径参数
- 强制覆盖参数

### 3. API层测试

#### test_rest_api.py - REST API测试

**测试内容**:
- 待办事项API端点
- 交易记录API端点
- 请求参数验证
- 响应数据格式
- 分页功能
- 错误处理

**关键测试用例**:
```python
def test_get_todos(self, test_app):
    """测试查询待办事项列表"""
    
def test_get_todos_with_filters(self, test_app):
    """测试带筛选条件的待办事项查询"""
    
def test_get_todos_pagination(self, test_app):
    """测试待办事项分页查询"""
```

### 4. 测试工具

#### test_cli_utilities.py - CLI工具类

**测试内容**:
- CLI测试基类
- 数据库依赖模拟
- 通用测试工具方法

**关键组件**:
```python
class CLITestBase:
    """CLI测试基类，提供通用测试方法"""
    
    def mock_db_dependency(self):
        """模拟数据库依赖"""
        
    def mock_init_db(self):
        """模拟数据库初始化"""
```

## 测试夹具

### 通用夹具

1. **db_session**: 创建内存 SQLite 数据库会话
   ```python
   @pytest.fixture
   def db_session():
       """创建测试数据库会话"""
       engine = create_engine(TEST_DATABASE_URL)
       Base.metadata.create_all(bind=engine)
       Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
       db = Session()
       
       try:
           yield db
       finally:
           db.close()
           Base.metadata.drop_all(bind=engine)
   ```

2. **sample_transactions**: 创建测试交易数据
   ```python
   @pytest.fixture
   def sample_transactions(db_session):
       """创建测试数据"""
       # 创建测试交易记录
   ```

3. **test_app**: 创建测试应用客户端
   ```python
   @pytest.fixture
   def test_app(test_db_file):
       """创建测试应用"""
       # 设置测试数据库和依赖项覆盖
   ```

## 运行测试

### 运行所有测试

```bash
uv run pytest
```

### 运行特定测试文件

```bash
uv run pytest tests/test_transaction_service.py
```

### 运行特定测试用例

```bash
uv run pytest tests/test_transaction_service.py::test_create_transaction_success
```

### 运行测试并显示覆盖率

```bash
uv run pytest --cov=cashlog
```

### 运行测试并生成HTML覆盖率报告

```bash
uv run pytest --cov=cashlog --cov-report=html
```

## 测试数据管理

### 测试数据库

- 服务层测试使用内存 SQLite 数据库，确保测试隔离
- API测试使用临时文件数据库，支持更复杂的测试场景
- 测试完成后自动清理测试数据

### 测试数据夹具

- 使用 pytest 夹具创建和管理测试数据
- 每个测试用例都有独立的测试数据环境
- 测试数据在测试结束后自动清理

## 测试最佳实践

### 1. 测试隔离

- 每个测试用例应独立运行，不依赖其他测试的状态
- 使用夹具确保测试环境的一致性
- 测试后清理所有创建的资源

### 2. 测试覆盖率

- 确保测试覆盖所有关键代码路径
- 测试正常流程和异常情况
- 验证边界条件和错误处理

### 3. 测试命名

- 使用描述性的测试方法名
- 遵循一致的命名约定
- 添加文档字符串说明测试目的

### 4. 测试断言

- 使用具体的断言验证预期行为
- 验证错误消息和状态码
- 检查副作用（如数据库更改）

## 持续集成

测试套件已集成到项目的持续集成流程中，确保每次代码提交都通过所有测试：

1. **单元测试**: 验证各组件功能
2. **集成测试**: 验证组件间交互
3. **API测试**: 验证接口功能
4. **CLI测试**: 验证命令行功能

## 故障排除

### 常见问题

1. **数据库连接错误**: 确保测试数据库配置正确
2. **导入错误**: 检查Python路径和模块导入
3. **权限问题**: 确保测试目录有读写权限
4. **依赖缺失**: 运行 `uv sync` 安装所有依赖

### 调试技巧

1. 使用 `-v` 参数显示详细测试输出
2. 使用 `-s` 参数禁用输出捕获
3. 使用 `--pdb` 在测试失败时进入调试器
4. 使用 `--lf` 只运行上次失败的测试

## 贡献指南

添加新测试时请遵循以下指南：

1. 为新功能添加对应的测试文件
2. 使用现有的测试夹具和工具
3. 确保测试覆盖正常流程和异常情况
4. 添加描述性的测试文档
5. 保持测试代码的简洁和可读性

测试是确保代码质量的重要手段，请为所有新功能编写充分的测试用例。