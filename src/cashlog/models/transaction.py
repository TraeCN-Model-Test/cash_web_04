"""交易数据模型"""
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from cashlog.models.db import Base


class Transaction(Base):
    """交易记录表模型"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    tags = Column(String(200), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关联关系
    todo = relationship("Todo", back_populates="transaction", uselist=False, primaryjoin="Transaction.id == Todo.transaction_id")

    @property
    def transaction_type(self):
        """根据金额判断交易类型"""
        return "收入" if self.amount > 0 else "支出"

    @property
    def month(self):
        """获取交易的年月，格式：YYYY-MM"""
        return self.created_at.strftime("%Y-%m")
