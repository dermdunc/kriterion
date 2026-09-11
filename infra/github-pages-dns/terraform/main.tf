# Single consumer: kriterion.theagentictekton.com -> dermdunc.github.io.
#
# A new, standalone root config, not an added module block in
# agentic-infra-lab's own shared github-pages-dns/terraform/main.tf. That
# file's hosted_zone_id/pages_host variables are single, shared values used
# identically across all 6 of its coderturtle.io module instances -- Kriterion
# needs a different zone (theagentictekton.com) and a different Pages host
# (dermdunc.github.io, not coderturtle.github.io), so it gets its own state
# here instead of refactoring a file that manages 6 other real, live
# subdomains. See ../README.md for the full reasoning and provenance.
module "pages_dns" {
  source = "./modules/pages-dns"

  hosted_zone_id             = var.hosted_zone_id
  subdomain_fqdn             = var.subdomain_fqdn
  pages_host                 = var.pages_host
  ttl                        = var.ttl
  domain_verification_name   = var.domain_verification_name
  domain_verification_value  = var.domain_verification_value
  create_domain_verification = var.create_domain_verification
}
