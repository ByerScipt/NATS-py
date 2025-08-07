import asyncio
import nats
import json
import time
import random
import datetime
import logging

# 1. NATS服务器的URL
NATS_URL = "nats://47.108.226.49:4222" 

# 2. 要发布到的主题
TARGET_SUBJECT = "anomaly_light_data"

# 3. 要模拟的路口ID
TARGET_INTERSECTION_ID = "My_Local_PC_Test" 

# 4. 消息发布的间隔时间（秒）
PUBLISH_INTERVAL = 1
# ---------------------------------------------

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - [LocalPublisher] - %(message)s')

def create_structured_log_message(inter_id):
    """
    创建一个结构化的、模仿真实算法输出的日志消息。
    """
    log_levels = ["INFO", "DEBUG", "WARNING"]
    level = random.choice(log_levels)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
    
    message_payload = {
        "algo_return": random.randint(1, 4),
        "details": f"This is a test message from {inter_id}",
        "waiting_vehicles_total": random.randint(0, 100)
    }
    
    structured_message = {
        "timestamp": timestamp,
        "level": level,
        "intersection_id": inter_id,
        "message": message_payload
    }
    
    return json.dumps(structured_message).encode('utf-8')

async def main():
    """
    主函数：连接到NATS服务器，并使用内置配置循环发布消息。
    """
    
    logging.info(f"正在尝试连接到NATS服务器: {NATS_URL} ...")
    try:
        nc = await nats.connect(NATS_URL)
        logging.info("成功连接到NATS服务器！")
    except Exception as e:
        logging.error(f"无法连接到NATS服务器: {e}")
        return

    try:
        logging.info(f"发布者已启动，将为路口 '{TARGET_INTERSECTION_ID}' 发布数据到主题 '{TARGET_SUBJECT}'。按 Ctrl+C 停止。")
        while True:
            payload = create_structured_log_message(TARGET_INTERSECTION_ID)
            await nc.publish(TARGET_SUBJECT, payload)
            logging.info(f"成功发布一条数据 (大小: {len(payload)} bytes)")
            await asyncio.sleep(PUBLISH_INTERVAL)
            
    except KeyboardInterrupt:
        logging.info("收到退出信号...")
    finally:
        await nc.close()
        logging.info("NATS连接已关闭。")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"程序启动失败: {e}")