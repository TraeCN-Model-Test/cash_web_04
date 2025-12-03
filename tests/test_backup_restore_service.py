"""数据服务单元测试"""
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cashlog.services.data_service import DataService
from cashlog.models.db import Base, get_db

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
def test_db_dir():
    """创建测试数据库目录"""
    # 在项目中创建临时文件夹
    project_root = os.path.dirname(os.path.dirname(__file__))
    test_data_dir = os.path.join(project_root, "test_temp", "data_service")
    os.makedirs(test_data_dir, exist_ok=True)
    
    # 设置测试数据库文件路径
    test_db_path = os.path.join(test_data_dir, "test.db")
    
    # 创建一个有效的SQLite数据库文件作为测试数据库
    import sqlite3
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    # 创建一个简单的表
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO test (name) VALUES ('test')")
    conn.commit()
    conn.close()
    
    yield test_db_path, test_data_dir
    
    # 清理：删除临时目录
    shutil.rmtree(test_data_dir)


def test_create_backup_default_path(db_session, test_db_dir):
    """测试使用默认路径创建备份"""
    test_db_path, test_data_dir = test_db_dir
    
    # 模拟当前日期，确保备份文件名可预测
    with patch('cashlog.services.data_service.datetime') as mock_datetime:
        mock_datetime.datetime.now.return_value.strftime.return_value = "20231201"
        # 同时patch DB_PATH，确保使用测试数据库路径
        with patch('cashlog.services.data_service.DB_PATH', test_db_path):
            backup_path = DataService.create_backup()
    
    # 验证备份文件存在
    assert os.path.exists(backup_path)
    # 验证备份文件以.db结尾
    assert backup_path.endswith('.db')
    # 验证备份路径在测试数据目录下的backups文件夹
    assert 'data_service/backups' in backup_path
    # 验证备份路径在测试数据库目录下，而不是项目目录中
    expected_backup_dir = os.path.join(test_data_dir, "backups")
    assert backup_path.startswith(expected_backup_dir)


def test_create_backup_custom_path(db_session, test_db_dir):
    """测试使用自定义路径创建备份"""
    _, test_data_dir = test_db_dir
    custom_backup_path = os.path.join(test_data_dir, "custom_backup.db")
    backup_path = DataService.create_backup(output_path=custom_backup_path)
    
    # 验证备份文件存在
    assert os.path.exists(backup_path)
    # 验证备份路径正确
    assert backup_path == os.path.abspath(custom_backup_path)


def test_create_backup_file_exists_without_overwrite(db_session, test_db_dir):
    """测试当文件已存在且不强制覆盖时的行为"""
    _, test_data_dir = test_db_dir
    backup_path = os.path.join(test_data_dir, "existing_backup.db")
    
    # 创建一个已存在的文件
    with open(backup_path, 'w') as f:
        f.write("dummy content")
    
    # 不使用overwrite参数时应抛出异常
    with pytest.raises(FileExistsError):
        DataService.create_backup(output_path=backup_path)


def test_create_backup_file_exists_with_overwrite(db_session, test_db_dir):
    """测试当文件已存在且强制覆盖时的行为"""
    _, test_data_dir = test_db_dir
    backup_path = os.path.join(test_data_dir, "existing_backup.db")
    
    # 创建一个已存在的文件
    with open(backup_path, 'w') as f:
        f.write("dummy content")
    
    # 记录原文件大小
    original_size = os.path.getsize(backup_path)
    
    # 使用overwrite参数
    backup_path = DataService.create_backup(output_path=backup_path, overwrite=True)
    
    # 验证备份文件存在且大小发生变化
    assert os.path.exists(backup_path)
    assert os.path.getsize(backup_path) != original_size


def test_create_backup_invalid_extension(db_session, test_db_dir):
    """测试无效的文件扩展名"""
    _, test_data_dir = test_db_dir
    invalid_path = os.path.join(test_data_dir, "backup.txt")
    
    with pytest.raises(ValueError):
        DataService.create_backup(output_path=invalid_path)


