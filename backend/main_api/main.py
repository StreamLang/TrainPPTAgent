import asyncio
import json
import re
import os
import dotenv
from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uuid
import httpx
from a2a.client import A2AClient
from a2a.types import (
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest
)
from outline_client import A2AOutlineClientWrapper
from content_client import A2AContentClientWrapper
dotenv.load_dotenv()

OUTLINE_API = os.environ["OUTLINE_API"]
CONTENT_API = os.environ["CONTENT_API"]
app = FastAPI()

# Allow CORS for the frontend development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AipptRequest(BaseModel):
    content: str
    language: str
    model: str
    stream: bool

class AipptContentRequest(BaseModel):
    content: str

class MaterialItem(BaseModel):
    id: str
    name: str
    description: str

class SectionItem(BaseModel):
    id: str
    title: str
    fields: list

async def stream_agent_response(prompt: str):
    """A generator that yields parts of the agent response."""
    try:
        outline_wrapper = A2AOutlineClientWrapper(session_id=uuid.uuid4().hex, agent_url=OUTLINE_API)
        has_data = False
        
        async for chunk_data in outline_wrapper.generate(prompt):
            print(f"生成大纲输出的chunk_data: {chunk_data}")
            
            # 检查chunk_data是否为空或无效
            if not chunk_data or not isinstance(chunk_data, dict):
                continue
                
            if chunk_data.get("type") == "text" and chunk_data.get("text"):
                has_data = True
                yield chunk_data["text"]
            elif chunk_data.get("type") == "error" and chunk_data.get("text"):
                # 直接传递错误信息
                has_data = True
                yield chunk_data["text"]
        
        # 如果整个流式传输过程中没有任何数据
        if not has_data:
            yield json.dumps({
                "status": "error", 
                "message": "AI服务未返回有效数据，请检查服务状态",
                "code": "NO_DATA_RECEIVED"
            })
            
    except Exception as e:
        # 全局异常处理 - 确保任何异常都有返回
        error_msg = f"大纲生成失败: {str(e)}"
        print(f"stream_agent_response异常: {error_msg}")
        yield json.dumps({
            "status": "error", 
            "message": error_msg,
            "code": "OUTLINE_GENERATION_FAILED"
        })


@app.post("/tools/aippt_outline")
async def aippt_outline(request: AipptRequest):
    assert request.stream, "只支持流式的返回大纲"
    return StreamingResponse(stream_agent_response(request.content), media_type="text/plain")

async def stream_content_response(markdown_content: str):
    """  # PPT的正文内容生成"""
    try:
        # 用正则找到第一个一级标题及之后的内容
        match = re.search(r"(# .*)", markdown_content, flags=re.DOTALL)

        if match:
            result = markdown_content[match.start():]
        else:
            result = markdown_content
        print(f"用户输入的markdown大纲是：{result}")

        
        content_wrapper = A2AContentClientWrapper(session_id=uuid.uuid4().hex, agent_url=CONTENT_API)
        has_data = False
        
        async for chunk_data in content_wrapper.generate(result ):
            # 检查chunk_data是否为空或无效
            if not chunk_data or not isinstance(chunk_data, dict):
                continue
                
            if chunk_data.get("type") == "text" and chunk_data.get("text"):
                has_data = True
                yield chunk_data["text"]
            elif chunk_data.get("type") == "error" and chunk_data.get("text"):
                # 直接传递错误信息
                has_data = True
                yield chunk_data["text"]
        
        # 如果整个流式传输过程中没有任何数据
        if not has_data:
            yield json.dumps({
                "status": "error", 
                "message": "内容生成服务未返回有效数据",
                "code": "CONTENT_NO_DATA"
            })
            
    except Exception as e:
        # 全局异常处理 - 确保任何异常都有返回
        error_msg = f"内容生成失败: {str(e)}"
        print(f"stream_content_response异常: {error_msg}")
        yield json.dumps({
            "status": "error", 
            "message": error_msg,
            "code": "CONTENT_GENERATION_FAILED"
        })

@app.post("/tools/aippt")
async def aippt_content(request: AipptContentRequest):
    markdown_content = request.content
    return StreamingResponse(stream_content_response(markdown_content), media_type="text/plain")

@app.post("/api/upload_material")
async def upload_material(
    file: UploadFile = File(...),
    description: str = Form("")
):
    """上传素材文件"""
    # 创建上传目录
    upload_dir = "./uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{file_id}{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # 返回文件信息
    return JSONResponse({
        "id": file_id,
        "name": file.filename,
        "path": file_path,
        "description": description,
        "size": len(content)
    })

@app.get("/data/{filename}")
async def get_data(filename: str):
    file_path = os.path.join("./template", filename)
    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=6800)