1. Parse a Terraform plan and score blast radius (deletes, IAM changes, data stores) with a PR comment.

2. Result:
   Acceptance: not measured  
   Performance: not measured  
   Correctness: not measured

3. Architecture:
```mermaid
flowchart LR
    Specification --> AwaitingWaveApproval --> Implementation
```

4. Run it:
No runnable implementation yet. This is a planned Wave 2 project.

5. Decisions and limits: Public repository reserved for independent work using public or synthetic data. Implementation has not started. No company affiliation or usage is claimed. Acceptance check: Catches 5 seeded risky changes; false-positive rate reported.

6. Next: Implement after approval for Wave 2, then run and publish the required acceptance commands.
