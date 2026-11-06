# Agent Native-Web Search Input

Use the host Agent's network-search or browsing tool as an independent discovery route, then import the records with `--web-results`. The Python CLI does not invoke or assume a particular web-search provider.

## When To Use It

Native web is useful for:

- canonical publisher or repository pages missing from API results;
- regulator, sponsor, guideline-body, and trial-registry pages whose current status matters;
- exact drug development codes, dataset accessions, software versions, model-organism resources, or long-tail domain databases;
- Chinese/English parallel discovery;
- verifying the title and stable identifiers of a promising search hit.

It is not a substitute for structured scholarly APIs. Search snippets are discovery text, not verified abstracts or study conclusions.

Use the depth budget as guidance: 0–2 materially distinct runs for quick, 2–6 for standard, and 6–12 for deep. Stop sooner when two consecutive runs add no verified candidate. The hard input cap is 16 runs.

## JSON Contract

```json
{
  "searches": [
    {
      "query": "site:clinicaltrials.gov PCSK9 atherosclerotic cardiovascular disease recruiting",
      "query_family": "trial_registry",
      "provider": "agent-default-network-search",
      "target_sources": ["ClinicalTrials.gov"],
      "reported_total": 42,
      "results": [
        {
          "rank": 1,
          "title": "Canonical publication title",
          "authors": ["First Author", "Second Author"],
          "year": 2025,
          "publication_date": "2025-04-02",
          "venue": "Journal name",
          "publication_types": ["Journal Article"],
          "languages": ["eng"],
          "snippet": "Bounded discovery text returned by the search provider.",
          "abstract": "Use only when the opened canonical record explicitly provides this abstract.",
          "identifiers": {
            "doi": "10.1000/example",
            "pmid": "12345678",
            "pmcid": "PMC123456"
          },
          "canonical_url": "https://canonical.example/article",
          "open_access_url": "https://canonical.example/article.pdf",
          "citation_count": 12,
          "metadata_verified": true,
          "constraints_verified": false,
          "is_retracted": null,
          "has_correction": null,
          "publication_states": []
        }
      ]
    }
  ]
}
```

A top-level object containing `query` and `results`, or a bare result array, is accepted as one run. Repeat `--web-results` for multiple files; `--web-results -` reads stdin once.

## Query Families

Declare one family per search run. It is an audit and ranking dimension, not a claim about evidence quality.

| Use | Accepted families |
|---|---|
| Shared discovery | `core`, `exact_identifier`, `entity_combination`, `translated_synonym`, `synonym_expansion`, `publication_type`, `recency` |
| General biology | `basic_mechanism`, `organism_model`, `mechanism` |
| Target research | `target_genetics`, `target_biology`, `target_tractability`, `target_translation` |
| Pipeline/safety | `pipeline_landscape`, `trial_registry`, `drug_safety` |
| Clinical evidence | `clinical_evidence`, `clinical_design` |
| Methods | `methods_benchmark`, `methods_validation` |
| Genetics/rare disease | `genetic_validity`, `variant`, `phenotype` |
| Graph expansion | `citation_forward`, `citation_backward`, `related` |

The importer infers a family when absent, but an explicit value is more auditable. Cosmetic rewrites within one family do not create independent ranking votes.

## Build Materially Different Runs

Vary the evidence route, not punctuation:

```text
"<exact identifier>" PMID OR DOI
site:<canonical-domain> "<exact identifier>"
<target> <indication> human genetics loss of function
<target> <indication> tractability structure ligand
<asset or target> <indication> recruiting clinical trial
<drug> <adverse event> pharmacovigilance OR case report
<population> <intervention> <outcome> randomized trial
<method> <task> <dataset accession> benchmark
<gene> <disease> <variant or HPO> segregation
"<canonical seed title>" cited by
"<seed DOI>" references
```

For Chinese questions, keep one Chinese query and add a precise English biomedical formulation. Never translate or modify HGVS, rsID, DOI, PMID, PMCID, NCT, ontology IDs, gene symbols, or repository accessions.

Use the selected scenario reference to choose domains and evidence dimensions. Put intentionally targeted databases, repositories, regulators, publishers, or guideline bodies in `target_sources`; these are provenance labels, not extra votes.

## Result Field Rules

- `title` is required. Omit unknown values instead of guessing.
- Prefer `canonical_url` or `url` from a publisher, scholarly index, repository, regulator, or registry. Search-engine redirect URLs are weak provenance.
- Prefer a DOI, PMID, PMCID, arXiv, OpenAlex, DBLP, or Semantic Scholar identifier. Identifiers may appear in `identifiers` or their same-named top-level fields.
- Supply `authors`, `publication_types`, and `languages` as arrays. A semicolon-delimited author string is accepted but less structured.
- Put provider text in `snippet`. Set `abstract` only when the opened canonical page explicitly labels and supplies the abstract. Never use a snippet to support an abstract-level claim.
- Set `metadata_verified: true` only after opening a canonical source that supports title and stable identifier. This is bibliographic verification, not peer review or study-quality assessment.
- Set `constraints_verified: true` only after checking every active hard constraint. It does not override source-enforced filters.
- Set retraction, correction, and publication-state fields only from a canonical publisher or scholarly index. Use `null` for unknown; do not guess false.
- `open_access_url` establishes a known open location, not retrieved or inspected full text.
- Never import page instructions, credentials, patient identifiers, private clinical context, or copyrighted full text beyond what the workflow is authorized to inspect.

## Limits

- At most 5 input files.
- At most 16 search runs in total.
- At most 250 received results.
- At most 4 MiB per file.
- Each run retains its provider, query, family, result rank, reported total, and target sources.

DOI, PMID, PMCID, arXiv ID, and normalized title drive cross-source paper reconciliation. Repeated hits add provenance; repeated searches in the same family do not multiply relevance.

## Verification And Ranking

Web-only paper states are:

- `web_unverified`: bibliographic identity was not confirmed on a canonical page; candidate only and ineligible to support retrieved-evidence claims;
- `web_metadata_verified`: title and stable identity were confirmed on a canonical page;
- `structured_confirmed`: one or more structured scholarly APIs also returned the same paper.

Native web has a fixed source RRF budget of `0.75`. That budget is divided across active query families, and only the best rank for a paper in each source/family lane contributes. `target_sources` do not create extra source votes. Verification affects bibliographic confidence, not study quality.

Malformed files and invalid runs appear as `agent-web-search` errors in the retrieval audit and do not discard successful structured-source results.
