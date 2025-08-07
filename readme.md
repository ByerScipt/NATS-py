# NATS 算法实时日志监听与归档服务 (NATS Real-time Log Listener)

本项目是一个基于 Python `asyncio` 和 `nats-py` 实现的轻量级NATS消息监听服务。可以订阅指定的NATS主题，接收来自算法系统的实时输出日志，并将其分类存储为日志文件。

## 功能特性 (Features)

-   **实时监听**: 异步IO架构，低延迟接收NATS消息流。
-   **自动归档**: 能够根据消息的主题（Subject）自动创建对应的日志文件，实现数据分类存储。
-   **目录管理**: 在写入日志前，会自动检查并创建所需的日志目录，无需手动干预。
-   **配置灵活**: 支持通过命令行参数自定义日志的存储根目录。

## 环境配置 (Environment Setup)

**1.确保Python版本**

建议使用Python3.10或更高版本
```bash
python3 --version
```

**2.安装依赖库**

本项目仅依赖nats-py库。
```bash
pip install nats-py
```

**3.启动NATS测试服务器**

本监听器是一个客户端程序，它需要连接到一个正在运行的NATS服务器才能工作。在开发和测试阶段，最便捷的方式是在本地或服务器上启动一个NATS实例。

**方法一：使用Docker（推荐）**

如果您本地或服务器上安装了Docker，这是最快、最干净的方式。

```bash
# 启动一个名为nats-dev的NATS服务器容器
# -d: 在后台运行
# --rm: 容器停止后自动删除
# -p 4222:4222: 将客户端端口映射出来
# -p 8222:8222: 将监控端口映射出来
docker run --rm -d -p 4222:4222 -p 8222:8222 --name nats-dev nats:latest
```

**方法二：直接运行二进制文件**

如果不使用Docker，也可以直接从NATS官网下载并运行。

1.访问 [NATS Server GitHub Releases](https://github.com/nats-io/nats-server/releases) 页面。

2.下载对应操作系统的最新版本（例如 ...-linux-amd64.zip）。

3.解压后，直接运行nats-server程序。

## 项目配置 (Configuration)

当前版本中，核心的参数直接在listener.py的main函数中进行配置。可以根据需要将其移至独立的配置文件中。

请打开 listener.py 并修改以下变量：

```python
# listener.py -> main()

async def main():
    # ...
    # 【配置项1】: NATS服务器的连接地址
    nats_url = "nats://47.108.226.49:4222"
    
    # 【配置项2】: 需要监听的NATS主题
    subject_to_listen = "anomaly_light_data"
    # ...
```

## 如何运行 (How to Run)
在已激活虚拟环境的终端中，进入项目根目录，然后执行以下命令：

**1. 启动监听服务（使用默认日志目录log）**

直接运行脚本，它将开始监听在代码中配置好的主题，并将日志保存在项目根目录下的log文件夹中。
```bash
python listener.py
```
预期输出:
```
2025-08-06 18:30:00,123 - INFO - [Listener] - 正在尝试连接到NATS服务器: nats://...
2025-08-06 18:30:00,125 - INFO - [Listener] - 成功连接到NATS，准备监听主题 'anomaly_light_data'...
# ... 当收到消息时 ...
2025-08-06 18:30:02,456 - INFO - [Listener] - 已将来自 'anomaly_light_data' 的原始消息存入 'raw_logs/anomaly_light_data.log'
```

**2.启动监听服务（自定义日志目录）**

可以使用--log参数来指定一个不同的文件夹来保存日志。
```bash
python listener.py --log /path/to/your/custom_logs
```
启动后，所有日志文件将被创建在/path/to/your/custom_logs目录下。

**3.启动数据发布器 (Publisher) (用于测试)**

publisher.py是一个独立的测试工具，位于tools文件夹，主要用来向NATS服务器发送模拟的算法输出消息。

修改以下变量：

```python
# tools/publisher.py

# 1. NATS服务器的URL
NATS_URL = "nats://47.108.226.49:4222" 

# 2. 要发布到的主题
TARGET_SUBJECT = "anomaly_light_data"
```

创建一个新的终端：
```bash
cd tools

python publisher.py
```


**4.停止运行**
```bash
Ctrl+C
```
