# CashLog API 模块

提供RESTful API接口，基于FastAPI框架实现。

## 📁 目录结构

```
src/cashlog/api/
├── __init__.py          # 模块初始化
├── main.py              # FastAPI应用入口
├── routers/             # API路由
│   ├── __init__.py
│   ├── todo.py          # 待办事项API
│   └── transaction.py   # 交易记录API
└── README.md            # API文档
```

## 🏗️ 架构设计

API模块采用FastAPI的路由模式，将不同功能模块分离到独立的路由文件中。

## � API端点

### 待办事项API
- `GET /api/todos` - 获取所有待办事项
- `POST /api/todos` - 创建新待办事项
- `GET /api/todos/{id}` - 获取指定ID的待办事项
- `PUT /api/todos/{id}` - 更新指定ID的待办事项
- `DELETE /api/todos/{id}` - 删除指定ID的待办事项

### 交易记录API
- `GET /api/transactions` - 获取所有交易记录
- `POST /api/transactions` - 创建新交易记录
- `GET /api/transactions/{id}` - 获取指定ID的交易记录
- `PUT /api/transactions/{id}` - 更新指定ID的交易记录
- `DELETE /api/transactions/{id}` - 删除指定ID的交易记录

## 📝 请求与响应格式

所有API请求和响应均采用JSON格式。

### 请求示例
```json
{
  "title": "购买办公用品",
  "amount": 120.50,
  "category": "办公用品",
  "date": "2023-01-15"
}
```

### 响应示例
```json
{
  "id": 1,
  "title": "购买办公用品",
  "amount": 120.50,
  "category": "办公用品",
  "date": "2023-01-15",
  "created_at": "2023-01-15T10:30:00",
  "updated_at": "2023-01-15T10:30:00"
}
```

## 🔍 查询参数

支持以下查询参数进行筛选：
- `limit` - 限制返回数量
- `offset` - 偏移量
- `category` - 按分类筛选
- `date_from` - 起始日期
- `date_to` - 结束日期

## ❌ 错误处理

API使用标准HTTP状态码表示请求结果：
- `200` - 请求成功
- `201` - 创建成功
- `400` - 请求参数错误
- `404` - 资源不存在
- `422` - 数据验证失败
- `500` - 服务器内部错误

错误响应格式：
```json
{
  "detail": "错误描述信息"
}
```

## ✅ 数据验证

使用Pydantic进行数据验证，确保请求数据的完整性和正确性。

## 📚 API文档

启动服务后，访问以下地址查看交互式API文档：
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 测试

API测试位于 `tests/test_rest_api.py` 文件中，使用pytest框架。

## �️ 开发指南

### 添加新API端点
1. 在api目录下创建或编辑路由文件
2. 定义请求和响应模型
3. 实现API处理函数
4. 添加数据验证和错误处理
5. 编写单元测试

### 数据库操作
API层通过Services层访问数据库，不直接操作数据库。