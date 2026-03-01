terraform {
  backend "s3" {
    bucket         = "starship-fleet-tf-state"
    key            = "dev/terraform.tfstate"
    region         = "ap-southeast-2"
    dynamodb_table = "starship-fleet-tf-lock"
    encrypt        = true
  }
}