@patch('cashlog.services.data_service.sqlite3.connect')
def test_is_valid_sqlite_db(mock_connect, test_db_dir):
    """测试SQLite数据库文件验证"""
    test_db_path, _ = test_db_dir
    
    # 模拟文件头读取
    mock_file = mock_open(read_data=b'SQLite format 3\x00')
    
    # 模拟游标
    mock_cursor = mock_connect.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = []
    
    with patch('cashlog.services.data_service.open', mock_file):
        # 测试有效的数据库文件
        assert DataService._is_valid_sqlite_db(test_db_path) is True
    
    # 测试无效的数据库文件头
    mock_file = mock_open(read_data=b'INVALID')
    with patch('cashlog.services.data_service.open', mock_file):
        assert DataService._is_valid_sqlite_db(test_db_path) is False
    
    # 测试SQLite连接失败
    mock_file = mock_open(read_data=b'SQLite format 3\x00')
    mock_connect.side_effect = Exception("Connection error")
    with patch('cashlog.services.data_service.open', mock_file):
        assert DataService._is_valid_sqlite_db(test_db_path) is False


def test_restore_backup_file_not_found(db_session, test_db_dir):
    """测试恢复不存在的备份文件"""
    _, test_data_dir = test_db_dir
    non_existent_path = os.path.join(test_data_dir, "non_existent.db")
    
    with pytest.raises(FileNotFoundError):
        DataService.restore_backup(input_path=non_existent_path)


def test_restore_backup_invalid_db(db_session, test_db_dir):
    """测试恢复无效的数据库文件"""
    _, test_data_dir = test_db_dir
    invalid_db_path = os.path.join(test_data_dir, "invalid.db")
    with open(invalid_db_path, 'w') as f:
        f.write("not a sqlite database")
    
    with pytest.raises(ValueError):
        DataService.restore_backup(input_path=invalid_db_path)


@patch('cashlog.services.data_service.shutil.copy2')
@patch('cashlog.services.data_service.DataService._is_valid_sqlite_db', return_value=True)
def test_restore_backup_with_current_backup(mock_is_valid, mock_copy2, db_session, test_db_dir):
    """测试恢复时备份当前数据库"""
    _, test_data_dir = test_db_dir
    
    # 创建另一个测试数据库作为备份源
    backup_source = os.path.join(test_data_dir, "backup_source.db")
    open(backup_source, 'w').close()
    
    # 模拟_get_database_stats返回
    with patch('cashlog.services.data_service.DataService._get_database_stats', return_value={"tables": {"test_table": 10}}):
        result = DataService.restore_backup(input_path=backup_source, backup_current=True)
    
    # 验证copy2被调用了两次：一次备份当前数据，一次恢复
    assert mock_copy2.call_count == 2
    # 验证结果包含当前备份路径
    assert 'current_backup_path' in result
    assert result['current_backup_path'] is not None


@patch('cashlog.services.data_service.shutil.copy2')
@patch('cashlog.services.data_service.DataService._is_valid_sqlite_db', return_value=True)
def test_restore_backup_without_current_backup(mock_is_valid, mock_copy2, db_session, test_db_dir):
    """测试恢复时不备份当前数据库"""
    _, test_data_dir = test_db_dir
    
    # 创建另一个测试数据库作为备份源
    backup_source = os.path.join(test_data_dir, "backup_source.db")
    open(backup_source, 'w').close()
    
    # 模拟_get_database_stats返回
    with patch('cashlog.services.data_service.DataService._get_database_stats', return_value={"tables": {"test_table": 10}}):
        result = DataService.restore_backup(input_path=backup_source, backup_current=False)
    
    # 验证copy2只被调用了一次：只恢复数据
    assert mock_copy2.call_count == 1
    # 验证结果包含current_backup_path，但值为None
    assert 'current_backup_path' in result
    assert result['current_backup_path'] is None


def test_get_database_stats(db_session, test_db_dir):
    """测试获取数据库统计信息"""
    test_db_path, _ = test_db_dir
    
    # 获取数据库统计信息
    stats = DataService._get_database_stats()
    
    # 验证返回的统计信息包含预期的键
    assert 'tables' in stats
    
    # 验证todos和transactions表存在
    assert 'todos' in stats['tables']
    assert 'transactions' in stats['tables']
    assert stats['tables']['todos'] >= 0
    assert stats['tables']['transactions'] >= 0