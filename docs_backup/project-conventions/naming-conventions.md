# Naming Conventions

This document defines naming conventions for the `ufc-2026-backend` project.

## File Names

### Python Files

- **Use**: lowercase with underscores
- **Pattern**: `<descriptive_name>.py`
- **Examples**:
  - `clinic_selector.py` ✓
  - `medical_care.py` ✓
  - `routePatcher.py` ✗ (camelCase)
  - `route-patcher.py` ✗ (kebab-case)

### Test Files

- **Pattern**: `test_<module_name>.py`
- **Examples**:
  - `test_clinic_selector.py` ✓
  - `test_medical_care.py` ✓
  - `clinic_selector_test.py` ✗

### Configuration Files

- **Pattern**: lowercase with underscores or exact model names
- **Examples**:
  - `model/llm.json` ✓
  - `model/LFM2.5-1.2B-Instruct-Q4_K_M.llm.json` ✓

## Function Names

### Python Functions

- **Use**: snake_case
- **Examples**:
  - `get_medical_care_advice()` ✓
  - `select_clinic()` ✓
  - `collect_condition()` ✓
  - `patchRoute()` ✗ (camelCase)

### DSPy Agent Functions

- **Pattern**: `<action>_<target>()` or `<target>_<action>()`
- **Examples**:
  - `select_clinic()` - selects a clinic
  - `collect_condition()` - collects condition info
  - `patch_route()` - patches a route

## Variable Names

### General Variables

- **Use**: snake_case
- **Examples**:
  - `clinic_id` ✓
  - `requirement_summary` ✓
  - `requirementFromUser` ✗ (camelCase)

### Booleans

- **Prefix**: `is_`, `has_`, `should_`, `can_`
- **Examples**:
  - `is_valid` ✓
  - `has_results` ✓
  - `requires_doctor_consultation` ✓

### Collections

- **Singular noun** for items, **plural** for collections
- **Examples**:
  - `clinic` - single clinic
  - `clinics` - list of clinics
  - `requirement` - single requirement
  - `requirements` - list of requirements

## Class Names

### Python Classes

- **Use**: PascalCase
- **Examples**:
  - `MedicalCareSignature` ✓
  - `ClinicSelectorSignature` ✓
  - `RoutePatcherSignature` ✓
  - `medical_care_signature` ✗ (snake_case)

### DSPy Signatures

- **Pattern**: `<Feature>Signature`
- **Examples**:
  - `MedicalCareSignature` ✓
  - `ClinicSelectorSignature` ✓

### DSPy ChainOfThought

- **Pattern**: `<Feature Cot>` or `<Feature>Collector`
- **Examples**:
  - `RoutePatcherCot` ✓
  - `collector` ✓ (lowercase, module-level instance)

## Constants

- **Use**: UPPER_SNAKE_CASE
- **Examples**:
  - `MAX_RETRIES = 3` ✓
  - `DEFAULT_TIMEOUT = 30` ✓

## Module Names

- **Use**: lowercase with underscores
- **Examples**:
  - `src.llm` ✓
  - `src.triager` ✓
  - `MedicalCare` ✗ (PascalCase)

## Type Names

### Pydantic Models

- **Use**: PascalCase
- **Examples**:
  - `class Result(BaseModel)` ✓

### Type Aliases

- **Use**: PascalCase or descriptive
- **Examples**:
  - `Result` ✓
  - `MedicalAdvice` ✓

## Special Naming

### Location IDs

- **Use**: snake_case (matches `AVAILABLE_LOCATIONS` dict)
- **Examples**:
  - `entrance` ✓
  - `registration_center` ✓
  - `emergency_clinic` ✓

### DSPy Fields

- **Input fields**: descriptive noun
- **Output fields**: descriptive noun or phrase
- **Examples**:
  - `body_parts` ✓
  - `clinic_selection` ✓
  - `requires_doctor_consultation` ✓ (boolean, is/has prefix implied)

## Quick Reference Table

| Type | Convention | Example |
|------|------------|---------|
| Python files | snake_case | `clinic_selector.py` |
| Test files | test_<name>.py | `test_clinic_selector.py` |
| Functions | snake_case | `select_clinic()` |
| Classes | PascalCase | `MedicalCareSignature` |
| Variables | snake_case | `clinic_id` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES` |
| Boolean vars | is_/has_ prefix | `is_valid` |
| DSPy fields | snake_case | `body_parts` |
