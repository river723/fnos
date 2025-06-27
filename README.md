以下是根据你的项目结构和功能，重新编写并补充 **通过 HACS 安装** 内容后的 `README.md`：

---

# 📦 FNOS Home Assistant 集成

这是一个用于监测飞牛 NAS（FNOS）状态的 Home Assistant 自定义集成。它支持加载以下平台：

- **sensor**：获取 CPU、内存、磁盘使用率、温度、网络速度等信息
- **button / switch**（可选）：提供控制功能（如关机、重启）

---

## ✅ 支持的安装方式

你可以通过以下两种方式安装该集成：

---

### 🚀 方式一：通过 HACS 安装（推荐）



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

### 💾 方式二：手动安装

#### 1. 下载项目文件

克隆或下载本项目，并将 `fnos` 文件夹复制到 Home Assistant 的自定义组件目录中：

```bash
custom_components/fnos/
```

确保包含以下关键文件：
- [__init__.py](file:///home/hwg/ha_dev/config/custom_components/fnos/__init__.py)
- [manifest.json](file:///home/hwg/ha_dev/config/custom_components/fnos/manifest.json)
- [const.py](file:///home/hwg/ha_dev/config/custom_components/fnos/const.py)
- [coordinator.py](file:///home/hwg/ha_dev/config/custom_components/fnos/coordinator.py)
- [sensor.py](file:///home/hwg/ha_dev/config/custom_components/fnos/sensor.py)
- [button.py](file:///home/hwg/ha_dev/config/custom_components/fnos/button.py)（如有）

> ⚠️ 如果没有启用开发者模式，请在 Home Assistant 设置中开启“开发者选项”。

---

#### 2. 添加集成

1. 在 Home Assistant 界面中，进入：
   ```
   配置 > 设备与服务
   ```
2. 点击右下角 **添加集成 (+)**。
3. 搜索并选择你的集成名称（如 `Fnos Monitor`）。
4. 根据提示填写必要的配置信息（如主机地址、认证凭据等）。
5. 点击 **提交** 完成配置。

---

#### 3. 查看传感器和按钮实体

集成成功后，Home Assistant 会自动加载以下平台：

- **sensor**：显示从设备获取的数据（如 CPU 使用率、内存、磁盘、温度、网络速度等）
- **button**（可选）：提供操作按钮（如关机、重启）

你可以在以下位置查看它们：

- **设备与服务** 查看设备及关联实体
- **开发者工具 > 实体** 查看所有实体 ID

---

#### 4. 卸载集成

如需卸载该集成：

1. 进入 **配置 > 设备与服务**
2. 找到对应的 `Fnos Monitor` 集成
3. 点击右侧三个点 `...` > 选择 **删除**
4. 确认卸载即可

---

## 🧪 支持的功能

| 功能 | 描述 |
|------|------|
| 📊 实时监控 | 获取 FNOS 的 CPU、内存、磁盘、温度、网络等指标 |
| ⚙️ 配置流支持 | 支持通过 HA UI 配置连接参数 |
| 🔄 自动刷新 | 数据定时刷新（默认每 5 分钟一次，可在配置中调整） |
| 🔘 控制按钮（可选） | 如支持，可通过按钮执行关机、重启等操作 |

---

## 📄 版本历史

| 版本 | 更新内容 |
|------|----------|
| v0.6 | 新增 disk IO 和 disk temperature 监控 |
| v0.5 | 初始版本，支持基本系统监控功能 |

---

## ❓ 问题反馈

如果你遇到任何问题，欢迎前往 GitHub Issues 页面提交反馈：

🔗 [GitHub Issues](https://github.com/river723/fnos/issues)

---

## 📝 致谢

感谢 [Home Assistant 社区](https://community.home-assistant.io/) 和 [HACS](https://hacs.xyz/) 提供的生态系统支持。

--- 

如需我帮你生成一个完整的 [hacs.json](file:///home/hwg/ha_dev/hacs.json) 或打包 zip 文件模板以便发布，也可以告诉我！