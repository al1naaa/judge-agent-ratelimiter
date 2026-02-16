# Judge Agent - Rate Limiter Code Evaluator

TSIS 2 Assignment - AI-powered code compliance evaluation system.

## Overview

This project implements a Judge Agent that evaluates Rate Limiter code implementations against a Product Requirements Document (PRD) using Google Gemini API.

## Files

- **prd.txt** - Product Requirements Document (11 requirements)
- **code_submission_unsafe.py** - Code with violations (Score: 65/100, FAIL)
- **code_submission_safe.py** - Fully compliant code (Score: 100/100, PASS)
- **judge.py** - Judge Agent evaluation script
- **compliance_report_unsafe.json** - Evaluation result for unsafe code
- **compliance_report_safe.json** - Evaluation result for safe code

## Requirements

- Python
- google-genai package
- Google API key

## Installation
```powershell
pip install google-genai
```

## Usage

Set your API key:
```powershell
$env:GOOGLE_API_KEY='your-api-key'
```

Run evaluation:
```powershell
python judge.py
```

## Results

### Unsafe Code
- Compliance Score: 65/100
- Status: FAIL
- Security: Unsafe
- Issues: Missing thread safety, no None/empty identifier validation

### Safe Code
- Compliance Score: 100/100
- Status: PASS
- Security: Safe
- All 11 requirements met
