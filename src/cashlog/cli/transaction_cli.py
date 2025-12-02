"""交易相关命令行接口"""
import click
from typing import Optional
from cashlog.models.db import get_db, init_db
from cashlog.services.transaction_service import TransactionService
from cashlog.utils.formatter import Formatter


@click.group()
def transaction():
    """交易管理命令组"""
    pass


@transaction.command()
@click.option("-a", "--amount", required=True, help="金额，收入为正，支出为负")
@click.option("-c", "--category", required=True, help="分类")
@click.option("-t", "--tags", help="标签，多个标签用逗号分隔")
@click.option("-n", "--notes", help="备注")
@click.option("-d", "--date", help="日期时间，格式：YYYY-MM-DD HH:MM:SS")
@click.option("--todo-id", type=int, help="关联的待办事项ID")
def add(amount: str, category: str, tags: Optional[str], notes: Optional[str], date: Optional[str], todo_id: Optional[int]):
    """
    添加交易记录
    
    示例:
    cashlog transaction add -a 100.50 -c 工资 -t "收入,月度"
    cashlog transaction add -a -50.00 -c 餐饮 -t "支出,日常" -n "午餐"
    cashlog transaction add -a -100.00 -c 购物 -t "支出" --todo-id 1
    """
    init_db()  # 确保数据库已初始化
    
    try:
        transaction_data = {
            "amount": amount,
            "category": category,
            "tags": tags,
            "notes": notes
        }
        if date:
            transaction_data["created_at"] = date
        if todo_id is not None:
            transaction_data["todo_id"] = todo_id
        
        db = next(get_db())
        transaction = TransactionService.create_transaction(db, transaction_data)
        
        message = f"交易记录已添加 (ID: {transaction.id})"
        if transaction.todo:
            message += f"，已关联待办事项ID: {transaction.todo.id}"
        Formatter.print_success(message)
    except ValueError as e:
        Formatter.print_error(str(e))
    except Exception as e:
        Formatter.print_error(f"添加交易记录失败: {str(e)}")


@transaction.command()
@click.option("-m", "--month", help="月份，格式：YYYY-MM")
@click.option("-c", "--category", help="分类")
@click.option("-t", "--tags", help="标签，多个标签用逗号分隔")
@click.option("--type", type=click.Choice(["income", "expense"]), help="交易类型: income(收入), expense(支出)")
@click.option("--with-todos", is_flag=True, help="显示关联的待办事项详细信息")
def list(month: Optional[str], category: Optional[str], tags: Optional[str], type: Optional[str], with_todos: bool):
    """
    列出交易记录
    
    示例:
    cashlog transaction list  # 列出所有交易
    cashlog transaction list -m 2023-10  # 列出10月交易
    cashlog transaction list --type income  # 列出所有收入
    cashlog transaction list -c 餐饮 -t "午餐,晚餐"  # 按分类和标签筛选
    cashlog transaction list --with-todos  # 列出所有交易并显示关联待办事项
    """
    init_db()  # 确保数据库已初始化
    
    try:
        filters = {}
        if month:
            filters["month"] = month
        if category:
            filters["category"] = category
        if tags:
            filters["tags"] = tags
        if type:
            filters["transaction_type"] = type
        
        db = next(get_db())
        transactions = TransactionService.get_transactions(db, **filters)
        
        # 格式化并打印
        formatted_data = Formatter.format_transactions(transactions, with_todos=with_todos)
        headers = {
            "id": "ID",
            "amount": "金额",
            "type": "类型",
            "category": "分类",
            "tags": "标签",
            "notes": "备注",
            "created_at": "时间"
        }
        
        if with_todos:
            headers["todo_id"] = "关联待办ID"
            headers["todo_content"] = "关联待办内容"
        
        if filters:
            Formatter.print_info(f"查询条件: {filters}")
        Formatter.print_table(formatted_data, headers)
        
    except ValueError as e:
        Formatter.print_error(str(e))
    except Exception as e:
        Formatter.print_error(f"查询交易记录失败: {str(e)}")


@transaction.command()
@click.argument("transaction_id")
@click.option("-a", "--amount", help="金额，收入为正，支出为负")
@click.option("-c", "--category", help="分类")
@click.option("-t", "--tags", help="标签，多个标签用逗号分隔")
@click.option("-n", "--notes", help="备注")
@click.option("--todo-id", type=int, help="关联的待办事项ID，设置为0可解除关联")
def update(transaction_id: str, amount: Optional[str], category: Optional[str], tags: Optional[str], notes: Optional[str], todo_id: Optional[int]):
    """
    更新交易记录
    
    示例:
    cashlog transaction update 1 -a -60.00 -n "晚餐"
    cashlog transaction update 2 --todo-id 3  # 关联待办事项3
    cashlog transaction update 3 --todo-id 0  # 解除待办事项关联
    """
    init_db()  # 确保数据库已初始化
    
    try:
        # 验证ID格式
        try:
            transaction_id_int = int(transaction_id)
        except ValueError:
            Formatter.print_error("交易ID必须为数字")
            return
        
        transaction_data = {}
        if amount is not None:
            transaction_data["amount"] = amount
        if category is not None:
            transaction_data["category"] = category
        if tags is not None:
            transaction_data["tags"] = tags
        if notes is not None:
            transaction_data["notes"] = notes
        if todo_id is not None:
            transaction_data["todo_id"] = todo_id if todo_id != 0 else None
        
        if not transaction_data:
            Formatter.print_error("请指定至少一个要更新的字段")
            return
        
        db = next(get_db())
        transaction = TransactionService.update_transaction(db, transaction_id_int, transaction_data)
        
        message = f"交易记录(ID: {transaction.id})已更新"
        if "todo_id" in transaction_data:
            if transaction.todo:
                message += f"，已关联待办事项ID: {transaction.todo.id}"
            else:
                message += "，已解除待办事项关联"
        Formatter.print_success(message)
    except ValueError as e:
        Formatter.print_error(str(e))
    except Exception as e:
        Formatter.print_error(f"更新交易记录失败: {str(e)}")


@transaction.command()
@click.argument("transaction_id")
def unlink(transaction_id: str):
    """
    解除交易记录与待办事项的关联
    
    示例:
    cashlog transaction unlink 1  # 解除交易1的待办关联
    """
    init_db()  # 确保数据库已初始化
    
    try:
        # 验证ID格式
        try:
            transaction_id_int = int(transaction_id)
        except ValueError:
            Formatter.print_error("交易ID必须为数字")
            return
        
        db = next(get_db())
        transaction = TransactionService.remove_transaction_todo_link(db, transaction_id_int)
        
        Formatter.print_success(f"交易记录(ID: {transaction.id})已解除待办事项关联")
    except ValueError as e:
        Formatter.print_error(str(e))
    except Exception as e:
        Formatter.print_error(f"解除关联失败: {str(e)}")
