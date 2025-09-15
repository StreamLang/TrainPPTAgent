from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
import logging
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 尝试多种方式导入task_manager
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

@router.post("/aippt_rest")
async def create_aippt_task(
    request: MarkdownRequest,
    background_tasks: BackgroundTasks
):
    """创建PPT生成任务"""
    task_id = task_manager.create_task()
    background_tasks.add_task(
        task_manager.start_processing,
        task_id,
        request.markdown
    )
    return {
        "task_id": task_id,
        "status": "processing"
    }

@router.get("/aippt_result")
async def get_aippt_result(task_id: str):
    """获取PPT生成结果"""
    task = task_manager.get_task_status(task_id)
    if not task:
        return {"status": "not_found"}
    
    # 清理已完成任务
    if task["status"] in ("completed", "failed"):
        task_manager._tasks.pop(task_id, None)
    
    return task