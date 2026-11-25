

import os
import sys
import hcl2

DEFAULT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIR


def clean(value):
    """Remove extra quotes added by the HCL parser."""
    if isinstance(value, str):
        return value.strip('"')
    return value


def find_tf_files(directory):
    for root, dirs, files in os.walk(directory):
        dirs[:] = [
            d for d in dirs
            if d not in (".terraform", ".venv", ".git")
        ]

        for filename in files:
            if filename.endswith(".tf"):
                yield os.path.join(root, filename)


def contains_public_ssh(ingress):
    if not isinstance(ingress, dict):
        return False

    try:
        from_port = int(ingress.get("from_port", -1))
        to_port = int(ingress.get("to_port", -1))
    except (TypeError, ValueError):
        return False

    protocol = clean(str(ingress.get("protocol", ""))).lower()

    cidrs = ingress.get("cidr_blocks", [])
    if isinstance(cidrs, str):
        cidrs = [cidrs]

    cidrs = [clean(str(cidr)) for cidr in cidrs]

    allows_ssh = (
        protocol == "-1"
        or (protocol in ("tcp", "6") and from_port <= 22 <= to_port)
    )

    return allows_ssh and "0.0.0.0/0" in cidrs


def scan_resources(directory):
    buckets = []
    encryption_configs = []
    security_groups = []

    for tf_file in find_tf_files(directory):
        try:
            with open(tf_file, "r", encoding="utf-8") as file:
                parsed = hcl2.load(file)

            for resource_block in parsed.get("resource", []):
                for resource_type, instances in resource_block.items():
                    resource_type = clean(resource_type)

                    for resource_name, config in instances.items():
                        resource_name = clean(resource_name)

                        if resource_type == "aws_s3_bucket":
                            buckets.append({
                                "directory": os.path.dirname(tf_file),
                                "name": resource_name
                            })

                        elif resource_type == "aws_s3_bucket_server_side_encryption_configuration":
                            buckets_ref = clean(str(config.get("bucket", "")))

                            rule = config.get("rule", [])
                            if isinstance(rule, dict):
                                rule = [rule]

                            algorithms = []
                            for item in rule:
                                encryption = item.get(
                                    "apply_server_side_encryption_by_default", []
                                )
                                if isinstance(encryption, dict):
                                    encryption = [encryption]

                                for setting in encryption:
                                    algorithms.append(
                                        clean(str(setting.get("sse_algorithm", "")))
                                    )

                            encryption_configs.append({
                                "directory": os.path.dirname(tf_file),
                                "bucket": buckets_ref,
                                "algorithms": algorithms
                            })

                        elif resource_type == "aws_security_group":
                            security_groups.append({
                                "name": resource_name,
                                "config": config
                            })

        except Exception as error:
            print(f"ERROR: Could not parse {tf_file}: {error}")
            sys.exit(2)

    return buckets, encryption_configs, security_groups


print("Starting custom Terraform security guardrails...\n")

buckets, encryption_configs, security_groups = scan_resources(ROOT_DIR)

failures = 0

# Guardrail 1: Every S3 bucket must have explicit encryption
for bucket in buckets:
    matching_config = any(
        config["directory"] == bucket["directory"]
        and f"aws_s3_bucket.{bucket['name']}.id" in config["bucket"]
        and any(
            algorithm in ("AES256", "aws:kms", "aws:kms:dsse")
            for algorithm in config["algorithms"]
        )
        for config in encryption_configs
    )

    if matching_config:
        print(f"PASS: S3 bucket '{bucket['name']}' has encryption.")
    else:
        print(f"FAIL: S3 bucket '{bucket['name']}' has no valid explicit encryption.")
        failures += 1


# Guardrail 2: No security group may allow public SSH
for group in security_groups:
    ingress_rules = group["config"].get("ingress", [])

    if isinstance(ingress_rules, dict):
        ingress_rules = [ingress_rules]

    public_ssh = any(
        contains_public_ssh(rule)
        for rule in ingress_rules
    )

    if public_ssh:
        print(f"FAIL: Security group '{group['name']}' allows public SSH.")
        failures += 1
    else:
        print(f"PASS: Security group '{group['name']}' does not allow public SSH.")


print("\n--------------------------------")
print(f"Total guardrail failures: {failures}")
print("--------------------------------")

if failures:
    print("Security guardrails FAILED!")
    sys.exit(1)

print("All custom security guardrails passed!")
