"""CLI测试基础类"""
import pytest
import tempfile
import os
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cashlog.models.db import Base


class CLITestBase:
    """CLI测试基础类，提供测试所需的通用功能"""
    
    @pytest.fixture(autouse=True)
    def setup_test_db(self):
        """为每个测试设置独立的内存数据库"""
        # 使用内存数据库进行测试
        self.test_engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=self.test_engine)
        self.TestSession = sessionmaker(autocommit=False, autoflush=False, bind=self.test_engine)
        
        # 创建临时目录用于测试数据文件
        self.temp_dir = tempfile.mkdtemp()
        
        yield
        
        # 清理
        Base.metadata.drop_all(bind=self.test_engine)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def get_test_db_session(self):
        """获取测试数据库会话"""
        return self.TestSession()
    
    def mock_db_dependency(self):
        """模拟数据库依赖，使CLI命令使用测试数据库"""
        def mock_get_db():
            yield self.get_test_db_session()
        
        return patch('cashlog.models.db.get_db', side_effect=mock_get_db)
    
    def mock_init_db(self):
        """模拟数据库初始化"""
        return patch('cashlog.models.db.init_db')