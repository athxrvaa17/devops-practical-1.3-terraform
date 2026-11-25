output "vpc_id" {
  description = "VPC ID"
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.network.public_subnet_ids
}

output "alb_dns_name" {
  description = "Application Load Balancer DNS"
  value       = module.load_balancer.alb_dns_name
}

output "autoscaling_group_name" {
  description = "Auto Scaling Group name"
  value       = module.autoscaling.autoscaling_group_name
}

output "s3_bucket_name" {
  description = "S3 bucket name"
  value       = module.storage.bucket_name
}

