import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def get_history(session_id: str):
    key = f"chat:{session_id}"
    history = r.get(key)
    return json.loads(history) if history else []

def save_message(session_id: str, role: str, content: str):
    key = f"chat:{session_id}"
    history = get_history(session_id)
    history.append({"role": role, "content": content})
    r.set(key, json.dumps(history), ex=3600)  # ex=3600 = TTL 1 jam
