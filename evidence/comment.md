Terraform plan risk check on seeded fixtures

- aws_db_instance.fixture_0: destructive action or replacement, data store destruction
- aws_iam_policy.fixture_1: IAM permission change
- aws_security_group.fixture_2: public ingress
- aws_s3_bucket.fixture_3: destructive action or replacement, data store destruction
- aws_instance.fixture_4: destructive action or replacement

Seeded risky changes caught: 5; false positives on safe fixtures: 0.
