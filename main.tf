terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1"
}

# Network Module
module "network" {
  source = "./modules/network"

  vpc_cidr           = "10.20.0.0/16"
  subnet_cidrs       = ["10.20.1.0/24", "10.20.2.0/24"]
  availability_zones = ["ap-south-1a", "ap-south-1b"]
}

# Load Balancer Module
module "load_balancer" {
  source = "./modules/load-balancer"

  vpc_id            = module.network.vpc_id
  public_subnet_ids = module.network.public_subnet_ids
}

# Auto Scaling Module
module "autoscaling" {
  source = "./modules/autoscaling"

  vpc_id                = module.network.vpc_id
  alb_security_group_id = module.load_balancer.alb_security_group_id
  public_subnet_ids     = module.network.public_subnet_ids
  target_group_arn      = module.load_balancer.target_group_arn
}

# S3 Storage Module
module "storage" {
  source = "./modules/storage"
}
