output "autoscaling_group_name" {
  description = "Name of Auto Scaling Group"
  value       = aws_autoscaling_group.app.name
}

output "autoscaling_group_arn" {
  description = "ARN of Auto Scaling Group"
  value       = aws_autoscaling_group.app.arn
}

output "scaling_policy_arn" {
  description = "ARN of CPU scaling policy"
  value       = aws_autoscaling_policy.cpu_scaling.arn
}
