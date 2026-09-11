variable "aws_region" {
  description = "AWS region for API calls. Route 53 is global; this does not affect where records live."
  type        = string
  default     = "eu-west-2" # matches agentic-tekton's own infra, same account/zone
}

variable "hosted_zone_id" {
  description = "Route 53 hosted zone ID that owns theagentictekton.com."
  type        = string
  default     = "Z00120023RP0P4IN9T3ZH" # confirmed via read-only aws route53 get-hosted-zone; matches
  # agentic-tekton/infra/aws-static-site/deploy-manifest.yaml's already-applied value (same account,
  # same zone the apex site and hekton.theagentictekton.com already use).
}

variable "subdomain_fqdn" {
  description = "Fully-qualified subdomain for Kriterion."
  type        = string
  default     = "kriterion.theagentictekton.com"
}

variable "pages_host" {
  description = "GitHub Pages target host this subdomain CNAMEs to (Kriterion's real Pages host)."
  type        = string
  default     = "dermdunc.github.io"
}

variable "ttl" {
  description = "TTL, in seconds, for both the CNAME and TXT records."
  type        = number
  default     = 300
}

variable "domain_verification_name" {
  description = <<-EOT
    Record name for the GitHub domain-verification TXT record, as issued by
    GitHub's account-level "Add a domain" step (github.com/settings/pages,
    dermdunc account, domain theagentictekton.com). No default: this value
    must come from a human completing that step, never derived or guessed --
    see infra/github-pages-dns/README.md and every prior consumer's tfvars
    comment in agentic-infra-lab for why.
  EOT
  type        = string
}

variable "domain_verification_value" {
  description = "Record value for the GitHub domain-verification TXT record, as issued by GitHub. No default -- same rule as domain_verification_name above."
  type        = string
}

variable "create_domain_verification" {
  description = "Whether to create the domain-verification TXT record. True unless a read-only preflight finds an existing record with this exact name already in the zone (re-onboarding case only -- see module README)."
  type        = bool
  default     = true
}
