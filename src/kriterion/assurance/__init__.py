"""Anti-corruption layer for generic assurance evidence (ADR-007).

Kriterion can optionally ingest an AssuranceEvidenceEnvelope document pair
(``envelope.json`` + ``decision.json``) produced by an external assurance
system, and translate it into Kriterion's own ``EvidenceItem`` domain type.

This package is the ONLY place in Kriterion allowed to know that document
format. It never imports assurance code — the contract is data (canonical
JSON documents), not a Python dependency, and Kriterion remains fully usable
when no assurance evidence exists at all.
"""

from kriterion.assurance.adapter import (
    AssuranceImportError,
    AssuranceSummary,
    adapt_envelope,
    load_assurance_documents,
)

__all__ = [
    "AssuranceImportError",
    "AssuranceSummary",
    "adapt_envelope",
    "load_assurance_documents",
]
