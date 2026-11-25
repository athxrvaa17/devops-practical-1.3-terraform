
import os
import sys
import ast
import hcl2

DEFAULT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIR


def clean(value):
    """Remove extra quotes and spaces."""
    if isinstance(value, str):
        return value.strip().strip('"').strip("'")
    return value


def flatten_strings(value):
    """Handle strings, lists, and stringified lists from HCL parser."""
    if isinstance(value, list):
        result = []
        for item in value:
            result.extend(flatten_strings(item))
        return result

    if value is None:
        return []

    if isinstance(value, str):
        value = clean(value)

        # Handle values such as "['AES256']"
        if value.startswith("[") and value.endswith("]"):
            try:
                parsed = ast.literal_eval(value)
                if isinstance(parsed, list):
                    return flatten_strings(parsed)
            except (ValueError, SyntaxError):
                pass

        return [value]

    return [str(value)]


def as_list(value):
    """Convert a dictionary or single value into a list."""
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value]
    return []


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
        from_ports = flatten_strings(ingress.get("from_port", -1))
        to_ports = flatten_strings(ingress.get("to_port", -1))

        from_port = int(from_ports[0]) if from_ports else -1
        to_port = int(to_ports[0]) if to_ports else -1
    except (TypeError, ValueError):
        return False

    protocols = flatten_strings(ingress.get("protocol", ""))
    protocol = protocols[0].lower() if protocols else ""

    cidrs = flatten_strings(ingress.get("cidr_blocks", []))

    allows_ssh = (
        protocol == "-1"
        or (
            protocol in ("tcp", "6")
            and from_port <= 22 <= to_port
        )
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

            file_directory = os.path.abspath(os.path.dirname(tf_file))

            for resource_block in parsed.get("resource", []):
                for resource_type, instances in resource_block.items():

                    resource_type = clean(resource_type)

                    for resource_name, config in instances.items():
                        resource_name = clean(resource_name)

                        if resource_type == "aws_s3_bucket":
                            buckets.append({
                                "directory": file_directory,
                                "name": resource_name
                            })

                        elif resource_type == (
                            "aws_s3_bucket_server_side_encryption_configuration"
                        ):
                            bucket_refs = flatten_strings(
                                config.get("bucket", "")
                            )

                            algorithms = []

                            for rule in as_list(config.get("rule", [])):
                                encryption_settings = as_list(
                                    rule.get(
                                        "apply_server_side_encryption_by_default",
                                        []
                                    )
                                )

                                for setting in encryption_settings:
                                    algorithms.extend(
                                        flatten_strings(
                                            setting.get("sse_algorithm", "")
                                        )
                                    )

                            encryption_configs.append({
                                "directory": file_directory,
                                "buckets": bucket_refs,
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
    expected_reference = (
        f"aws_s3_bucket.{bucket['name']}.id"
    )

    matching_config = any(
        config["directory"] == bucket["directory"]
        and any(
            expected_reference in reference
            for reference in config["buckets"]
        )
        and any(
            algorithm in ("AES256", "aws:kms", "aws:kms:dsse")
            for algorithm in config["algorithms"]
        )
        for config in encryption_configs
    )

    if matching_config:
        print(
            f"PASS: S3 bucket '{bucket['name']}' has encryption."
        )
    else:
        print(
            f"FAIL: S3 bucket '{bucket['name']}' "
            "has no valid explicit encryption."
        )
        failures += 1


# Guardrail 2: No security group may allow public SSH
for group in security_groups:
    ingress_rules = as_list(
        group["config"].get("ingress", [])
    )

    public_ssh = any(
        contains_public_ssh(rule)
        for rule in ingress_rules
    )

    if public_ssh:
        print(
            f"FAIL: Security group '{group['name']}' "
            "allows public SSH."
        )
        failures += 1
    else:
        print(
            f"PASS: Security group '{group['name']}' "
            "does not allow public SSH."
        )


print("\n--------------------------------")
print(f"Total guardrail failures: {failures}")
print("--------------------------------")

if failures:
    print("Security guardrails FAILED!")
    sys.exit(1)

print("All custom security guardrails passed!")
