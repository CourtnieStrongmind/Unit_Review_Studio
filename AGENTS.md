# Project context for AI assistants

Read this before making changes. The README covers how to use the tool. This file covers why things are the way they are.

This repo is public-facing once published. Don't add secrets, tokens, internal-only URLs, or private StrongMind details to it.

## Who you're working with

- Court is a curriculum developer at StrongMind, not an engineer. She builds and ships interactive HTML learning content for K–8 and embeds it in Helios with an iframe.
- She is comfortable with git basics: branch, commit, push, PR, merge, then Dev Deploy and Prod Deploy through GitHub Actions.
- Explain technical terms in plain English.
- When a decision is hers to make, offer a few clear options instead of an open-ended question.
- Make targeted edits to existing files rather than rewriting them.
- Text written in her voice should be plain sentences. Avoid arrows, slashes, parentheses, and inline numbered lists in those drafts.
- She reviews closely for visual polish. Check layout at desktop, tablet, and phone widths before saying something is done.

## Naming

- **Unit Review Studio** is the repo and the authoring tool.
- Students see a unit review. Do not use “Review Quest” as a product name in student or training copy.

## The goal

A set of authoring studios so the curriculum team can build interactives without code. Related work:

1. Sort and match studio. Separate repo (`Sort_Interactive_Studio`).
2. Unit Review Studio. This repo.
3. Venn diagram and branching scenario. Not started.

## Where things stand

- v1 ships Multiple choice, Select all, Match, and Sort.
- Themes are Fanny Pack only for now. Extra skins come later.
- Remote publish helper is not turned on. Authors click Publish to download a zip for the repo.
- Teacher analytics view is out of scope for v1.

## How it works

### The player: `review/index.html`

- One self-contained HTML file. Outside resources: Google Fonts and iframe-resizer 4.2.11 from cdnjs.
- Loads `review/sets/<slug>/content.json` via `?set=<slug>`.
- With `?preview=1` or `srcdoc`, waits for studio `postMessage` types: `review-preview`, `review-ping`, `review-player-ready`.
- Screens: Start, Activity (one question at a time), End.
- Three tries per item by default. Correct earns points. Missed items show explanation and optional lesson link.
- End screen summarizes strong and weak objectives.
- Cards and choices shuffle where it makes sense.

### The studio: `studio/review/index.html`

- Self-contained. JSZip 3.10.1 for export and open.
- Sections: Basics, Questions, Feedback, Ready to publish checklist, live preview.
- After any change to `review/index.html`, run `python tools/build_studio.py`.
- Draft key: `review-studio-draft-v1`.
- `CONFIG.publishUrl` empty until a publish helper exists. `CONFIG.liveBase` points at the player URL.

## Design rules (Fanny Pack)

- Fonts: Poppins 500/600 headings and buttons; Nunito Sans body.
- Background: Pearl Brush 50 `#F9F6F3` only. No colored glows or gradients behind the page.
- Primary buttons: Lilac Bush 600 `#8F5CB4`, hover 700 `#7E4BA3`, pill-shaped.
- Correct: Highland. Errors: Cinnabar. Never reuse those for decoration.
- Frosted cards: white 72%, 16px blur, 2px Lilac Bush 200 border `#D0B4E4`, 20px radius.
- No emoji. Inline SVG icons.
- Sentence case, no exclamation marks in product copy.
- Text contrast at least 4.5:1.

## Testing

Serve with `python -m http.server` or Live Server. Check player interactions, tries, end summary, phone width, bad `?set=`, studio edit/publish/draft/clear, and built-in preview fallback.
