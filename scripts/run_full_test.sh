#!/bin/zsh

# 完整功能测试脚本
set -e
  
echo "==================================="
echo "开始执行完整功能测试"
echo "==================================="
echo ""

# 1. 运行报表服务单元测试
echo "1. 运行报表服务单元测试..."
uv run pytest tests/test_report_service.py -v
if [ $? -ne 0 ]; then
    echo "报表服务单元测试失败！"
    exit 1
fi
echo "单元测试全部通过 ✅"
echo ""

# 初始化数据库
echo "初始化数据库表结构..."
uv run python -c "
from cashlog.models.db import init_db
init_db()
"
echo "数据库初始化完成 ✅"
echo ""

# 2. 测试报表服务各个功能
echo "2. 测试报表服务功能..."

# 测试月度报表
echo "  测试月度报表生成..."
uv run python -c "
from cashlog.services.report_service import ReportService
from cashlog.models.db import get_db
db_generator = get_db()
db_session = next(db_generator)
try:
    report = ReportService.generate_monthly_report(db_session)
    print('    月度报表生成成功: {}，总收入: {}'.format(report['period'], report['total_income']))
finally:
    db_session.close()
"

# 测试日报表
echo "  测试日报表生成..."
uv run python -c "
from cashlog.services.report_service import ReportService
from cashlog.models.db import get_db
db_generator = get_db()
db_session = next(db_generator)
try:
    report = ReportService.generate_report(db_session, time_dimension='daily')
    print('    日报表生成成功: {}，总收入: {}'.format(report['period'], report['total_income']))
finally:
    db_session.close()
"

# 测试周报表
echo "  测试周报表生成..."
uv run python -c "
from cashlog.services.report_service import ReportService
from cashlog.models.db import get_db
db_generator = get_db()
db_session = next(db_generator)
try:
    report = ReportService.generate_report(db_session, time_dimension='weekly')
    print('    周报表生成成功: {}，总收入: {}'.format(report['period'], report['total_income']))
finally:
    db_session.close()
"

# 测试季度报表
echo "  测试季度报表生成..."
uv run python -c "
from cashlog.services.report_service import ReportService
from cashlog.models.db import get_db
db_generator = get_db()
db_session = next(db_generator)
try:
    report = ReportService.generate_report(db_session, time_dimension='quarterly')
    print('    季度报表生成成功: {}，总收入: {}'.format(report['period'], report['total_income']))
finally:
    db_session.close()
"

# 测试分类筛选
echo "  测试分类筛选功能..."
uv run python -c "
from cashlog.services.report_service import ReportService
from cashlog.models.db import get_db
db_generator = get_db()
db_session = next(db_generator)
try:
    report = ReportService.generate_report(db_session, time_dimension='daily', categories=['餐饮'])
    print('    分类筛选报表生成成功，分类统计数量: {}'.format(len(report['category_stats'])))
finally:
    db_session.close()
"

# 测试自定义字段
echo "  测试自定义字段功能..."
uv run python -c "
from cashlog.services.report_service import ReportService
from cashlog.models.db import get_db
db_generator = get_db()
db_session = next(db_generator)
try:
    report = ReportService.generate_report(db_session, time_dimension='daily')
    formatted_report = ReportService.format_report(report, fields=['total_income', 'total_expense', 'balance'])
    print('    自定义字段报表生成成功:')
    print('    {}'.format(formatted_report))
finally:
    db_session.close()
"

echo ""
echo "报表服务功能测试全部通过 ✅"
echo ""

# 3. 测试CLI命令
echo "3. 测试CLI命令..."

# 测试月度报表CLI
  echo "  测试月度报表CLI..."
  uv run python main.py report generate --monthly
echo ""

# 测试日报表CLI
  echo "  测试日报表CLI..."
  uv run python main.py report generate --daily

echo ""

# 测试周报表CLI
  echo "  测试周报表CLI..."
  uv run python main.py report generate --weekly

echo ""

# 测试季度报表CLI
  echo "  测试季度报表CLI..."
  uv run python main.py report generate --quarterly

echo ""
echo "=================================="
echo "所有功能测试完成！🎉"
echo "=================================="
