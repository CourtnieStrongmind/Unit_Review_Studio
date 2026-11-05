"""Copy the current player into the Unit Review Studio so its preview always works.

Run this after any change to review/index.html:
    python tools/build_studio.py
"""
import pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
player = (root / "review" / "index.html").read_text(encoding="utf-8")
studio_path = root / "studio" / "review" / "index.html"
studio = studio_path.read_text(encoding="utf-8")

safe = player.replace("</script", "<\\/script")
block = '<script type="text/plain" id="playerSource">' + safe + "</script>"
new, n = re.subn(
    r'<script type="text/plain" id="playerSource">.*?</script>(?=\s*<!-- PLAYER-END -->)',
    lambda m: block,
    studio,
    flags=re.S,
)
if n != 1:
    raise SystemExit("Couldn't find the PLAYER-START/PLAYER-END block in the studio.")
studio_path.write_text(new, encoding="utf-8")
print("Studio updated with the current player.")
