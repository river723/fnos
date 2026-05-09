#!/usr/bin/env python3
"""
FNOS 集成打包脚本
用于创建符合 HACS 要求的 fnos.zip 发布文件

使用方法:
  python3 build_release.py                    # 创建发布包
  python3 build_release.py --version 1.2.2   # 指定版本号
  python3 build_release.py --check            # 检查当前发布包
"""

import zipfile
import os
import sys
import argparse

def create_release_zip(version=None):
    """创建 HACS 发布包"""

    print("开始创建 FNOS 集成发布包...")

    # 删除旧的 zip 文件
    if os.path.exists('fnos.zip'):
        os.remove('fnos.zip')
        print("已删除旧的 fnos.zip")

    try:
        with zipfile.ZipFile('fnos.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 打包 custom_components/fnos 目录的内容
            fnos_dir = 'custom_components/fnos'

            if not os.path.exists(fnos_dir):
                print(f"错误: {fnos_dir} 目录不存在！")
                return False

            for root, dirs, files in os.walk(fnos_dir):
                # 排除 __pycache__ 和隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

                for file in files:
                    # 排除 .pyc 文件和隐藏文件
                    if not file.endswith('.pyc') and not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        # 移除 'custom_components/fnos/' 前缀
                        relative_path = file_path.replace('custom_components/fnos/', '', 1)
                        zipf.write(file_path, relative_path)
                        print(f"添加: {relative_path}")

            # 添加根目录文件
            root_files = ['README.md', 'hacs.json', 'info.md', '.hacs.json']
            for file in root_files:
                if os.path.exists(file):
                    zipf.write(file)
                    print(f"添加根文件: {file}")

        print(f"\\n发布包创建完成: fnos.zip")

        # 显示包内容
        print("\\n发布包内容:")
        with zipfile.ZipFile('fnos.zip', 'r') as zipf_read:
            for name in sorted(zipf_read.namelist()):
                print(f"  {name}")

        # 验证包结构
        print("\\n结构验证:")
        with zipfile.ZipFile('fnos.zip', 'r') as zipf_read:
            files = zipf_read.namelist()
            if '__init__.py' in files and 'manifest.json' in files:
                print("  ✅ 包含必需的 __init__.py 和 manifest.json")
            else:
                print("  ❌ 缺少必需文件！")
                return False

        print(f"\\n发布包大小: {os.path.getsize('fnos.zip'):,} 字节")

        if version:
            print(f"版本: v{version}")
            print(f"\n下一步: 将 fnos.zip 上传到 GitHub Release v{version}")

        return True

    except Exception as e:
        print(f"创建发布包时出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    parser = argparse.ArgumentParser(description='创建 FNOS 集成发布包')
    parser.add_argument('--version', '-v', help='版本号 (如: 1.2.2)')
    parser.add_argument('--check', '-c', action='store_true', help='只检查当前状态')

    args = parser.parse_args()

    if args.check:
        print("检查当前发布包状态...")
        if os.path.exists('fnos.zip'):
            print(f"✅ fnos.zip 已存在 (大小: {os.path.getsize('fnos.zip'):,} 字节)")
            print("\n发布包内容:")
            try:
                with zipfile.ZipFile('fnos.zip', 'r') as zipf:
                    for name in sorted(zipf.namelist()):
                        print(f"  {name}")
            except Exception as e:
                print(f"读取 zip 文件时出错: {e}")
        else:
            print("❌ fnos.zip 不存在")
        return

    success = create_release_zip(args.version)

    if success:
        print("\n🎉 发布包创建成功！")
        print("\n使用步骤:")
        print("1. 上传到 GitHub Release")
        print("2. 在 HACS 中测试安装")
        print("3. 重启 Home Assistant")
    else:
        print("\n❌ 发布包创建失败")
        sys.exit(1)

if __name__ == "__main__":
    main()