variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "alb_security_group_id" {
  description = "ALB security group ID"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs for EC2 instances"
  type        = list(string)
}

variable "target_group_arn" {
  description = "ALB target group ARN"
  type        = string
}
