# coordinator.py

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
import paramiko
import backoff
import time
from datetime import timedelta
import logging

_LOGGER = logging.getLogger(__name__)

# 定义远程执行的 shell 命令
SHELL_COMMAND = r'''
echo "CPU:$(top -b -n1 | fgrep "Cpu(s)" | tail -1 | awk -F'id,' '{split($1, vs, ","); v=vs[length(vs)]; sub(/\s+/, "", v);sub(/\s+/, "", v); printf "%s", 100-v; }');
MEMORY:$(free | awk 'NR==2{printf "%.1f", $3/$2 * 100}');
DISK:$(df --output=pcent / | awk 'NR==2{print $1}' | tr -d '%');
NET:$(cat /proc/net/dev | grep ens18 | awk '{print $2, $10}');
UPTIME:$(cat /proc/uptime | awk '{printf "%d", $1/3600}');
CPU_TEMP:$(sensors | grep -m 1 'Package id 0' | awk '{print substr($4, 2)}' | tr -d '°C' || echo 0);
DISK_INFO:$(lsblk -d -o NAME,SIZE --json);
DISK_IO:$(cat /proc/diskstats);
DISK_TEMPS:$(for disk in $(lsblk -d -o NAME | grep sd); do echo -n "$disk:"; sudo smartctl -A /dev/$disk | grep Temperature_Celsius | awk '{print $10}' || echo 0; done)"
'''

