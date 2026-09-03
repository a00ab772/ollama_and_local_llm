import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Target the existing test/resources folder
RESOURCES_DIR = Path(__file__).resolve().parent / "resources"
RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

# Dataset size configurations
SIZES = {
    "1": ("Small", 50),
    "2": ("Medium", 200),
    "3": ("Big", 700),
    "4": ("Humungous", 5000),
}

print("Select dataset size to generate:")
print("1) Small     (~50 records per file)")
print("2) Medium    (~200 records per file)")
print("3) Big       (~700 records per file)")
print("4) Humungous (~5,000 records per file)")

choice = input("\nEnter choice (1-4) [default: 3]: ").strip()
size_name, target_count = SIZES.get(choice, SIZES["3"])

print(f"\nGenerating '{size_name}' dataset (~{target_count} records per file)...")

# IAM Users with assigned cost weights to simulate realistic user behavior
USER_PROFILES = [
    {"user": "analytics_team", "min_cost": 150.00, "max_cost": 1200.00},
    {"user": "dev_lead", "min_cost": 50.00, "max_cost": 600.00},
    {"user": "intern_app", "min_cost": 10.00, "max_cost": 150.00},
    {"user": "db_admin", "min_cost": 200.00, "max_cost": 800.00},
    {"user": "devops_team", "min_cost": 100.00, "max_cost": 500.00},
]

SERVICES = [
    ("Amazon Elastic Compute Cloud - Compute", "EC2 Running Hours"),
    ("Amazon Relational Database Service", "RDS Database Instance Usage"),
    ("Amazon Simple Storage Service", "S3 Storage & Data Transfer"),
    ("AWS Lambda", "Lambda Invocations"),
]

FINDING_TYPES = [
    ("S3 bucket public read access enabled", "HIGH", "arn:aws:s3:::company-data-bucket-"),
    ("IAM AdministratorAccess policy attached directly", "CRITICAL", "arn:aws:iam::123456789012:user/"),
    ("Security Group allows unrestricted SSH", "MEDIUM", "arn:aws:ec2:us-east-1:123456789012:sg-"),
]

EVENTS = [
    ("PutBucketPolicy", "s3.amazonaws.com", "company-data-bucket-"),
    ("CreateAccessKey", "iam.amazonaws.com", "AKIAIOSFODNN7EXAMPLE"),
    ("AuthorizeSecurityGroupIngress", "ec2.amazonaws.com", "sg-"),
    ("RunInstances", "ec2.amazonaws.com", "i-0a1b2c3d4e5f"),
]

# 1. Cost Explorer Data with explicit IAM User Tag attributions
cost_groups = []
user_cost_totals = {p["user"]: 0.0 for p in USER_PROFILES}

for i in range(target_count):
    profile = random.choice(USER_PROFILES)
    user = profile["user"]
    service, usage_type = random.choice(SERVICES)
    amount = round(random.uniform(profile["min_cost"], profile["max_cost"]), 2)
    user_cost_totals[user] += amount

    cost_groups.append(
        {
            "Keys": [
                service,
                f"Tag:user:IAMUser${user}",
                f"UsageType:{usage_type}",
            ],
            "Metrics": {
                "UnblendedCost": {"Amount": f"{amount:.2f}", "Unit": "USD"},
                "UsageQuantity": {"Amount": f"{random.randint(10, 500)}", "Unit": "Hours/Requests"},
            },
        }
    )

overall_total = sum(user_cost_totals.values())

mock_cost = {
    "ResultsByTime": [
        {
            "TimePeriod": {"Start": "2026-08-01", "End": "2026-08-31"},
            "Total": {"UnblendedCost": {"Amount": f"{overall_total:.2f}", "Unit": "USD"}},
            "Groups": cost_groups,
        }
    ]
}

# 2. Security Findings tied to specific IAM Users
sec_findings = []
for i in range(target_count):
    title, severity, res_prefix = random.choice(FINDING_TYPES)
    profile = random.choice(USER_PROFILES)
    user = profile["user"]
    sec_findings.append(
        {
            "Title": f"{title} #{i + 1}",
            "Severity": {"Label": severity},
            "Resources": [{"Id": f"{res_prefix}{i + 1000}"}],
            "ResponsibleUser": user,
            "Description": f"Security compliance violation initiated by IAM User: {user}",
        }
    )

mock_security = {"Findings": sec_findings}

# 3. CloudTrail Audit Events with explicit event-level cost metadata
trail_events = []
base_time = datetime(2026, 8, 1, 8, 0, 0)

for i in range(target_count):
    event_name, source, res_prefix = random.choice(EVENTS)
    profile = random.choice(USER_PROFILES)
    username = profile["user"]
    event_time = (base_time + timedelta(minutes=i * 5)).strftime("%Y-%m-%d %H:%M:%S")

    # Calculate explicit event cost based on user profile range
    event_cost = round(random.uniform(profile["min_cost"] / 10, profile["max_cost"] / 5), 2)

    trail_events.append(
        {
            "EventName": event_name,
            "Username": username,
            "EventTime": event_time,
            "EventSource": source,
            "DirectCostImpactUSD": f"{event_cost:.2f}",
            "Resources": [{"ResourceName": f"{res_prefix}{i + 1000}"}],
            "UserIdentity": {
                "Type": "IAMUser",
                "UserName": username,
                "Arn": f"arn:aws:iam::123456789012:user/{username}",
            },
        }
    )

mock_cloudtrail = {"Events": trail_events}

# Write output files directly into src/finance_analysis/test/resources/
with open(RESOURCES_DIR / "mock_cost.json", "w", encoding="utf-8") as f:
    json.dump(mock_cost, f, indent=2)

with open(RESOURCES_DIR / "mock_security.json", "w", encoding="utf-8") as f:
    json.dump(mock_security, f, indent=2)

with open(RESOURCES_DIR / "mock_cloudtrail.json", "w", encoding="utf-8") as f:
    json.dump(mock_cloudtrail, f, indent=2)

print(f"\nFiles generated successfully in: {RESOURCES_DIR}")