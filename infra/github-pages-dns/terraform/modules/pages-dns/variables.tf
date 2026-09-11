variable "hosted_zone_id" {
  description = "Route 53 hosted zone ID that owns the root domain (e.g. theagentictekton.com)."
  type        = string
}

variable "subdomain_fqdn" {
  description = "Fully-qualified subdomain (e.g. kriterion.theagentictekton.com)."
  type        = string
}

variable "pages_host" {
  description = "GitHub Pages target host the subdomain CNAMEs to (e.g. dermdunc.github.io)."
  type        = string
}

variable "ttl" {
  description = "TTL, in seconds, for both the CNAME and TXT records."
  type        = number
  default     = 300
}

variable "domain_verification_name" {
  description = "Record name for the GitHub domain-verification TXT record (e.g. _github-pages-challenge-dermdunc.kriterion.theagentictekton.com)."
  type        = string
}

variable "domain_verification_value" {
  description = "Record value for the GitHub domain-verification TXT record, as issued by GitHub."
  type        = string
}

variable "create_domain_verification" {
  description = <<-EOT
    Whether to create the domain-verification TXT record. Defaults to true.
    Corrected 2026-07-04 (RISK-0003) upstream: the record name is scoped per
    subdomain, not per owner account, so every consumer needs its own TXT
    record and this should stay true. Kept only for the narrower case of
    re-onboarding the exact same subdomain after teardown, or (temporarily) a
    new consumer whose GitHub-issued TXT value isn't known yet. See
    ../../README.md "Blast radius".
  EOT
  type        = bool
  default     = true
}
