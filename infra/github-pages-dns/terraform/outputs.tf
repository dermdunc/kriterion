output "record_fqdn" {
  description = "FQDN of the CNAME record (kriterion.theagentictekton.com -> dermdunc.github.io)."
  value       = module.pages_dns.record_fqdn
}

output "verification_record_fqdn" {
  description = "FQDN of the domain-verification TXT record."
  value       = module.pages_dns.verification_record_fqdn
}

output "site_url" {
  description = "Primary URL for Kriterion under its own subdomain."
  value       = module.pages_dns.site_url
}
