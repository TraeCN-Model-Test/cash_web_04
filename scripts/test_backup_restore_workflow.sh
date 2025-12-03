#!/bin/bash

# =============================================================================
# 数据备份与恢复功能 - 正常流程测试脚本
# =============================================================================
# 
# 目的:
#   此脚本用于测试CashLog数据备份与恢复功能的正常工作流程，
#   验证系统能够正确创建备份、恢复数据并保持数据完整性。
#
# 功能说明:
#   1. 初始化数据库并确保系统正常工作
#   2. 添加测试交易数据（收入和支出）
#   3. 创建数据库备份
#   4. 修改数据（添加新交易模拟数据变更）
#   5. 从备份恢复数据
#   6. 验证恢复后的数据完整性
#   7. 提供彩色输出和详细的步骤反馈
#
# 使用方法:
#   在项目根目录执行: ./scripts/test_backup_restore_workflow.sh
#
# 注意事项:
#   - 脚本会在项目根目录下创建tmp_cashlog_backup_test.db临时备份文件
#   - 测试过程中需要人工确认某些步骤
#   - 测试完成后可选择是否删除临时备份文件
# =============================================================================

# 正常流程测试脚本：添加交易→备份→修改→恢复

echo "========================================="
echo "数据备份与恢复功能 - 正常流程测试"
echo "========================================="

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 定义项目内的临时备份文件路径
BACKUP_FILE="$(pwd)/tmp_cashlog_backup_test.db"

# 清理之前的测试文件
if [ -f "$BACKUP_FILE" ]; then
    echo -e "${YELLOW}清理之前的测试备份文件...${NC}"
    rm "$BACKUP_FILE"
fi

# 步骤1: 确保数据库已初始化
echo -e "\n${BLUE}步骤1: 初始化数据库${NC}"
python main.py data backup -o "$BACKUP_FILE" -f
if [ $? -ne 0 ]; then
    echo -e "${RED}数据库初始化失败${NC}"
    exit 1
fi

# 步骤2: 添加测试交易
echo -e "\n${BLUE}步骤2: 添加测试交易${NC}"
echo -e "${GREEN}添加收入交易...${NC}"
python main.py transaction add -a 1000.00 -c "工资" -t "收入,测试" -n "备份测试收入"

if [ $? -ne 0 ]; then
    echo -e "${RED}添加收入交易失败${NC}"
    exit 1
fi

echo -e "${GREEN}添加支出交易...${NC}"
python main.py transaction add -a -200.50 -c "餐饮" -t "支出,测试" -n "备份测试支出"

if [ $? -ne 0 ]; then
    echo -e "${RED}添加支出交易失败${NC}"
    exit 1
fi

# 步骤3: 列出当前交易
echo -e "\n${BLUE}步骤3: 查看当前交易记录${NC}"
python main.py transaction list -t "测试"

# 人工确认点
echo -e "\n${YELLOW}请确认已成功添加测试交易记录，按Enter键继续...${NC}"
read

# 步骤4: 创建备份
echo -e "\n${BLUE}步骤4: 创建数据库备份${NC}"
python main.py data backup -o "$BACKUP_FILE" -f

if [ $? -ne 0 ]; then
    echo -e "${RED}创建备份失败${NC}"
    exit 1
fi

echo -e "${GREEN}备份成功，备份文件位于: $BACKUP_FILE${NC}"

# 步骤5: 修改数据（添加新交易模拟数据变更）
echo -e "\n${BLUE}步骤5: 修改数据（添加新交易）${NC}"
python main.py transaction add -a -50.00 -c "交通" -t "支出,临时" -n "临时添加的交易"

if [ $? -ne 0 ]; then
    echo -e "${RED}添加临时交易失败${NC}"
    exit 1
fi

# 步骤6: 查看修改后的数据
echo -e "\n${BLUE}步骤6: 查看修改后的数据${NC}"
python main.py transaction list

# 人工确认点
echo -e "\n${YELLOW}请确认数据已被修改（多了一条临时交易），按Enter键继续恢复...${NC}"
read

# 步骤7: 恢复数据
echo -e "\n${BLUE}步骤7: 从备份恢复数据${NC}"
python main.py data restore -i "$BACKUP_FILE" -y -b False

if [ $? -ne 0 ]; then
    echo -e "${RED}恢复数据失败${NC}"
    exit 1
fi

# 步骤8: 验证恢复后的数据
echo -e "\n${BLUE}步骤8: 验证恢复后的数据${NC}"
python main.py transaction list

# 人工确认点
echo -e "\n${YELLOW}请确认数据已成功恢复（临时交易应不存在）${NC}"
echo -e "${GREEN}测试完成！${NC}"

# 清理测试文件
read -p "是否删除测试备份文件？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm "$BACKUP_FILE"
    echo -e "${GREEN}测试备份文件已删除${NC}"
fi

echo -e "\n${BLUE}正常流程测试完成${NC}"
echo "========================================="
