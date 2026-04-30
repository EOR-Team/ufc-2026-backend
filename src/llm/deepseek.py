# llm/deepseek.py
# 加载deepseek模型
#
# @author n1ghts4kura
# @date 2026-04-18
#

import os
import dspy
from dotenv import load_dotenv


# 加载 DEEPSEEK_API_KEY 环境变量
load_dotenv()


class DeepseekLM(dspy.LM):

    """
    基于 Deepseek API 的 lm 封装
    """

    def __init__(self):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("未找到 DEEPSEEK_API_KEY 环境变量")
        super().__init__("deepseek/deepseek-v4-flash", api_key=api_key)