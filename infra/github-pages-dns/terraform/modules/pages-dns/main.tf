# main.tf: Route 53 records that point a workshop subdomain at GitHub Pages.
#
# Deliberately minimal compared to modules/static-site: no us-east-1 provider,
# no ACM certificate, no wait-for-validation. GitHub issues and enforces its own
# certificate asynchronously once the CNAME resolves publicly — nothing here
# blocks on that (see patterns/github-pages-dns/interpreter-notes.md).
#
# Vendored verbatim from agentic-infra-lab's github-pages-dns pattern
# (patterns/github-pages-dns/terraform/modules/pages-dns/main.tf), per that
# lab's own convention: consuming projects vendor a local copy rather than
# reference the module across repos. See ../../README.md for provenance.

# ---------------------------------------------------------------------------
# CNAME: {subdomain}.{root_domain} -> {owner}.github.io.
# ---------------------------------------------------------------------------
resource "aws_route53_record" "cname" {
  zone_id = var.hosted_zone_id
  name    = var.subdomain_fqdn
  type    = "CNAME"
  ttl     = var.ttl
  records = [var.pages_host]
}

# ---------------------------------------------------------------------------
# TXT: domain-verification challenge. Created by default so the subdomain is
# claimed to this GitHub account and cannot be taken over by another account
# if the workshop repo is ever deleted or renamed.
#
# Corrected 2026-07-04 (RISK-0003): the name/value GitHub actually issues is
# scoped per SUBDOMAIN, not per owner account — a real onboarding disproved
# the original per-owner-account assumption (the actual issued name included
# the specific subdomain). Every consumer needs its own TXT record;
# create_domain_verification should stay true for every workshop. It exists
# only for the narrower case of re-onboarding the exact same subdomain after
# teardown, where a record with that exact name might already exist — see
# README.md "Blast radius" and patterns/github-pages-dns/interpreter-notes.md.
# ---------------------------------------------------------------------------
resource "aws_route53_record" "domain_verification" {
  count   = var.create_domain_verification ? 1 : 0
  zone_id = var.hosted_zone_id
  name    = var.domain_verification_name
  type    = "TXT"
  ttl     = var.ttl
  # Do NOT wrap this in literal quotes: the AWS provider (confirmed empirically
  # against a real account, provider 6.53.0) already quotes TXT/SPF record
  # values for the Route53 API. Adding our own quotes here double-quotes the
  # value and Route53 rejects it (InvalidChangeBatch: "Value should be
  # enclosed in quotation marks", seen with a literal `""value""`).
  records = [var.domain_verification_value]
}
