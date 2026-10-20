from main import assess, fixtures


def test_seeded_risks_and_safe_controls():
    assert all(bool(assess(case)) == case["risky"] for case in fixtures())


def test_replacement_and_unknown_iam_are_flagged():
    assert assess(fixtures()[4])
    plan = {
        "resource_changes": [
            {
                "address": "iam.x",
                "type": "aws_iam_policy",
                "change": {"actions": ["update"], "after_unknown": {"policy": True}},
            }
        ]
    }
    assert "unknown IAM values require review" in assess(plan)[0]["reasons"]
