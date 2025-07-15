import asyncio
import json
import kss
import threading


class SentenceQueueManager:
    def __init__(self):
        self.session_queues = {}
        self.buffer = {}
        self.lock = threading.Lock()

    def init_session(self, session_id):
        self.session_queues[session_id] = []
        self.buffer[session_id] = ''
        print(f'session init : {session_id}')

    def clear_session(self, session_id):
        if session_id in self.session_queues:
            del self.session_queues[session_id]
            del self.buffer[session_id]
            print(f"session delete : {session_id}")
        else:
            print(f'sessio not found : {session_id}')

    def add_text(self, websocket, session_id: str, text: str):
        if session_id not in self.session_queues:
            print(f"session {session_id} is not found => ignore")
            return

        self.session_queues[session_id].append(text)

        with self.lock:
            self.buffer[session_id] += f" {str(text).strip()}"
            print("📕 text :", text)
            self.extract_and_queue_sentences(websocket, session_id)

    def extract_and_queue_sentences(self, websocket, session_id: str):
        try:
            buffer_text = str(self.buffer[session_id]).strip()
            sentences = kss.split_sentences(buffer_text)

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

    # def get_next_sentence(self):
    #     try:
    #         return self.sentence_queue.get_nowait()
    #     except queue.Empty:
    #         return None
