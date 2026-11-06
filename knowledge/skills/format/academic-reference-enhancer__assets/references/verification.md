# Reference Verification

Use this process for candidate reference lists, generated references, existing bibliographies, and `reference/*.md` suggestions.

## Metadata Checks

For each reference, verify:

- Title exists and matches exactly or with explainable punctuation/case differences.
- Authors match the source record.
- Publication year is correct.
- Venue, publisher, conference, standard body, or official source is correct.
- Volume, issue, pages, article number, or standard number are correct when present.
- DOI exists and resolves to the same work when a DOI is claimed.
- Document type is correct: journal article, conference paper, standard, regulation, electronic resource, dataset, preprint, book, or chapter.
- The work supports the intended claim.

## Evidence Record

Record verification evidence for every kept reference:

```text
source_name:
source_url_or_doi:
matched_title:
matched_authors:
matched_year:
matched_venue:
access_date:
mismatch_notes:
```

## Grades

- **A**: Verified by DOI or publisher page; metadata complete; relevance is clear.
- **B**: Verified by reliable academic or official database; minor metadata is missing but not material.
- **C**: Partially verified or relevance is plausible but needs user confirmation.
- **D**: Metadata conflict, weak relevance, wrong document type, or not recommended.
- **E**: Cannot be verified or appears fabricated; must be replaced or removed.

Use Grade A/B directly. Ask before using Grade C. Replace or remove Grade D/E.

## Replacement Rules

When replacing a problematic reference:

- Prefer journal articles if the user has a journal-ratio requirement.
- Use a source that supports the same or closely related claim.
- Verify the replacement through DOI, publisher page, or authoritative database.
- Preserve topic coverage across chapters.
- Record the original reference, replacement reference, and reason for replacement.

## Ratio Checks

When calculating journal ratio, count only formally published journal articles as journal articles. Do not count conference papers, standards, regulations, preprints, web pages, books, or reports as journal articles.
