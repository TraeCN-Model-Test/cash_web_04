"""API接口单元测试"""
import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cashlog.api import create_app
from cashlog.models.db import Base, get_db
from cashlog.models.todo import Todo, TodoStatus
from cashlog.models.transaction import Transaction
from datetime import datetime

# 使用临时文件数据库进行测试
@pytest.fixture
def test_db_file():
    """创建临时测试数据库文件"""
    # 在项目中创建临时文件夹
    test_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_temp")
    os.makedirs(test_dir, exist_ok=True)
    
    # 创建临时数据库文件
    db_file = os.path.join(test_dir, "test_api.db")
    print(f"创建临时测试数据库文件: {db_file}")
    
    # 如果文件已存在，先删除
    if os.path.exists(db_file):
        os.remove(db_file)
    
    yield db_file
    
    # 测试结束后保留临时文件，以便检查
    print(f"保留临时测试数据库文件: {db_file}")
    # 如果需要删除文件，取消下面的注释
    # if os.path.exists(db_file):
    #     os.remove(db_file)


@pytest.fixture
def test_app(test_db_file):
    """创建测试应用"""
    # 创建测试数据库引擎
    TEST_DATABASE_URL = f"sqlite:///{test_db_file}"
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # 创建测试数据库会话
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # 确保导入所有模型，以便Base.metadata.create_all能够找到所有表
    from cashlog.models import transaction, todo
    from cashlog.models.todo import Todo
    from cashlog.models.transaction import Transaction
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 添加测试数据
    db = TestingSessionLocal()
    
    # 添加测试待办事项
    todo1 = Todo(
        content="测试待办1",
        category="工作",
        tags="测试,API",
        deadline=datetime(2023, 12, 31, 23, 59, 59),
        status=TodoStatus.TODO
    )
    
    todo2 = Todo(
        content="测试待办2",
        category="生活",
        tags="测试,生活",
        status=TodoStatus.DOING
    )
    
    todo3 = Todo(
        content="测试待办3",
        category="工作",
        tags="API,完成",
        deadline=datetime(2023, 12, 15, 23, 59, 59),
        status=TodoStatus.DONE
    )
    
    # 添加测试交易
    transaction1 = Transaction(
        amount=100.0,
        category="工资",
        tags="收入,工资",
        notes="12月工资",
        created_at=datetime(2023, 12, 1, 10, 0, 0)
    )
    
    transaction2 = Transaction(
        amount=-50.0,
        category="餐饮",
        tags="支出,吃饭",
        notes="午餐",
        created_at=datetime(2023, 12, 15, 12, 0, 0)
    )
    
    transaction3 = Transaction(
        amount=-200.0,
        category="购物",
        tags="支出,网购",
        notes="购买衣服",
        created_at=datetime(2023, 12, 20, 15, 0, 0)
    )
    
    # 关联待办和交易
    todo1.transaction = transaction1
    todo3.transaction = transaction3
    
    db.add_all([todo1, todo2, todo3, transaction1, transaction2, transaction3])
    db.commit()
    
    # 重写依赖项，使用测试数据库
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    # 创建测试应用
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    
    # 创建测试客户端
    client = TestClient(app)
    
    yield client
    
    # 测试结束后删除所有表
    Base.metadata.drop_all(bind=engine)


class TestTodoAPI:
    """待办事项API测试"""
    
    def test_get_todos(self, test_app):
        """测试查询待办事项列表"""
        response = test_app.get("/api/todos/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["items"][0]["content"] == "测试待办3"
        assert data["items"][0]["status"] == "done"
    
    def test_get_todos_with_filters(self, test_app):
        """测试带筛选条件的待办事项查询"""
        # 按状态筛选
        response = test_app.get("/api/todos/?status=todo")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["status"] == "todo"
        
        # 按分类筛选
        response = test_app.get("/api/todos/?category=工作")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        
        # 按标签筛选
        response = test_app.get("/api/todos/?tags=API")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
    
    def test_get_todo_by_id(self, test_app):
        """测试根据ID查询待办事项"""
        response = test_app.get("/api/todos/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["content"] == "测试待办1"
        
        # 测试查询不存在的待办事项
        response = test_app.get("/api/todos/999")
        assert response.status_code == 404
    
    def test_get_todos_pagination(self, test_app):
        """测试待办事项分页查询"""
        # 每页1条
        response = test_app.get("/api/todos/?page=1&size=1")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 1
        assert data["page"] == 1
        assert data["size"] == 1
        
        # 第2页
        response = test_app.get("/api/todos/?page=2&size=1")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["items"][0]["content"] == "测试待办2"


class TestTransactionAPI:
    """交易账单API测试"""
    
    def test_get_transactions(self, test_app):
        """测试查询交易账单列表"""
        response = test_app.get("/api/transactions/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
        assert data["items"][0]["amount"] == -200.0
        assert data["items"][0]["category"] == "购物"
    
    def test_get_transactions_with_filters(self, test_app):
        """测试带筛选条件的交易账单查询"""
        # 按月份筛选
        response = test_app.get("/api/transactions/?month=2023-12")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        
        # 按交易类型筛选（收入）
        response = test_app.get("/api/transactions/?transaction_type=income")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["items"][0]["amount"] == 100.0
        
        # 按交易类型筛选（支出）
        response = test_app.get("/api/transactions/?transaction_type=expense")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        
        # 按分类筛选
        response = test_app.get("/api/transactions/?category=餐饮")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
    
    def test_get_transaction_by_id(self, test_app):
        """测试根据ID查询交易账单"""
        response = test_app.get("/api/transactions/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["amount"] == 100.0
        
        # 测试查询不存在的交易账单
        response = test_app.get("/api/transactions/999")
        assert response.status_code == 404
    
    def test_get_transactions_pagination(self, test_app):
        """测试交易账单分页查询"""
        # 每页2条
        response = test_app.get("/api/transactions/?page=1&size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2
        assert data["page"] == 1
        assert data["size"] == 2
        
        # 第2页
        response = test_app.get("/api/transactions/?page=2&size=2")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert len(data["items"]) == 1
        assert data["items"][0]["amount"] == 100.0