#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/6/18 14:44
# @File  : create_model.py.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : little llm 不要设置timeout，超过一定时间会断
import os
import litellm
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
# 开启LLM的debug模式
# litellm._turn_on_debug()

load_dotenv()

# 禁用工具调用功能
litellm.enable_auto_tool_choice = False
litellm.tool_call_parser = None

def create_model(model:str, provider: str):
    """
    创建模型，返回字符串或者LiteLlm
    LiteLlm(model="deepseek/deepseek-chat", api_key="xxx", api_base="")
    :return:
    """
    if provider == "google":
        # google的模型直接使用名称
        assert os.environ.get("GOOGLE_API_KEY"), "GOOGLE_API_KEY is not set"
        return model
    elif provider == "claude":
        # Claude 模型需要使用 LiteLlm，并遵循 LiteLLM 的模型命名规范
        assert os.environ.get("CLAUDE_API_KEY"), "CLAUDE_API_KEY is not set"
        # 正确的做法是使用 "claude/" 前缀
        if not model.startswith("anthropic/"):
            model = "anthropic/" + model

        return LiteLlm(
            model=model,  # 例如: "claude/claude-3-opus-20240229"
            api_key=os.environ.get("CLAUDE_API_KEY"),
        )
    elif provider == "openai":
        # openai的模型需要使用LiteLlm
        assert os.environ.get("OPENAI_API_KEY"), "OPENAI_API_KEY is not set"
        if not model.startswith("openai/"):
            # 表示兼容openai的模型请求
            model = "openai/" + model
        # 禁用工具调用
        return LiteLlm(model=model, api_key=os.environ.get("OPENAI_API_KEY"), api_base="https://api.openai.com/v1", 
                      enable_auto_tool_choice=False, tool_call_parser=None)
    elif provider == "deepseek":
        # deepseek的模型需要使用LiteLlm
        assert os.environ.get("DEEPSEEK_API_KEY"),  "DEEPSEEK_API_KEY is not set"
        if not model.startswith("openai/"):
            # 表示兼容openai的模型请求
            model = "openai/" + model
        # 禁用工具调用
        return LiteLlm(model=model, api_key=os.environ.get("DEEPSEEK_API_KEY"), api_base="https://api.deepseek.com/v1",
                      enable_auto_tool_choice=False, tool_call_parser=None)
    elif provider == "local_google":
        assert os.environ.get("GOOGLE_API_KEY"),  "GOOGLE_API_KEY is not set"
        if not model.startswith("openai/"):
            # 表示兼容openai的模型请求
            model = "openai/" + model
        # 禁用工具调用
        return LiteLlm(model=model, api_key=os.environ.get("GOOGLE_API_KEY"), api_base="http://localhost:6688",
                      enable_auto_tool_choice=False, tool_call_parser=None)
    elif provider == "local_deepseek":
        # deepseek的模型需要使用LiteLlm
        assert os.environ.get("DEEPSEEK_API_KEY"),  "DEEPSEEK_API_KEY is not set"
        if not model.startswith("openai/"):
            # 表示兼容openai的模型请求
            model = "openai/" + model
        # 禁用工具调用
        return LiteLlm(model=model, api_key=os.environ.get("DEEPSEEK_API_KEY"), api_base="http://localhost:6688",
                      enable_auto_tool_choice=False, tool_call_parser=None)
    elif provider == "ali":
        # huggingface的模型需要使用LiteLlm
        assert os.environ.get("ALI_API_KEY"), "ALI_API_KEY is not set"
        if not model.startswith("openai/"):
            # 表示兼容openai的模型请求
            model = "openai/" + model
        # 禁用工具调用
        return LiteLlm(model=model, api_key=os.environ.get("ALI_API_KEY"), api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
                      enable_auto_tool_choice=False, tool_call_parser=None)
    elif provider == "local_ali":
        assert os.environ.get("ALI_API_KEY"), "ALI_API_KEY is not set"
        if not model.startswith("openai/"):
            # 表示兼容openai的模型请求
            model = "openai/" + model
        # 禁用工具调用
        return LiteLlm(model=model, api_key=os.environ.get("ALI_API_KEY"), api_base="http://localhost:6688",
                      enable_auto_tool_choice=False, tool_call_parser=None)
    elif provider == "doubao":
        # huggingface的模型需要使用LiteLlm
        assert os.environ.get("DOUBAO_API_KEY"), "DOUBAO_API_KEY is not set"
        if not model.startswith("openai/"):
            # 表示兼容openai的模型请求
            model = "openai/" + model
        # 禁用工具调用
        return LiteLlm(model=model, api_key=os.environ.get("DOUBAO_API_KEY"), api_base="https://ark.cn-beijing.volces.com/api/v3",
                      enable_auto_tool_choice=False, tool_call_parser=None)
    elif provider == "vllm":
        # huggingface的模型需要使用LiteLlm
        assert os.environ.get("VLLM_API_KEY"), "VLLM_API_KEY is not set"
        assert os.environ.get("VLLM_API_URL"), "VLLM_API_URL is not set"
        if not model.startswith("openai/"):
            # 表示兼容openai的模型请求
            model = "openai/" + model
        # 禁用工具调用
        return LiteLlm(model=model, api_key=os.environ.get("VLLM_API_KEY"), api_base=os.environ.get("VLLM_API_URL"),
                      enable_auto_tool_choice=False, tool_call_parser=None)
    elif provider == "silicon":
        # huggingface的模型需要使用LiteLlm
        assert os.environ.get("SILICON_API_KEY"), "SILICON_API_KEY is not set"
        if not model.startswith("openai/"):
            # 表示兼容openai的模型请求
            model = "openai/" + model
        # 禁用工具调用
        return LiteLlm(model=model, api_key=os.environ.get("SILICON_API_KEY"), api_base="https://api.siliconflow.cn/v1",
                      enable_auto_tool_choice=False, tool_call_parser=None)
    elif provider == "modelscope":
        # modelscope的模型需要使用LiteLlm
        assert os.environ.get("MODELSCOPE_API_KEY"), "MODEL_SCOPE_API_KEY is not set"
        if not model.startswith("openai/"):
            # 表示兼容openai的模型请求
            model = "openai/" + model
        # 禁用工具调用
        return LiteLlm(model=model, api_key=os.environ.get("MODELSCOPE_API_KEY"),
                       api_base="https://api-inference.modelscope.cn/v1",
                      enable_auto_tool_choice=False, tool_call_parser=None)
    elif provider == "ollama":
        # huggingface的模型需要使用LiteLlm
        assert os.environ.get("OLLAMA_API_KEY"), "OLLAMA_API_KEY is not set"
        assert os.environ.get("OLLAMA_API_URL"), "OLLAMA_API_URL is not set"
        if not model.startswith("openai/"):
            # 表示兼容openai的模型请求
            model = "openai/" + model
        # 禁用工具调用
        return LiteLlm(model=model, api_key=os.environ.get("OLLAMA_API_KEY"), api_base=os.environ.get("OLLAMA_API_URL"),
                      enable_auto_tool_choice=False, tool_call_parser=None)
    elif provider == "local_openai":
        assert os.environ.get("LOCAL_API_URL"), "LOCAL_API_URL is not set"
        if not model.startswith("openai/"):
            # 表示兼容openai的模型请求
            model = "openai/" + model
        # 使用本地模型的API密钥，如果没有设置则使用EMPTY
        api_key = os.environ.get("LOCAL_API_KEY", "EMPTY")
        # 禁用工具调用
        return LiteLlm(model=model, api_key=api_key, api_base=os.environ.get("LOCAL_API_URL"),
                      enable_auto_tool_choice=False, tool_call_parser=None)
    else:
        raise ValueError(f"Unsupported provider: {provider}")