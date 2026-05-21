variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "home-essentials-eks"
}
variable "db_password" {
  description = "RDS database password"
  type        = string
  sensitive   = true
}
variable "tags" {
  description = "Common resource tags"
  type        = map(string)
  default = {
    Project     = "home-essentials"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}
