import json
import os
import re
import uuid
import dotenv
from outline_client import A2AOutlineClientWrapper
from content_client import A2AContentClientWrapper

# 加载环境变量
dotenv.load_dotenv()

# 获取环境变量
OUTLINE_API = os.environ.get("OUTLINE_API", "http://localhost:10001")
CONTENT_API = os.environ["CONTENT_API"]



async def stream_agent_response(prompt: str):
    """A generator that yields parts of the agent response."""
    try:
        outline_wrapper = A2AOutlineClientWrapper(session_id=uuid.uuid4().hex, agent_url=OUTLINE_API)
        has_data = False
        
        async for chunk_data in outline_wrapper.generate(prompt):
            # print(f"生成大纲输出的chunk_data: {chunk_data}")
            
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

        async for chunk_data in content_wrapper.generate(result):
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