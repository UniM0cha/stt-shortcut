# CLAUDE.md

## Project Overview

**stt-shortcut** is a Python script that programmatically generates an Apple Shortcuts `.shortcut` file for speech-to-text transcription. The generated shortcut records audio on iPhone/iPad/Mac, sends it to the Groq Whisper API for transcription, and copies the result to the clipboard.

Primary language of the project (code comments, UI strings, README): **Korean**.

## Repository Structure

```
.
├── generate_stt_shortcut.py   # Main (and only) script — generates the .shortcut file
├── README.md                  # User-facing documentation (Korean)
├── .gitignore                 # Ignores generated *.shortcut files
└── CLAUDE.md                  # This file
```

This is a single-file project with no subdirectories, no tests, and no package management.

## Tech Stack

- **Python 3** (standard library only — no third-party dependencies)
- Key stdlib modules: `plistlib`, `uuid`, `subprocess`, `sys`, `os`
- **Apple Shortcuts CLI** (`shortcuts sign`) — required at runtime on macOS to sign the generated shortcut
- **Groq Whisper API** — external STT service (OpenAI-compatible endpoint)

## How to Run

```bash
python3 generate_stt_shortcut.py YOUR_GROQ_API_KEY
```

This produces a signed `음성받아쓰기.shortcut` file in the script directory. Requires macOS with the `shortcuts` CLI available.

## Architecture

The script follows a **builder pattern** to construct an Apple Shortcut plist:

1. **Helper functions** (`make_uuid`, `make_text`, `make_attachment`, `make_inline_var`, `make_file_field`, `make_bearer_header`) create the data structures that represent Shortcut action parameters and inter-action references.

2. **`generate_shortcut(api_key)`** assembles a 6-action shortcut pipeline:
   - Action 0: Record audio (lossless, immediate start)
   - Action 1: Get Text (stores API key; populated via import question)
   - Action 2: HTTP POST to Groq API (multipart/form-data with audio file)
   - Action 3: Extract `"text"` from JSON response
   - Action 4: Copy to clipboard
   - Action 5: Show notification

3. **`main()`** serializes the shortcut to binary plist, then signs it via `shortcuts sign --mode anyone`.

Actions are linked by UUIDs — each action's output UUID is referenced by downstream actions.

## Key Conventions

- **No external dependencies** — everything uses Python's standard library. Do not introduce `pip` packages.
- **Korean strings** — all user-facing text (shortcut name, notifications, CLI messages, comments) is in Korean. Maintain this convention.
- **Configurable parameters** are inline in `generate_shortcut()`:
  - API URL: `https://api.groq.com/openai/v1/audio/transcriptions`
  - Model: `whisper-large-v3`
  - Language: `ko` (ISO 639-1)
  - Recording quality: `Lossless`
- **No linting/formatting config** exists. Follow the existing code style: simple functions, clear variable names, Korean docstrings/comments.
- **Generated `.shortcut` files are gitignored** — never commit them.

## Development Notes

- There are no tests, CI/CD, or build systems. The script is validated by running it on macOS and importing the generated shortcut.
- The `shortcuts sign` command only works on macOS. On other platforms, the script will produce the unsigned plist at `/tmp/stt_shortcut_unsigned.shortcut` but fail at the signing step.
- The Apple Shortcut plist format is undocumented. The data structures in this script were reverse-engineered. When modifying action parameters, preserve the exact `WFSerializationType` and `WFItemType` values.
- API key is passed as a CLI argument and embedded as a default value in an import question, so end-users can override it when installing the shortcut.
