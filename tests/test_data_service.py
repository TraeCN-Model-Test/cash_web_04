"""数据服务单元测试"""
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open
from cashlog.services.data_service import DataService
from cashlog.models.db import DB_PATH


class TestDataService(unittest.TestCase):
    """数据服务测试类"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        # 设置测试数据目录结构
        self.test_data_dir = os.path.join(self.temp_dir, "data")
        os.makedirs(self.test_data_dir, exist_ok=True)
        # 设置测试数据库文件路径
        self.test_db_path = os.path.join(self.test_data_dir, "test.db")
        
        # 保存原始DB_PATH
        self.original_db_path = DB_PATH
        # 使用monkey patch替换DB_PATH常量
        self._monkey_patch_db_path()
        
        # 创建一个有效的SQLite数据库文件作为测试数据库
        import sqlite3
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        # 创建一个简单的表
        cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("INSERT INTO test (name) VALUES ('test')")
        conn.commit()
        conn.close()
        
    def _monkey_patch_db_path(self):
        """使用monkey patch替换DB_PATH常量"""
        # 直接修改导入的模块中的DB_PATH
        import cashlog.models.db
        cashlog.models.db.DB_PATH = self.test_db_path
    
    def tearDown(self):
        """测试后清理"""
        # 恢复原始DB_PATH
        import cashlog.models.db
        cashlog.models.db.DB_PATH = self.original_db_path
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_create_backup_default_path(self):
        """测试使用默认路径创建备份"""
        # 模拟当前日期，确保备份文件名可预测
        with patch('cashlog.services.data_service.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value.strftime.return_value = "20231201"
            # 同时patch DB_PATH，确保使用测试数据库路径
            with patch('cashlog.services.data_service.DB_PATH', self.test_db_path):
                backup_path = DataService.create_backup()
        
        # 验证备份文件存在
        self.assertTrue(os.path.exists(backup_path))
        # 验证备份文件以.db结尾
        self.assertTrue(backup_path.endswith('.db'))
        # 验证备份路径在测试数据目录下的backups文件夹
        self.assertIn('data/backups', backup_path)
        # 验证备份路径在测试数据库目录下，而不是项目目录中
        expected_backup_dir = os.path.join(self.test_data_dir, "backups")
        self.assertTrue(backup_path.startswith(expected_backup_dir))
    
    def test_create_backup_custom_path(self):
        """测试使用自定义路径创建备份"""
        custom_backup_path = os.path.join(self.temp_dir, "custom_backup.db")
        backup_path = DataService.create_backup(output_path=custom_backup_path)
        
        # 验证备份文件存在
        self.assertTrue(os.path.exists(backup_path))
        # 验证备份路径正确
        self.assertEqual(backup_path, os.path.abspath(custom_backup_path))
    
    def test_create_backup_file_exists_without_overwrite(self):
        """测试当文件已存在且不强制覆盖时的行为"""
        backup_path = os.path.join(self.temp_dir, "existing_backup.db")
        
        # 创建一个已存在的文件
        with open(backup_path, 'w') as f:
            f.write("dummy content")
        
        # 不使用overwrite参数时应抛出异常
        with self.assertRaises(FileExistsError):
            DataService.create_backup(output_path=backup_path)
    
    def test_create_backup_file_exists_with_overwrite(self):
        """测试当文件已存在且强制覆盖时的行为"""
        backup_path = os.path.join(self.temp_dir, "existing_backup.db")
        
        # 创建一个已存在的文件
        with open(backup_path, 'w') as f:
            f.write("dummy content")
        
        # 记录原文件大小
        original_size = os.path.getsize(backup_path)
        
        # 使用overwrite参数
        backup_path = DataService.create_backup(output_path=backup_path, overwrite=True)
        
        # 验证备份文件存在且大小发生变化
        self.assertTrue(os.path.exists(backup_path))
        self.assertNotEqual(os.path.getsize(backup_path), original_size)
    
    def test_create_backup_invalid_extension(self):
        """测试无效的文件扩展名"""
        invalid_path = os.path.join(self.temp_dir, "backup.txt")
        
        with self.assertRaises(ValueError):
            DataService.create_backup(output_path=invalid_path)
    
    @patch('cashlog.services.data_service.sqlite3.connect')
    def test_is_valid_sqlite_db(self, mock_connect):
        """测试SQLite数据库文件验证"""
        # 模拟文件头读取
        mock_file = mock_open(read_data=b'SQLite format 3\x00')
        
        # 模拟游标
        mock_cursor = mock_connect.return_value.cursor.return_value
        mock_cursor.fetchall.return_value = []
        
        with patch('cashlog.services.data_service.open', mock_file):
            # 测试有效的数据库文件
            self.assertTrue(DataService._is_valid_sqlite_db(self.test_db_path))
        
        # 测试无效的数据库文件头
        mock_file = mock_open(read_data=b'INVALID')
        with patch('cashlog.services.data_service.open', mock_file):
            self.assertFalse(DataService._is_valid_sqlite_db(self.test_db_path))
        
        # 测试SQLite连接失败
        mock_file = mock_open(read_data=b'SQLite format 3\x00')
        mock_connect.side_effect = Exception("Connection error")
        with patch('cashlog.services.data_service.open', mock_file):
            self.assertFalse(DataService._is_valid_sqlite_db(self.test_db_path))
    
    def test_restore_backup_file_not_found(self):
        """测试恢复不存在的备份文件"""
        non_existent_path = os.path.join(self.temp_dir, "non_existent.db")
        
        with self.assertRaises(FileNotFoundError):
            DataService.restore_backup(input_path=non_existent_path)
    
    def test_restore_backup_invalid_db(self):
        """测试恢复无效的数据库文件"""
        invalid_db_path = os.path.join(self.temp_dir, "invalid.db")
        with open(invalid_db_path, 'w') as f:
            f.write("not a sqlite database")
        
        with self.assertRaises(ValueError):
            DataService.restore_backup(input_path=invalid_db_path)
    
    @patch('cashlog.services.data_service.shutil.copy2')
    @patch('cashlog.services.data_service.DataService._is_valid_sqlite_db', return_value=True)
    def test_restore_backup_with_current_backup(self, mock_is_valid, mock_copy2):
        """测试恢复时备份当前数据库"""
        # 创建另一个测试数据库作为备份源
        backup_source = os.path.join(self.temp_dir, "backup_source.db")
        open(backup_source, 'w').close()
        
        # 模拟_get_database_stats返回
        with patch('cashlog.services.data_service.DataService._get_database_stats', return_value={"tables": {"test_table": 10}}):
            result = DataService.restore_backup(input_path=backup_source, backup_current=True)
        
        # 验证copy2被调用了两次：一次备份当前数据，一次恢复
        self.assertEqual(mock_copy2.call_count, 2)
        # 验证结果包含当前备份路径
        self.assertIn('current_backup_path', result)
        self.assertIsNotNone(result['current_backup_path'])
    
    @patch('cashlog.services.data_service.shutil.copy2')
    @patch('cashlog.services.data_service.DataService._is_valid_sqlite_db', return_value=True)
    def test_restore_backup_without_current_backup(self, mock_is_valid, mock_copy2):
        """测试恢复时不备份当前数据库"""
        # 创建另一个测试数据库作为备份源
        backup_source = os.path.join(self.temp_dir, "backup_source.db")
        open(backup_source, 'w').close()
        
        # 模拟_get_database_stats返回
        with patch('cashlog.services.data_service.DataService._get_database_stats', return_value={"tables": {"test_table": 10}}):
            result = DataService.restore_backup(input_path=backup_source, backup_current=False)
        
        # 验证copy2只被调用了一次：只有恢复操作
        self.assertEqual(mock_copy2.call_count, 1)
        # 验证结果不包含当前备份路径
        self.assertIn('current_backup_path', result)
        self.assertIsNone(result['current_backup_path'])
    
    def test_get_database_stats(self):
        """测试获取数据库统计信息"""
        # 由于我们没有真正的SQLite数据库，这里只是测试异常处理
        with patch('cashlog.services.data_service.sqlite3.connect', side_effect=Exception):
            stats = DataService._get_database_stats()
            self.assertEqual(stats, {})


if __name__ == '__main__':
    unittest.main()
