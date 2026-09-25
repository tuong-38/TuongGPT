import json
import shutil
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from langchain_core.messages import HumanMessage, ToolMessage

from database import (
    init_db,
    create_or_update_conversation,
    list_conversations,
    get_chat_history,
    save_chat_message,
    delete_conversation_by_thread_id
)
from tools import set_current_thread_id
from rag import add_document_to_rag
from agent import get_agent

init_db()

app = FastAPI(title="TuongGPT API")
templates = Jinja2Templates(directory="templates")


def extract_text_content(content) -> str:
    """Trích xuất chuỗi văn bản thuần túy từ content của LangChain/Gemini."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        extracted = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                extracted.append(part.get("text", ""))
            elif isinstance(part, str):
                extracted.append(part)
        return "".join(extracted)
    return ""


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/conversations")
def api_get_conversations():
    conversations = list_conversations()
    return [
        {
            "thread_id": conv.thread_id,
            "title": conv.title,
            "updated_at": conv.updated_at.isoformat() if conv.updated_at else ""
        }
        for conv in conversations
    ]


@app.delete("/api/conversations/{thread_id}")
def api_delete_conversation(thread_id: str):
    success = delete_conversation_by_thread_id(thread_id)
    return {"status": "success" if success else "error"}


@app.get("/api/chat-history/{thread_id}")
def api_get_history(thread_id: str):
    history = get_chat_history(thread_id)
    return [{"role": msg.role, "content": msg.content} for msg in history]


@app.post("/api/upload")
async def api_upload_file(file: UploadFile = File(...), thread_id: str = Form(...)):
    save_path = Path("uploads") / file.filename
    save_path.parent.mkdir(exist_ok=True)
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = add_document_to_rag(str(save_path), thread_id)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/chat-stream")
def api_chat_stream(thread_id: str, message: str, model_name: str = "gemini-3.5-flash-lite"):
    set_current_thread_id(thread_id)
    create_or_update_conversation(thread_id, first_message=message)
    save_chat_message(thread_id, role="user", content=message)

    agent = get_agent(model_name)
    config = {"configurable": {"thread_id": thread_id}}

    def event_generator():
        full_content = ""
        try:
            for message_chunk, metadata in agent.stream(
                {"messages": [HumanMessage(content=message)]},
                config=config,
                stream_mode="messages"
            ):
                # Bỏ qua hoàn toàn dữ liệu thô do Tool trả về
                if isinstance(message_chunk, ToolMessage):
                    continue

                # Bỏ qua nếu chunk chỉ chứa lời gọi tool (tool calls)
                if getattr(message_chunk, "tool_call_chunks", None):
                    continue

                # Trích xuất nội dung văn bản thuần
                raw_content = getattr(message_chunk, "content", "")
                text_chunk = extract_text_content(raw_content)

                if text_chunk:
                    full_content += text_chunk
                    yield f"data: {json.dumps({'chunk': text_chunk})}\n\n"

            if full_content.strip():
                save_chat_message(thread_id, role="assistant", content=full_content)

            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")