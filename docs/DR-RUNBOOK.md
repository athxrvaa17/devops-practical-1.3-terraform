
# Disaster Recovery Runbook
## Project: Nimbus Retail - Q1.3 Terraform Infrastructure

### 1. Objective
This runbook describes the recovery process for Terraform-managed AWS infrastructure when Terraform state is lost, damaged, or requires correction.

### 2. Recovery Preparation
- Keep Terraform code and configuration backed up in GitHub.
- Securely store Terraform state backups.
- Never share state files publicly because they may contain sensitive information.
- Verify AWS credentials and region before recovery.
- Use the same Terraform provider configuration as the original deployment.

### 3. State Backup

Before making any state changes, create a backup:

```bash
terraform state pull > terraform-state-backup.json
```

Keep this backup in a secure location.

### 4. Recovery Procedures

#### A. Import an Existing AWS Resource

If an AWS resource exists but is missing from Terraform state:

```bash
terraform import aws_s3_bucket.assets YOUR_BUCKET_NAME
```

Replace YOUR_BUCKET_NAME with the actual bucket name.

#### B. Move a Resource in Terraform State

If a resource address changes in Terraform configuration:

```bash
terraform state mv \
  aws_s3_bucket.assets \
  module.storage.aws_s3_bucket.assets
```

Use the actual old and new resource addresses from the configuration.

#### C. Remove a Resource from Terraform State

If Terraform should stop managing a resource:

```bash
terraform state rm aws_s3_bucket.assets
```

Important: This removes the resource from Terraform state only. It does not delete the actual AWS resource.

### 5. Validation After Recovery

Run the following commands:

```bash
terraform init
terraform validate
terraform plan
terraform state list
```

Review the plan carefully before applying any changes.

### 6. Disaster Recovery Best Practices

- Maintain regular state backups.
- Protect state files with restricted access and encryption.
- Use remote state storage with locking for team environments.
- Never manually edit Terraform state files.
- Never run terraform apply without reviewing the plan.
- Document every recovery operation.

### 7. Recovery Completion

Recovery is considered successful when Terraform state is consistent with the actual AWS infrastructure and terraform plan shows no unexpected changes.
