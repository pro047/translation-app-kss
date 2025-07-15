from .sentence_queue import SentenceQueueManager


class SessionMessageHandler:
    def __init__(self):
        self.queue_manager = SentenceQueueManager()

    def handle_message(self, data, websocket):
        msg_type = data.get("type")

        if msg_type == "session":
            self.handle_session_control(data)
        elif msg_type == "transcript":
            self.handle_transcript(data, websocket)
        else:
            print(f'알 수 없는 메시지 타입 : {msg_type}')

    def handle_session_control(self, data):
        session_id = data.get("sessionId")
        action = data.get("action")

        if action == "start":
            self.queue_manager.init_session(session_id)
            print(f"session start : {session_id}")
        elif action == "stop":
            self.queue_manager.clear_session(session_id)
            print(f"session stop : {session_id}")
        else:
            print(f'알 수 없는 action : {action}')

    def handle_transcript(self, data, websocket):
        session_id = data.get('sessionId')
        text = data.get("text", "")

        if not session_id or not text:
            print('텍스트 누락')
            return
        self.queue_manager.add_text(websocket, session_id, text)
