from ml.experiments.run_ab import RESPONSE_FORMAT, validate_output_contract, is_retryable_call_error


def test_output_contract_accepts_fenced_json():
    result = validate_output_contract('```json\n{"answer":"ok","assumptions":[],"warnings":[]}\n```')
    assert result["json_valid"] is True
    assert result["contract_valid"] is True


def test_output_contract_rejects_invalid_json():
    result = validate_output_contract('{"answer":')
    assert result["json_valid"] is False
    assert result["contract_valid"] is False


def test_output_contract_rejects_misspelled_required_key():
    result = validate_output_contract('{"answer":"ok","assumptions":[],"warnigs":[]}')
    assert result["json_valid"] is True
    assert result["contract_valid"] is False
    assert "missing" in result["format_error"]


def test_request_uses_strict_json_schema():
    assert RESPONSE_FORMAT["type"] == "json_schema"
    assert RESPONSE_FORMAT["strict"] is True
    assert RESPONSE_FORMAT["schema"]["required"] == ["answer", "assumptions", "warnings"]


def test_output_contract_rejects_non_string_warning_items():
    result = validate_output_contract('{"answer":"ok","assumptions":[],"warnings":[{"warning":"x"}]}')
    assert result["json_valid"] is True
    assert result["contract_valid"] is False


def test_output_contract_rejects_numeric_answer_array_items():
    result = validate_output_contract('{"answer":["ok",3],"assumptions":[],"warnings":[]}')
    assert result["json_valid"] is True
    assert result["contract_valid"] is False


def test_retry_predicate_accepts_empty_sdk_message_response():
    class ValidationError(Exception):
        __module__ = "pydantic_core._pydantic_core"
    exc = ValidationError("choices.0.message.role Field required; input_value={'content': ''}")
    assert is_retryable_call_error(exc) is True


def test_retry_predicate_does_not_retry_other_validation_errors():
    class ValidationError(Exception):
        __module__ = "pydantic_core._pydantic_core"
    assert is_retryable_call_error(ValidationError("answer missing")) is False


def test_retry_predicate_does_not_retry_unrelated_errors():
    assert is_retryable_call_error(ValueError("choices.0.message.role content")) is False
