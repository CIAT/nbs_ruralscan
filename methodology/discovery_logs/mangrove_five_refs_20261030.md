# Five mangrove cited-source recoveries — 2026-10-30

> **Provenance.** Tracked copy of the discovery agent's report (`pipeline/staging/discovery/`, gitignored). Run `mangrove_five_refs_20261030_refs`, ruleset **v1.8.1**, actual family `mangrove_restoration__tidal_coastal`. Registered by `scripts/register-discovery.py` on 2026-10-30: candidates → `pipeline/acquisition_queue.csv` (status `pending`), SRCH rows `mangrove_five_refs_20261030_refs`, ledger per `--ledger`.


## Scope and screening

Bounded reference follow-up to Worthington and Spalding2018 PDF14/18/20;
mangrove_restoration / mangrove_restoration__tidal_coastal / T3 and T6. Discovery
v1.8.1. Five unique cited works inspected; mirrors and summary manifestations are
not extra studies. Two literature candidates (T6), three grey candidates (two T3,
all three T6). Carbon papers support model/stock context and original-study tracing;
no stock-to-rate conversion or effect eligibility assumed. Seven table/process
memberships across five works. The five-step funnel and provisional six-axis
credibility assessments are retained in screening.json/candidates.json.

Actual channels: title/author/year web search, publisher pages, institutional and
author-organization repositories, Crossref and DataCite identity services. Stock
reconciliation limited to canonical SRC/queue dedupe; no new stock survey. Tool/code,
Lens/OpenAlex bibliographic sweeps, AGRIS and multilingual expansion were not run:
this is recovery of five named English referrals, not a new comprehensive search.
Stop: all five named PDFs obtained; not saturation. No ledger-completion stamp.

## Identity findings

Hutchison seed title was inaccurate: authoritative title is *Predicting Global
Patterns in Mangrove Forest Biomass*. Crossref citation uses online-issued2013;
PDF issue is May/June2014. Existing candidate ID uses print year, no duplicate work.
Two journal DOIs pass Crossref title overlap1.0 and citations are rebuilt from its
records. Staffordshire and Blue Ventures are author-institution mirrors.

Spalding coastal defence and Hutchison fisheries were obtained from publisher
Wetlands International. Losada technical report came from publisher TNC's
Conservation Gateway, 44 pages, not the separate12-page summary. Current publisher
landing-page citation confusingly points to summary authors/identifier; PDF2 and
DataCite resolve the technical report identity. Its DOI10.7291/V9DV1H2S is valid in
DataCite but Crossref returns404. Preserve full DOI evidence in acquisition audit;
leave registry DOI blank under current Crossref rule and explicitly hold promotion/
extraction pending DOI-provider handling. This is not an inaccessible or paywalled paper.

No author contact, dataset/code intake, source promotion, evidence extraction,
human review, or analytical synthesis. Prior ontology/transfer holds remain.

## Verbatim queries

- `Hutchison Predicting global patterns carbon storage mangrove forests 2014 pdf`
- `Sanderman 2018 global map mangrove forest soil carbon 30 m pdf`
- `Losada 2018 global value mangroves risk reduction report pdf`
- `Spalding McIvor Tonneijck Tol van Eijk 2014 Mangroves coastal defence pdf`
- `Hutchison Spalding Ermgassen 2014 role mangroves fisheries enhancement pdf`

## Next action

Verify opening titles and immutable cache/library hashes; register acquired artifacts.
Read and inventory eligible original methods before staging effects. Guidance reviews
are source maps, not independent repetitions of the studies they cite. Resolve Losada's
DOI-provider hold through an explicit metadata-policy change rather than self-verification.
