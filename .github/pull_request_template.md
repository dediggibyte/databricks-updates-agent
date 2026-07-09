<!-- databricks-updates-agent-pr-template: v1 -->
<!--
  databricks-updates-agent · unified pull-request template.

  Keep the `databricks-updates-agent-pr-template` marker comment above — it is
  required by .github/workflows/pr-template-check.yml so every PR shares ONE
  format. Fill in each section and delete the guidance comments. Do not add or
  remove top-level (`##`) sections.
-->

## Summary

<!-- What does this PR do, and why? 1-3 sentences focused on the "why". -->

## Change type

<!-- Check all that apply. Keep the list; just tick boxes. -->
- [ ] Feature
- [ ] Fix
- [ ] Refactor / chore
- [ ] Docs
- [ ] CI/CD or config
- [ ] Dependencies

## Changes

<!-- Bullet the notable changes. -->
-

## Test plan

<!-- How did you verify this? Commands run and expected results. -->
- [ ] `pytest -q` passes
- [ ] `pip install -e .` succeeds
- [ ] `python -m dbx_onepager fixtures --mock` runs clean (offline pipeline)
- [ ] `python -m dbx_onepager build` renders the site (if templates/render changed)

## Checklist

- [ ] Single concern — this PR is scoped to one feature/fix/refactor (unrelated changes split out)
- [ ] Generated output (`site/`, `email/`) is not committed
- [ ] README / config.yaml comments updated if behavior or configuration changed
- [ ] No secrets committed (`.env` stays out of git)
