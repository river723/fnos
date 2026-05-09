# FNOS 集成打包指南

本文档介绍如何使用打包脚本创建符合 HACS 要求的发布包。

## 快速开始

### 1. 创建发布包

```bash
# 创建发布包（使用默认版本）
python3 build_release.py

# 创建指定版本的发布包
python3 build_release.py --version 1.2.2
```

### 2. 检查现有发布包

```bash
# 检查当前 fnos.zip 的状态
python3 build_release.py --check
```

## 脚本功能

### build_release.py

自动创建符合 HACS 要求的 `fnos.zip` 文件：

- ✅ 自动打包 `custom_components/fnos/` 目录内容
- ✅ 排除 `.pyc` 和 `__pycache__` 等临时文件
- ✅ 包含必要的根目录文件（README.md, hacs.json 等）
- ✅ 验证包结构完整性
- ✅ 显示详细的打包过程

### 使用方法

```bash
# 显示帮助信息
python3 build_release.py --help

# 基本使用
python3 build_release.py

# 指定版本号
python3 build_release.py --version 1.2.2

# 检查现有发布包
python3 build_release.py --check
```

## 发布流程

### 1. 准备工作

```bash
# 确保所有更改已提交到 git
git status
git add .
git commit -m "更新功能"
git push origin master
```

### 2. 创建发布包

```bash
# 创建发布包
python3 build_release.py --version 1.2.2
```

### 3. 更新版本信息

```bash
# 如果需要，更新 hacs.json 中的版本号
# 然后重新创建发布包
python3 build_release.py --version 1.2.2
```

### 4. 创建 GitHub Release

1. 访问 GitHub 仓库：https://github.com/river723/fnos/releases
2. 点击 "Draft a new release"
3. 创建新标签（如 `v1.2.2`）或选择现有标签
4. 上传 `fnos.zip` 文件
5. 添加发布说明
6. 发布 Release

### 5. 测试安装

1. 在 Home Assistant 的 HACS 中添加自定义仓库
2. 搜索并安装 FNOS Monitor
3. 重启 Home Assistant
4. 验证集成是否正常工作

## 文件结构说明

### 生成的 zip 文件结构

```
fnos.zip
├── __init__.py          # 集成主文件
├── manifest.json        # 集成清单文件
├── sensor.py            # 传感器组件
├── button.py            # 按钮组件
├── coordinator.py       # 数据协调器
├── devices.py           # 设备通信
├── config_flow.py       # 配置流程
├── const.py             # 常量定义
├── entities.py          # 实体基类
├── disk_coordinator.py  # 磁盘监控协调器
├── static/
│   └── icons/
│       ├── fnos.ico
│       ├── fnos.png
│       └── fnos.svg
├── README.md            # 项目文档
├── hacs.json            # HACS 配置
├── info.md              # HACS 信息
└── .hacs.json           # HACS 仓库配置
```

### HACS 安装后结构

```
custom_components/
└── fnos/
    ├── __init__.py
    ├── manifest.json
    ├── sensor.py
    ├── button.py
    └── ...其他文件
```

## 常见问题

### Q: 为什么 zip 文件不包含 `fnos/` 目录？

A: HACS 会自动创建 `custom_components/fnos/` 目录，所以 zip 文件应该直接包含 fnos 目录的内容，而不是再包装一层 fnos 目录。

### Q: 如何更新版本号？

A: 
1. 更新 `hacs.json` 中的 `"version"` 字段
2. 重新运行打包脚本：`python3 build_release.py --version x.x.x`
3. 创建新的 GitHub Release

### Q: 打包脚本会包含哪些文件？

A: 打包脚本会自动包含：
- `custom_components/fnos/` 目录下的所有 `.py` 文件
- 静态资源文件（icons 等）
- 根目录的文档和配置文件
- 自动排除 `.pyc`、`__pycache__` 等临时文件

## 自动化建议

### 创建发布脚本

```bash
#!/bin/bash
# release.sh

VERSION=$1
if [ -z "$VERSION" ]; then
    echo "请指定版本号，例如: ./release.sh 1.2.2"
    exit 1
fi

echo "开始发布版本 v$VERSION..."

# 更新 hacs.json 版本号
sed -i "s/\"version\": \"[^\"]*\"/"version\": \"$VERSION\"/g" hacs.json

# 创建发布包
python3 build_release.py --version $VERSION

# 提交更改
git add .
git commit -m "发布版本 v$VERSION"
git push origin master

echo ""
echo "发布包创建完成！"
echo "请手动创建 GitHub Release 并上传 fnos.zip"
```

保存为 `release.sh` 并运行：`./release.sh 1.2.2`