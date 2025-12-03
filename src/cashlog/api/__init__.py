"""API接口入口"""
from fastapi import FastAPI
from fastapi_pagination import add_pagination
from cashlog.api.todo import router as todo_router
from cashlog.api.transaction import router as transaction_router


def create_app():
    """创建FastAPI应用"""
    app = FastAPI(
        title="现金日志API",
        description="现金日志管理系统的API接口",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # 注册路由
    app.include_router(todo_router, prefix="/api")
    app.include_router(transaction_router, prefix="/api")
    
    # 添加分页支持
    add_pagination(app)
    
    return app


app = create_app()
