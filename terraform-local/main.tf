terraform {
  required_version = ">= 1.3.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }

  backend "s3" {
  bucket       = "home-essentials-tfstate-624782989130"
  key          = "prod/terraform.tfstate"
  region       = "us-east-1"
  use_lockfile = true
}
  
}

provider "aws" {
  region = var.aws_region
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

provider "helm" {
  kubernetes {
    host                   = module.eks.cluster_endpoint
    cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)
    token                  = data.aws_eks_cluster_auth.cluster.token
  }
}

data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_name
}

# ---------- EKS ----------
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = var.cluster_name
  cluster_version = "1.30"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access = true

  eks_managed_node_groups = {
    general = {
      desired_size   = 2
      min_size       = 1
      max_size       = 4
      instance_types = ["t3.micro"]
      capacity_type  = "ON_DEMAND"
    }
  }

  tags = var.tags
}

# ---------- ECR ----------
resource "aws_ecr_repository" "home_essentials" {
  name                 = "home-essentials"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.tags
}
resource "aws_db_instance" "main" {
  identifier        = "home-essentials-db"
  engine            = "postgres"        # or "mysql"
  engine_version    = "15.7"
  instance_class    = "db.t3.small"
  allocated_storage = 20

  db_name  = "homeessentials"
  username = "admin"
  password = var.db_password            # use a variable, never hardcode

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  skip_final_snapshot = true
}
resource "aws_security_group" "rds_sg" {
  name        = "home-essentials-rds-sg"
  description = "Allow EKS nodes to access RDS"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432   # use 3306 if MySQL
    to_port         = 5432
    protocol        = "tcp"
    cidr_blocks     =["10.0.0.0/8"]
 }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "home-essentials-rds-sg"
  }
}
resource "aws_db_subnet_group" "main" {
  name       = "home-essentials-subnet-group"
  subnet_ids = module.vpc.private_subnets
}
# ---------- ArgoCD via Helm ----------
resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  namespace        = "argocd"
  create_namespace = true
  version          = "6.7.3"

  set {
    name  = "server.service.type"
    value = "LoadBalancer"
  }

  depends_on = [module.eks]
}

# ---------- Prometheus + Grafana ----------
resource "helm_release" "kube_prometheus_stack" {
  name             = "kube-prometheus-stack"
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  namespace        = "monitoring"
  create_namespace = true
  version          = "58.1.3"

  values           = [file("${path.module}/../helm/monitoring/prometheus/values.yaml")]

  depends_on = [module.eks]
}
