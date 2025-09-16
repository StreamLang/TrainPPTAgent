import uuid
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional
import logging
import json
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from slide_agent.slide_agent.utils import parse_markdown_to_slides

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
            # 解析Markdown为幻灯片结构
            slide_structure = parse_markdown_to_slides(markdown)
            
            # 将结构化数据转换为PPTist格式
            slides = self._convert_to_pptist_format(slide_structure)
            
            # 返回结果，与前端PPT页面使用相同的数据结构
            return {
                "slides": slides,
                "markdown": markdown,
                "model": model  # 返回使用的模型信息
            }
        except Exception as e:
            logger.error(f"PPT generation failed: {str(e)}")
            raise
    
    def _convert_to_pptist_format(self, slide_structure: list) -> list:
        """将结构化数据转换为PPTist格式，与前端PPT页面使用相同的格式"""
        """将结构化数据转换为PPTist格式"""
        import uuid
        
        slides = []
        
        for i, slide_data in enumerate(slide_structure):
            slide_id = str(uuid.uuid4())
            slide_type = slide_data.get("type", "content")
            
            # 创建幻灯片对象
            slide = {
                "id": slide_id,
                "elements": [],
                "type": slide_type
            }
            
            # 根据幻灯片类型添加元素
            if slide_type == "cover":
                # 封面页
                data = slide_data.get("data", {})
                title = data.get("title", "")
                subtitle = data.get("text", "")
                
                # 添加标题文本元素
                if title:
                    title_element = {
                        "id": str(uuid.uuid4()),
                        "type": "text",
                        "content": f"<h1>{title}</h1>",
                        "left": 100,
                        "top": 150,
                        "width": 800,
                        "height": 100,
                        "rotate": 0,
                        "defaultFontName": "Arial",
                        "defaultColor": "#000000",
                        "textType": "title"
                    }
                    slide["elements"].append(title_element)
                
                # 添加副标题文本元素
                if subtitle:
                    subtitle_element = {
                        "id": str(uuid.uuid4()),
                        "type": "text",
                        "content": f"<p>{subtitle}</p>",
                        "left": 100,
                        "top": 300,
                        "width": 800,
                        "height": 50,
                        "rotate": 0,
                        "defaultFontName": "Arial",
                        "defaultColor": "#666666",
                        "textType": "subtitle"
                    }
                    slide["elements"].append(subtitle_element)
                    
            elif slide_type == "contents":
                # 目录页
                data = slide_data.get("data", {})
                items = data.get("items", [])
                
                # 添加标题
                title_element = {
                    "id": str(uuid.uuid4()),
                    "type": "text",
                    "content": "<h2>目录</h2>",
                    "left": 100,
                    "top": 100,
                    "width": 800,
                    "height": 60,
                    "rotate": 0,
                    "defaultFontName": "Arial",
                    "defaultColor": "#000000",
                    "textType": "title"
                }
                slide["elements"].append(title_element)
                
                # 添加目录项
                for j, item in enumerate(items):
                    item_element = {
                        "id": str(uuid.uuid4()),
                        "type": "text",
                        "content": f"<p>{j+1}. {item}</p>",
                        "left": 150,
                        "top": 200 + j * 50,
                        "width": 700,
                        "height": 40,
                        "rotate": 0,
                        "defaultFontName": "Arial",
                        "defaultColor": "#333333",
                        "textType": "content"
                    }
                    slide["elements"].append(item_element)
                    
            elif slide_type == "content":
                # 内容页
                data = slide_data.get("data", {})
                title = data.get("title", "")
                items = data.get("items", [])
                
                # 添加标题
                if title:
                    title_element = {
                        "id": str(uuid.uuid4()),
                        "type": "text",
                        "content": f"<h2>{title}</h2>",
                        "left": 100,
                        "top": 100,
                        "width": 800,
                        "height": 60,
                        "rotate": 0,
                        "defaultFontName": "Arial",
                        "defaultColor": "#000000",
                        "textType": "title"
                    }
                    slide["elements"].append(title_element)
                
                # 添加内容项
                for j, item in enumerate(items):
                    item_title = item.get("title", "")
                    item_text = item.get("text", "")
                    
                    # 添加要点标题
                    if item_title:
                        title_element = {
                            "id": str(uuid.uuid4()),
                            "type": "text",
                            "content": f"<h3>{item_title}</h3>",
                            "left": 150,
                            "top": 200 + j * 120,
                            "width": 700,
                            "height": 40,
                            "rotate": 0,
                            "defaultFontName": "Arial",
                            "defaultColor": "#333333",
                            "textType": "itemTitle"
                        }
                        slide["elements"].append(title_element)
                    
                    # 添加要点内容
                    if item_text:
                        text_element = {
                            "id": str(uuid.uuid4()),
                            "type": "text",
                            "content": f"<p>{item_text}</p>",
                            "left": 150,
                            "top": 240 + j * 120,
                            "width": 700,
                            "height": 60,
                            "rotate": 0,
                            "defaultFontName": "Arial",
                            "defaultColor": "#666666",
                            "textType": "content"
                        }
                        slide["elements"].append(text_element)
                        
            elif slide_type == "transition":
                # 过渡页
                data = slide_data.get("data", {})
                title = data.get("title", "")
                text = data.get("text", "")
                
                # 添加标题
                if title:
                    title_element = {
                        "id": str(uuid.uuid4()),
                        "type": "text",
                        "content": f"<h2>{title}</h2>",
                        "left": 100,
                        "top": 200,
                        "width": 800,
                        "height": 60,
                        "rotate": 0,
                        "defaultFontName": "Arial",
                        "defaultColor": "#000000",
                        "textType": "title"
                    }
                    slide["elements"].append(title_element)
                
                # 添加内容
                if text:
                    text_element = {
                        "id": str(uuid.uuid4()),
                        "type": "text",
                        "content": f"<p>{text}</p>",
                        "left": 100,
                        "top": 300,
                        "width": 800,
                        "height": 50,
                        "rotate": 0,
                        "defaultFontName": "Arial",
                        "defaultColor": "#666666",
                        "textType": "content"
                    }
                    slide["elements"].append(text_element)
                    
            elif slide_type == "end":
                # 结束页
                title_element = {
                    "id": str(uuid.uuid4()),
                    "type": "text",
                    "content": "<h1>谢谢观看</h1>",
                    "left": 100,
                    "top": 200,
                    "width": 800,
                    "height": 100,
                    "rotate": 0,
                    "defaultFontName": "Arial",
                    "defaultColor": "#000000",
                    "textType": "title"
                }
                slide["elements"].append(title_element)
                
                text_element = {
                    "id": str(uuid.uuid4()),
                    "type": "text",
                    "content": "<p>Thank you for your attention</p>",
                    "left": 100,
                    "top": 350,
                    "width": 800,
                    "height": 50,
                    "rotate": 0,
                    "defaultFontName": "Arial",
                    "defaultColor": "#666666",
                    "textType": "content"
                }
                slide["elements"].append(text_element)
            
            slides.append(slide)
        
        return slides

# 全局单例
task_manager = AIPPTTaskManager()