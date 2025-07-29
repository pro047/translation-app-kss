import asyncio
import json
import kss
import threading
import time


class SentenceQueueManager:
    def __init__(self):
        self.session_queues = {}
        self.buffer = {}
        self.lock = threading.Lock()
        self.websocket = {}
        self.session_timestamps = {}
        self.loop = asyncio.get_event_loop()

        threading.Thread(target=self._flush_timeout_loop, daemon=True).start()

    def init_session(self, session_id):
        self.session_queues[session_id] = []
        self.buffer[session_id] = ''

        print(f'session init : {session_id}')

    def clear_session(self, session_id):
        if session_id in self.session_queues:
            del self.session_queues[session_id]
            del self.buffer[session_id]
            del self.session_timestamps[session_id]
            self.websocket.pop(session_id, None)
            print(f"session delete : {session_id}")
        else:
            print(f'sessio not found : {session_id}')

    def add_transcript(self, websocket, session_id: str, trasncript: str):
        if session_id not in self.session_queues:
            print(f"session {session_id} is not found => ignore")
            return

        self.session_queues[session_id].append(trasncript)

        with self.lock:
            self.buffer[session_id] += f" {str(trasncript).strip()}"
            self.session_timestamps[session_id] = time.time()
            self.websocket[session_id] = websocket
            print("📕 trasncript :", trasncript)
            self.extract_and_queue_sentences(websocket, session_id)

    def extract_and_queue_sentences(self, websocket, session_id: str):
        try:
            buffer_trasncript = str(self.buffer[session_id]).strip()
            sentences = kss.split_sentences(buffer_trasncript)

            if not sentences:
                return []

            if len(sentences) > 1:
                *complete, remain = sentences
            else:
                complete = []
                remain = sentences[0] if sentences else ""

            self.buffer[session_id] = remain

            for s in complete:
                sentence = s.strip()
                print(f"✅ sentence : {sentence}")
                if sentence:
                    asyncio.run_coroutine_threadsafe(
                        websocket.send(json.dumps({
                            "sessionId": session_id,
                            "sentence": sentence
                        })),
                        asyncio.get_event_loop()
                    )
        except Exception as e:
            print('문장 분리 오류:', str(e))

    def _flush_timeout_loop(self):
        while True:
            time.sleep(1.0)
            now = time.time()
            with self.lock:
                for session_id in list(self.buffer.keys()):
                    last_time = self.session_timestamps.get(session_id, 0)
                    if now - last_time > 5.0 and self.buffer[session_id].strip():
                        sentence = self.buffer[session_id].strip()
                        print(f'timeout flush : {sentence}')
                        self.buffer[session_id] = ''
                        ws = self.websocket.get(session_id)
                        if ws != None:
                            try:
                                asyncio.run_coroutine_threadsafe(
                                    ws.send(json.dumps({
                                        "sessionId": session_id,
                                        "sentence": sentence
                                    })),
                                    self.loop
                                )
                            except Exception as e:
                                print('timeout flush error : ', e)
