variable "vpc_id" {
  description = "VPC ID for Load Balancer"
  type        = string
}

variable "public_subnet_ids" {
  description = "Public subnet IDs for ALB"
  type        = list(string)
}
