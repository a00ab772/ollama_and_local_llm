import sys
from pathlib import Path
from unittest.mock import patch

# Add parent directory (src/finance_analysis) containing main.py to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from main import InteractiveAWSApp


def mock_aws_data():
    """Mock metrics including vulnerable resource configurations for AI security analysis."""
    mock_cost = {
        "ResultsByTime": [
            {
                "TimePeriod": {"Start": "2026-08-01", "End": "2026-08-31"},
                "Total": {"UnblendedCost": {"Amount": "239.60", "Unit": "USD"}},
                "Groups": [
                    {
                        "Keys": ["Amazon EC2", "Tag:Owner$dev_lead"],
                        "Metrics": {"UnblendedCost": {"Amount": "142.50", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["Amazon RDS", "Tag:Owner$db_admin"],
                        "Metrics": {"UnblendedCost": {"Amount": "85.00", "Unit": "USD"}},
                    },
                    {
                        "Keys": ["Amazon S3", "Tag:Owner$intern_app"],
                        "Metrics": {"UnblendedCost": {"Amount": "12.10", "Unit": "USD"}},
                    },
                ],
            }
        ]
    }

    mock_security = {
        "Findings": [
            {
                "Title": "S3 bucket public read access enabled",
                "Severity": {"Label": "HIGH"},
                "Resources": [{"Id": "arn:aws:s3:::company-confidential-bucket"}],
                "Description": "Bucket policy allows wildcard principal read access without encryption.",
            },
            {
                "Title": "IAM Administrator Access attached to user",
                "Severity": {"Label": "CRITICAL"},
                "Resources": [{"Id": "arn:aws:iam::123456789012:user/intern_app"}],
                "Description": "User has inline policy containing Action: * on Resource: *.",
            },
            {
                "Title": "Cleartext Hardcoded AWS Secret Key Detected",
                "Severity": {"Label": "HIGH"},
                "Resources": [{"Id": "arn:aws:ec2:us-east-1:123456789012:instance/i-0a1b2c3d4e5f6g7h8"}],
                "Description": "Hardcoded credentials found in UserData script.",
            },
        ]
    }

    mock_cloudtrail = {
        "Events": [
            {
                "EventName": "PutBucketPolicy",
                "Username": "intern_app",
                "EventTime": "2026-08-30 14:22:00",
                "EventSource": "s3.amazonaws.com",
                "Resources": [{"ResourceName": "company-confidential-bucket"}],
            },
            {
                "EventName": "CreateAccessKey",
                "Username": "dev_lead",
                "EventTime": "2026-08-30 15:10:05",
                "EventSource": "iam.amazonaws.com",
                "Resources": [{"ResourceName": "AKIAIOSFODNN7EXAMPLE"}],
            },
        ]
    }

    return mock_cost, mock_security, mock_cloudtrail


if __name__ == "__main__":
    app = InteractiveAWSApp()

    # Patch fetch_aws_metrics to supply mocked telemetry data
    patch.object(app, "fetch_aws_metrics", side_effect=mock_aws_data).start()

    # Launch GUI in full interactive mode with live Ollama calls
    app.mainloop()