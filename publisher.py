import asyncio 
import nats
import json
import time
import logging
import random
import argparse

# 命令行设置路口ID
parser = argparse.ArgumentParser(
    description='NATS Traffic Data Publisher: 为指定路口发布模拟交通数据。'
)

parser.add_argument(
    'intersection_id', 
    type=str, 
    help='需要模拟数据的路口ID (例如: intersection_1_1 或 BDL_QHDD)'
)
args = parser.parse_args()

# 读取配置文件
with open('nats_config.json', 'r') as f:
    config = json.load(f)

# 设置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_traffic_state():
    """
    模拟交通相位字典
    """
    # 12个基础相位
    directions = ["WN","WE","WS","ES","EW","EN","NE","NS","NW","SN","SE","SW"]
    waiting_vehicles = {direction: random.randint(0, 25) for direction in directions}
    running_vehicles = {direction: random.randint(0, 10) for direction in directions}
    state = {
        args.intersection_id: {
            "waiting_vehicles": waiting_vehicles,
            "running_vehicles": running_vehicles,
            "timestamp": int(time.time())
        }
    }
    return json.dumps(state).encode()

async def main():
    """
    主函数，连接到NATS服务器并循环发布消息
    """
    # 读取配置
    nats_url = config['NATS']['URL']
    subject_prefix = config['NATS']['SUBJECT_PREFIX']
    interval = int(config['PUBLISHER']['INTERVAL'])

    logging.info(f"Connecting to NATS server at {nats_url}")
    nc = await nats.connect(nats_url)
    logging.info("Connected to NATS server")

    subject = f"{subject_prefix}.{args.intersection_id}"

    try:
        logging.info("Starting to publish traffic states, press Ctrl+C to stop")
        while True:
            # 生成交通状态
            traffic_state = generate_traffic_state()
            # 发布消息到指定主题
            await nc.publish(subject, traffic_state)
            # 打印日志
            logging.info(f"Published message to {subject}: {traffic_state.decode()}")
            # 等待interval秒钟
            await asyncio.sleep(interval)
    except KeyboardInterrupt:
        logging.info("Publisher stopped by user")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        await nc.close()
        logging.info("Connection to NATS server closed")

if __name__ == "__main__":
    asyncio.run(main())
    