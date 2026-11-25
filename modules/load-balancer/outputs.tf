output "alb_dns_name" {
  description = "DNS name of Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "target_group_arn" {
  description = "ARN of ALB target group"
  value       = aws_lb_target_group.main.arn
}

output "alb_security_group_id" {
  description = "Security group ID of ALB"
  value       = aws_security_group.alb.id
}
