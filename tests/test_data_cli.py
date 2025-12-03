"""数据管理CLI命令单元测试"""
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cashlog.cli.data_cli import data
from tests.test_cli_base import CLITestBase


class TestDataCLI(CLITestBase):
    """数据管理CLI命令测试类"""
    
    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.runner = CliRunner()
    
    def test_backup_success_default_path(self):
        """测试备份成功（默认路径）"""
        with self.mock_db_dependency() as mock_get_db, \
             patch('cashlog.models.db.init_db') as mock_init_db, \
             patch('cashlog.services.data_service.DataService.create_backup') as mock_backup:
            
            # 模拟备份成功
            mock_backup.return_value = "/path/to/backup.db"
            
            # 执行CLI命令
            result = self.runner.invoke(data, ['backup'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '数据库备份成功' in result.output
            assert '备份文件' in result.output
            mock_backup.assert_called_once_with(output_path=None, overwrite=False)
    
    def test_backup_success_custom_path(self):
        """测试备份成功（自定义路径）"""
        with self.mock_db_dependency() as mock_get_db, \
             patch('cashlog.models.db.init_db') as mock_init_db, \
             patch('cashlog.services.data_service.DataService.create_backup') as mock_backup:
            
            # 模拟备份成功
            mock_backup.return_value = "/custom/path/backup.db"
            
            # 执行CLI命令
            result = self.runner.invoke(data, ['backup', '--output', '/custom/path/backup.db'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '数据库备份成功' in result.output
            assert '备份文件' in result.output
            mock_backup.assert_called_once_with(output_path='/custom/path/backup.db', overwrite=False)
    
    def test_backup_success_force_overwrite(self):
        """测试备份成功（强制覆盖）"""
        with self.mock_db_dependency() as mock_get_db, \
             patch('cashlog.models.db.init_db') as mock_init_db, \
             patch('cashlog.services.data_service.DataService.create_backup') as mock_backup:
            
            # 模拟备份成功
            mock_backup.return_value = "/custom/path/backup.db"
            
            # 执行CLI命令
            result = self.runner.invoke(data, ['backup', '--output', '/custom/path/backup.db', '--overwrite'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '数据库备份成功' in result.output
            assert '备份文件' in result.output
            mock_backup.assert_called_once_with(output_path='/custom/path/backup.db', overwrite=True)
    
    def test_backup_failure_invalid_path(self):
        """测试备份时路径无效"""
        with self.mock_db_dependency() as mock_get_db, \
             patch('cashlog.models.db.init_db') as mock_init_db, \
             patch('cashlog.services.data_service.DataService.create_backup') as mock_backup:
            
            # 模拟备份失败，抛出ValueError
            mock_backup.side_effect = ValueError("输出目录不存在")
            
            # 创建一个无效的路径（指向文件而不是目录）
            invalid_path = "/invalid/path/that/does/not/exist/backup.db"
            
            # 执行CLI命令
            result = self.runner.invoke(data, ['backup', '--output', invalid_path])
            
            # 验证结果
            assert result.exit_code != 0
            assert '备份失败' in result.output or '参数错误' in result.output
    
    def test_restore_success(self):
        """测试恢复数据库成功"""
        with self.mock_db_dependency() as mock_get_db, \
             patch('cashlog.models.db.init_db') as mock_init_db, \
             patch('cashlog.services.data_service.DataService.restore_backup') as mock_restore:
            
            # 模拟恢复成功
            mock_restore.return_value = {
                'restored_from': '/path/to/backup.db',
                'current_backup_path': None,
                'after_stats': {'tables': {'transactions': 10, 'todos': 5}}
            }
            
            # 执行CLI命令
            result = self.runner.invoke(data, ['restore', '--input', '/path/to/backup.db', '--confirm'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '数据库恢复成功' in result.output
            assert '恢复源' in result.output
    
    def test_restore_success_auto_backup(self):
        """测试恢复数据库成功（自动备份当前数据）"""
        with self.mock_db_dependency() as mock_get_db, \
             patch('cashlog.models.db.init_db') as mock_init_db, \
             patch('cashlog.services.data_service.DataService.restore_backup') as mock_restore:
            
            # 模拟恢复成功，返回包含自动备份路径的结果
            mock_restore.return_value = {
                'restored_from': '/path/to/backup.db',
                'current_backup_path': '/path/to/auto_backup.db',
                'after_stats': {'tables': {'transactions': 10, 'todos': 5}}
            }
            
            # 执行CLI命令（使用--confirm跳过交互确认，不指定--backup-current使用默认值True）
            result = self.runner.invoke(data, ['restore', '--input', '/path/to/backup.db', '--confirm'])
            
            # 验证结果
            assert result.exit_code == 0
            assert '数据库恢复成功' in result.output
            assert '恢复源' in result.output
            assert '当前数据备份' in result.output
    
    def test_restore_cancelled_by_user(self):
        """测试用户取消恢复"""
        with self.mock_db_dependency() as mock_get_db, \
             patch('cashlog.models.db.init_db') as mock_init_db, \
             patch('cashlog.services.data_service.DataService.restore_backup') as mock_restore:
            
            # 使用临时文件作为恢复源
            with tempfile.NamedTemporaryFile(suffix='.db') as temp_file:
                # 执行CLI命令，用户输入N取消
                result = self.runner.invoke(data, ['restore', '--input', temp_file.name], input='N\n')
                
                # 验证结果
                assert result.exit_code == 0
                assert '恢复操作已取消' in result.output
                mock_restore.assert_not_called()
    
    def test_restore_failure_invalid_source(self):
        """测试恢复数据库时源文件无效"""
        with self.mock_db_dependency() as mock_get_db, \
             patch('cashlog.models.db.init_db') as mock_init_db, \
             patch('cashlog.services.data_service.DataService.restore_backup') as mock_restore:
            
            # 模拟恢复失败，抛出FileNotFoundError
            mock_restore.side_effect = FileNotFoundError("备份文件不存在: /invalid/path/backup.db")
            
            # 执行CLI命令
            result = self.runner.invoke(data, ['restore', '--input', '/invalid/path/backup.db', '--confirm'])
            
            # 验证结果
            assert result.exit_code != 0
            assert '备份文件不存在' in result.output or '恢复失败' in result.output
    
    def test_restore_failure_source_not_db_file(self):
        """测试恢复数据库时源文件不是有效的SQLite数据库"""
        with self.mock_db_dependency() as mock_get_db, \
             patch('cashlog.models.db.init_db') as mock_init_db, \
             patch('cashlog.services.data_service.DataService.restore_backup') as mock_restore:
            
            # 模拟恢复失败，抛出ValueError
            mock_restore.side_effect = ValueError("无效的SQLite数据库文件")
            
            # 创建一个临时文件作为"无效"的数据库文件
            with tempfile.NamedTemporaryFile(suffix='.db') as temp_file:
                # 写入一些非SQLite内容
                temp_file.write(b"This is not a SQLite database file")
                temp_file.flush()
                
                # 执行CLI命令
                result = self.runner.invoke(data, ['restore', '--input', temp_file.name, '--confirm'])
                
                # 验证结果
                assert result.exit_code != 0
                assert '无效的SQLite数据库文件' in result.output or '恢复失败' in result.output
    
    def test_restore_missing_source(self):
        """测试恢复数据库时缺少源文件参数"""
        with self.mock_db_dependency() as mock_get_db, \
             self.mock_init_db() as mock_init_db:
            
            # 执行CLI命令
            result = self.runner.invoke(data, ['restore'])
            
            # 验证结果
            assert result.exit_code != 0
            assert 'Missing option' in result.output and '--input' in result.output