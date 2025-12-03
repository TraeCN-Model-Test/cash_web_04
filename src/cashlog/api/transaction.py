"""交易账单API路由"""
from typing import Optional
from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi_pagination import Page, paginate
from cashlog.models.db import get_db
from cashlog.services.transaction_service import TransactionService
from cashlog.models.schemas import Transaction

router = APIRouter(
    prefix="/transactions",
    tags=["交易账单"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=Page[Transaction], summary="查询交易账单列表", description="根据条件查询交易账单列表，支持分页")
def get_transactions(
    month: Optional[str] = Query(None, description="交易月份，格式：YYYY-MM"),
    category: Optional[str] = Query(None, description="交易分类"),
    tags: Optional[str] = Query(None, description="标签，多个标签用逗号分隔"),
    transaction_type: Optional[str] = Query(None, description="交易类型，可选值：income（收入）, expense（支出）"),
    db: Session = Depends(get_db)
):
    """
    查询交易账单列表
    
    - **month**: 交易月份，格式：YYYY-MM
    - **category**: 交易分类
    - **tags**: 标签，多个标签用逗号分隔
    - **transaction_type**: 交易类型，可选值：income（收入）, expense（支出）
    """
    filters = {}
    if month:
        filters["month"] = month
    if category:
        filters["category"] = category
    if tags:
        filters["tags"] = tags
    if transaction_type:
        filters["transaction_type"] = transaction_type
    
    transactions = TransactionService.get_transactions(db, **filters)
    return paginate(transactions)


@router.get("/{transaction_id}", response_model=Transaction, summary="根据ID查询交易账单", description="根据ID查询单个交易账单的详细信息")
def get_transaction_by_id(
    transaction_id: int, 
    db: Session = Depends(get_db)
):
    """
    根据ID查询交易账单
    
    - **transaction_id**: 交易账单ID
    """
    transaction = TransactionService.get_transaction_by_id(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="交易账单不存在")
    return transaction