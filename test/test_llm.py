# test_llm.py
#
# @author n1ghts4kura
# @date 2026-04-18
#

import pytest
from pathlib import Path

from src.llm.llama import load_model, get_model_and_cfg, unload_model, _models
from src.utils import Result


# Test fixtures
MODEL_FILENAME = "LFM2.5-1.2B-Instruct-Q4_K_M"
MODEL_ID = "test-model"


@pytest.fixture(autouse=True)
def cleanup_models():
    """Clean up loaded models before and after each test."""
    # Clean before
    for model_id in list(_models.keys()):
        unload_model(model_id)
    yield
    # Clean after
    for model_id in list(_models.keys()):
        unload_model(model_id)


class TestLoadModel:
    def test_load_model_success(self):
        """Test loading a model successfully returns success Result."""
        result = load_model(MODEL_ID, MODEL_FILENAME)
        assert result.success is True
        assert result.error is None

    def test_load_model_duplicate_id_fails(self):
        """Test that loading with duplicate model_id returns error."""
        load_model(MODEL_ID, MODEL_FILENAME)
        result = load_model(MODEL_ID, MODEL_FILENAME)
        assert result.success is False
        assert "已存在" in result.error


class TestGetModelAndCfg:
    def test_get_model_not_found(self):
        """Test getting a non-existent model returns error."""
        result = get_model_and_cfg("nonexistent-id")
        assert result.success is False
        assert "不存在" in result.error

    def test_get_model_success(self):
        """Test getting a loaded model returns the model and config."""
        load_model(MODEL_ID, MODEL_FILENAME)
        result = get_model_and_cfg(MODEL_ID)
        assert result.success is True
        assert result.value is not None
        model, infer_config = result.value
        assert "n_ctx" in infer_config


class TestUnloadModel:
    def test_unload_model_not_found(self):
        """Test unloading a non-existent model returns error."""
        result = unload_model("nonexistent-id")
        assert result.success is False
        assert "不存在" in result.error

    def test_unload_model_success(self):
        """Test unloading a model removes it from the registry."""
        load_model(MODEL_ID, MODEL_FILENAME)
        result = unload_model(MODEL_ID)
        assert result.success is True
        # Verify model is no longer accessible
        get_result = get_model_and_cfg(MODEL_ID)
        assert get_result.success is False


class TestModelInference:
    def test_create_chat_completion_produces_output(self):
        """Test that loaded model can actually generate text via create_chat_completion."""
        load_model(MODEL_ID, MODEL_FILENAME)
        result = get_model_and_cfg(MODEL_ID)
        assert result.success is True
        model, _ = result.value

        # Call create_chat_completion to verify model works
        response = model.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"},
            ],
            max_tokens=20,
        )

        # Verify response structure
        assert response is not None
        assert "choices" in response
        assert len(response["choices"]) > 0
        assert "message" in response["choices"][0]

        # Verify it actually generated something
        generated_text = response["choices"][0]["message"].get("content", "")
        assert len(generated_text) > 0, "Model should generate some text"

    def test_chat_completion_math_question(self):
        """Test model can answer a simple math question."""
        load_model(MODEL_ID, MODEL_FILENAME)
        result = get_model_and_cfg(MODEL_ID)
        model, _ = result.value

        response = model.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are a math tutor."},
                {"role": "user", "content": "What is 2 + 2?"},
            ],
            max_tokens=20,
        )

        generated_text = response["choices"][0]["message"]["content"]
        assert len(generated_text) > 0
        # Should contain "4" in the response
        assert "4" in generated_text, f"Expected '4' in response, got: {generated_text}"

    def test_chat_completion_multiturn_conversation(self):
        """Test multi-turn conversation with assistant message history."""
        load_model(MODEL_ID, MODEL_FILENAME)
        result = get_model_and_cfg(MODEL_ID)
        model, _ = result.value

        response = model.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "My name is Alice."},
                {"role": "assistant", "content": "Hello Alice! Nice to meet you. How can I help you today?"},
                {"role": "user", "content": "What is my name?"},
            ],
            max_tokens=30,
        )

        generated_text = response["choices"][0]["message"]["content"]
        assert len(generated_text) > 0
        # Should remember the name "Alice"
        assert "Alice" in generated_text, f"Expected 'Alice' in response, got: {generated_text}"

    def test_chat_completion_code_generation(self):
        """Test model can generate simple code."""
        load_model(MODEL_ID, MODEL_FILENAME)
        result = get_model_and_cfg(MODEL_ID)
        model, _ = result.value

        response = model.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are a Python programmer."},
                {"role": "user", "content": "Write a hello world program in Python."},
            ],
            max_tokens=50,
        )

        generated_text = response["choices"][0]["message"]["content"]
        assert len(generated_text) > 0
        # Should contain Python code
        assert "print" in generated_text or "def " in generated_text, \
            f"Expected Python code in response, got: {generated_text}"
