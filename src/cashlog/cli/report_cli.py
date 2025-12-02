"""报表相关命令行接口"""
import click
from typing import Optional, List
from cashlog.models.db import get_db, init_db
from cashlog.services.report_service import ReportService
from cashlog.utils.formatter import Formatter


@click.group()
def report():
    """报表管理命令组"""
    pass


def validate_categories(ctx, param, value):
    """验证分类参数"""
    if not value:
        return None
    categories = [c.strip() for c in value.split(",") if c.strip()]
    return categories if categories else None


def validate_fields(ctx, param, value):
    """验证展示字段参数"""
    if not value:
        return None
    valid_fields = ["金额", "分类", "待办 ID", "日期", "交易描述"]
    fields = [f.strip() for f in value.split(",") if f.strip()]
    
    # 验证字段有效性
    invalid_fields = [f for f in fields if f not in valid_fields]
    if invalid_fields:
        raise click.BadParameter(f"无效字段: {', '.join(invalid_fields)}，有效字段为: {', '.join(valid_fields)}")
    
    return fields if fields else None


@report.command()
@click.option("--daily", "time_dimension", flag_value="daily", help="按日维度生成报表")
@click.option("--weekly", "time_dimension", flag_value="weekly", help="按周维度生成报表")
@click.option("--quarterly", "time_dimension", flag_value="quarterly", help="按季度维度生成报表")
@click.option("--monthly", "time_dimension", flag_value="monthly", default=True, help="按月度维度生成报表（默认）")
@click.option("--start", help="自定义开始日期，格式：YYYY-MM-DD")
@click.option("--end", help="自定义结束日期，格式：YYYY-MM-DD")
@click.option("--category", callback=validate_categories, help="分类筛选，支持多分类英文逗号分隔")
@click.option("--fields", callback=validate_fields, help="指定展示字段，可选值：金额，分类，待办 ID, 日期，交易描述，英文逗号分隔")
@click.option("--format", type=click.Choice(["text", "markdown"]), default="text", help="输出格式，默认为text")
def generate(time_dimension: str, start: Optional[str], end: Optional[str], category: Optional[List[str]], fields: Optional[List[str]], format: str):
    """
    生成多维度收支报表
    
    示例:
    cashlog report generate --daily  # 生成今日报表
    cashlog report generate --weekly  # 生成本周报表
    cashlog report generate --quarterly  # 生成本季度报表
    cashlog report generate --start 2023-10-01 --end 2023-10-31  # 生成自定义区间报表
    cashlog report generate --category 餐饮,交通  # 筛选餐饮和交通分类
    cashlog report generate --fields 金额,分类,笔数  # 指定展示字段
    """
    init_db()  # 确保数据库已初始化
    
    try:
        db = next(get_db())
        
        # 如果指定了start或end，则使用自定义维度
        if start or end:
            time_dimension = "custom"
        
        report_data = ReportService.generate_report(db, time_dimension, start, end, category)
        formatted_report = ReportService.format_report(report_data, format, fields)
        
        if not report_data["has_data"]:
            period = report_data.get("period", "当前时间段")
            Formatter.print_info(f"{period} 暂无交易数据")
        
        # 打印报表
        from rich.console import Console
        console = Console()
        console.print(formatted_report)
        
    except ValueError as e:
        Formatter.print_error(str(e))
    except Exception as e:
        Formatter.print_error(f"生成报表失败: {str(e)}")


@report.command()
@click.option("-m", "--month", help="月份，格式：YYYY-MM，默认为当前月")
@click.option("--format", type=click.Choice(["text", "markdown"]), default="text", help="输出格式，默认为text")
def monthly(month: Optional[str], format: str):
    """
    生成月度收支报表（兼容旧接口）
    
    示例:
    cashlog report monthly  # 生成当前月报表
    cashlog report monthly -m 2023-10  # 生成指定月份报表
    """
    init_db()  # 确保数据库已初始化
    
    try:
        db = next(get_db())
        report_data = ReportService.generate_monthly_report(db, month)
        formatted_report = ReportService.format_report(report_data, format)
        
        if not report_data["has_data"]:
            Formatter.print_info(f"{month or '当前月'} 暂无交易数据")
        
        # 打印报表
        from rich.console import Console
        console = Console()
        console.print(formatted_report)
        
    except ValueError as e:
        Formatter.print_error(str(e))
    except Exception as e:
        Formatter.print_error(f"生成报表失败: {str(e)}")
