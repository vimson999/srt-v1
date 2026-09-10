# Semantic Asset Retrieval and Reuse Planning

Use `scripts/plan_asset_reuse.py` after asset intake and review metadata are
available. It ranks existing shared-library assets for shot needs and records
an inspectable reuse plan. It does not download, copy, move, delete, or mutate
raw media, the generated catalog, durable metadata, or usage history.

The planner follows the existing source-of-truth chain:

```text
catalog/assets.json + catalog/metadata.json + catalog/usage.json
                                ↓
                    shot-level asset needs
                                ↓
          ranked candidate cards + asset-reuse-plan.json
```

Stable `asset_id` is the join key throughout. Paths are computed catalog data;
metadata sidecars may refine reviewed semantic fields but may not overwrite
paths, hashes, file existence, or sizes.

## Command

```bash
python3 scripts/plan_asset_reuse.py \
  --catalog <factory_root>/asset-library/catalog/assets.json \
  --metadata <factory_root>/asset-library/catalog/metadata.json \
  --usage <factory_root>/asset-library/catalog/usage.json \
  --needs projects/<project_id>/storyboard/asset-needs.json \
  --output projects/<project_id>/manifest/asset-reuse-plan.json
```

When `--metadata` or `--usage` is omitted, the planner looks beside
`assets.json` and tolerates a missing default sidecar. An explicitly supplied
path must exist so provenance or usage controls are not silently discarded.

`asset-needs.json` contains:

```json
{
  "needs": [
    {
      "shot_id": "S04",
      "visual_action": "establish",
      "shot_language": "context_establish",
      "purpose": "Electronics manufacturing context",
      "keywords": ["electronics", "manufacturing"],
      "asset_role": "context",
      "treatment": {
        "trim": "00:06-00:10",
        "crop": "detail",
        "scale": "base",
        "speed": "slow",
        "opacity": "base",
        "layout": "full_frame"
      }
    }
  ]
}
```

`shot_language` is the selected family ID, not a renderer component name.
Keywords should come from inspected descriptions and tags rather than filename
guesses.

## Candidate cards

For every need, the report returns ranked candidate cards with:

`asset_id,shot_id,visual_action,shot_language,decision,semantic_fit,intended_use,prohibited_interpretation,publication_gate,prior_usage,selection_status,provenance_status,license_status,resolution_warning,warnings`

The deterministic rank uses reviewed keyword overlap, asset-role compatibility,
selection status, and prior usage. It prefers an equally fitting less-used
asset, but never invents semantic similarity. A context asset cannot satisfy an
`evidence` need merely because its description mentions a report.
Human-reviewed descriptions, tags, `use_as`, `acceptance_basis`, and
`do_not_claim_as` remain authoritative.

Candidate decisions are separate from publication clearance:

- `primary`: a semantically fitting `keep` asset;
- `fallback`: a fitting `backup` or `transition_only` asset;
- `review_required`: a fitting asset whose selection status is not resolved;
- `unavailable`: no semantic overlap, rejected status, or a missing file.

An unverified asset may remain a preview candidate while
`publication_gate.required=true`. Gate reasons distinguish unverified
provenance, uncleared license, and incomplete selection review. Never convert a
gate into `verified` merely because the asset ranks well.

## Evidence and low resolution

Authentic low-resolution report screenshots remain eligible when their
reviewed metadata matches the evidence need. Preserve `resolution_warning` in
both the candidate card and assignment. Resolution must not change `keep` to
`backup` or create a false gap. If pixels are unreadable, the asset may provide
report backing and source identity, but exact wording still comes from readable
source text.

## Reuse and treatment variation

Reuse is allowed. Each assignment records its treatment and compares it with
the immediately preceding use of the same asset. Variation dimensions include
trim, crop, scale, speed, opacity, and layout, without requiring every reuse to
change every dimension.

Adjacent reuse with an identical treatment receives an
`immediate_identical_reuse` warning; it is not hidden or misreported as unique
footage. Varied reuse remains allowed and records the dimensions that changed.
Historical usage count and last project/Shot stay visible in every candidate
card.

## Genuine gaps

Create a gap only when no semantically fitting, non-rejected, existing asset is
available. A related context asset may be a fallback when `do_not_claim_as`
keeps its interpretation honest. Unique footage duration, prior use, low
resolution, or an unresolved publication gate alone must not create a gap.

Each gap contains:

`shot_id,need,reason,genuine`

The current stable reason is `no_honest_available_candidate`. Programmatic
visuals and existing honest reuse should be considered before requesting new
media.

## Limits

The planner trusts reviewed catalog semantics; it does not inspect frames,
authenticate reports, clear licenses, or write usage records after final
binding. Perform visual/provenance review before planning, then update
`catalog/usage.json` after assignments are accepted and bound to shots.