class FnosDataCoordinator(DataUpdateCoordinator):
    """主协调器：通过 SSH 获取远程服务器状态数据（CPU、内存、网络等）"""

    def __init__(self, hass, config_entry):
        super().__init__(
            hass,
            _LOGGER,
            name="FnosDataCoordinator",
            update_interval=timedelta(seconds=config_entry.options.get("scan_interval", 300)),
        )
        self.config_entry = config_entry
        self.ssh = None
        self._last_net_stats = None
        self._last_update_time = None
        self._last_disk_io = None

    async def connect_ssh(self):
        if self.ssh and self._is_ssh_active():
            return

        try:
            if self.ssh:
                self.ssh.close()
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            host = self.config_entry.data["host"]
            port = self.config_entry.data.get("port", 22)
            username = self.config_entry.data["username"]
            password = self.config_entry.data.get("password")

            await self.hass.async_add_executor_job(
                self.ssh.connect, host, port, username, password, None, None, None, 10
            )
            _LOGGER.debug("SSH连接成功")

        except Exception as e:
            _LOGGER.error("SSH连接失败: %s", e)
            self.ssh = None
            raise

    def _is_ssh_active(self):
        return self.ssh and self.ssh.get_transport() and self.ssh.get_transport().is_active()

    @backoff.on_exception(backoff.expo, (paramiko.SSHException, ConnectionResetError), max_tries=3)
    async def _async_update_data(self):
        try:
            await self.connect_ssh()

            stdin, stdout, stderr = await self.hass.async_add_executor_job(
                self.ssh.exec_command,
                SHELL_COMMAND
            )

            output = stdout.read().decode().strip()
            _LOGGER.debug("命令输出: %s", output)

            data = self._parse_output(output)
            self._last_update_time = time.time()

            return data

        except Exception as e:
            _LOGGER.error("数据获取失败: %s", e, exc_info=True)
            self.ssh = None
            raise

    def _parse_output(self, output):
        data = {}
        parsers = {
            "DISK_INFO": self._parse_disk_info,
            "DISK_IO": self._parse_disk_io,
            "DISK_TEMPS": self._parse_disk_temps,
            "UPTIME": self._parse_uptime,
            "CPU_TEMP": self._parse_cpu_temp,
            "NET": self._parse_net_stats,
            "DISK": self._parse_disk_usage,     # 新增
            "MEMORY": self._parse_memory_usage, # 新增
        }

        for item in output.split(";"):
            if ":" in item:
                key, value = item.split(":", 1)
                parser = parsers.get(key.strip())
                if parser:
                    parser(data, value.strip())
                else:
                    try:
                        data[key.lower()] = float(value.strip())
                    except ValueError:
                        _LOGGER.warning(f"无法解析数据项: {item}")
        return data

    def _parse_disk_info(self, data, value):
        try:
            import json
            disk_info = json.loads(value)
            data["disk_info"] = disk_info.get("blockdevices", [])
        except Exception as e:
            _LOGGER.warning("解析 DISK_INFO 失败: %s", e)

    def _parse_disk_io(self, data, value):
        lines = value.strip().split("\n")
        io_stats = {}
        interval=1
        for line in lines:
            parts = line.split()
            if len(parts) > 13:
                device = parts[2]
                read_sectors = int(parts[5])
                write_sectors = int(parts[9])
                io_stats[device] = (read_sectors, write_sectors)

        now = time.time()
        speeds = {}

        if self._last_disk_io and self._last_update_time:
            interval = max(now - self._last_update_time, 300)

            for dev, (r, w) in io_stats.items():
                last_r, last_w = self._last_disk_io.get(dev, (0, 0))
                try:
                    read_speed = round((r - last_r) * 512 / interval / 1_000_000, 2)
                    write_speed = round((w - last_w) * 512 / interval / 1_000_000, 2)

                    # 添加合理性判断（比如单次读取不能超过 10GB 扇区变化）
                    if abs(r - last_r) > 20_000_000:  # 超过 10GB 扇区变化，不合理
                        _LOGGER.warning(f"检测到不合理扇区变化（{dev}）: {abs(r - last_r)} sectors")
                        speeds[dev] = (0.0, 0.0)
                    else:
                        speeds[dev] = (read_speed, write_speed)
                except Exception as e:
                    _LOGGER.warning(f"计算磁盘 {dev} 速度失败: {e}")
                    speeds[dev] = (0.0, 0.0)
        else:
            _LOGGER.debug("首次更新，不计算磁盘 IO 速度")

 

        data["disk_speeds"] = speeds
        self._last_disk_io = io_stats
        

        # 调试日志
        # _LOGGER.debug("本次磁盘IO: %s", io_stats)
        # _LOGGER.debug("上次磁盘IO: %s", self._last_disk_io)
        _LOGGER.debug("时间间隔: %.2f 秒", interval)
        
    

    def _parse_disk_temps(self, data, value):
        temps = {}
        for line in value.strip().split("\n"):
            if ":" in line:
                disk, temp = line.split(":", 1)
                try:
                    temps[disk.strip()] = float(temp.strip())
                except ValueError:
                    temps[disk.strip()] = None
        data["disk_temps"] = temps

    def _parse_uptime(self, data, value):
        try:
            data["uptime"] = int(value.strip())
        except ValueError:
            data["uptime"] = None

    def _parse_cpu_temp(self, data, value):
        try:
            data["cpu_temp"] = float(value.strip())
        except (ValueError, TypeError):
            data["cpu_temp"] = None

    def _parse_net_stats(self, data, value):
        try:
            rx_bytes, tx_bytes = map(int, value.strip().split())
            now = time.time()
            if self._last_net_stats and self._last_update_time:
                interval = now - self._last_update_time
                data["download_speed"] = round(
                    (rx_bytes - self._last_net_stats[0]) * 512 / interval / 1_000_000, 2
                )
                data["upload_speed"] = round(
                    (tx_bytes - self._last_net_stats[1]) * 512 / interval / 1_000_000, 2
                )
            self._last_net_stats = (rx_bytes, tx_bytes)
            # self._last_update_time = now
        except Exception as e:
            _LOGGER.warning("解析 NET 失败: %s", e)

    def _parse_disk_usage(self, data, value):
        try:
            data["disk"] = float(value.strip())
        except (ValueError, TypeError):
            data["dis"] = None
            _LOGGER.warning("解析 DISK 失败: %s", value)

    def _parse_memory_usage(self, data, value):
        try:
            data["memory"] = float(value.strip())
        except (ValueError, TypeError):
            data["memory"] = None
            _LOGGER.warning("解析 MEMORY 失败: %s", value)

    async def shutdown(self):
        if self.ssh:
            await self.hass.async_add_executor_job(self.ssh.close)
            _LOGGER.debug("SSH连接已关闭")