---
name: tes-upstream-first
description: >-
  Check for an existing upstream solution BEFORE hand-rolling config, glue, or a
  workaround for any library/framework/tooling friction. Trigger this whenever you
  are about to wire up build/test/lint config by hand, whenever something "doesn't
  work out of the box" and you reach for a manual fix (custom resolve/alias rules,
  shims, polyfills, glue code, patched configs), whenever you pick a dependency
  version, or whenever you hit an integration error from a library and your first
  instinct is to configure around it. Also use before adding a dependency, bumping
  a version, or updating packages. The hand-rolled path is the fallback, not the
  default — a maintained helper is fewer lines, fewer assumptions, and tracks
  upstream. Use this even when you think you already know the manual fix; your
  knowledge of a library's testing/integration helpers may be stale.
license: MIT
---

# Upstream-First

A discipline gate that fires at design time — before you write a workaround, not
after. Manual config that "works" still costs: it reinvents wiring the ecosystem
already maintains and carries assumptions the framework's own helper had already
solved. The failure mode is silent — the hand-rolled config passes the gate and
ships, because nobody paused at the instinct to hand-roll to look for the better
path first.

The origin and full rationale for this gate live in `docs/CONTRACT-HISTORY.md`
alongside this skill. This file is the acting copy that fires in the moment of
decision.

## When this fires

The trigger is the *instinct to hand-roll*. The moment you catch yourself about to:

- add custom `resolve`/`alias`/`conditions`, a shim, a polyfill, or glue code to
  make a library work under a build/test/lint tool;
- write a config block because something "doesn't work out of the box";
- configure around an integration error from a framework or test runner;
- add a dependency, bump a version, or update packages,

stop and run the checklist below first. The whole point is that the typical miss
happens because no one pauses at this exact instinct — the manual fix feels
obvious, so the better path is never looked for.

## The checklist (in order)

Run these before writing the workaround. Most frictions die at step 1 or 2.

1. **Read the library's own testing/integration docs.** Use Context7 first (per
   the global Context7 rule) — your training data may not reflect recent helpers.
   Many frictions have a named, supported solution that the README buries.
2. **Look for a first-party helper or plugin.** Check the package's `exports`
   map, not just its README: `npm view <pkg> exports`. Look for a `*/vite`,
   `*/vitest`, `*-testing`, `setup`, or `plugin` subpath that encapsulates the
   wiring. A framework's official test helper is often sitting in its `exports`
   map doing exactly the wiring you were about to write by hand.
3. **Check if a newer patch/minor already fixes it.** `pnpm outdated` and
   `cargo update --dry-run`. The friction may be a known, already-released bug —
   updating is cheaper and safer than coding around it.
4. **Scope the cost of the helper.** Its peer deps and version constraints
   (`npm view <pkg> peerDependencies`). A helper that drags in a breaking major you
   don't want may not be worth it; a compatible one (right peer range) almost
   always is. Weigh "+1 maintained dep" against "N lines of config I now own."
5. **Only then hand-roll.** If the upstream path genuinely doesn't fit, write the
   manual fix — and leave a comment citing what you checked and why it didn't fit,
   so the next person (or the next you) can revisit when the ecosystem catches up.

## Stable releases only — never pre-release

This pairs with the checklist whenever step 3/4 or any dependency change picks a
version. Install the latest **stable** release only — never an alpha, beta, RC,
`-next`, `-canary`, `-rc`, or `-pre`, even when `@latest`-style tooling or a
"newest available" query surfaces one. A pre-release is not something we ship.

- Verify the channel before installing: `npm view <pkg> version` is the stable
  dist-tag. Reject any resolved version whose string carries a pre-release suffix
  (`-alpha`, `-beta`, `-rc.N`, `-next.N`, `-canary`, `-pre`, `0.0.0-…`).
- For cargo, `cargo update` already stays on stable semver; never pin a
  pre-release in `Cargo.toml`.
- If only a pre-release fixes a real blocker, that is a deliberate, user-approved
  exception — surface it and ask. Never default to it.

## Why it's a gate on the approach, not a test

This can't be a `commit:check` assertion — by the time a workaround is in the diff,
the wrong path is already taken and the cost (an extra maintained-by-you config) is
paid. The leverage is entirely at design time: a few `npm view` / Context7 lookups
before the first line of the workaround. That's where this skill earns its keep.
