# Route 53 is a global service; the region only selects the API endpoint,
# not where records live. No us-east-1 alias is needed here (unlike
# aws-static-site) because this pattern has no ACM/CloudFront surface.
provider "aws" {
  region = var.aws_region
}
