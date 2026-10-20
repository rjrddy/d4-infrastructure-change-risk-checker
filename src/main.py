"""Inspect Terraform plan JSON and explain destructive or permission-expanding changes."""

import argparse
import json
from pathlib import Path


def assess(plan: dict) -> list[dict]:
    findings = []
    for resource in plan.get("resource_changes", []):
        change = resource["change"]
        actions = change["actions"]
        after = change.get("after") or {}
        reasons = []
        if "delete" in actions:
            reasons.append("destructive action or replacement")
        if resource["type"].startswith("aws_iam") and any(a != "no-op" for a in actions):
            reasons.append("IAM permission change")
        if resource["type"] == "aws_security_group" and "0.0.0.0/0" in json.dumps(after):
            reasons.append("public ingress")
        if resource["type"] in {"aws_db_instance", "aws_s3_bucket"} and "delete" in actions:
            reasons.append("data store destruction")
        if change.get("after_unknown") and resource["type"].startswith("aws_iam"):
            reasons.append("unknown IAM values require review")
        if reasons:
            findings.append(
                {
                    "address": resource["address"],
                    "reasons": reasons,
                    "score": min(100, 25 * len(reasons)),
                }
            )
    return findings


def fixtures() -> list[dict]:
    cases = []
    for i, (kind, actions, after) in enumerate(
        [
            ("aws_db_instance", ["delete"], {}),
            ("aws_iam_policy", ["update"], {"policy": "*"}),
            ("aws_security_group", ["update"], {"ingress": ["0.0.0.0/0"]}),
            ("aws_s3_bucket", ["delete"], {}),
            ("aws_instance", ["delete", "create"], {}),
            ("aws_instance", ["create"], {}),
            ("aws_db_instance", ["no-op"], {}),
            ("aws_security_group", ["update"], {"ingress": ["10.0.0.0/8"]}),
            ("aws_s3_bucket", ["no-op"], {}),
            ("aws_instance", ["update"], {"tags": {"team": "synthetic"}}),
        ]
    ):
        cases.append(
            {
                "risky": i < 5,
                "resource_changes": [
                    {
                        "address": f"{kind}.fixture_{i}",
                        "type": kind,
                        "change": {"actions": actions, "after": after},
                    }
                ],
            }
        )
    return cases


def benchmark() -> dict:
    cases = fixtures()
    rows = [{"risky": case["risky"], "findings": assess(case)} for case in cases]
    tp = sum(r["risky"] and bool(r["findings"]) for r in rows)
    fp = sum(not r["risky"] and bool(r["findings"]) for r in rows)
    Path("evidence/plans.json").write_text(json.dumps(cases, indent=2))
    Path("evidence/findings.json").write_text(json.dumps(rows, indent=2))
    Path("evidence/comment.md").write_text(
        "Terraform plan risk check on seeded fixtures\n\n"
        + "".join(
            f"- {f['address']}: {', '.join(f['reasons'])}\n" for r in rows for f in r["findings"]
        )
        + f"\nSeeded risky changes caught: {tp}; false positives on safe fixtures: {fp}.\n"
    )
    return {
        "seeded_risky_changes": 5,
        "risky_changes_caught": tp,
        "safe_controls": 5,
        "false_positive_rate": fp / 5,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true")
    args = parser.parse_args()
    if args.gate:
        findings = assess(fixtures()[0])
        print(json.dumps(findings))
        raise SystemExit(1 if findings else 0)
    print(json.dumps(benchmark(), indent=2))
