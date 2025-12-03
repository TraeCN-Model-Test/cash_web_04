"""数据备份与恢复命令行接口"""
import click
import os
from typing import Optional
from cashlog.services.data_service import DataService
from cashlog.utils.formatter import Formatter
from cashlog.models.db import init_db


@click.group()
def data():
    """
    数据备份与恢复命令组
    
    用于管理数据库的备份和恢复操作，支持指定备份路径、强制覆盖、自动备份当前数据等功能。
    """
    pass


@data.command()
@click.option("-o", "--output", help="指定备份文件路径（含文件名，后缀.db）")
@click.option("-f", "--overwrite", is_flag=True, default=False, help="强制覆盖已有备份文件")
def backup(output: Optional[str], overwrite: bool):
    """
    创建数据库备份
    
    示例:
    cashlog data backup                      # 使用默认路径备份到 ~/.cashlog16/backup_YYYYMMDD.db
    cashlog data backup -o ~/cashlog_backup.db  # 指定备份路径
    cashlog data backup -o ~/cashlog_backup.db -f  # 强制覆盖已存在的备份文件
    """
    init_db()  # 确保数据库已初始化
    
    try:
        backup_path = DataService.create_backup(output_path=output, overwrite=overwrite)
        Formatter.print_success(f"\n✅ 数据库备份成功")
        Formatter.print_info(f"   备份文件: [bold]{backup_path}[/bold]")
        
        # 显示备份文件大小
        try:
            file_size = os.path.getsize(backup_path) / 1024  # KB
            Formatter.print_info(f"   文件大小: {file_size:.2f} KB")
        except (OSError, IOError):
            # 在测试环境中，模拟路径可能不存在，忽略文件大小显示
            pass
        
    except FileExistsError as e:
        Formatter.print_error(f"\n❌ {str(e)}")
        raise click.ClickException(str(e))
    except ValueError as e:
        Formatter.print_error(f"\n❌ 参数错误: {str(e)}")
        raise click.ClickException(str(e))
    except IOError as e:
        Formatter.print_error(f"\n❌ IO错误: {str(e)}")
        raise click.ClickException(str(e))
    except Exception as e:
        Formatter.print_error(f"\n❌ 备份失败: {str(e)}")
        raise click.ClickException(str(e))


@data.command()
@click.option("-i", "--input", required=True, help="指定备份文件路径（需为合法SQLite文件）")
@click.option("-b", "--backup-current", default=True, help="恢复前自动备份当前数据库")
@click.option("-y", "--confirm", is_flag=True, default=False, help="跳过恢复二次确认")
def restore(input: str, backup_current: bool, confirm: bool):
    """
    从备份文件恢复数据库
    
    示例:
    cashlog data restore -i ~/cashlog_backup.db             # 从指定备份文件恢复，恢复前自动备份当前数据
    cashlog data restore -i ~/cashlog_backup.db -y           # 跳过确认直接恢复
    cashlog data restore -i ~/cashlog_backup.db -y -b False  # 跳过确认且不备份当前数据直接恢复
    """
    init_db()  # 确保数据库已初始化
    
    # 展开用户路径
    input_path = os.path.expanduser(input)
    
    # 二次确认
    if not confirm:
        Formatter.print_warning("⚠️  警告：数据恢复操作将替换当前数据库内容！")
        Formatter.print_info(f"   恢复源：{input_path}")
        if backup_current:
            Formatter.print_info("   系统将自动备份当前数据库")
        
        response = click.prompt("是否继续？(y/N)", default="N")
        if response.lower() != 'y':
            Formatter.print_info("恢复操作已取消")
            return  # 直接返回，不执行后续操作
    
    try:
        result = DataService.restore_backup(
            input_path=input_path,
            backup_current=backup_current,
            confirm=confirm
        )
        
        Formatter.print_success(f"\n✅ 数据库恢复成功")
        Formatter.print_info(f"   恢复源: [bold]{result['restored_from']}[/bold]")
        
        if result['current_backup_path']:
            Formatter.print_info(f"   当前数据备份: [bold]{result['current_backup_path']}[/bold]")
        
        # 显示数据统计信息
        Formatter.print_info("\n📊 数据统计:")
        
        # 输出恢复后的表统计
        if result['after_stats'] and 'tables' in result['after_stats']:
            Formatter.print_info("   恢复后:")
            for table, count in result['after_stats']['tables'].items():
                if not table.startswith('sqlite_'):  # 跳过SQLite系统表
                    Formatter.print_info(f"     - {table}: {count} 条记录")
        else:
            Formatter.print_info("   无法获取表统计信息")
    
    except FileNotFoundError as e:
        Formatter.print_error(f"\n❌ {str(e)}")
        raise click.ClickException(str(e))
    except ValueError as e:
        Formatter.print_error(f"\n❌ 参数错误: {str(e)}")
        raise click.ClickException(str(e))
    except IOError as e:
        Formatter.print_error(f"\n❌ IO错误: {str(e)}")
        raise click.ClickException(str(e))
    except Exception as e:
        Formatter.print_error(f"\n❌ 恢复失败: {str(e)}")
        raise click.ClickException(str(e))