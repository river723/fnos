# FNOS Home Assistant 插件

这是一个为 Home Assistant 设计的自定义集成插件，用于监控和管理运行 FNOS 系统的设备。通过此插件，您可以监控系统资源使用情况，并远程控制您的 FNOS 设备。

## 功能特性

### 系统监控
- CPU 使用率监控
- 内存使用率监控
- 磁盘使用率监控
- 网络上传/下载速度监控
- 系统运行时间监控
- CPU 温度监控

### 远程控制
- 远程重启设备
- 远程关闭设备

## 安装方法

### 方法一：通过 HACS 安装（推荐）

#### 1. 添加自定义仓库到 HACS

1. 打开 Home Assistant > 进入 **HACS**
2. 点击右上角 `...` > 选择 **“高级设置” (Settings)**
3. 滚动到底部找到 **“自定义存储库” (Custom repositories)**
4. 输入以下内容：
   - URL: `https://github.com/river723/fnos`
   - 类型: `Integration`
5. 点击 **添加**

#### 2. 安装集成

1. 返回 HACS 主页 > 点击 **"Explore & Add Repositories"**
2. 搜索 `fnos` 或查看已加入的仓库
3. 点击对应条目 > 点击 **Install** 安装
4. 安装完成后，重启 Home Assistant

#### 3. 添加集成

1. 进入：
   ```
   配置 > 设备与服务 > 添加集成 (+)
   ```
2. 搜索并选择 `Fnos Monitor`
3. 填写配置信息（主机地址、端口、用户名、密码等）
4. 提交后即可在实体中看到传感器数据

---
### 方法二：手动安装

1. 将 `fnos` 文件夹复制到 Home Assistant 配置目录下的 `custom_components` 文件夹中：
   ```
   <config_directory>/custom_components/fnos/
   ```

2. 重启 Home Assistant

## 配置步骤

1. 在 Home Assistant 中添加集成：
   - 进入 设置 → 设备与服务 → 集成
   - 点击 "添加集成"
   - 搜索并选择 "FNOS"

2. 在配置对话框中填写以下信息：
   - **主机地址** (host)：FNOS 设备的 IP 地址
   - **用户名** (username)：SSH 登录用户名
   - **密码** (password)：SSH 登录密码
   - **端口** (port)：SSH 端口号（默认为 22）

3. 可选配置：
   - **扫描间隔** (scan_interval)：数据更新间隔（默认为 300 秒）

## 传感器说明

集成将创建以下传感器：

| 传感器名称 | 单位 | 图标 | 说明 |
|------------|------|------|------|
| CPU Usage | % | `mdi:cpu-64-bit` | CPU 使用率 |
| Memory Usage | % | `mdi:memory` | 内存使用率 |
| Disk Usage | % | `mdi:harddisk` | 磁盘使用率 |
| Download Speed | MB/s | `mdi:download` | 网络下载速度 |
| Upload Speed | MB/s | `mdi:upload` | 网络上传速度 |
| System Uptime | hours | `mdi:clock-start` | 系统运行时间 |
| CPU Temperature | °C | `mdi:thermometer` | CPU 温度 |

## 控制实体

集成还提供以下控制实体：

- **重启设备** 按钮 - 用于远程重启 FNOS 设备
- **关闭设备** 按钮 - 用于远程关闭 FNOS 设备

## 工作原理

该插件通过 SSH 连接到 FNOS 设备并执行系统命令来获取状态信息：

1. 使用 paramiko 库建立 SSH 连接
2. 执行 Linux 系统命令收集硬件和系统信息
3. 解析命令输出并转换为 Home Assistant 传感器数据
4. 提供按钮实体用于执行远程控制命令

## 依赖项

- `paramiko>=2.7.2` - 用于 SSH 连接

## 注意事项

- 确保 FNOS 设备已启用 SSH 服务
- 提供的凭据需要有足够的权限执行相关命令
- 出于安全考虑，建议在防火墙中限制对 SSH 端口的访问
- 传感器更新频率不宜过高，以免对系统性能造成影响

## 故障排除

如果遇到连接问题，请检查：

1. FNOS 设备的 SSH 服务是否正常运行
2. 提供的主机地址、端口、用户名和密码是否正确
3. 网络连接是否正常
4. 防火墙设置是否允许 SSH 连接

查看 Home Assistant 日志可获取更多调试信息。
