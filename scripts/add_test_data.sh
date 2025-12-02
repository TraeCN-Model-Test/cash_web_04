#!/bin/zsh

# 添加测试交易数据
echo "开始添加测试交易数据..."

# 添加本月（12月）收入
uv run python main.py transaction add -a 8000.00 -c 工资 -d "2025-12-01 09:00:00"
uv run python main.py transaction add -a 2000.00 -c 奖金 -d "2025-12-15 15:00:00"

# 添加本月支出
uv run python main.py transaction add -a -200.00 -c 餐饮 -t "支出,日常" -n "午餐" -d "2025-12-02 12:00:00"
uv run python main.py transaction add -a -150.00 -c 餐饮 -t "支出,日常" -n "晚餐" -d "2025-12-03 19:00:00"
uv run python main.py transaction add -a -1000.00 -c 购物 -t "支出,日常" -n "生活用品" -d "2025-12-05 10:00:00"
uv run python main.py transaction add -a -300.00 -c 交通 -t "支出,日常" -n "地铁卡充值" -d "2025-12-10 08:00:00"
uv run python main.py transaction add -a -1500.00 -c 房租 -d "2025-12-01 10:00:00"

# 添加上月（11月）数据，用于环比计算
uv run python main.py transaction add -a 7500.00 -c 工资 -d "2025-11-01 09:00:00"
uv run python main.py transaction add -a -180.00 -c 餐饮 -t "支出,日常" -n "午餐" -d "2025-11-28 12:00:00"
uv run python main.py transaction add -a -900.00 -c 购物 -t "支出,日常" -n "电子产品" -d "2025-11-20 14:00:00"
uv run python main.py transaction add -a -1500.00 -c 房租 -d "2025-11-01 10:00:00"

echo ""
echo "测试数据添加完成！"
echo ""
echo "可使用以下命令查看数据:"
echo "  uv run python main.py transaction list"
echo "  uv run python main.py transaction list -m 2025-12"
