from fastapi import APIRouter
from pydantic import BaseModel
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 直接导入PPT生成服务
try:
    from slide_agent.aippt_service_v2 import task_manager
except ImportError:
    try:
        from backend.slide_agent.aippt_service_v2 import task_manager
    except ImportError:
        # 最后尝试直接导入
        slide_agent_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "slide_agent")
        sys.path.append(slide_agent_path)
        from aippt_service_v2 import task_manager

router = APIRouter()
logger = logging.getLogger(__name__)

class MarkdownRequest(BaseModel):
    markdown: str
    model: str = "qwen3-235b"  # 添加模型参数，默认值为qwen3-235b

class TaskResponse(BaseModel):
    task_id: str
    status: str

@router.post("/aippt_rest", response_model=TaskResponse)
async def create_aippt_task(request: MarkdownRequest):
    """创建异步PPT生成任务，使用 aippt_rest 创建异步任务并获取 task_id"""
    try:
        # 创建任务并获取任务ID
        task_id = task_manager.create_task()
        
        # 启动异步处理任务
        task_manager.start_processing(task_id, request.markdown, request.model)
        
        return {
            "task_id": task_id,
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Failed to create PPT task: {str(e)}")
        return {
            "task_id": "",
            "status": "failed",
            "error": str(e)
        }

@router.get("/aippt_rest_result/{task_id}")
async def get_aippt_result(task_id: str):
    """获取PPT生成任务结果，使用 aippt_rest_result 获取任务结果"""
    try:
        # 获取任务状态
        task_status = task_manager.get_task_status(task_id)
        
        if task_status is None:
            return {
                "status": "not_found",
                "error": "Task not found"
            }
        
        return task_status
    except Exception as e:
        logger.error(f"Failed to get PPT task result: {str(e)}")
        return {
            "status": "failed",
            "error": str(e)
        }