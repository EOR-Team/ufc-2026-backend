# llm/llama.py
# 加载和管理所有通过 llama 启动的大语言模型
#
# @author n1ghts4kura
# @date 2026-04-18
#

import json
import dspy
from llama_cpp import Llama
from typing import Any

from src.utils import ROOT_DIR, Result
from src import logger


# 储存模型实例
# key: model_id, value: (模型实例, 模型配置)
_models: dict[str, tuple[Llama, dict[str, Any]]] = {}


def load_model(model_id: str, model_filename: str) -> Result:
    """
    根据 model/ 文件夹中的配置加载 gguf 模型

    Args:
        model_id: 模型 ID. 可用于表示同一个模型同时运行的多个实例
        model_filename: 模型文件名（无后缀名），位于 model/ 文件夹中
    
    Returns:
        Result 对象，成功时包含模型实例和配置，失败时包含错误信息
    """

    if model_id in _models:
        return Result(success=True, warn=f"模型 ID '{model_id}' 已存在") # 已存在则直接返回成功，避免重复加载

    with open(ROOT_DIR / "model" / f"{model_filename}.llm.json", "r") as f:
        llm_config = json.load(f)
    
    with open(ROOT_DIR / "model" / f"{model_filename}.infer.json", "r") as f:
        infer_config = json.load(f)
    
    model = Llama(
        model_path = (ROOT_DIR / "model" / f"{model_filename}.gguf").as_posix(),
        **llm_config
    )
    _models[model_id] = (model, infer_config)
    return Result(success=True)


def get_model_and_cfg(model_id: str) -> Result:
    """
    获取已加载的模型实例和配置

    Args:
        model_id: 模型 ID
    
    Returns:
        Result 对象，成功时包含模型实例和配置，失败时包含错误信息
    """

    if model_id not in _models:
        return Result(success=False, error=f"模型 ID '{model_id}' 不存在")
    
    model, infer_config = _models[model_id]
    return Result(success=True, value=(model, infer_config))


def unload_model(model_id: str) -> Result:
    """
    卸载模型实例，释放资源

    Args:
        model_id: 模型 ID
    
    Returns:
        Result 对象，成功时表示卸载成功，失败时包含错误信息
    """

    if model_id not in _models:
        return Result(success=False, error=f"模型 ID '{model_id}' 不存在")
    
    del _models[model_id]
    return Result(success=True)


class LlamaCppLM(dspy.LM):
    """
    基于 llama-cpp-python 的 lm 封装
    """

    def __init__(self, model_id: str, model_filename: str, **kwargs) -> None:
        # DSPy LM requires a model name string - use model_id as identifier
        super().__init__(model=model_id, **kwargs)

        resp = load_model(model_id, model_filename)

        if not resp.success:
            logger.error(f"加载模型失败: {resp.error}")
        
        if resp.warn is not None:
            logger.warn(f"加载模型成功，但存在警告: {resp.warn}")
        
        self.model, self.infer_config = get_model_and_cfg(model_id).value
        # DSPy 期望 lm.model 是字符串，但实际 llama 对象需要存储为其他名称
        self._llama_model = self.model
        self.model = f"llama-cpp/{model_id}"  # DSPy adapter 期望的格式
    

    def forward(self, prompt=None, messages=None, **kwargs):
        if messages is None:
            messages = [{"role": "user", "content": prompt}]

        response = self._llama_model.create_chat_completion(
            messages=messages,
            **self.infer_config
        )
        
        content = response['choices'][0]['message']['content']
        
        # Return OpenAI-like response format DSPy expects
        class Message:
            def __init__(self, content):
                self.content = content
        
        class Choice:
            def __init__(self, content):
                self.message = Message(content)
                self.index = 0
                self.finish_reason = "stop"
        
        class Response:
            def __init__(self, content):
                self.choices = [Choice(content)]
                self.usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
                self.model = "llama-cpp"
                self.cache_hit = False
        
        return Response(content)
    
    async def aforward(self, prompt=None, messages=None, **kwargs):
        return self.forward(prompt=prompt, messages=messages, **kwargs)


__all__ = ["load_model", "get_model_and_cfg", "unload_model"]
