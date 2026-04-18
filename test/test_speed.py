# test_speed.py
#
# DSPy LM 速度测试
# 使用 ChainOfThought 进行复杂问题推理，输出 decode 速度
#
# @author n1ghts4kura
# @date 2026-04-18
#

import argparse
import time

import dspy

from src.llm.llama import LlamaCppLM
from src.llm.deepseek import DeepseekLM

try:
    import tiktoken
    _encoding = tiktoken.get_encoding("cl100k_base")
    def count_tokens(text: str) -> int:
        return len(_encoding.encode(text))
except ImportError:
    def count_tokens(text: str) -> int:
        return len(text) // 4  # rough estimate


class CoTSignature(dspy.Signature):
    """ChainOfThought 签名：输入问题，逐步推理后输出答案"""
    question = dspy.InputField(desc="需要深入思考的复杂问题")
    reasoning = dspy.OutputField(desc="逐步推理过程")
    answer = dspy.OutputField(desc="最终答案")


def run_speed_test(model_id: str, model: str, n_runs: int, prompt: str):
    """运行速度测试"""

    # 设置 DSPy 默认 LM
    if model == "deepseek":
        llm = DeepseekLM()
    else:
        llm = LlamaCppLM(model_id=model_id, model_filename=model)

    dspy.configure(lm=llm)

    # 预热
    dspy.ChainOfThought(CoTSignature)(question="1+1等于几?")

    # 正式测试
    speeds = []
    for i in range(n_runs):
        start_time = time.perf_counter()

        result = dspy.ChainOfThought(CoTSignature)(question=prompt)
        generated_text = result.answer

        end_time = time.perf_counter()
        elapsed = end_time - start_time

        # 获取精确 token 数（本地模型）或字符数（在线模型）
        if model == "deepseek":
            char_count = len(generated_text)
            rate = char_count / elapsed if elapsed > 0 else 0
            unit = "char/s"
            count = char_count
        else:
            token_count = count_tokens(generated_text)
            rate = token_count / elapsed if elapsed > 0 else 0
            unit = "token/s"
            count = token_count

        speeds.append(rate)

        print(f"Run {i+1}: {rate:.2f} {unit} | {count} {unit.split('/')[0]} | {elapsed:.2f}s")

    # 输出统计
    avg_speed = sum(speeds) / len(speeds)
    print(f"\n{'='*50}")
    print(f"Decode speed test ({n_runs} runs)")
    print(f"Average: {avg_speed:.2f} {unit}")
    print(f"Min: {min(speeds):.2f} {unit} | Max: {max(speeds):.2f} {unit}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DSPy LM 速度测试")
    parser.add_argument("--runs", type=int, default=5, help="推理次数 (默认: 5)")
    parser.add_argument(
        "--prompt",
        type=str,
        default="为什么天空是蓝色的？请从物理学角度逐步解释。",
        help="推理输入的复杂问题"
    )
    parser.add_argument(
        "--model-id",
        type=str,
        default="speed-test",
        help="模型 ID"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="LFM2.5-1.2B-Instruct-Q4_K_M",
        help="模型名称：本地文件名 或 'deepseek'"
    )

    args = parser.parse_args()
    run_speed_test(
        model_id=args.model_id,
        model=args.model,
        n_runs=args.runs,
        prompt=args.prompt
    )
