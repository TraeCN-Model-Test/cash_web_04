"""API响应模型定义"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from cashlog.models.todo import TodoStatus


class TodoBase(BaseModel):
    """待办事项基础模型"""
    content: str
    category: str
    tags: Optional[str] = None
    deadline: Optional[datetime] = None
    transaction_id: Optional[int] = None
    status: TodoStatus = TodoStatus.TODO


class TodoCreate(TodoBase):
    """创建待办事项模型"""
    pass


class TodoUpdate(TodoBase):
    """更新待办事项模型"""
    pass


class Todo(TodoBase):
    """待办事项响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    status_text: str
    
    class Config:
        """配置类"""
        from_attributes = True


class TransactionBase(BaseModel):
    """交易基础模型"""
    amount: float
    category: str
    tags: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime


class TransactionCreate(TransactionBase):
    """创建交易模型"""
    pass


class TransactionUpdate(TransactionBase):
    """更新交易模型"""
    pass


class Transaction(TransactionBase):
    """交易响应模型"""
    id: int
    updated_at: datetime
    transaction_type: str
    month: str
    
    class Config:
        """配置类"""
        from_attributes = True
