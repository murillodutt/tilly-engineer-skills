# Skill Packaging

Use this reference only when the current risk is packaging a local skill whose
behavior is already clear.

## Packaging Check

1. Does the `description` route the skill with specific triggers?
2. Is `SKILL.md` the shortest useful operating contract?
3. Would a reference file reduce context load?
4. Would a deterministic script prevent repeated generated logic?
5. Is an example needed to remove activation or output ambiguity?

## Sequence

1. Resolve behavior first through prospecting, mining, or both.
2. Keep the main skill file small.
3. Move rare details into `references/**`.
4. Add scripts only for deterministic work.
5. Record local history when the change preserves a useful lesson.

## Stop

Stop if packaging starts inventing behavior, public claims, installer surface,
or edits to `tes-mine` or `tes-prospect`.
