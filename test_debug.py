#!/usr/bin/env python3
"""
FNOS 插件调试脚本
用于测试 SSH 连接和数据获取功能
"""

import asyncio
import sys
import os

# 添加当前目录到 Python 路径
sys.path.insert(0, '/home/hwg/ha-components/fnos')

from custom_components.fnos.coordinator import FnosCoordinator
from custom_components.fnos.devices import FnosDevice

async def test_fnos_connection():
    """测试 FNOS 设备连接"""

    # 设备配置 - 请根据实际情况修改
    device_config = {
        'host': '192.168.1.100',  # FNOS 设备 IP
        'username': 'admin',        # SSH 用户名
        'password': 'password',     # SSH 密码
        'port': 22,                 # SSH 端口
        'scan_interval': 300        # 扫描间隔
    }

    try:
        # 创建设备实例
        device = FnosDevice(
            host=device_config['host'],
            username=device_config['username'],
            password=device_config['password'],
            port=device_config['port']
        )

        print("正在连接 FNOS 设备...")

        # 测试连接
        if await device.test_connection():
            print("✓ SSH 连接成功")

            # 获取系统信息
            print("\n正在获取系统信息...")
            system_info = await device.get_system_info()
            print(f"CPU 使用率: {system_info.get('cpu_usage', 'N/A')}%")
            print(f"内存使用率: {system_info.get('memory_usage', 'N/A')}%")
            print(f"磁盘使用率: {system_info.get('disk_usage', 'N/A')}%")
            print(f"CPU 温度: {system_info.get('cpu_temp', 'N/A')}°C")

        else:
            print("✗ SSH 连接失败")

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fnos_connection())