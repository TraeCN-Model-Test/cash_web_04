#!/bin/bash

# =============================================================================
# CashLog交易与待办双向关联功能测试脚本
# =============================================================================
# 
# 目的:
#   此脚本用于全面测试CashLog系统中交易记录与待办事项之间的
#   双向关联功能，验证关联创建、更新、查询和解除等操作的完整性。
#
# 功能说明:
#   1. 初始化数据库环境
#   2. 创建测试交易和待办事项数据
#   3. 测试交易与待办的双向关联创建
#   4. 验证关联信息的查询和显示
#   5. 测试关联关系的更新和修改
#   6. 测试关联关系的解除
#   7. 验证边界条件和异常处理
#   8. 提供测试数据清理功能
#
# 使用方法:
#   在项目根目录执行: ./scripts/test_association.sh
#
# 注意事项:
#   - 脚本使用set -e，任何测试失败将立即终止执行
#   - 测试过程中会删除并重建数据库文件(data/cashlog.db)
#   - 每个测试步骤后需要按回车键继续
#   - 最后一步提供3秒时间用于保留测试数据，否则将自动清理
# =============================================================================

# cashlog交易与待办双向关联功能测试脚本
set -e

echo "==============================================="
echo "cashlog 交易与待办双向关联功能测试"
echo "==============================================="
echo ""

# 步骤1: 初始化数据库
echo "测试步骤1: 初始化数据库"
echo "-----------------------------------------------"
# 删除旧数据库文件
rm -f data/cashlog.db
# 初始化数据库
uv run python -c "from cashlog.models.db import init_db; init_db()"
echo "✅ 数据库初始化完成"
echo ""
read -p "按回车键继续下一步..."

# 步骤2: 创建测试交易
echo "测试步骤2: 创建测试交易"
echo "-----------------------------------------------"
echo "创建3笔测试交易："
echo "1. 工资收入 8000元"
uv run python src/cashlog/cli/main_cli.py transaction add -a 8000 -c 工资 -t "收入,月度" -n "12月工资"
echo ""
echo "2. 餐饮支出 -50元"
uv run python src/cashlog/cli/main_cli.py transaction add -a -50 -c 餐饮 -t "支出,日常" -n "午餐"
echo ""
echo "3. 购物支出 -200元"
uv run python src/cashlog/cli/main_cli.py transaction add -a -200 -c 购物 -t "支出,日常" -n "购买日用品"
echo ""
echo "✅ 测试交易创建完成"
read -p "按回车键继续下一步..."

# 步骤3: 创建测试待办事项
echo ""
echo "测试步骤3: 创建测试待办事项"
echo "-----------------------------------------------"
echo "创建3个测试待办："
echo "1. 完成月度总结"
uv run python src/cashlog/cli/main_cli.py todo add -c "完成12月度工作总结" -C 工作 -t "重要,月度"
echo ""
echo "2. 还信用卡账单"
uv run python src/cashlog/cli/main_cli.py todo add -c "还招商银行信用卡账单" -C 财务 -t "紧急,月度"
echo ""
echo "3. 购买生日礼物"
uv run python src/cashlog/cli/main_cli.py todo add -c "为老婆购买生日礼物" -C 个人 -t "重要"
echo ""
echo "✅ 测试待办创建完成"
read -p "按回车键继续下一步..."

# 步骤4: 创建带关联的交易和待办
echo ""
echo "测试步骤4: 创建带关联的交易和待办"
echo "-----------------------------------------------"
echo "创建关联待办事项2的交易（还信用卡）:"
uv run python src/cashlog/cli/main_cli.py transaction add -a -5000 -c 还款 -t "支出,月度" -n "信用卡还款" --todo-id 2
echo ""
echo "创建关联交易1的待办事项（工资到账）:"
uv run python src/cashlog/cli/main_cli.py todo add -c "核对12月工资到账情况" -C 财务 -t "重要" --transaction-id 1
echo ""
echo "✅ 带关联的记录创建完成"
read -p "按回车键继续下一步..."

# 步骤5: 查看关联信息
echo ""
echo "测试步骤5: 查看关联信息"
echo "-----------------------------------------------"
echo "1. 查看所有交易并显示关联待办:"
uv run python src/cashlog/cli/main_cli.py transaction list --with-todos
echo ""
echo "2. 查看所有待办并显示关联交易:"
uv run python src/cashlog/cli/main_cli.py todo list --with-transactions
echo ""
echo "✅ 关联信息查看完成"
read -p "按回车键继续下一步..."

# 步骤6: 更新关联关系
echo ""
echo "测试步骤6: 更新关联关系"
echo "-----------------------------------------------"
echo "将交易3（购物支出）关联到待办3（购买生日礼物）:"
uv run python src/cashlog/cli/main_cli.py transaction update 3 --todo-id 3
echo ""
echo "查看更新后的交易关联:"
uv run python src/cashlog/cli/main_cli.py transaction list --with-todos --category 购物
echo ""
echo "✅ 关联关系更新完成"
read -p "按回车键继续下一步..."

# 步骤7: 解除关联
echo ""
echo "测试步骤7: 解除关联"
echo "-----------------------------------------------"
echo "解除交易3的待办关联:"
uv run python src/cashlog/cli/main_cli.py transaction unlink 3
echo ""
echo "使用update命令解除交易4的待办关联:"
uv run python src/cashlog/cli/main_cli.py transaction update 4 --todo-id 0
echo ""
echo "查看解除关联后的结果:" 
uv run python src/cashlog/cli/main_cli.py transaction list --with-todos
echo ""
echo "✅ 关联解除完成"
read -p "按回车键继续下一步..."

# 步骤8: 测试边界条件
echo ""
echo "测试步骤8: 测试边界条件"
echo "-----------------------------------------------"
echo "1. 测试关联不存在的待办ID:"
echo "预期结果：报错提示待办事项不存在"
uv run python src/cashlog/cli/main_cli.py transaction add -a -100 -c 交通 --todo-id 999 || true
echo ""
echo "2. 测试循环关联（交易1关联待办1，待办1关联交易1）:"
echo "先将交易1关联到待办1:"
uv run python src/cashlog/cli/main_cli.py transaction update 1 --todo-id 1
echo "再尝试将待办1关联到交易1:"
uv run python src/cashlog/cli/main_cli.py todo update 1 --transaction-id 1 || true
echo ""
echo "✅ 边界条件测试完成"
read -p "按回车键继续下一步..."

# 步骤9: 清理测试数据
echo ""
echo "测试步骤9: 清理测试数据"
echo "-----------------------------------------------"
echo "测试完成，如需保留测试数据请按 Ctrl+C 退出，否则将清理数据库..."
sleep 3
rm -f data/cashlog.db
echo "✅ 测试数据已清理"

# 完成
echo ""
echo "==============================================="
echo "🎉 所有测试步骤完成！"
echo "==============================================="