"""待办事项数据模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy import Enum as SQLEnum
import enum
from cashlog.models.db import Base


class TodoStatus(str, enum.Enum):
    """待办事项状态枚举"""
    TODO = "todo"
    DOING = "doing"
    DONE = "done"


class Todo(Base):
    """待办事项表模型"""
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    tags = Column(String(200), nullable=True)
    deadline = Column(DateTime, nullable=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"), nullable=True)
    status = Column(SQLEnum(TodoStatus), default=TodoStatus.TODO, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    transaction = relationship("Transaction", back_populates="todo")

    @property
    def status_text(self):
        """获取状态的中文描述"""
        status_map = {
            TodoStatus.TODO: "待办",
            TodoStatus.DOING: "进行中",
            TodoStatus.DONE: "已完成"
        }
        return status_map.get(self.status, self.status)
