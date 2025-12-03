"""格式化工具类"""
from typing import List, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.text import Text


class Formatter:
    """格式化工具类"""
    
    @staticmethod
    def format_table(data: List[Dict[str, Any]], headers: Dict[str, str]) -> Table:
        """
        格式化数据为表格

        Args:
            data: 数据列表
            headers: 表头映射，格式为 {"字段名": "显示名称"}

        Returns:
            Rich表格对象
        """
        table = Table(show_header=True, header_style="bold magenta")
        
        # 添加表头
        for field, display_name in headers.items():
            table.add_column(display_name, style="dim")
        
        # 添加数据行
        for row in data:
            values = []
            for field in headers.keys():
                value = row.get(field)
                # 格式化时间
                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                # 格式化数字
                elif isinstance(value, float):
                    value = f"{value:.2f}"
                # 空值处理
                elif value is None:
                    value = "-"
                values.append(str(value))
            table.add_row(*values)
        
        return table
    
    @staticmethod
    def print_table(data: List[Dict[str, Any]], headers: Dict[str, str]) -> None:
        """
        打印表格

        Args:
            data: 数据列表
            headers: 表头映射
        """
        console = Console()
        if not data:
            console.print("[yellow]暂无数据[/yellow]")
            return
        
        table = Formatter.format_table(data, headers)
        console.print(table)
    
    @staticmethod
    def format_transactions(transactions: List[Any], with_todos: bool = False) -> List[Dict[str, Any]]:
        """
        格式化交易数据

        Args:
            transactions: 交易对象列表
            with_todos: 是否显示关联的待办事项信息

        Returns:
            格式化后的数据列表
        """
        formatted = []
        for t in transactions:
            item = {
                "id": t.id,
                "amount": t.amount,
                "type": t.transaction_type,
                "category": t.category,
                "tags": t.tags or "-",
                "notes": t.notes or "-",
                "created_at": t.created_at
            }
            
            if with_todos:
                item["todo_id"] = t.todo.id if t.todo else "-"
                if t.todo:
                    item["todo_info"] = f"{t.todo.content} ({t.todo.status_text})"
                else:
                    item["todo_info"] = "-"
            formatted.append(item)
        return formatted
    
    @staticmethod
    def format_todos(todos: List[Any], with_transactions: bool = False) -> List[Dict[str, Any]]:
        """
        格式化待办事项数据

        Args:
            todos: 待办事项对象列表
            with_transactions: 是否显示关联的交易信息

        Returns:
            格式化后的数据列表
        """
        formatted = []
        for t in todos:
            item = {
                "id": t.id,
                "content": t.content,
                "category": t.category,
                "status": t.status_text,
                "tags": t.tags or "-",
                "deadline": t.deadline,
                "created_at": t.created_at
            }
            
            if with_transactions:
                item["transaction_id"] = t.transaction_id or "-"
                if t.transaction:
                    item["transaction_info"] = f"{t.transaction.amount:.2f} ({t.transaction.category} - {t.transaction.transaction_type})"
                else:
                    item["transaction_info"] = "-"
            formatted.append(item)
        return formatted
    
    @staticmethod
    def print_success(message: str) -> None:
        """
        打印成功消息

        Args:
            message: 消息内容
        """
        console = Console()
        console.print(f"[green]✓ {message}[/green]")
    
    @staticmethod
    def print_error(message: str) -> None:
        """
        打印错误消息

        Args:
            message: 消息内容
        """
        console = Console()
        console.print(f"[red]✗ {message}[/red]")
    
    @staticmethod
    def print_info(message: str) -> None:
        """
        打印信息消息

        Args:
            message: 消息内容
        """
        console = Console()
        console.print(f"[blue]ℹ {message}[/blue]")
    
    @staticmethod
    def print_warning(message: str) -> None:
        """
        打印警告消息

        Args:
            message: 消息内容
        """
        console = Console()
        console.print(f"[yellow]⚠ {message}[/yellow]")