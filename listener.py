import asyncio
import nats
import json
import logging
import argparse
import os
import datetime

# 命令行设置路口ID
parser = argparse.ArgumentParser(
    description='NATS Traffic Data Listener: 监听指定路口的交通数据。'
)
parser.add_argument(
    'intersection_id', 
    nargs='?', 
    default='>', 
    type=str, 
    help='要监听的路口ID或通配符 (例如: intersection_1_1, *, >)。默认为 ">"，监听所有。'
)
args = parser.parse_args()

# 读取配置文件
with open('nats_config.json', 'r') as f:
    config = json.load(f)

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def message_handler(msg):
    """
    回调函数，用于处理接收到的消息
    """
    data = msg.data.decode()
    data = json.loads(data)
    logging.info(f"Received message on subject {msg.subject}: {data}")

    try:
        output_dir = 'log'
        os.makedirs(output_dir, exist_ok=True)  # 确保输出目录存在
        # 1. 从消息主题中，解析出路口ID
        #    例如: 从 "dev.traffic.test.intersection_1_1" 中，提取出 "intersection_1_1"
        intersection_id = msg.subject.split('.')[-1]
        
        # 2. 根据路口ID动态生成文件名
        filename = os.path.join(output_dir, f"{intersection_id}.log")
        
        # 3. 解码、解析并写入到对应的文件中
        data_str = msg.data.decode()

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
        level = "INFO"
        log_line = f"{timestamp} - {level} - {data_str}\n"
        
        logging.info(f"Message from subject '{msg.subject}' received, writing to '{filename}'")
        
        with open(filename, "a", encoding='utf-8') as f:
            f.write(log_line)
            
    except Exception as e:
        logging.error(f"Failed to process message from subject '{msg.subject}': {e}")


async def main():
    # 读取配置
    nats_url = config['NATS']['URL']
    subject_prefix = config['NATS']['SUBJECT_PREFIX']
    subject = f"{subject_prefix}.{args.intersection_id}"

    logging.info(f"Connecting to NATS server at {nats_url}")
    nc = await nats.connect(nats_url)
    logging.info(f"Successfully connected to NATS server, subscribing to subject {subject}")

    await nc.subscribe(subject, cb=message_handler)

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        logging.info("Listener stopped by user")
    finally:
        await nc.close()
        logging.info("Connection to NATS server closed")

    pass

if __name__ == "__main__":
    asyncio.run(main())