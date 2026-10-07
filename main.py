import json
import logging
import uuid

from dotenv import load_dotenv

load_dotenv(override=True)

from backend.src.graph.workflow import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("azure-multimodal-compliance")


def run_cli_simulation():
    """Run one sample audit from the terminal."""
    session_id = str(uuid.uuid4())

    inputs = {
        "video_url": "https://youtu.be/dT7S75eYhcQ",
        "video_id": f"vid_{session_id[:8]}",
        "compliance_results": [],
        "errors": [],
    }

    print("\nStarting compliance audit...")
    print(json.dumps(inputs, indent=2))

    try:
        result = app.invoke(inputs)

        print("\n=== COMPLIANCE AUDIT REPORT ===")
        print(f"Video ID: {result.get('video_id')}")
        print(f"Status: {result.get('final_status')}")

        print("\nViolations:")
        issues = result.get("compliance_results", [])

        if not issues:
            print("No violations found.")
        else:
            for issue in issues:
                print(
                    f"- [{issue.get('severity')}] "
                    f"{issue.get('category')}: "
                    f"{issue.get('description')}"
                )

        print("\nFinal Summary:")
        print(result.get("final_report"))

    except Exception as error:
        logger.exception("Workflow failed")
        raise error


if __name__ == "__main__":
    run_cli_simulation()
