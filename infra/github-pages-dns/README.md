# infra/github-pages-dns — kriterion.theagentictekton.com

Gives Kriterion's existing GitHub Pages site (`https://dermdunc.github.io/kriterion/`, served from
this repo's `docs/` on `main`, unchanged) a subdomain of `theagentictekton.com`. Produced under the
**Agentic Infra Lab** operating model: *the agent plans, the human applies.*

## Pattern

`github-pages-dns` — a Route53 CNAME (`kriterion.theagentictekton.com` → `dermdunc.github.io`) plus
a domain-verification TXT record, nothing else. No new AWS hosting: content stays on GitHub Pages
exactly as it is today; GitHub issues and enforces its own HTTPS certificate once the CNAME
resolves publicly.

```text
Route53 (CNAME + TXT)  →  dermdunc.github.io  →  GitHub Pages (docs/ on main, unchanged)
```

Vendored from `~/Development/hekton/labs/agentic-infra-lab/patterns/github-pages-dns/terraform/modules/pages-dns`
(copied verbatim into `terraform/modules/pages-dns/`) per that lab's own convention: consuming
projects vendor a local copy of a pattern's module rather than reference it across repos (the same
convention `blog-factory-lab`'s and `agentic-tekton`'s own infra directories follow). This gets its
own, new root Terraform config rather than adding a module block to `agentic-infra-lab`'s existing
`github-pages-dns/terraform/main.tf` — that file's `hosted_zone_id`/`pages_host` are single, shared
values across its 6 existing `coderturtle.io` consumers; Kriterion needs a different zone
(`theagentictekton.com`) and a different Pages host (`dermdunc.github.io`, not
`coderturtle.github.io`), so it gets isolated state instead of risking a refactor of a file that
manages 6 other real, live subdomains.

## What this does NOT do

Per the module's own upstream README: enabling GitHub Pages, setting the custom domain, and HTTPS
enforcement on the `kriterion` repo are each **this repo's own concern**, not Terraform's — see
"After apply" below.

## The human-apply gate

This terraform is **generated and reviewed, not deployed.** Per the Infrastructure Gremlin
contract (`agentic-infra-lab/workflows/provision-infra-from-manifest.md`), an agent may run
read-only `terraform plan` but never `terraform apply`. The blast-radius classification and
approval are recorded in `deploy-manifest.yaml`.

## How to launch (human steps)

```bash
cd infra/github-pages-dns/terraform
cp terraform.tfvars.example terraform.tfvars
# Fill domain_verification_name/value with the exact values GitHub issues at
# github.com/settings/pages (dermdunc account) -> Add a domain -> theagentictekton.com.
# Never guess these.

terraform init

# Plan, then summarise + classify with the Infrastructure Gremlin:
terraform plan -out=tfplan
~/Development/hekton/labs/agentic-infra-lab/scripts/plan-summary.sh --chdir .

# Review the GREEN/AMBER/RED classification.
# Record the approval in ../deploy-manifest.yaml, then:
terraform apply tfplan        # ← the only human-only step
```

## After apply (this repo's own concern, not Terraform's)

Set the GitHub Pages custom domain on `dermdunc/kriterion` so GitHub actually serves the site at
the new subdomain and issues its own certificate for it:

```bash
gh api -X PUT repos/dermdunc/kriterion/pages -f cname=kriterion.theagentictekton.com
```

(or commit a `docs/CNAME` file containing `kriterion.theagentictekton.com` via the normal PR flow —
either has the same effect; the `gh api` route was the one actually used, see `docs/decisions.md`).
Then verify: `dig kriterion.theagentictekton.com` resolves, and the URL serves Kriterion's site over
HTTPS (GitHub's own certificate issuance can take a few minutes after DNS resolves — not instant).

## Prerequisites (not assumed present)

- Terraform >= 1.7, AWS CLI configured with credentials that can manage Route53 records in the
  `theagentictekton.com` hosted zone (same account `agentic-tekton`'s own infra already uses).
- The `theagentictekton.com` Route53 hosted zone must exist (it does — zone id in
  `deploy-manifest.yaml`, confirmed via a read-only `aws route53 get-hosted-zone` call).
- A verified domain (`theagentictekton.com`) on the `dermdunc` GitHub account, via that account's
  own "Add a domain" step — a one-time, browser-only, human action; this is what issues the TXT
  value `terraform.tfvars` needs.

## Notes

- `terraform.tfvars`, `*.tfstate*`, and `.terraform/` are gitignored — never commit state or real
  values (see the repo's own `.gitignore`).
- This is a deliberate, narrow exception to `agentic-tekton`'s 2026-09-02 default of linking
  standalone products from its `/work` page rather than giving them subdomains (made for
  Tektograph, a fully independent product). Kriterion is a Hekton factory-output experiment being
  showcased *from* theagentictekton.com, closer in kind to the Field Journal
  (`hekton.theagentictekton.com`) than to Tektograph — see both projects' `docs/decisions.md` for
  the recorded reasoning.
