#!/bin/zsh

# =============================================================================
# 测试待办事项数据添加脚本
# =============================================================================
# 
# 目的:
#   此脚本用于向CashLog数据库添加多样化的测试待办事项数据，以便测试和演示
#   待办事项管理功能。
#
# 功能说明:
#   1. 添加多种类别的待办事项：工作、个人事务、学习、娱乐等
#   2. 设置不同的状态：待办、进行中、已完成
#   3. 包含不同的标签和截止时间，模拟真实使用场景
#   4. 提供查看数据的命令示例
#
# 使用方法:
#   在项目根目录执行: ./scripts/setup_todo_test_data.sh
#
# 注意事项:
#   - 执行前请确保数据库已初始化
#   - 重复执行会添加重复数据，建议清理后重新添加
# =============================================================================

# 添加测试待办事项数据
echo "开始添加测试待办事项数据..."

# 添加工作相关待办事项
uv run python main.py todo add -c "完成项目报告" -C 工作 -t "重要,紧急" -d "2025-12-25 18:00:00"
uv run python main.py todo add -c "准备季度总结会议" -C 工作 -t "会议,重要" -d "2025-12-20 14:00:00"
uv run python main.py todo add -c "代码审查" -C 工作 -t "开发,日常" -d "2025-12-15 17:00:00"
uv run python main.py todo add -c "更新项目文档" -C 工作 -t "文档,日常" -d "2025-12-30 18:00:00"

# 添加个人事务待办事项
uv run python main.py todo add -c "购买生日礼物" -C 个人 -t "购物,节日" -d "2025-12-20 12:00:00"
uv run python main.py todo add -c "预约体检" -C 健康 -t "医疗,重要" -d "2025-12-28 10:00:00"
uv run python main.py todo add -c "缴纳水电费" -C 生活 -t "账单,紧急" -d "2025-12-10 23:59:59"
uv run python main.py todo add -c "整理衣柜" -C 家务 -t "日常,整理" -d "2025-12-31 20:00:00"

# 添加学习相关待办事项
uv run python main.py todo add -c "阅读《深入理解计算机系统》" -C 学习 -t "读书,技术" -d "2025-12-31 23:59:59"
uv run python main.py todo add -c "完成在线课程第5章" -C 学习 -t "课程,编程" -d "2025-12-22 20:00:00"
uv run python main.py todo add -c "练习算法题" -C 学习 -t "编程,算法" -d "2025-12-18 22:00:00"

# 添加娱乐休闲待办事项
uv run python main.py todo add -c "观看电影《星际穿越》" -C 娱乐 -t "电影,科幻" -d "2025-12-24 21:00:00"
uv run python main.py todo add -c "周末爬山" -C 运动 -t "户外,健身" -d "2025-12-23 08:00:00"
uv run python main.py todo add -c "尝试新餐厅" -C 美食 -t "餐饮,探索" -d "2025-12-26 19:00:00"

# 添加一些已完成的待办事项
uv run python main.py todo add -c "提交项目提案" -C 工作 -t "重要,已完成" -d "2025-12-01 17:00:00"
uv run python main.py todo add -c "购买新年装饰" -C 个人 -t "节日,购物" -d "2025-12-05 15:00:00"

# 将一些待办事项标记为进行中
uv run python main.py todo update-status 1 doing
uv run python main.py todo update-status 5 doing
uv run python main.py todo update-status 9 doing

# 将一些待办事项标记为已完成
uv run python main.py todo update-status 13 done
uv run python main.py todo update-status 14 done

echo ""
echo "测试待办事项数据添加完成！"
echo ""
echo "可使用以下命令查看数据:"
echo "  uv run python main.py todo list"
echo "  uv run python main.py todo list -s todo"
echo "  uv run python main.py todo list -s doing"
echo "  uv run python main.py todo list -s done"
echo "  uv run python main.py todo list -c 工作"