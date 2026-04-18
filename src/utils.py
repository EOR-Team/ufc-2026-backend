# utils.py
#
# @author n1ghts4kura
# @date 2026-04-18
#

from pathlib import Path
from typing import Any
from pydantic import BaseModel, Field


ROOT_DIR = Path(__file__).parent.parent # ../src => 项目根目录


class Result(BaseModel):
    """
    统一的结果对象
    """

    success: bool = Field(...) # 是否成功

    warn: str | None = Field(default = None) # 警告信息

    error: str | None = Field(default = None) # 错误信息

    value: Any = Field(default = None) # 返回值
