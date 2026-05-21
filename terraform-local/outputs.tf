output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}
output "rds_endpoint" {
  value = aws_db_instance.main.endpoint
}
output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = module.eks.cluster_endpoint
}

output "ecr_repository_url" {
  description = "ECR repository URL"
  value       = aws_ecr_repository.home_essentials.repository_url
}

output "kubeconfig_command" {
  description = "Command to update kubeconfig"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${module.eks.cluster_name}"
}

