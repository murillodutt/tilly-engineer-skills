# Tilly Engineer Skills

TES is a local operating layer for AI-assisted engineering. It gives Codex,
Claude Code, Cursor, and similar coding agents a shared way to remember project
context, run gates, preserve evidence, and make repo changes that a team can
inspect after the chat is gone.

## A Small New Voice In The Workshop

`tes-tts` is growing from a simple read-aloud helper into a local voice
interface for engineering sessions. The interesting part is not just that TES
can speak. It is that it can prepare technical prose for speech while keeping
secrets redacted, code as text, paths as useful references, and mixed PT-BR plus
English engineering terms closer to how humans actually say them.

For users who want a stronger local voice, TES can now use OmniVoice as an
optional provider. OmniVoice is not bundled with TES, and TES does not claim
ownership over it. The provider lives in a local ignored runtime folder, uses a
local voice profile, and can warm a protected voice prompt cache so the first
read does not pay the full setup cost every time.

The result is simple: keep TES small, keep the voice local, and let the agent
read technical work back to you in a way that can be paused, replayed, compared,
and improved.

Start with the guide:

- [TES TTS OmniVoice Guide](../docs/install/TES-TTS-OMNIVOICE.md)
- [Public manual](https://murillodutt.github.io/tilly-engineer-skills/install/USER-MANUAL.html)
- [Repository README](../README.md)

Responsible use matters. Voice cloning should only use voices you own or are
authorized to use, and generated audio should stay under local runtime folders
unless the user explicitly chooses otherwise.
