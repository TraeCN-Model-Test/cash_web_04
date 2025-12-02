"""交易业务逻辑服务"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from cashlog.models.transaction import Transaction
from cashlog.models.todo import Todo


class TransactionService:
    """交易服务类"""

    @staticmethod
    def create_transaction(db: Session, transaction_data: Dict[str, Any]) -> Transaction:
        """
        创建新交易

        Args:
            db: 数据库会话
            transaction_data: 交易数据，包含amount、category等

        Returns:
            创建的交易对象
        """
        # 验证金额格式
        try:
            amount = float(transaction_data["amount"])
        except (ValueError, TypeError):
            raise ValueError("金额需为数字")

        # 验证必填字段
        if not transaction_data.get("category"):
            raise ValueError("分类为必填项")
        
        # 验证关联待办事项ID
        todo_id = transaction_data.get("todo_id")
        if todo_id is not None:
            from cashlog.models.todo import Todo
            todo = db.query(Todo).filter(Todo.id == todo_id).first()
            if not todo:
                raise ValueError(f"待办事项ID {todo_id} 不存在")
            # 避免循环关联
            if todo.transaction_id is not None:
                raise ValueError(f"待办事项ID {todo_id} 已关联交易ID {todo.transaction_id}")

        # 创建交易对象
        tags = transaction_data.get("tags", "")
        if tags:
            tags = tags.strip()
        notes = transaction_data.get("notes", "")
        if notes:
            notes = notes.strip()
            
        transaction = Transaction(
            amount=amount,
            category=transaction_data["category"].strip(),
            tags=tags or None,
            notes=notes or None
        )
        
        # 如果有待办事项关联，更新待办事项的交易ID
        if todo_id is not None:
            todo.transaction_id = transaction.id

        # 如果提供了时间，设置时间
        if transaction_data.get("created_at"):
            try:
                # 支持多种时间格式
                formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"]
                for fmt in formats:
                    try:
                        transaction.created_at = datetime.strptime(transaction_data["created_at"], fmt)
                        break
                    except ValueError:
                        continue
                else:
                    raise ValueError("时间格式不正确，请使用YYYY-MM-DD HH:MM:SS格式")
            except ValueError as e:
                raise e

        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction

    @staticmethod
    def get_transactions(db: Session, **filters) -> List[Transaction]:
        """
        查询交易列表

        Args:
            db: 数据库会话
            filters: 查询条件，包括month、category、tags、transaction_type等

        Returns:
            交易列表
        """
        query = db.query(Transaction)

        # 按月份筛选
        if filters.get("month"):
            month = filters["month"]
            # 验证月份格式
            try:
                # 检查是否为YYYY-MM格式
                if len(month) != 7 or month[4] != "-":
                    raise ValueError("月份格式应为YYYY-MM")
                datetime.strptime(month + "-01", "%Y-%m-%d")
                # 构建月份的开始和结束时间
                start_date = datetime.strptime(month + "-01", "%Y-%m-%d")
                # 计算下个月的第一天
                if start_date.month == 12:
                    end_date = datetime.strptime(f"{start_date.year + 1}-01-01", "%Y-%m-%d")
                else:
                    end_date = datetime.strptime(f"{start_date.year}-{start_date.month + 1:02d}-01", "%Y-%m-%d")
                query = query.filter(and_(Transaction.created_at >= start_date, Transaction.created_at < end_date))
            except ValueError:
                raise ValueError("月份格式应为YYYY-MM")

        # 按分类筛选
        if filters.get("category"):
            query = query.filter(Transaction.category == filters["category"])

        # 按标签筛选（包含任一标签即可）
        if filters.get("tags"):
            tags = filters["tags"].split(",")
            tag_filters = [Transaction.tags.like(f"%{tag.strip()}%") for tag in tags if tag.strip()]
            if tag_filters:
                query = query.filter(or_(*tag_filters))

        # 按交易类型筛选
        transaction_type = filters.get("transaction_type")
        if transaction_type == "income":
            query = query.filter(Transaction.amount > 0)
        elif transaction_type == "expense":
            query = query.filter(Transaction.amount < 0)

        # 按时间排序
        query = query.order_by(Transaction.created_at.desc())

        return query.all()

    @staticmethod
    def get_transaction_by_id(db: Session, transaction_id: int) -> Optional[Transaction]:
        """
        根据ID获取交易

        Args:
            db: 数据库会话
            transaction_id: 交易ID

        Returns:
            交易对象或None
        """
        return db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    @staticmethod
    def update_transaction(db: Session, transaction_id: int, transaction_data: Dict[str, Any]) -> Transaction:
        """
        更新交易信息
        
        Args:
            db: 数据库会话
            transaction_id: 交易ID
            transaction_data: 更新的交易数据
            
        Returns:
            更新后的交易对象
        """
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise ValueError(f"交易ID {transaction_id} 不存在")
            
        # 更新基本信息
        if "amount" in transaction_data:
            try:
                transaction.amount = float(transaction_data["amount"])
            except (ValueError, TypeError):
                raise ValueError("金额需为数字")
                
        if "category" in transaction_data:
            category = transaction_data["category"].strip()
            if not category:
                raise ValueError("分类不能为空")
            transaction.category = category
            
        if "tags" in transaction_data:
            transaction.tags = transaction_data["tags"].strip() or None
            
        if "notes" in transaction_data:
            transaction.notes = transaction_data["notes"].strip() or None
            
        # 更新关联待办事项
        if "todo_id" in transaction_data:
            todo_id = transaction_data["todo_id"]
            if todo_id is None:
                # 解除关联
                existing_todo = db.query(Todo).filter(Todo.transaction_id == transaction.id).first()
                if existing_todo:
                    existing_todo.transaction_id = None
            else:
                todo = db.query(Todo).filter(Todo.id == todo_id).first()
                if not todo:
                    raise ValueError(f"待办事项ID {todo_id} 不存在")
                # 避免循环关联
                if todo.transaction_id is not None and todo.transaction_id != transaction.id:
                    raise ValueError(f"待办事项ID {todo_id} 已关联交易ID {todo.transaction_id}")
                # 先解除原有关联
                existing_todo = db.query(Todo).filter(Todo.transaction_id == transaction.id).first()
                if existing_todo:
                    existing_todo.transaction_id = None
                # 建立新关联
                todo.transaction_id = transaction.id
                
        transaction.updated_at = datetime.now()
        db.commit()
        db.refresh(transaction)
        return transaction
    
    @staticmethod
    def remove_transaction_todo_link(db: Session, transaction_id: int) -> Transaction:
        """
        解除交易与待办事项的关联
        
        Args:
            db: 数据库会话
            transaction_id: 交易ID
            
        Returns:
            更新后的交易对象
        """
        transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
        if not transaction:
            raise ValueError(f"交易ID {transaction_id} 不存在")
            
        from cashlog.models.todo import Todo
        existing_todo = db.query(Todo).filter(Todo.transaction_id == transaction.id).first()
        if existing_todo:
            existing_todo.transaction_id = None
            transaction.updated_at = datetime.now()
            db.commit()
            db.refresh(transaction)
            
        return transaction
