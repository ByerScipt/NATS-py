import asyncio
import nats
import logging
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument(
    '--log', 
    default='log', 
    type=str, 
    help='用于保存原始日志文件的根目录 (默认为log)'
)
args = parser.parse_args()

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - [Listener] - %(message)s'
)

async def message_handler(msg):
    """
    回调函数，只负责将收到的原始消息内容，根据主题写入文件。
    """
    try:
        #为了避免通配符'>'或'*'成为文件名，做一个替换
        subject_for_filename = msg.subject.replace('>', '_wildcard_')
        filename = os.path.join(args.log, f"{subject_for_filename}.log")
        os.makedirs(args.log, exist_ok=True)
        raw_message_content = msg.data.decode('utf-8', errors='ignore')
        with open(filename, "a", encoding='utf-8') as f:
            f.write(raw_message_content + "\n")
            
        logging.info(f"已将来自 '{msg.subject}' 的原始消息存入 '{filename}'")
        
    except Exception as e:
        logging.error(f"处理主题 '{msg.subject}' 的消息时发生错误: {e}")

async def main():
    """ 
    主函数，连接到NATS服务器并订阅指定主题。
    """
    nats_url = "nats://47.108.226.49:4222"
    subject_to_listen = "anomaly_light_data"

    logging.info(f"正在尝试连接到NATS服务器: {nats_url} ...")
    nc = await nats.connect(nats_url)
    logging.info(f"成功连接到NATS，准备监听主题 '{subject_to_listen}'...")

    await nc.subscribe(subject_to_listen, cb=message_handler)

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        logging.info("收到退出信号...")
    finally:
        await nc.close()
        logging.info("NATS连接已关闭。")

if __name__ == '__main__':
    asyncio.run(main())