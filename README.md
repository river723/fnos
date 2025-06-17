以下为该项目的使用方法，适用于 Home Assistant 集成：

---

### 📦 项目简介

该项目是一个 Home Assistant 自定义集成（custom integration），用于获取飞牛NAS(FNOS)的监测和控制。它支持加载 **sensor** 和 **switch** 平台。

---

### ✅ 使用步骤

#### 1. 安装集成

将整个文件夹（例如：`fnos`）复制到 Home Assistant 的自定义组件目录中：

```bash
custom_components/fnos/
```

确保包含以下关键文件：
- `__init__.py`
- `const.py`
- [sensor.py](file:///home/hwg/ha_dev/fnos/sensor.py)
- [switch.py](file:///home/hwg/ha_dev/fnos/switch.py)
- [config_flow.py](file:///home/hwg/ha_dev/fnos/config_flow.py)（如有）

> ⚠️ 如果没有启用开发者模式，请在 Home Assistant 设置中开启“开发者选项”。

---

#### 2. 添加集成

1. 在 Home Assistant 界面中，进入：
   ```
   配置 (Configuration) > 设备与服务 (Devices & Services)
   ```
2. 点击右下角 **添加集成 (+)**。
3. 搜索并选择你的集成名称（如 `Fnos`）。
4. 根据提示填写必要的配置信息（如主机地址、认证凭据等）。
5. 点击 **提交** 完成配置。


#### 3. 查看传感器和开关实体

集成成功后，Home Assistant 会自动加载以下平台：
- [sensor]显示从设备获取的数据（如温度、状态等）
- [switch]提供可控制的开关实体（如关闭和重启功能）

你可以在以下位置查看它们：
- **设备与服务 (Devices & Services)** 查看设备及关联实体
- **开发者工具 (Developer Tools) > 实体 (Entities)** 查看所有实体 ID


#### 4. 卸载集成

如需卸载该集成：

1. 进入 **配置 > 设备与服务**
2. 找到对应的 `Fnos` 集成
3. 点击右侧三个点 `...` > 选择 **删除**
4. 确认卸载即可
