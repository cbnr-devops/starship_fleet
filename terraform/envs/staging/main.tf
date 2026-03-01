module "staging_cluster" {
  source         = "../../modules/eks-cluster"
  env            = "staging"
  aws_region     = var.aws_region
  vpc_cidr       = "10.1.0.0/16"
  aws_account_id = var.aws_account_id
}
