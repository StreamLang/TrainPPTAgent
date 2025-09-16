import logging
import os
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slide_agent.utils import parse_markdown_to_slides
from slide_agent.advanced_parser import parse_markdown_to_slides_advanced

logger = logging.getLogger(__name__)


class AIPPTTaskManager:
    def __init__(self):
        self._tasks: Dict[str, dict] = {}
        self._executor = ThreadPoolExecutor(max_workers=4)

    def create_task(self) -> str:
        """生成唯一任务ID并初始化任务状态"""
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = {
            "status": "pending",
            "result": None,
            "error": None
        }
        return task_id

    def start_processing(self, task_id: str, markdown_content: str, model: str = "qwen3-235b"):
        """启动异步处理任务"""

        def _process():
            try:
                # 使用实际的PPT生成逻辑，传递模型参数
                result = self._generate_ppt(markdown_content, model)
                self._tasks[task_id] = {
                    "status": "completed",
                    "result": result,
                    "error": None
                }
            except Exception as e:
                logger.error(f"Task {task_id} failed: {str(e)}")
                self._tasks[task_id] = {
                    "status": "failed",
                    "result": None,
                    "error": str(e)
                }

        self._tasks[task_id]["status"] = "processing"
        self._executor.submit(_process)

    def get_task_status(self, task_id: str) -> Optional[dict]:
        """获取任务状态"""
        return self._tasks.get(task_id)

    def _generate_ppt(self, markdown: str, model: str = "qwen3-235b") -> dict:
        """实际的PPT生成逻辑"""
        try:
            # 检查Markdown中是否包含@符号，如果有则使用高级解析器
            if '@' in markdown:
                # 使用高级解析器，直接从Markdown中提取详细内容说明
                slide_structure = parse_markdown_to_slides_advanced(markdown)
            else:
                # 使用原始解析器
                slide_structure = parse_markdown_to_slides(markdown)

            # 直接返回幻灯片结构，与前端PPT页面使用相同的数据结构
            return slide_structure
        except Exception as e:
            logger.error(f"PPT generation failed: {str(e)}")
            raise


# 全局单例
task_manager = AIPPTTaskManager()
