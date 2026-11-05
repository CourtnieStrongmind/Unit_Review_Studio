# Unit Review Studio

Authors build **Review Quest** activities here: short, replayable unit reviews that practice exam-style questions. No code required.

Student-facing name: **Review Quest**.  
Authoring tool name: **Unit Review Studio**.

## Style

Fanny Pack design system: Poppins for headings and buttons, Nunito Sans for body text, Lilac Bush pill buttons, Pearl Brush backgrounds, Highland for correct, and Cinnabar for errors. Icons are inline SVG, with no emoji.

## Folder layout

```
review/
  index.html                  The Review Quest player students see
  sets/
    <activity-name>/          One folder per activity
      content.json            Questions, feedback, and media file names
      media/                  Pictures and audio for that activity
studio/
  review/
    index.html                The Unit Review Studio, where authors build activities
tools/
  build_studio.py             Copies the player into the Studio for its preview
```

## Question types in v1

- Multiple choice
- Select all that apply
- Match (term to definition, or similar pairs)
- Sort into bins

## Links

These assume the repo is named `unit-review-studio` on interactives hosting. Change `CONFIG.liveBase` in `studio/review/index.html` if the live path differs.

- Player: `https://interactives.strongmind.com/unit-review-studio/review/index.html?set=<activity-name>`
- Studio: `https://interactives.strongmind.com/unit-review-studio/studio/review/index.html`

Embed the player link in Helios like other interactives. It includes iframe-resizer 4.2.11.

## How authors make an activity (for now)

1. Open the Studio and fill in Basics, Questions, and Feedback. The preview updates as you type.
2. Fix anything listed under "Ready to publish?"
3. Click **Publish**. You get `<activity-name>.zip`.
4. Unzip it into `review/sets/`, then branch, commit, open a PR, merge, and deploy as usual.

The Studio keeps a draft in the browser automatically. That draft lives only in that person's browser. Publish downloads the zip you keep in the repo.

## Changing the player

After any change to `review/index.html`, run:

```
python tools/build_studio.py
```

## Content rules

- At least 1 question. Aim for 3–5 per objective when building a full unit review.
- Every picture needs alt text.
- Images up to 2 MB. Large photos are scaled down to 800 pixels on the longest side when added.
- Audio up to 5 MB (MP3 recommended).
- Activity names use only lowercase letters, numbers, and dashes.
- Each question needs an objective label, a prompt, type-specific answers, a one-line explanation, and an optional lesson link.
