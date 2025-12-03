"""待办事项API路由"""
from typing import Optional
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_pagination import Page, paginate
from cashlog.models.db import get_db
from cashlog.services.todo_service import TodoService
from cashlog.models.schemas import Todo

router = APIRouter(
    prefix="/todos",
    tags=["待办事项"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=Page[Todo], summary="查询待办事项列表", description="根据条件查询待办事项列表，支持分页")
def get_todos(
    status: Optional[str] = Query(None, description="待办状态，可选值：todo, doing, done"),
    category: Optional[str] = Query(None, description="待办分类"),
    deadline_before: Optional[str] = Query(None, description="截止时间之前，格式：YYYY-MM-DD"),
    deadline_after: Optional[str] = Query(None, description="截止时间之后，格式：YYYY-MM-DD"),
    tags: Optional[str] = Query(None, description="标签，多个标签用逗号分隔"),
    db: Session = Depends(get_db)
):
    """
    查询待办事项列表
    
    - **status**: 待办状态，可选值：todo, doing, done
    - **category**: 待办分类
    - **deadline_before**: 截止时间之前，格式：YYYY-MM-DD
    - **deadline_after**: 截止时间之后，格式：YYYY-MM-DD
    - **tags**: 标签，多个标签用逗号分隔
    """
    filters = {}
    if status:
        filters["status"] = status
    if category:
        filters["category"] = category
    if deadline_before:
        filters["deadline_before"] = deadline_before
    if deadline_after:
        filters["deadline_after"] = deadline_after
    if tags:
        filters["tags"] = tags
    
    todos = TodoService.get_todos(db, **filters)
    return paginate(todos)


@router.get("/{todo_id}", response_model=Todo, summary="根据ID查询待办事项", description="根据ID查询单个待办事项的详细信息")
def get_todo_by_id(
    todo_id: int, 
    db: Session = Depends(get_db)
):
    """
    根据ID查询待办事项
    
    - **todo_id**: 待办事项ID
    """
    todo = TodoService.get_todo_by_id(db, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="待办事项不存在")
    return todo
