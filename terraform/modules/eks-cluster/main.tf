module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "starship-fleet-${var.env}-vpc"
  cidr = var.vpc_cidr

  azs             = ["${var.aws_region}a", "${var.aws_region}b"]
  private_subnets = ["${cidrsubnet(var.vpc_cidr, 8, 1)}", "${cidrsubnet(var.vpc_cidr, 8, 2)}"]
  public_subnets  = ["${cidrsubnet(var.vpc_cidr, 8, 101)}", "${cidrsubnet(var.vpc_cidr, 8, 102)}"]

  enable_nat_gateway = true
  single_nat_gateway = true
}

module "eks" {
  source          = "terraform-aws-modules/eks/aws"
  version         = "21.15.1"
  cluster_name    = "starship-fleet-${var.env}"
  cluster_version = "1.29"

  subnet_ids = module.vpc.private_subnets
  vpc_id     = module.vpc.vpc_id

  enable_irsa = true

  eks_managed_node_groups = {
    default = {
      instance_types = ["t3.medium"]
      min_size       = var.env == "prod" ? 2 : 1
      max_size       = var.env == "prod" ? 5 : 3
      desired_size   = var.env == "prod" ? 3 : 2
    }
  }
}
