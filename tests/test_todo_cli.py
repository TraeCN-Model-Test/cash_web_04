"""待办事项CLI命令单元测试"""
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cashlog.cli.todo_cli import todo
from tests.test_cli_utilities import CLITestBase


class TestTodoCLI(CLITestBase):
    """待办事项CLI命令测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.runner = CliRunner()
    
    def test_add_todo_success(self):
        """测试成功添加待办事项"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.todo_service.TodoService.create_todo') as mock_create:
            
            # 模拟返回的待办对象
            mock_todo = MagicMock()
            mock_todo.id = 1
            mock_todo.transaction_id = None
            mock_create.return_value = mock_todo
            
            # 执行CLI命令
            result = self.runner.invoke(todo, ['add', '-c', '完成项目报告', '-C', '工作'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '待办事项已添加 (ID: 1)' in result.output
            mock_create.assert_called_once()
    
    def test_add_todo_with_transaction_link(self):
        """测试添加待办事项并关联交易"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.todo_service.TodoService.create_todo') as mock_create:
            
            # 模拟返回的待办对象
            mock_todo = MagicMock()
            mock_todo.id = 1
            mock_todo.transaction_id = 3
            mock_create.return_value = mock_todo
            
            # 执行CLI命令
            result = self.runner.invoke(todo, ['add', '-c', '购买生日礼物', '-C', '个人', '--transaction-id', '3'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '待办事项已添加 (ID: 1)，已关联交易ID: 3' in result.output
    
    def test_add_todo_missing_required_fields(self):
        """测试添加待办事项缺少必填字段"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db:
            
            # 执行CLI命令，缺少必填的内容参数
            result = self.runner.invoke(todo, ['add', '-C', '工作'])
            
            # 验证结果
            assert result.exit_code != 0
            assert 'Missing option' in result.output and '-c' in result.output
    
    def test_update_status_success(self):
        """测试成功更新待办事项状态"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.todo_service.TodoService.update_todo_status') as mock_update:
            
            # 模拟返回的待办对象
            mock_todo = MagicMock()
            mock_todo.id = 1
            mock_todo.status_text = '进行中'
            mock_update.return_value = mock_todo
            
            # 执行CLI命令
            result = self.runner.invoke(todo, ['update-status', '1', 'doing'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '待办事项(ID: 1)状态已更新为: 进行中' in result.output
            mock_update.assert_called_once()
            # 验证调用参数中的ID和状态是否正确
            call_args = mock_update.call_args
            assert call_args[0][1] == 1  # 第二个参数是待办事项ID
            assert call_args[0][2] == 'doing'  # 第三个参数是状态
    
    def test_update_status_invalid_id(self):
        """测试更新待办事项状态时ID格式错误"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db:
            
            # 执行CLI命令
            result = self.runner.invoke(todo, ['update-status', 'abc', 'doing'])
            
            # 验证结果
            assert result.exit_code == 0  # CLI命令本身成功执行，但内部逻辑报错
            assert '待办事项ID必须为数字' in result.output
    
    def test_update_status_invalid_status(self):
        """测试更新待办事项状态时状态值无效"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db:
            
            # 执行CLI命令
            result = self.runner.invoke(todo, ['update-status', '1', 'invalid'])
            
            # 验证结果
            assert result.exit_code != 0
            assert 'Invalid value' in result.output
    
    def test_update_todo_success(self):
        """测试成功更新待办事项信息"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.todo_service.TodoService.update_todo') as mock_update:
            
            # 模拟返回的待办对象
            mock_todo = MagicMock()
            mock_todo.id = 1
            mock_todo.transaction_id = None
            mock_update.return_value = mock_todo
            
            # 执行CLI命令
            result = self.runner.invoke(todo, ['update', '1', '-c', '完成项目终稿'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '待办事项(ID: 1)已更新' in result.output
            mock_update.assert_called_once()
    
    def test_update_todo_with_transaction_link(self):
        """测试更新待办事项并关联交易"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.todo_service.TodoService.update_todo') as mock_update:
            
            # 模拟返回的待办对象
            mock_todo = MagicMock()
            mock_todo.id = 1
            mock_todo.transaction_id = 3
            mock_update.return_value = mock_todo
            
            # 执行CLI命令
            result = self.runner.invoke(todo, ['update', '1', '--transaction-id', '3'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '待办事项(ID: 1)已更新，已关联交易ID: 3' in result.output
    
    def test_update_todo_unlink_transaction(self):
        """测试更新待办事项并解除交易关联"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.todo_service.TodoService.update_todo') as mock_update:
            
            # 模拟返回的待办对象
            mock_todo = MagicMock()
            mock_todo.id = 1
            mock_todo.transaction_id = None
            mock_update.return_value = mock_todo
            
            # 执行CLI命令
            result = self.runner.invoke(todo, ['update', '1', '--transaction-id', '0'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '待办事项(ID: 1)已更新，已解除交易关联' in result.output
    
    def test_update_todo_invalid_id(self):
        """测试更新待办事项时ID格式错误"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db:
            
            # 执行CLI命令
            result = self.runner.invoke(todo, ['update', 'abc', '-c', '完成项目终稿'])
            
            # 验证结果
            assert result.exit_code == 0  # CLI命令本身成功执行，但内部逻辑报错
            assert '待办事项ID必须为数字' in result.output
    
    def test_update_todo_no_fields(self):
        """测试更新待办事项时不指定任何字段"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db:
            
            # 执行CLI命令
            result = self.runner.invoke(todo, ['update', '1'])
            
            # 验证结果
            assert result.exit_code == 0  # CLI命令本身成功执行，但内部逻辑报错
            assert '请指定至少一个要更新的字段' in result.output
    
    def test_unlink_todo_success(self):
        """测试成功解除待办事项关联"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.todo_service.TodoService.remove_todo_transaction_link') as mock_unlink:
            
            # 模拟返回的待办对象
            mock_todo = MagicMock()
            mock_todo.id = 1
            mock_unlink.return_value = mock_todo
            
            # 执行CLI命令
            result = self.runner.invoke(todo, ['unlink', '1'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '待办事项(ID: 1)已解除交易关联' in result.output
            mock_unlink.assert_called_once()
            # 验证调用参数中的ID是否正确
            call_args = mock_unlink.call_args
            assert call_args[0][1] == 1  # 第二个参数是待办事项ID
    
    def test_unlink_todo_invalid_id(self):
        """测试解除待办事项关联时ID格式错误"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db:
            
            # 执行CLI命令
            result = self.runner.invoke(todo, ['unlink', 'abc'])
            
            # 验证结果
            assert result.exit_code == 0  # CLI命令本身成功执行，但内部逻辑报错
            assert '待办事项ID必须为数字' in result.output
    
    def test_list_todos_success(self):
        """测试列出待办事项成功"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.todo_service.TodoService.get_todos') as mock_get, \
             patch('cashlog.utils.formatter.Formatter.format_todos') as mock_format:
            
            # 模拟返回的数据
            mock_get.return_value = []
            mock_format.return_value = []
            
            # 执行CLI命令
            result = self.runner.invoke(todo, ['list'])
            
            # 验证结果
            assert result.exit_code == 0
            mock_get.assert_called_once()
            mock_format.assert_called_once()
    
    def test_list_todos_with_filters(self):
        """测试带筛选条件列出待办事项"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db, \
             patch('cashlog.services.todo_service.TodoService.get_todos') as mock_get, \
             patch('cashlog.utils.formatter.Formatter.format_todos') as mock_format:
            
            # 模拟返回的数据
            mock_get.return_value = []
            mock_format.return_value = []
            
            # 执行CLI命令
            result = self.runner.invoke(todo, ['list', '-s', 'todo', '-c', '工作'])
            
            # 验证结果
            assert result.exit_code == 0
            mock_get.assert_called_once()