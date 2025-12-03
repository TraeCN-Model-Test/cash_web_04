"""报表服务单元测试"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cashlog.models.db import Base
from cashlog.services.transaction_service import TransactionService
from cashlog.services.report_service import ReportService

# 使用内存数据库进行测试
TEST_DATABASE_URL = "sqlite:///:memory:"


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


@pytest.fixture
def sample_transactions(db_session):
    """创建测试数据"""
    # 2023-12月份交易
    TransactionService.create_transaction(db_session, {
        "amount": "5000.00",
        "category": "工资",
        "created_at": "2023-12-01 10:00:00"
    })
    TransactionService.create_transaction(db_session, {
        "amount": "1000.00",
        "category": "奖金",
        "created_at": "2023-12-15 10:00:00"
    })
    TransactionService.create_transaction(db_session, {
        "amount": "-1000.00",
        "category": "餐饮",
        "created_at": "2023-12-05 12:00:00"
    })
    TransactionService.create_transaction(db_session, {
        "amount": "-500.00",
        "category": "交通",
        "created_at": "2023-12-10 08:00:00"
    })
    TransactionService.create_transaction(db_session, {
        "amount": "-2000.00",
        "category": "购物",
        "created_at": "2023-12-20 14:00:00"
    })
    
    # 2023-11月份交易
    TransactionService.create_transaction(db_session, {
        "amount": "4500.00",
        "category": "工资",
        "created_at": "2023-11-01 10:00:00"
    })


def test_generate_monthly_report(sample_transactions, db_session):
    """测试生成月度报表"""
    report_data = ReportService.generate_monthly_report(db_session, "2023-12")
    
    # 验证汇总数据
    assert report_data["month"] == "2023-12"
    assert report_data["total_income"] == 6000.00  # 5000 + 1000
    assert report_data["total_expense"] == 3500.00  # 1000 + 500 + 2000
    assert report_data["balance"] == 2500.00  # 6000 - 3500
    assert report_data["transaction_count"] == 5
    assert report_data["has_data"] is True
    
    # 验证分类统计
    category_stats = report_data["category_stats"]
    assert "工资" in category_stats
    assert "奖金" in category_stats
    assert "餐饮" in category_stats
    assert "交通" in category_stats
    assert "购物" in category_stats
    
    # 验证分类金额
    assert category_stats["工资"]["income"] == 5000.00
    assert category_stats["奖金"]["income"] == 1000.00
    assert category_stats["餐饮"]["expense"] == 1000.00
    assert category_stats["交通"]["expense"] == 500.00
    assert category_stats["购物"]["expense"] == 2000.00
    
    # 验证分类占比（使用近似比较避免浮点数精度问题）
    assert abs(category_stats["工资"]["income_percentage"] - 83.33333333333334) < 1e-9  # 5000/6000*100
    assert abs(category_stats["奖金"]["income_percentage"] - 16.666666666666664) < 1e-9  # 1000/6000*100
    assert abs(category_stats["餐饮"]["expense_percentage"] - 28.571428571428573) < 1e-9  # 1000/3500*100
    assert abs(category_stats["交通"]["expense_percentage"] - 14.285714285714285) < 1e-9  # 500/3500*100
    assert abs(category_stats["购物"]["expense_percentage"] - 57.14285714285714) < 1e-9  # 2000/3500*100


def test_generate_monthly_report_no_data(db_session):
    """测试生成无数据的月度报表"""
    report_data = ReportService.generate_monthly_report(db_session, "2023-10")
    
    assert report_data["month"] == "2023-10"
    assert report_data["total_income"] == 0
    assert report_data["total_expense"] == 0
    assert report_data["balance"] == 0
    assert report_data["category_stats"] == {}
    assert report_data["has_data"] is False


def test_generate_monthly_report_without_month_parameter(db_session):
    """测试不指定月份参数时的报表生成"""
    # 创建一些交易数据
    TransactionService.create_transaction(db_session, {
        "amount": "5000.00",
        "category": "工资",
        "created_at": "2023-12-01 10:00:00"
    })
    
    # 不指定月份参数，将使用当前月份（但我们不验证具体月份值，只验证功能正常）
    try:
        report_data = ReportService.generate_monthly_report(db_session)
        # 验证返回的数据结构正确
        assert "month" in report_data
        assert "total_income" in report_data
        assert "total_expense" in report_data
        assert "balance" in report_data
        assert "category_stats" in report_data
        assert "has_data" in report_data
    except Exception as e:
        # 如果出现任何异常，测试失败
        assert False, f"调用generate_monthly_report()时出错: {str(e)}"


def test_generate_monthly_report_invalid_month(db_session):
    """测试无效的月份格式"""
    with pytest.raises(ValueError, match="月份格式应为YYYY-MM"):
        ReportService.generate_monthly_report(db_session, "202312")
    
    with pytest.raises(ValueError, match="月份格式应为YYYY-MM"):
        ReportService.generate_monthly_report(db_session, "2023/12")


def test_format_report_text(sample_transactions, db_session):
    """测试文本格式报表"""
    report_data = ReportService.generate_monthly_report(db_session, "2023-12")
    text_report = ReportService.format_report(report_data, "text")
    
    # 验证文本报表包含关键信息
    assert "2023-12 收支报表" in text_report
    assert "总收入: 6000.00" in text_report
    assert "总支出: 3500.00" in text_report
    assert "结余: 2500.00" in text_report
    assert "工资:" in text_report
    assert "餐饮:" in text_report


def test_format_report_markdown(sample_transactions, db_session):
    """测试Markdown格式报表"""
    report_data = ReportService.generate_monthly_report(db_session, "2023-12")
    markdown_report = ReportService.format_report(report_data, "markdown")
    
    # 验证Markdown报表包含关键信息
    assert "# 2023-12 收支报表" in markdown_report
    assert "| 总收入 | 6000.00 |" in markdown_report
    assert "| 总支出 | 3500.00 |" in markdown_report
    assert "| 结余 | 2500.00 |" in markdown_report
    assert "| 工资 |" in markdown_report
    assert "| 餐饮 |" in markdown_report


def test_format_report_no_data_text(db_session):
    """测试无数据文本格式报表"""
    report_data = ReportService.generate_monthly_report(db_session, "2023-10")
    text_report = ReportService.format_report(report_data, "text")
    
    assert "2023-10 收支报表" in text_report
    assert "暂无数据" in text_report


def test_format_report_no_data_markdown(db_session):
    """测试无数据Markdown格式报表"""
    report_data = ReportService.generate_monthly_report(db_session, "2023-10")
    markdown_report = ReportService.format_report(report_data, "markdown")
    
    assert "# 2023-10 收支报表" in markdown_report
    assert "暂无数据" in markdown_report


def test_generate_report_daily(sample_transactions, db_session):
    """测试按日维度生成报表"""
    report_data = ReportService.generate_report(db_session, "daily", "2023-12-01", "2023-12-01")
    
    assert report_data["period"] == "2023-12-01"
    assert report_data["time_dimension"] == "daily"
    assert report_data["total_income"] == 5000.00  # 12月1日的工资
    assert report_data["total_expense"] == 0
    assert report_data["balance"] == 5000.00
    assert report_data["has_data"] is True


def test_generate_report_weekly(sample_transactions, db_session):
    """测试按周维度生成报表"""
    report_data = ReportService.generate_report(db_session, "custom", "2023-12-04", "2023-12-10")
    
    assert report_data["time_dimension"] == "custom"
    assert report_data["total_income"] == 0
    assert report_data["total_expense"] == 1500.00  # 餐饮1000 + 交通500
    assert report_data["balance"] == -1500.00
    assert report_data["has_data"] is True


def test_generate_report_category_filter(sample_transactions, db_session):
    """测试分类筛选功能"""
    report_data = ReportService.generate_report(db_session, "monthly", "2023-12-01", "2023-12-31", ["餐饮", "交通"])
    
    assert report_data["total_income"] == 0
    assert report_data["total_expense"] == 1500.00  # 餐饮1000 + 交通500
    assert len(report_data["category_stats"]) == 2
    assert "餐饮" in report_data["category_stats"]
    assert "交通" in report_data["category_stats"]


def test_generate_report_custom_interval(sample_transactions, db_session):
    """测试自定义时间区间"""
    report_data = ReportService.generate_report(db_session, "custom", "2023-12-01", "2023-12-15")
    
    assert report_data["time_dimension"] == "custom"
    assert report_data["total_income"] == 6000.00  # 工资5000 + 奖金1000
    assert report_data["total_expense"] == 1500.00  # 餐饮1000 + 交通500
    assert report_data["balance"] == 4500.00


def test_generate_report_missing_end_date(db_session):
    """测试缺少结束日期的自定义区间"""
    with pytest.raises(ValueError, match="自定义区间必须同时提供开始和结束日期"):
        ReportService.generate_report(db_session, "custom", "2023-12-01", None)


def test_generate_report_invalid_date_order(db_session):
    """测试结束日期早于开始日期的情况"""
    with pytest.raises(ValueError, match="结束日期必须晚于开始日期"):
        ReportService.generate_report(db_session, "custom", "2023-12-31", "2023-12-01")


def test_generate_report_comparison(sample_transactions, db_session):
    """测试环比计算功能"""
    report_data = ReportService.generate_report(db_session, "monthly", "2023-12-01", "2023-12-31")
    
    assert "comparison" in report_data
    assert report_data["comparison"] is not None
    assert report_data["comparison"]["period"] == "2023-11"
    assert report_data["comparison"]["total_income"] == 4500.00  # 11月工资
    assert report_data["comparison"]["income_change"] == 33.33  # (6000-4500)/4500*100


def test_format_report_with_custom_fields(sample_transactions, db_session):
    """测试自定义字段展示功能"""
    report_data = ReportService.generate_report(db_session, "monthly", "2023-12-01", "2023-12-31")
    text_report = ReportService.format_report(report_data, "text", ["金额", "分类"])
    
    assert "总收入: 6000.00" in text_report
    assert "总支出: 3500.00" in text_report
    assert "工资:" in text_report
    assert "餐饮:" in text_report
    assert "交易描述" not in text_report
    assert "待办 ID" not in text_report
