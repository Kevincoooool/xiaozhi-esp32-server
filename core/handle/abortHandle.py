import json
import logging

logger = logging.getLogger(__name__)


async def handleAbortMessage(conn):
    logger.info("Abort message received") 
    # 设置成打断状态
    conn.client_abort = True

    # 清空TTS队列中的待处理任务
    while not conn.tts_queue.empty():
        try:
            conn.tts_queue.get_nowait()
        except:
            pass

    # 添加发送空字符串显示
    await conn.websocket.send(json.dumps({
        "type": "tts",
        "state": "sentence_start", 
        "text": "",
        "session_id": conn.session_id
    }))

    # 打断屏显任务 
    conn.stop_all_tasks()
    await conn.websocket.send(json.dumps({
        "type": "tts", 
        "state": "stop",
        "session_id": conn.session_id
    }))
    conn.clearSpeakStatus()
    logger.info("Abort message received-end")
