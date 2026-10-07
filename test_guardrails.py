from backend.src.guardrails.compliance_guard import guard


test_output = """
{
    "status": "FAIL",
    "compliance_results": [
        {
            "category": "Claim Validation",
            "severity": "CRITICAL",
            "description": "The advertisement contains an unsupported claim."
        }
    ],
    "final_report": "The advertisement requires compliance review."
}
"""


result = guard.parse(
    test_output
)


print("Validation passed:")
print(result.validation_passed)

print("\nValidated output:")
print(result.validated_output)