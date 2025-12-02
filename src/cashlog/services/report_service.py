"""报表业务逻辑服务"""
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from cashlog.models.transaction import Transaction


class ReportService:
    """报表服务类"""

    @staticmethod
    def _get_date_range(time_dimension: str = "monthly", start: Optional[str] = None, end: Optional[str] = None) -> Tuple[datetime, datetime, str]:
        """
        获取指定时间维度的日期范围

        Args:
            time_dimension: 时间维度，可选值：daily, weekly, monthly, quarterly, custom
            start: 自定义开始日期，格式YYYY-MM-DD
            end: 自定义结束日期，格式YYYY-MM-DD

        Returns:
            开始时间、结束时间、时间维度描述
        """
        now = datetime.now()
        start_date: datetime
        end_date: datetime
        desc: str
        
        # 如果用户指定了start和end，优先使用用户提供的日期
        if start and end:
            try:
                start_date = datetime.strptime(start, "%Y-%m-%d")
                end_date = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1) - timedelta(microseconds=1)  # 包含结束日期当天
            except ValueError:
                raise ValueError("日期格式应为YYYY-MM-DD")
            
            if start_date > end_date:
                raise ValueError("结束日期必须晚于开始日期")
            
            desc = f"{start} 至 {end}"
            return start_date, end_date, desc
        # 如果仅指定start且时间维度为monthly，解析为月份
        elif start and time_dimension == "monthly":
            try:
                month_date = datetime.strptime(start, "%Y-%m-%d")
                start_date = datetime(month_date.year, month_date.month, 1)
                if month_date.month == 12:
                    end_date = datetime(month_date.year, 12, 31, 23, 59, 59, 999999)
                else:
                    end_date = datetime(month_date.year, month_date.month + 1, 1) - timedelta(microseconds=1)
                desc = f"{month_date.strftime('%Y-%m')}"
                return start_date, end_date, desc
            except ValueError:
                raise ValueError("日期格式应为YYYY-MM-DD")

        if time_dimension == "daily":
            # 当日
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            desc = start_date.strftime("%Y-%m-%d")
        elif time_dimension == "weekly":
            # 本周（周一到周日）
            start_date = now - timedelta(days=now.weekday())
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=6)
            end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            desc = f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
        elif time_dimension == "quarterly":
            # 本季度
            quarter = (now.month - 1) // 3 + 1
            start_month = (quarter - 1) * 3 + 1
            start_date = datetime(now.year, start_month, 1)
            end_month = quarter * 3
            end_day = 31 if end_month in [1, 3, 5, 7, 8, 10, 12] else 30 if end_month != 2 else 28
            end_date = datetime(now.year, end_month, end_day, 23, 59, 59, 999999)
            desc = f"Q{quarter} {now.year}"
        elif time_dimension == "custom":
            # 自定义区间必须提供开始和结束日期
            raise ValueError("自定义区间必须同时提供开始和结束日期")
        else:  # monthly
            # 月度
            if not start:
                month = now.strftime("%Y-%m")
                start_date = datetime.strptime(month + "-01", "%Y-%m-%d")
            else:
                # Fix variable name order: parse input start string to start_date
                start_date = datetime.strptime(start, "%Y-%m-%d")
                month = start_date.strftime("%Y-%m")
            
            # Get last day of the month with full time to match other time dimension logic
            if start_date.month == 12:
                end_date = datetime(start_date.year, 12, 31, 23, 59, 59, 999999)
            else:
                end_date = datetime(start_date.year, start_date.month + 1, 1) - timedelta(microseconds=1)
            desc = month
    
        return start_date, end_date, desc
    
    @staticmethod
    def get_base_period(time_dimension: str, start_date: datetime, end_date: datetime) -> Tuple[datetime, datetime]:
        """
        获取环比基准周期

        Args:
            time_dimension: 时间维度
            start_date: 当前周期开始时间
            end_date: 当前周期结束时间

        Returns:
            基准周期的开始时间和结束时间
        """
        from datetime import date
        start_date_date = start_date.date() if isinstance(start_date, datetime) else start_date
        end_date_date = end_date.date() if isinstance(end_date, datetime) else end_date
        
        if time_dimension == "daily":
            base_start_date = start_date_date - timedelta(days=1)
            base_start = datetime.combine(base_start_date, datetime.min.time())
            base_end = datetime.combine(base_start_date, datetime.max.time())
        elif time_dimension == "weekly":
            base_start_date = start_date_date - timedelta(weeks=1)
            base_end_date = end_date_date - timedelta(weeks=1)
            base_start = datetime.combine(base_start_date, datetime.min.time())
            base_end = datetime.combine(base_end_date, datetime.max.time())
        elif time_dimension == "quarterly":
            # 上季度同期
            quarter = (start_date_date.month -1) //3 +1
            base_quarter = quarter -1 if quarter >1 else 4
            base_year = start_date_date.year if quarter>1 else start_date_date.year-1
            base_start_month = (base_quarter -1)*3 +1
            base_start_date = date(base_year, base_start_month,1)
            base_end_month = base_quarter*3
            if base_end_month ==12:
                base_end_date = date(base_year,12,31)
            else:
                base_end_date = date(base_year, base_end_month+1,1) - timedelta(days=1)
            base_start = datetime.combine(base_start_date, datetime.min.time())
            base_end = datetime.combine(base_end_date, datetime.max.time())
        elif time_dimension == "custom":
            # 自定义区间使用相同长度的上期区间
            duration = end_date_date - start_date_date
            base_start_date = start_date_date - duration
            base_end_date = end_date_date - duration
            base_start = datetime.combine(base_start_date, datetime.min.time())
            base_end = datetime.combine(base_end_date, datetime.max.time())
        else: # monthly
            # 上月同期
            year = start_date_date.year if start_date_date.month>1 else start_date_date.year-1
            month = start_date_date.month-1 if start_date_date.month>1 else 12
            base_start_date = date(year, month,1)
            # 获取上月最后一天
            if month == 12:
                base_end_date = date(year, 12, 31)
            else:
                base_end_date = date(year, month+1,1) - timedelta(days=1)
            base_start = datetime.combine(base_start_date, datetime.min.time())
            base_end = datetime.combine(base_end_date, datetime.max.time())
        
        return (base_start, base_end)
    
    @staticmethod
    def generate_report(db: Session, time_dimension: str = "monthly", 
                       start: Optional[str] = None, end: Optional[str] = None,
                       categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        生成多维度收支报表

        Args:
            db: 数据库会话
            time_dimension: 时间维度，可选值：daily, weekly, monthly, quarterly, custom
            start: 自定义开始日期，格式YYYY-MM-DD
            end: 自定义结束日期，格式YYYY-MM-DD
            categories: 筛选分类列表

        Returns:
            报表数据，包含收入、支出、结余、分类统计等
        """
        # 获取日期范围
        start_date, end_date, desc = ReportService._get_date_range(time_dimension, start, end)

        # 查询交易
        query = db.query(Transaction).filter(
            and_(Transaction.created_at >= start_date, Transaction.created_at <= end_date)
        )
        
        # 分类筛选
        if categories:
            valid_categories = [c.strip() for c in categories if c.strip()]
            if valid_categories:
                query = query.filter(Transaction.category.in_(valid_categories))

        transactions = query.all()

        # 计算总收入和支出
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expense = -sum(t.amount for t in transactions if t.amount < 0)
        balance = total_income - total_expense

        # 按分类统计
        category_stats = {}
        for transaction in transactions:
            if transaction.category not in category_stats:
                category_stats[transaction.category] = {
                    "income": 0,
                    "expense": 0,
                    "count": 0
                }
            
            if transaction.amount > 0:
                category_stats[transaction.category]["income"] += transaction.amount
            else:
                category_stats[transaction.category]["expense"] += -transaction.amount
            category_stats[transaction.category]["count"] += 1

        # 计算分类占比
        for category, stats in category_stats.items():
            if total_income > 0:
                stats["income_percentage"] = (stats["income"] / total_income) * 100
            else:
                stats["income_percentage"] = 0
            if total_expense > 0:
                stats["expense_percentage"] = (stats["expense"] / total_expense) * 100
            else:
                stats["expense_percentage"] = 0

        # 计算环比数据
        base_start, base_end = ReportService.get_base_period(time_dimension, start_date, end_date)
        base_income = 0
        base_expense = 0
        base_balance = 0
        comparison_data = None
        
        if base_start and base_end:
            # 基准周期确保为datetime对象
            from datetime import date
            if isinstance(base_start, date):
                base_start = datetime.combine(base_start, datetime.min.time())
                base_end = datetime.combine(base_end, datetime.max.time())
            base_transactions = db.query(Transaction).filter(
                and_(Transaction.created_at >= base_start, Transaction.created_at <= base_end)
            )
            
            if categories:
                valid_categories = [c.strip() for c in categories if c.strip()]
                if valid_categories:
                    base_transactions = base_transactions.filter(Transaction.category.in_(valid_categories))
                    
            base_transactions = base_transactions.all()
            base_income = sum(t.amount for t in base_transactions if t.amount > 0)
            base_expense = -sum(t.amount for t in base_transactions if t.amount < 0)
            base_balance = base_income - base_expense

        # 计算环比变化率
        income_change = 0
        expense_change = 0
        balance_change = 0
        
        if base_start and base_end:
            income_change = round(((total_income - base_income) / base_income * 100), 2) if base_income != 0 else 0
            expense_change = round(((total_expense - base_expense) / base_expense * 100), 2) if base_expense != 0 else 0
            balance_change = round(((balance - base_balance) / base_balance * 100), 2) if base_balance != 0 else 0
            
            comparison_data = {
                "period": f"{base_start.strftime('%Y-%m-%d')} ~ {base_end.strftime('%Y-%m-%d')}" if time_dimension == "custom" else base_start.strftime("%Y-%m" if time_dimension == "monthly" else "%Y-%W" if time_dimension == "weekly" else "%Y-%m-%d"),
                "total_income": round(base_income, 2),
                "total_expense": round(base_expense, 2),
                "balance": round(base_balance, 2),
                "income_change": income_change,
                "expense_change": expense_change,
                "balance_change": balance_change
            }

        # 构建返回结果
        result = {
            "period": f"{start_date.strftime('%Y-%m-%d')}" if time_dimension == "daily" else f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}" if time_dimension == "custom" else start_date.strftime("%Y-%m" if time_dimension == "monthly" else "%Y-%W" if time_dimension == "weekly" else "%Y-Q%q" if time_dimension == "quarterly" else desc),
            "time_dimension": time_dimension,
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "balance": round(balance, 2),
            "transaction_count": len(transactions),
            "category_stats": category_stats,
            "has_data": len(transactions) > 0
        }
        
        # 添加环比数据（如果有基准周期）
        if 'comparison_data' in locals() and comparison_data:
            result["comparison"] = comparison_data
            
        return result
    
    @staticmethod
    def generate_monthly_report(db: Session, month: Optional[str] = None) -> Dict[str, Any]:
        """
        生成月度收支报表（兼容旧接口）

        Args:
            db: 数据库会话
            month: 月份，格式：YYYY-MM，默认为当前月

        Returns:
            报表数据，包含收入、支出、结余、分类统计等
        """
        if month:
            try:
                datetime.strptime(month, "%Y-%m")
            except ValueError:
                raise ValueError("月份格式应为YYYY-MM")
            start_date_str = f"{month}-01"
            report_data = ReportService.generate_report(db, "monthly", start=start_date_str)
        else:
            report_data = ReportService.generate_report(db, "monthly")
        
        # 兼容旧接口格式
        report_data["month"] = report_data["period"]
        return report_data

    @staticmethod
    def format_report(report_data: Dict[str, Any], format_type: str = "text", fields: Optional[List[str]] = None) -> str:
        """
        格式化报表输出

        Args:
            report_data: 报表数据
            format_type: 输出格式，text 或 markdown
            fields: 指定展示字段列表

        Returns:
            格式化后的报表字符串
        """
        # 默认展示所有字段
        default_fields = ["金额", "分类", "日期"]
        display_fields = fields if fields and len(fields) > 0 else default_fields
        
        if not report_data["has_data"]:
            period = report_data.get("period", report_data.get("month", "未知时间段"))
            if format_type == "markdown":
                return f"# {period} 收支报表\n\n暂无数据"
            else:
                return f"{period} 收支报表\n\n暂无数据"

        if format_type == "markdown":
            return ReportService._format_report_markdown(report_data, display_fields)
        else:
            return ReportService._format_report_text(report_data, display_fields)

    @staticmethod
    def _format_report_text(report_data: Dict[str, Any], display_fields: List[str]) -> str:
        """格式化为文本格式"""
        lines = []
        period = report_data.get("period", report_data.get("month", "未知时间段"))
        lines.append(f"{period} 收支报表")
        lines.append("=" * 70)
        
        # 基础信息
        lines.append(f"总收入: {report_data['total_income']:.2f}")
        if report_data.get("base_income", 0) != 0:
            change_sign = "+" if report_data["income_change"] >= 0 else ""
            lines.append(f"  环比: {change_sign}{report_data['income_change']:.2f}% (上期: {report_data['base_income']:.2f})")
        
        lines.append(f"总支出: {report_data['total_expense']:.2f}")
        if report_data.get("base_expense", 0) != 0:
            change_sign = "+" if report_data["expense_change"] >= 0 else ""
            lines.append(f"  环比: {change_sign}{report_data['expense_change']:.2f}% (上期: {report_data['base_expense']:.2f})")
        
        lines.append(f"结余: {report_data['balance']:.2f}")
        if report_data.get("base_balance", 0) != 0:
            change_sign = "+" if report_data["balance_change"] >= 0 else ""
            lines.append(f"  环比: {change_sign}{report_data['balance_change']:.2f}% (上期: {report_data['base_balance']:.2f})")
        
        lines.append(f"交易笔数: {report_data['transaction_count']}")
        lines.append(f"对比周期: {report_data.get('base_period', '无')}")
        
        lines.append("\n分类统计:")
        lines.append("-" * 70)

        for category, stats in sorted(
            report_data["category_stats"].items(),
            key=lambda x: x[1]["income"] + x[1]["expense"],
            reverse=True
        ):
            total = stats["income"] + stats["expense"]
            lines.append(f"{category}:")
            
            if "金额" in display_fields:
                lines.append(f"  收入: {stats['income']:.2f} ({stats['income_percentage']:.1f}%)")
                lines.append(f"  支出: {stats['expense']:.2f} ({stats['expense_percentage']:.1f}%)")
                lines.append(f"  总金额: {total:.2f}")
            if "笔数" in display_fields or "count" in display_fields:
                lines.append(f"  笔数: {stats['count']}")
            
            lines.append("-" * 70)

        return "\n".join(lines)

    @staticmethod
    def _format_report_markdown(report_data: Dict[str, Any], display_fields: List[str]) -> str:
        """格式化为Markdown格式"""
        lines = []
        period = report_data.get("period", report_data.get("month", "未知时间段"))
        lines.append(f"# {period} 收支报表")
        lines.append("")
        
        # 汇总信息
        lines.append("## 汇总信息")
        lines.append("| 项目 | 当前周期 | 上期同期 | 环比变化 |")
        lines.append("|-----|--------|--------|--------|")
        
        income_change = f"{report_data['income_change']:.2f}%" if report_data.get('base_income', 0) != 0 else "-"
        lines.append(f"| 总收入 | {report_data['total_income']:.2f} | {report_data.get('base_income', 0):.2f} | {income_change} |")
        
        expense_change = f"{report_data['expense_change']:.2f}%" if report_data.get('base_expense', 0) != 0 else "-"
        lines.append(f"| 总支出 | {report_data['total_expense']:.2f} | {report_data.get('base_expense', 0):.2f} | {expense_change} |")
        
        balance_change = f"{report_data['balance_change']:.2f}%" if report_data.get('base_balance', 0) != 0 else "-"
        lines.append(f"| 结余 | {report_data['balance']:.2f} | {report_data.get('base_balance', 0):.2f} | {balance_change} |")
        
        lines.append(f"| 交易笔数 | {report_data['transaction_count']} | - | - |")
        lines.append(f"| 对比周期 | {report_data.get('base_period', '无')} | - | - |")
        lines.append("")

        # 分类统计
        lines.append("## 分类统计")
        
        # 动态构建表格列
        table_headers = ["分类"]
        if "金额" in display_fields:
            table_headers.extend(["收入", "收入占比", "支出", "支出占比", "总金额"])
        if "笔数" in display_fields or "count" in display_fields:
            table_headers.append("笔数")
        
        header_line = "| " + " | ".join(table_headers) + " |"
        separator_line = "| " + " | ".join(["-----" for _ in table_headers]) + " |"
        
        lines.append(header_line)
        lines.append(separator_line)

        for category, stats in sorted(
            report_data["category_stats"].items(),
            key=lambda x: x[1]["income"] + x[1]["expense"],
            reverse=True
        ):
            total = stats["income"] + stats["expense"]
            row = [category]
            
            if "金额" in display_fields:
                row.extend([
                    f"{stats['income']:.2f}",
                    f"{stats['income_percentage']:.1f}%",
                    f"{stats['expense']:.2f}",
                    f"{stats['expense_percentage']:.1f}%",
                    f"{total:.2f}"
                ])
            if "笔数" in display_fields or "count" in display_fields:
                row.append(f"{stats['count']}")
            
            lines.append("| " + " | ".join(row) + " |")

        return "\n".join(lines)
