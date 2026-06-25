# Skill Packaging

Use external skill-design input as packaging guidance, not as a new authority layer.

## Packaging Principles

1. Treat `description` as the routing contract, not a summary.
2. Keep `SKILL.md` as the short operating contract.
3. Move rare or deep material into references by progressive disclosure.
4. Add scripts only for deterministic validation, formatting, or repeatable error handling.
5. Add examples only when they reduce ambiguity at activation or output.

## Packaging Check

Before reinforcing a local skill, ask:

1. Does the `description` route the skill with specific triggers?
2. Is `SKILL.md` the shortest useful operating contract?
3. Would a reference file reduce context load?
4. Would a deterministic script prevent repeated generated logic?
5. Is an example needed to remove activation or output ambiguity?

Apply packaging work only after behavior is clear. Packaging cannot rescue an unclear workflow.

## Do Not Promote

Do not turn packaging guidance into public product surface, installer docs, package manifests, or commercial claims until repeated local evidence proves it improves precision without adding contextual noise.
