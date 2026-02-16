#!/usr/bin/env python3
"""
Judge Agent - AI Code Compliance Evaluator
TSIS 2 Assignment - Rate Limiter System
"""

import json
import os
import sys

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("ERROR: google-genai package not installed")
    print("Install with: pip install google-genai")
    sys.exit(1)


SYSTEM_PROMPT = """You are a QA Judge Agent and Senior Architect. Your goal is to score code compliance from 0 to 100 based on the provided PRD.

You must check for functionality, error handling and thread safety.

SCORING RULES:
- Start at 100 points
- Deduct points for each unmet requirement:
  * CRITICAL issues (no validation, no thread safety, wrong return type): -15 to -20 points each
  * HIGH issues (missing error handling, not removing expired requests): -10 to -12 points each
  * MEDIUM issues (missing methods, incomplete functionality): -6 to -9 points each

PASS/FAIL:
- Score >= 95: PASS
- Score < 95: FAIL

SECURITY CHECK:
- If code has no thread safety (requirement #11): Unsafe
- If code has no validation (requirements #2, #3): Unsafe
- If code does not handle None/empty identifier (requirement #9): Unsafe
- Otherwise: Safe

You must output ONLY valid JSON with this EXACT structure:

{
  "compliance_score": 45,
  "status": "FAIL",
  "audit_log": [
    {
      "requirement": "The __init__ method must validate that max_requests is greater than 0",
      "met": false,
      "comment": "No validation is performed on max_requests parameter. The method accepts any value without checking if it is positive."
    },
    {
      "requirement": "The check_rate_limit method must return tuple (bool, int)",
      "met": false,
      "comment": "The method returns a boolean (True/False) instead of a tuple. The return type does not match requirement."
    },
    {
      "requirement": "The check_rate_limit method must track request timestamps for each identifier",
      "met": true,
      "comment": "Request timestamps are tracked using requests[identifier].append(current_time)."
    }
  ],
  "security_check": "Unsafe"
}

IMPORTANT RULES:
1. Each item in audit_log must have exactly 3 fields: "requirement", "met", "comment"
2. "requirement" should be a clear statement from the PRD (paraphrased if needed)
3. "met" must be boolean (true or false)
4. "comment" should explain WHY with specific code evidence
5. "status" must be exactly "PASS" or "FAIL" (all caps)
6. "security_check" must be exactly "Safe" or "Unsafe" (capitalized)
7. Do NOT add any extra fields
8. Output ONLY the JSON object, nothing else

Check all requirements from the PRD systematically. Be thorough and fair."""


def load_file(filepath):
    """Load file contents."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERROR: File not found - {filepath}")
        return None
    except Exception as e:
        print(f"ERROR reading {filepath}: {e}")
        return None


def evaluate_code(prd_text, code_text, api_key):
    """Evaluate code against PRD using Gemini API."""
    client = genai.Client(api_key=api_key)
    
    user_prompt = f"""Evaluate this code submission against the PRD.

PRODUCT REQUIREMENTS DOCUMENT:
{prd_text}

CODE SUBMISSION:
{code_text}

Check each requirement carefully. Output your evaluation as JSON following the exact format in your instructions."""

    try:
        print("  Sending request to Gemini API...")
        print("  This may take 15-30 seconds...")
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{SYSTEM_PROMPT}\n\n{user_prompt}",
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
            )
        )
        
        response_text = response.text.strip()
        result = json.loads(response_text)
        
        print("  Evaluation completed successfully\n")
        return result
        
    except json.JSONDecodeError as e:
        print(f"  ERROR: Invalid JSON from API: {e}")
        print(f"\n  Response text:")
        print(response_text[:1000])
        return None
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def save_report(report, output_file):
    """Save report to JSON file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"  Report saved: {output_file}")
        return True
    except Exception as e:
        print(f"  ERROR saving report: {e}")
        return False


def print_summary(report, title):
    """Print formatted report summary."""
    print("\n" + "=" * 70)
    print(f"{title}")
    print("=" * 70)
    print(f"\nCompliance Score: {report['compliance_score']}/100")
    print(f"Status: {report['status']}")
    print(f"Security Check: {report['security_check']}")
    
    print(f"\nAudit Log ({len(report['audit_log'])} findings):")
    print("-" * 70)
    
    for i, item in enumerate(report['audit_log'], 1):
        status = "PASS" if item['met'] else "FAIL"
        print(f"\n{i}. [{status}] {item['requirement']}")
        print(f"   {item['comment']}")
    
    print("\n" + "=" * 70)


def main():
    """Main execution."""
    print("Judge Agent - AI Code Compliance Evaluator")
    print("TSIS 2 Assignment - Dual Evaluation Mode")
    print("=" * 70 + "\n")
    
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not set\n")
        print("Windows PowerShell: $env:GOOGLE_API_KEY='your-key'")
        print("Get key at: https://aistudio.google.com/apikey")
        sys.exit(1)
    
    # Load PRD
    print("Loading prd.txt...")
    prd_content = load_file("prd.txt")
    if not prd_content:
        sys.exit(1)
    
    # Evaluate UNSAFE version
    print("\n" + "=" * 70)
    print("EVALUATING: code_submission_unsafe.py")
    print("=" * 70 + "\n")
    
    code_unsafe = load_file("code_submission_unsafe.py")
    if code_unsafe:
        report_unsafe = evaluate_code(prd_content, code_unsafe, api_key)
        if report_unsafe:
            save_report(report_unsafe, "compliance_report_unsafe.json")
            print_summary(report_unsafe, "UNSAFE CODE - EVALUATION REPORT")
    
    # Evaluate SAFE version
    print("\n" + "=" * 70)
    print("EVALUATING: code_submission_safe.py")
    print("=" * 70 + "\n")
    
    code_safe = load_file("code_submission_safe.py")
    if code_safe:
        report_safe = evaluate_code(prd_content, code_safe, api_key)
        if report_safe:
            save_report(report_safe, "compliance_report_safe.json")
            print_summary(report_safe, "SAFE CODE - EVALUATION REPORT")
    
    print("\n" + "=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)
    print("\nGenerated files:")
    print("  - compliance_report_unsafe.json")
    print("  - compliance_report_safe.json")
    print("\n")


if __name__ == "__main__":
    main()