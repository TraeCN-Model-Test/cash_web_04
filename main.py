"""cashlog 主入口文件"""
import sys
from cashlog.cli.main_cli import cli


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "api":
        # 启动API服务
        from cashlog.models.db import init_db
        import uvicorn
        
        init_db()
        uvicorn.run(
            "cashlog.api:app", 
            host="0.0.0.0", 
            port=8000,
            reload=True
        )
    else:
        # 启动CLI
        cli()
