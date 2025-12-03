"""交易CLI命令单元测试"""
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cashlog.cli.transaction_cli import transaction
from tests.test_cli_utilities import CLITestBase


class TestTransactionCLI(CLITestBase):
    """交易CLI命令测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.runner = CliRunner()
    
    def test_add_transaction_success(self):
        """测试成功添加交易记录"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.transaction_service.TransactionService.create_transaction') as mock_create:
            
            # 模拟返回的交易对象
            mock_transaction = MagicMock()
            mock_transaction.id = 1
            mock_transaction.todo = None
            mock_create.return_value = mock_transaction
            
            # 执行CLI命令
            result = self.runner.invoke(transaction, ['add', '-a', '100.50', '-c', '工资'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '交易记录已添加 (ID: 1)' in result.output
            mock_create.assert_called_once()
    
    def test_add_transaction_with_todo_link(self):
        """测试添加交易记录并关联待办事项"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.transaction_service.TransactionService.create_transaction') as mock_create:
            
            # 模拟返回的交易对象
            mock_todo = MagicMock()
            mock_todo.id = 5
            mock_transaction = MagicMock()
            mock_transaction.id = 1
            mock_transaction.todo = mock_todo
            mock_create.return_value = mock_transaction
            
            # 执行CLI命令
            result = self.runner.invoke(transaction, ['add', '-a', '100.50', '-c', '工资', '--todo-id', '5'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '交易记录已添加 (ID: 1)，已关联待办事项ID: 5' in result.output
    
    def test_add_transaction_invalid_amount(self):
        """测试添加交易记录时金额格式错误"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.transaction_service.TransactionService.create_transaction') as mock_create:
            
            # 模拟抛出ValueError异常
            mock_create.side_effect = ValueError("金额需为数字")
            
            # 执行CLI命令
            result = self.runner.invoke(transaction, ['add', '-a', 'invalid', '-c', '工资'])
            
            # 验证结果
            assert result.exit_code == 0  # CLI命令本身成功执行，但内部逻辑报错
            assert '金额需为数字' in result.output
    
    def test_add_transaction_missing_required_fields(self):
        """测试添加交易记录缺少必填字段"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db:
            
            # 执行CLI命令，缺少必填的分类参数
            result = self.runner.invoke(transaction, ['add', '-a', '100.50'])
            
            # 验证结果
            assert result.exit_code != 0
            assert 'Missing option' in result.output and '-c' in result.output
    
    def test_list_transactions_success(self):
        """测试列出交易记录成功"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.transaction_service.TransactionService.get_transactions') as mock_get, \
             patch('cashlog.utils.formatter.Formatter.format_transactions') as mock_format:
            
            # 模拟返回的数据
            mock_get.return_value = []
            mock_format.return_value = []
            
            # 执行CLI命令
            result = self.runner.invoke(transaction, ['list'])
            
            # 验证结果
            assert result.exit_code == 0
            mock_get.assert_called_once()
            mock_format.assert_called_once()
    
    def test_list_transactions_with_filters(self):
        """测试带筛选条件列出交易记录"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.transaction_service.TransactionService.get_transactions') as mock_get, \
             patch('cashlog.utils.formatter.Formatter.format_transactions') as mock_format:
            
            # 模拟返回的数据
            mock_get.return_value = []
            mock_format.return_value = []
            
            # 执行CLI命令
            result = self.runner.invoke(transaction, ['list', '-m', '2023-10', '-c', '餐饮'])
            
            # 验证结果
            assert result.exit_code == 0
            mock_get.assert_called_once()
    
    def test_update_transaction_success(self):
        """测试成功更新交易记录"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.transaction_service.TransactionService.update_transaction') as mock_update:
            
            # 模拟返回的交易对象
            mock_transaction = MagicMock()
            mock_transaction.id = 1
            mock_transaction.todo = None
            mock_update.return_value = mock_transaction
            
            # 执行CLI命令
            result = self.runner.invoke(transaction, ['update', '1', '-a', '-60.00'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '交易记录(ID: 1)已更新' in result.output
            mock_update.assert_called_once()
    
    def test_update_transaction_invalid_id(self):
        """测试更新交易记录时ID格式错误"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db:
            
            # 执行CLI命令
            result = self.runner.invoke(transaction, ['update', 'abc', '-a', '-60.00'])
            
            # 验证结果
            assert result.exit_code == 0  # CLI命令本身成功执行，但内部逻辑报错
            assert '交易ID必须为数字' in result.output
    
    def test_update_transaction_no_fields(self):
        """测试更新交易记录时不指定任何字段"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db:
            
            # 执行CLI命令
            result = self.runner.invoke(transaction, ['update', '1'])
            
            # 验证结果
            assert result.exit_code == 0  # CLI命令本身成功执行，但内部逻辑报错
            assert '请指定至少一个要更新的字段' in result.output
    
    def test_unlink_transaction_success(self):
        """测试成功解除交易记录关联"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.transaction_service.TransactionService.remove_transaction_todo_link') as mock_unlink:
            
            # 模拟返回的交易对象
            mock_transaction = MagicMock()
            mock_transaction.id = 1
            mock_unlink.return_value = mock_transaction
            
            # 执行CLI命令
            result = self.runner.invoke(transaction, ['unlink', '1'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '交易记录(ID: 1)已解除待办事项关联' in result.output
            mock_unlink.assert_called_once()
            # 验证调用参数中的ID是否正确
            call_args = mock_unlink.call_args
            assert call_args[0][1] == 1  # 第二个参数是交易ID
    
    def test_unlink_transaction_invalid_id(self):
        """测试解除交易记录关联时ID格式错误"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db:
            
            # 执行CLI命令
            result = self.runner.invoke(transaction, ['unlink', 'abc'])
            
            # 验证结果
            assert result.exit_code == 0  # CLI命令本身成功执行，但内部逻辑报错
            assert '交易ID必须为数字' in result.output