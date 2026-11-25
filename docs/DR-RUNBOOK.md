
# Disaster Recovery Runbook
## Project: Nimbus Retail - Q1.3 Terraform Infrastructure

### 1. Objective

This runbook explains how to recover Terraform-managed AWS infrastructure when Terraform state is lost, damaged, or requires correction.

The infrastructure includes:
- VPC and public subnets
- Application Load Balancer
- Auto Scaling Group
- EC2 Launch Template
- Encrypted S3 bucket

### 2. Recovery Preparation

Before starting recovery:

- Verify AWS credentials and region.
- Keep Terraform configuration backed up in GitHub.
- Securely store Terraform state backups.
- Never share state files publicly because they may contain sensitive information.
- Ensure the correct Terraform working directory is selected.

AWS region: ap-south-1

### 3. Create a Terraform State Backup

Before making any state changes, create a backup:

```bash
terraform state pull > terraform-state-backup.json
```

Keep this backup in a secure location.

### 4. Recovery Procedures

#### A. Import an Existing AWS Resource

If an AWS resource already exists but is missing from Terraform state, import it.

Example: Import the S3 bucket managed by the storage module.

```bash
terraform import module.storage.aws_s3_bucket.assets YOUR_BUCKET_NAME
```

Replace YOUR_BUCKET_NAME with the actual S3 bucket name.

Other resources can be imported using their corresponding Terraform resource addresses and AWS resource IDs.

#### B. Move a Resource in Terraform State

If a resource address changes because of a module or configuration restructuring, use:

```bash
terraform state mv \
  module.storage.aws_s3_bucket.assets \
  module.storage.aws_s3_bucket.static_assets
```

This example assumes the resource name changes from `assets` to `static_assets` inside the same module.

The destination address must exist in the updated Terraform configuration.

#### C. Remove a Resource from Terraform State

If Terraform should stop managing a resource:

```bash
terraform state rm module.storage.aws_s3_bucket.assets
```

Important:
- This command removes the resource from Terraform state only.
- It does not delete the actual AWS resource.
- Terraform may attempt to create a replacement if the resource remains declared in configuration.

### 5. Validation After Recovery

After completing recovery, execute:

```bash
terraform init
terraform fmt -check -recursive
terraform validate
terraform state list
terraform plan
```

Review the plan carefully and investigate unexpected changes before applying anything.

### 6. Disaster Recovery Best Practices

- Maintain regular Terraform state backups.
- Protect state files with encryption and restricted access.
- Use remote state storage with state locking for team environments.
- Never manually edit Terraform state files.
- Never execute `terraform apply` without reviewing the plan.
- Document every recovery operation.
- Keep Terraform configuration and recovery documentation in GitHub.

### 7. Recovery Completion Criteria

Recovery is successful when:

1. Terraform state is accessible and consistent.
2. Existing AWS resources are correctly associated with Terraform configuration.
3. Terraform validation succeeds.
4. Terraform plan shows no unexpected infrastructure changes.

### 8. Emergency Recovery Checklist

- [ ] Verify AWS credentials.
- [ ] Verify AWS region.
- [ ] Back up current Terraform state.
- [ ] Import or move resources if required.
- [ ] Verify Terraform state.
- [ ] Run Terraform validation.
- [ ] Review Terraform plan.
- [ ] Document recovery actions.
