# CRO: On-Demand Claim Summary

Architecture for the CRO on-demand claim summary service (The Hartford, EDS Claims).

- Data in Snowflake; orchestration and state in AWS; all AI workload on GCP (Vertex AI Agent Engine, Gemini) reached via Workload Identity Federation.
- Summaries are generated only on handler request, only for flagged claims older than 30 days, and only when the claim has changed since the last summary.
- Internal UI follows HIG pattern SPA_Internal_04 with declared deviations (see page 5 of the current diagram).

## Layout

| Path | Contents |
|---|---|
| `architecture/diagrams/` | draw.io files, one per version. Open in diagrams.net or the draw.io desktop app. |
| `architecture/previews/` | PNG render of each page of the current version. |
| `architecture/generator/` | Python source that produces the draw.io file and previews. The diagram is generated, not hand-edited. |
| `architecture/references/` | Enterprise patterns and inputs the design responds to. |

## Current version: v0.4 (2026-10-26)

| Page | Content |
|---|---|
| 1 - Conceptual | Solution architecture with numbered request and ingest paths |
| 2 - Deployment | AWS reference-architecture view with service icons |
| 3 - Handler access control | Four-layer model: SSO, AD group, claim entitlement (ENT# vs CLAIM#), audit |
| 4 - Auth sequence | Authentication and API authorization sequence per pattern section 4 |
| 5 - Pattern conformance | Adopted / adapted (D1-D4) / not applicable / open items |

## Regenerating

The generator depends on the `cloud-architecture-diagrams` skill library (`archdiagram.py` and its icon pack).
Point `ARCHDIAGRAM_SCRIPTS` at that library's `scripts/` folder, then:

```
pip install cairosvg
python3 architecture/generator/cro_v04.py architecture/diagrams/CRO_Architecture_v0.4
```

## Version history

- v0.4: aligned to HIG pattern SPA_Internal_04 (private API Gateway, MSAL.js + Azure AD, Lambda Authorizer); Cognito/CloudFront/WAF removed; sequence and conformance pages added.
- v0.3: UI and SSO infrastructure added; handler-level access control page added.
- v0.2: official cloud icons; two-page conceptual + deployment format.
