output "record_fqdn" {
  description = "FQDN of the CNAME record (subdomain -> GitHub Pages host)."
  value       = aws_route53_record.cname.fqdn
}

output "verification_record_fqdn" {
  description = "FQDN of the domain-verification TXT record, or null when create_domain_verification is false."
  value       = try(aws_route53_record.domain_verification[0].fqdn, null)
}

output "site_url" {
  description = "Primary URL for the site."
  value       = "https://${var.subdomain_fqdn}"
}
