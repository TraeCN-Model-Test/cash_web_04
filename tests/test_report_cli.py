"""报表CLI命令单元测试"""
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cashlog.cli.report_cli import report
from tests.test_cli_base import CLITestBase


class TestReportCLI(CLITestBase):
    """报表CLI命令测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.runner = CliRunner()
    
    def test_generate_report_daily_success(self):
        """测试成功生成日报表"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.report_service.ReportService.generate_report') as mock_generate, \
             patch('cashlog.services.report_service.ReportService.format_report') as mock_format:
            
            # 模拟返回的数据
            mock_generate.return_value = {"has_data": True, "period": "今日"}
            mock_format.return_value = "日报表"
            
            # 执行CLI命令
            result = self.runner.invoke(report, [
                'generate', 
                '--daily'
            ])
            
            # 验证结果
            assert result.exit_code == 0
            mock_generate.assert_called_once()
            mock_format.assert_called_once()
    
    def test_generate_report_weekly_success(self):
        """测试成功生成周报表"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.report_service.ReportService.generate_report') as mock_generate, \
             patch('cashlog.services.report_service.ReportService.format_report') as mock_format:
            
            # 模拟返回的数据
            mock_generate.return_value = {"has_data": True, "period": "本周"}
            mock_format.return_value = "周报表"
            
            # 执行CLI命令
            result = self.runner.invoke(report, [
                'generate', 
                '--weekly'
            ])
            
            # 验证结果
            assert result.exit_code == 0
            mock_generate.assert_called_once()
            mock_format.assert_called_once()
    
    def test_generate_report_monthly_success(self):
        """测试成功生成月度报表"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.report_service.ReportService.generate_report') as mock_generate, \
             patch('cashlog.services.report_service.ReportService.format_report') as mock_format:
            
            # 模拟返回的数据
            mock_generate.return_value = {"has_data": True, "period": "本月"}
            mock_format.return_value = "月度报表"
            
            # 执行CLI命令
            result = self.runner.invoke(report, [
                'generate', 
                '--monthly'
            ])
            
            # 验证结果
            assert result.exit_code == 0
            mock_generate.assert_called_once()
            mock_format.assert_called_once()
    
    def test_generate_report_quarterly_success(self):
        """测试成功生成季度报表"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.report_service.ReportService.generate_report') as mock_generate, \
             patch('cashlog.services.report_service.ReportService.format_report') as mock_format:
            
            # 模拟返回的数据
            mock_generate.return_value = {"has_data": True, "period": "本季度"}
            mock_format.return_value = "季度报表"
            
            # 执行CLI命令
            result = self.runner.invoke(report, [
                'generate', 
                '--quarterly'
            ])
            
            # 验证结果
            assert result.exit_code == 0
            mock_generate.assert_called_once()
            mock_format.assert_called_once()
    
    def test_generate_report_custom_success(self):
        """测试成功生成自定义时间段报表"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.report_service.ReportService.generate_report') as mock_generate, \
             patch('cashlog.services.report_service.ReportService.format_report') as mock_format:
            
            # 模拟返回的数据
            mock_generate.return_value = {"has_data": True, "period": "自定义时间段"}
            mock_format.return_value = "自定义时间段报表"
            
            # 执行CLI命令
            result = self.runner.invoke(report, [
                'generate', 
                '--start', '2023-01-01',
                '--end', '2023-01-31'
            ])
            
            # 验证结果
            assert result.exit_code == 0
            mock_generate.assert_called_once()
            mock_format.assert_called_once()
    
    def test_generate_report_with_category_filter(self):
        """测试生成带分类筛选的报表"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.report_service.ReportService.generate_report') as mock_generate, \
             patch('cashlog.services.report_service.ReportService.format_report') as mock_format:
            
            # 模拟返回的数据
            mock_generate.return_value = {"has_data": True, "period": "本月"}
            mock_format.return_value = "分类筛选报表"
            
            # 执行CLI命令
            result = self.runner.invoke(report, [
                'generate',
                '--category', '餐饮,交通'
            ])
            
            # 验证结果
            assert result.exit_code == 0
            mock_generate.assert_called_once()
            mock_format.assert_called_once()
    
    def test_generate_report_with_field_selection(self):
        """测试生成指定字段的报表"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.report_service.ReportService.generate_report') as mock_generate, \
             patch('cashlog.services.report_service.ReportService.format_report') as mock_format:
            
            # 模拟返回的数据
            mock_generate.return_value = {"has_data": True, "period": "本月"}
            mock_format.return_value = "字段选择报表"
            
            # 执行CLI命令
            result = self.runner.invoke(report, [
                'generate',
                '--fields', '金额,分类,日期'
            ])
            
            # 验证结果
            assert result.exit_code == 0
            mock_generate.assert_called_once()
            mock_format.assert_called_once()
    
    def test_generate_report_output_format_markdown(self):
        """测试生成Markdown格式的报表"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.report_service.ReportService.generate_report') as mock_generate, \
             patch('cashlog.services.report_service.ReportService.format_report') as mock_format:
            
            # 模拟返回的数据
            mock_generate.return_value = {"has_data": True, "period": "本月"}
            mock_format.return_value = "Markdown格式报表"
            
            # 执行CLI命令
            result = self.runner.invoke(report, [
                'generate',
                '--format', 'markdown'
            ])
            
            # 验证结果
            assert result.exit_code == 0
            mock_generate.assert_called_once()
            mock_format.assert_called_once()
    
    def test_generate_report_invalid_period(self):
        """测试生成报表时周期参数无效"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db:
            
            # 执行CLI命令 - 使用不存在的选项
            result = self.runner.invoke(report, ['generate', '--yearly'])
            
            # 验证结果
            assert result.exit_code != 0
            assert 'no such option' in result.output.lower()
    
    def test_generate_report_missing_start_date_for_custom(self):
        """测试生成自定义报表时缺少开始日期"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db:
            
            # 执行CLI命令 - 只有结束日期没有开始日期
            result = self.runner.invoke(report, [
                'generate',
                '--end', '2023-01-31'
            ])
            
            # 验证结果 - 这种情况下应该使用默认的月度报表
            assert result.exit_code == 0
    
    def test_generate_report_missing_end_date_for_custom(self):
        """测试生成自定义报表时缺少结束日期"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db:
            
            # 执行CLI命令 - 只有开始日期没有结束日期
            result = self.runner.invoke(report, [
                'generate',
                '--start', '2023-01-01'
            ])
            
            # 验证结果 - 这种情况下应该使用默认的月度报表
            assert result.exit_code == 0
    
    def test_generate_report_invalid_date_format(self):
        """测试生成报表时日期格式无效"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.report_service.ReportService.generate_report') as mock_generate:
            
            # 模拟服务抛出异常
            mock_generate.side_effect = ValueError("日期格式无效")
            
            # 执行CLI命令
            result = self.runner.invoke(report, [
                'generate',
                '--start', '2023/01/01',
                '--end', '2023-01-31'
            ])
            
            # 验证结果
            assert result.exit_code == 0
            assert '日期格式无效' in result.output
    
    def test_monthly_report_success(self):
        """测试成功生成月度报表（兼容旧接口）"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.report_service.ReportService.generate_monthly_report') as mock_generate, \
             patch('cashlog.services.report_service.ReportService.format_report') as mock_format, \
             patch('rich.console.Console.print') as mock_print:
            
            # 模拟返回的数据
            mock_generate.return_value = {"has_data": True, "period": "2023-01"}
            mock_format.return_value = "月度报表"
            
            # 执行CLI命令 - 使用-m选项指定月份
            result = self.runner.invoke(report, ['monthly', '-m', '2023-01'])
            
            # 验证结果
            assert result.exit_code == 0
            mock_generate.assert_called_once()
            mock_format.assert_called_once()
            mock_print.assert_called_once()
    
    def test_monthly_report_invalid_month_format(self):
        """测试月度报表时月份格式无效"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.report_service.ReportService.generate_monthly_report') as mock_generate, \
             patch('cashlog.utils.formatter.Formatter.print_error') as mock_print_error:
            
            # 模拟服务抛出异常
            mock_generate.side_effect = ValueError("月份格式应为YYYY-MM")
            
            # 执行CLI命令 - 使用-m选项指定月份
            result = self.runner.invoke(report, ['monthly', '-m', '2023-13'])
            
            # 验证结果 - CLI命令本身成功执行，但内部逻辑报错
            assert result.exit_code == 0
            mock_print_error.assert_called_once_with("月份格式应为YYYY-MM")
    
    def test_monthly_report_missing_month(self):
        """测试月度报表时缺少月份参数"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.report_service.ReportService.generate_monthly_report') as mock_generate, \
             patch('cashlog.services.report_service.ReportService.format_report') as mock_format, \
             patch('rich.console.Console.print') as mock_print:
            
            # 模拟返回的数据
            mock_generate.return_value = {"has_data": True, "period": "2023-12"}
            mock_format.return_value = "月度报表"
            
            # 执行CLI命令 - 不提供月份参数，应该使用当前月份
            result = self.runner.invoke(report, ['monthly'])
            
            # 验证结果 - 应该成功执行，使用当前月份
            assert result.exit_code == 0
            mock_generate.assert_called_once()
            mock_format.assert_called_once()
            mock_print.assert_called_once()