#!/bin/bash

# =============================================================================
# 数据备份与恢复功能 - 异常场景测试脚本
# =============================================================================
# 
# 目的:
#   此脚本用于测试CashLog数据备份与恢复功能在各种异常情况下的行为，
#   验证系统的错误处理能力和健壮性。
#
# 功能说明:
#   1. 测试使用无效文件（文本文件）恢复数据
#   2. 测试使用假数据库文件（无SQLite头）恢复数据
#   3. 测试备份文件覆盖冲突处理
#   4. 测试无效文件扩展名处理
#   5. 测试恢复不存在的文件
#   6. 提供彩色输出和详细的测试结果反馈
#
# 使用方法:
#   在项目根目录执行: ./scripts/backup_restore_error.sh
#
# 注意事项:
#   - 脚本会在项目根目录下创建tmp_cashlog_test临时目录
#   - 测试过程中需要人工确认某些步骤
#   - 测试完成后可选择是否删除临时文件
# =============================================================================

# 异常场景测试脚本：测试各种错误情况

echo "========================================="
echo "数据备份与恢复功能 - 异常场景测试"
echo "========================================="

# 设置颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 定义项目内的测试文件路径
TEST_DIR="$(pwd)/tmp_cashlog_test"
VALID_BACKUP="$TEST_DIR/valid_backup.db"
INVALID_BACKUP="$TEST_DIR/invalid_backup.db"
NON_DB_FILE="$TEST_DIR/text_file.txt"

# 创建测试目录
mkdir -p "$TEST_DIR"

# 清理函数
cleanup() {
    echo -e "\n${YELLOW}清理测试文件...${NC}"
    rm -rf "$TEST_DIR"
    echo -e "${GREEN}测试文件已清理${NC}"
}

# 测试1: 创建有效备份作为参考
echo -e "\n${BLUE}测试1: 创建有效备份作为参考${NC}"
python main.py data backup -o "$VALID_BACKUP" -f

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 有效备份创建成功${NC}"
else
    echo -e "${RED}✗ 有效备份创建失败${NC}"
    cleanup
    exit 1
fi

# 测试2: 创建无效的备份文件（文本文件）
echo -e "\n${BLUE}测试2: 创建无效的备份文件（纯文本文件）${NC}"
echo "This is not a SQLite database" > "$NON_DB_FILE"
echo -e "${GREEN}✓ 无效文本文件创建成功${NC}"

# 测试3: 尝试使用无效的文本文件恢复
echo -e "\n${BLUE}测试3: 尝试使用无效的文本文件恢复（应该失败）${NC}"
echo -e "${YELLOW}预期结果: 系统应提示'无效的SQLite数据库文件'${NC}"
python main.py data restore -i "$NON_DB_FILE" -y -b False

if [ $? -ne 0 ]; then
    echo -e "${GREEN}✓ 正确拒绝了无效的文本文件${NC}"
else
    echo -e "${RED}✗ 错误：系统接受了无效的文本文件${NC}"
fi

# 人工确认点
echo -e "\n${YELLOW}请确认系统正确拒绝了无效文件，按Enter键继续...${NC}"
read

# 测试4: 创建一个假的数据库文件（没有SQLite头）
echo -e "\n${BLUE}测试4: 创建假的数据库文件（没有SQLite头）${NC}"
echo -n "INVALID DB CONTENT" > "$INVALID_BACKUP"
echo -e "${GREEN}✓ 假数据库文件创建成功${NC}"

# 测试5: 尝试使用假数据库文件恢复
echo -e "\n${BLUE}测试5: 尝试使用假数据库文件恢复（应该失败）${NC}"
echo -e "${YELLOW}预期结果: 系统应提示'无效的SQLite数据库文件'${NC}"
python main.py data restore -i "$INVALID_BACKUP" -y -b False

if [ $? -ne 0 ]; then
    echo -e "${GREEN}✓ 正确拒绝了假数据库文件${NC}"
else
    echo -e "${RED}✗ 错误：系统接受了假数据库文件${NC}"
fi

# 人工确认点
echo -e "\n${YELLOW}请确认系统正确拒绝了假数据库文件，按Enter键继续...${NC}"
read

# 测试6: 测试文件覆盖冲突
echo -e "\n${BLUE}测试6: 测试备份文件覆盖冲突（不使用-f参数）${NC}"
echo -e "${YELLOW}预期结果: 系统应提示文件已存在，需要使用-f参数${NC}"
python main.py data backup -o "$VALID_BACKUP"

if [ $? -ne 0 ]; then
    echo -e "${GREEN}✓ 正确检测到文件覆盖冲突${NC}"
else
    echo -e "${RED}✗ 错误：系统未检测到文件覆盖冲突${NC}"
fi

# 测试7: 测试无效的文件扩展名
echo -e "\n${BLUE}测试7: 测试无效的备份文件扩展名${NC}"
echo -e "${YELLOW}预期结果: 系统应提示'备份文件必须以.db为后缀'${NC}"
python main.py data backup -o "$TEST_DIR/backup.txt"

if [ $? -ne 0 ]; then
    echo -e "${GREEN}✓ 正确检测到无效的文件扩展名${NC}"
else
    echo -e "${RED}✗ 错误：系统接受了无效的文件扩展名${NC}"
fi

# 测试8: 测试不存在的输入文件恢复
echo -e "\n${BLUE}测试8: 测试恢复不存在的文件${NC}"
echo -e "${YELLOW}预期结果: 系统应提示文件不存在${NC}"
python main.py data restore -i "$TEST_DIR/non_existent.db" -y -b False

if [ $? -ne 0 ]; then
    echo -e "${GREEN}✓ 正确检测到文件不存在${NC}"
else
    echo -e "${RED}✗ 错误：系统未检测到文件不存在${NC}"
fi

# 测试完成
echo -e "\n${GREEN}=========================================${NC}"
echo -e "${GREEN}所有异常场景测试完成${NC}"
echo -e "${GREEN}=========================================${NC}"

# 清理测试文件
read -p "是否删除所有测试文件？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cleanup
fi

echo -e "\n${BLUE}异常场景测试脚本结束${NC}"
