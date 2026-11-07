"""Build a SharePoint-friendly Word guide with a clickable table of contents."""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "training" / "screenshots"
OUT = ROOT / "training" / "Unit-Review-Studio-Developer-Guide.docx"

BRAND = "8F5CB4"
BRAND_RGB = RGBColor(0x8F, 0x5C, 0xB4)
INK_RGB = RGBColor(0x4D, 0x1A, 0x72)
SOFT_RGB = RGBColor(0x73, 0x73, 0x73)

# bookmark id counter
_bookmark_id = 1


def next_bookmark_id():
    global _bookmark_id
    bid = _bookmark_id
    _bookmark_id += 1
    return bid


def set_run_font(run, size=11, bold=False, color=None):
    run.font.name = "Calibri"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Calibri")
    run.font.size = Pt(size)
    run.bold = bold
    if color is not None:
        run.font.color.rgb = color


def add_bookmark(paragraph, name):
    bid = str(next_bookmark_id())
    start = OxmlElement("w:bookmarkStart")
    start.set(qn("w:id"), bid)
    start.set(qn("w:name"), name)
    end = OxmlElement("w:bookmarkEnd")
    end.set(qn("w:id"), bid)
    paragraph._p.insert(0, start)
    paragraph._p.append(end)


def style_hyperlink_run(run_el, size_pt=11, bold=False):
    rPr = OxmlElement("w:rPr")

    rFonts = OxmlElement("w:rFonts")
    rFonts.set(qn("w:ascii"), "Calibri")
    rFonts.set(qn("w:hAnsi"), "Calibri")
    rPr.append(rFonts)

    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), str(int(size_pt * 2)))
    rPr.append(sz)
    szCs = OxmlElement("w:szCs")
    szCs.set(qn("w:val"), str(int(size_pt * 2)))
    rPr.append(szCs)

    color = OxmlElement("w:color")
    color.set(qn("w:val"), BRAND)
    rPr.append(color)

    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rPr.append(u)

    if bold:
        rPr.append(OxmlElement("w:b"))

    run_el.insert(0, rPr)


def add_internal_hyperlink(paragraph, anchor, text, size=11, bold=False):
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("w:anchor"), anchor)

    run = OxmlElement("w:r")
    style_hyperlink_run(run, size_pt=size, bold=bold)
    text_el = OxmlElement("w:t")
    text_el.text = text
    run.append(text_el)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)
    return hyperlink


def add_external_hyperlink(paragraph, url, text, size=11):
    part = paragraph.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)

    run = OxmlElement("w:r")
    style_hyperlink_run(run, size_pt=size)
    text_el = OxmlElement("w:t")
    text_el.text = text
    run.append(text_el)
    hyperlink.append(run)
    paragraph._p.append(hyperlink)
    return hyperlink


def add_title(doc, text, bookmark=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    set_run_font(run, size=24, bold=True, color=INK_RGB)
    p.paragraph_format.space_after = Pt(6)
    if bookmark:
        add_bookmark(p, bookmark)
    return p


def add_heading(doc, text, level=1, bookmark=None):
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        set_run_font(run, size=16 if level == 1 else 13, bold=True, color=INK_RGB)
    if bookmark:
        add_bookmark(p, bookmark)
    return p


def add_body(doc, text):
    p = doc.add_paragraph()
    parts = text.split("**")
    for i, part in enumerate(parts):
        run = p.add_run(part)
        set_run_font(run, size=11, bold=(i % 2 == 1))
    p.paragraph_format.space_after = Pt(8)
    return p


def add_link_line(doc, label, url):
    p = doc.add_paragraph()
    lab = p.add_run(label + " ")
    set_run_font(lab, size=11, bold=True)
    add_external_hyperlink(p, url, url, size=11)
    p.paragraph_format.space_after = Pt(8)
    return p


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        parts = item.split("**")
        for i, part in enumerate(parts):
            run = p.add_run(part)
            set_run_font(run, size=11, bold=(i % 2 == 1))


def add_numbered(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Number")
        parts = item.split("**")
        for i, part in enumerate(parts):
            run = p.add_run(part)
            set_run_font(run, size=11, bold=(i % 2 == 1))


def add_image(doc, filename, caption):
    path = SHOTS / filename
    if not path.exists():
        add_body(doc, f"[Screenshot missing: {filename}]")
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(path), width=Inches(5.8))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(caption)
    set_run_font(r, size=9, color=SOFT_RGB)
    cap.paragraph_format.space_after = Pt(12)


def add_back_to_contents(doc):
    p = doc.add_paragraph()
    add_internal_hyperlink(p, "toc", "Back to contents", size=10)
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(14)


def add_toc(doc, entries):
    """entries: list of (label, bookmark, indent_level)"""
    add_heading(doc, "Contents", level=1, bookmark="toc")
    intro = doc.add_paragraph()
    r = intro.add_run("Jump to a section:")
    set_run_font(r, size=11, color=SOFT_RGB)
    intro.paragraph_format.space_after = Pt(6)

    for label, bookmark, indent in entries:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.2 * indent)
        p.paragraph_format.space_after = Pt(4)
        add_internal_hyperlink(p, bookmark, label, size=11, bold=(indent == 0))


def main():
    global _bookmark_id
    _bookmark_id = 1

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.85)
    section.bottom_margin = Inches(0.85)
    section.left_margin = Inches(0.9)
    section.right_margin = Inches(0.9)

    add_title(doc, "Unit Review Studio", bookmark="top")
    sub = doc.add_paragraph()
    r = sub.add_run("Developer guide")
    set_run_font(r, size=14, bold=True, color=BRAND_RGB)
    sub.paragraph_format.space_after = Pt(8)

    add_body(
        doc,
        "Self-serve resource for curriculum developers building unit review activities.",
    )
    add_body(
        doc,
        "**Unit Review Studio** is the authoring tool. Students see a unit review on a lesson road.",
    )
    add_body(
        doc,
        "You do not need to write code. You fill in the studio, preview as a student, then publish a zip into the repo.",
    )

    toc_entries = [
        ("Links", "links", 0),
        ("What students get", "students", 0),
        ("Student start / road", "student-road", 1),
        ("A question", "student-question", 1),
        ("Match with Clear", "student-match", 1),
        ("Finished road", "student-finished", 1),
        ("End screen with lesson to revisit", "student-end", 1),
        ("Before you build", "before", 0),
        ("Build a review in the studio", "build", 0),
        ("1. About this unit and questions", "build-about", 1),
        ("2. Name each lesson", "build-name", 1),
        ("3. Add questions", "build-questions", 1),
        ("Question-type tips", "build-tips", 1),
        ("4. Name and publish", "build-publish", 1),
        ("Put it in the repo and ship it", "ship", 0),
        ("Ship checklist", "checklist", 0),
        ("Common questions", "faq", 0),
    ]
    add_toc(doc, toc_entries)

    add_heading(doc, "Links", 1, bookmark="links")
    add_link_line(
        doc,
        "Studio:",
        "https://courtniestrongmind.github.io/Unit_Review_Studio/studio/",
    )
    add_link_line(
        doc,
        "Sample student view:",
        "https://courtniestrongmind.github.io/Unit_Review_Studio/review/index.html?set=sample-unit-review",
    )
    add_body(doc, "Open these in Chrome or Edge.")
    add_body(
        doc,
        "Progress only lasts while the browser tab is open. Close the tab or use **Start over** on the road screen to begin at Lesson 1 again.",
    )
    add_back_to_contents(doc)

    add_heading(doc, "What students get", 1, bookmark="students")
    add_body(doc, "Students travel a road of lessons for one unit.")
    add_numbered(
        doc,
        [
            "They see the course name, unit title, short directions, and numbered stops.",
            "They answer a few questions per lesson. Types can be multiple choice, select all, match, or sort.",
            "They get a few tries. After a miss, they see a tip. Correct answers show short feedback.",
            "When the dotted trail reaches the flag, a yellow star appears.",
            "The end screen congratulates them. If anything was missed, it lists **Lessons to look at again** with the lesson number and topic as plain text. There are no Course Builder hyperlinks in the interactive.",
        ],
    )

    add_heading(doc, "Student start / road", 2, bookmark="student-road")
    add_image(doc, "01-student-road.png", "Student road with numbered lesson stops")

    add_heading(doc, "A question", 2, bookmark="student-question")
    add_image(doc, "02-student-question.png", "Multiple choice question with Check")

    add_heading(doc, "Match with Clear", 2, bookmark="student-match")
    add_image(doc, "03-student-match.png", "Match activity with Clear and Check")

    add_heading(doc, "Finished road", 2, bookmark="student-finished")
    add_image(doc, "04-student-road-complete.png", "Completed road with yellow star at the flag")

    add_heading(doc, "End screen with lesson to revisit", 2, bookmark="student-end")
    add_image(doc, "05-student-end.png", "End screen listing lessons as plain text")
    add_back_to_contents(doc)

    add_heading(doc, "Before you build", 1, bookmark="before")
    add_body(doc, "Have ready:")
    add_bullets(
        doc,
        [
            "The course, grade, and unit number",
            "Lesson titles for that unit",
            "Rough ideas for the questions you want in each lesson",
            "Topic names for each lesson on the road",
        ],
    )
    add_body(
        doc,
        "Try the sample student link once so you know the experience you are building.",
    )
    add_back_to_contents(doc)

    add_heading(doc, "Build a review in the studio", 1, bookmark="build")

    add_heading(doc, "1. About this unit and questions", 2, bookmark="build-about")
    add_body(doc, "Open the studio and click **Start**.")
    add_body(doc, "Under **About this unit**, set:")
    add_bullets(
        doc,
        [
            "**Grade**",
            "**This unit**",
            "**Course**",
            "**Lessons in this unit** (this builds the road stops)",
        ],
    )
    add_body(
        doc,
        "Optional: open **Tries per question** if you want something other than 3 tries.",
    )
    add_image(doc, "06-studio-about.png", "Studio About this unit, outline, and question editor")

    add_heading(doc, "2. Name each lesson", 2, bookmark="build-name")
    add_body(
        doc,
        "Each lesson keeps a fixed **Lesson 1**, **Lesson 2** label. Next to it, type the topic or lesson name in its own box.",
    )
    add_body(
        doc,
        "That topic helps authors stay oriented. Students mainly see numbered stops on the road. On the end-screen revisit list, topics show as **Lesson 3: Training paths**.",
    )

    add_heading(doc, "3. Add questions", 2, bookmark="build-questions")
    add_numbered(
        doc,
        [
            "Open a lesson and add a question.",
            "Pick a type: **Multiple choice**, **Select all**, **Match**, or **Sort**.",
            "Use **Generate a question** for a starting draft, or choose **I will write this question myself**.",
            "Fill in objective, prompt, answers, correct feedback, and incorrect feedback.",
            "Fill in objective, prompt, answers, correct feedback, and incorrect feedback.",
        ],
    )
    add_body(doc, "Repeat for each lesson on the road.")
    add_body(
        doc,
        "Wrong-answer tips and the end screen do not link out to Course Builder. The end list is only a reminder of which lessons felt shaky.",
    )

    add_heading(doc, "Question-type tips", 2, bookmark="build-tips")
    add_body(doc, "**Multiple choice / Select all**")
    add_bullets(
        doc,
        [
            "Keep choices short and parallel.",
            "Avoid making the longest choice the only correct one every time.",
            "For select all, mark every correct choice.",
        ],
    )
    add_body(doc, "**Match**")
    add_bullets(
        doc,
        [
            "Keep left and right items short enough to read at a glance.",
            "Students connect pairs, then press Check.",
            "**Clear** removes unlocked connections.",
        ],
    )
    add_body(doc, "**Sort**")
    add_bullets(
        doc,
        [
            "Name groups clearly.",
            "Assign each card to the correct group in the authoring view.",
            "Students sort cards into bins, then press Check.",
            "**Clear** sends unlocked cards back.",
        ],
    )

    add_heading(doc, "4. Name and publish", 2, bookmark="build-publish")
    add_body(doc, "Click **Name and publish**.")
    add_image(doc, "07-studio-publish.png", "Name and publish step with checklist")
    add_numbered(
        doc,
        [
            "Set the **Title students see** and **Directions for students**.",
            "Optional: edit shared feedback lines and the end message.",
            "Read the **Checklist** and fix anything it flags.",
            "Click **Publish** and save the downloaded zip.",
        ],
    )
    add_body(
        doc,
        "The studio also saves a draft in **that browser** automatically. Drafts do not sync to other computers. Publish is how you get the files that belong in the repo.",
    )
    add_back_to_contents(doc)

    add_heading(doc, "Put it in the repo and ship it", 1, bookmark="ship")
    add_numbered(
        doc,
        [
            "Unzip the publish folder into review/sets/. You should get something like review/sets/my-activity-name/content.json.",
            "Activity folder names use lowercase letters, numbers, and dashes only.",
            "Branch, commit, open a PR, merge, then run Dev Deploy and Prod Deploy the usual way.",
            "Student link pattern after hosting is live: .../review/index.html?set=<activity-name>",
            "Embed that player URL in Helios in an iframe, same as other interactives.",
        ],
    )
    add_body(
        doc,
        "Until the shared StrongMind interactives host is pointed at this repo, use the GitHub Pages links above for review.",
    )
    add_back_to_contents(doc)

    add_heading(doc, "Ship checklist", 1, bookmark="checklist")
    add_bullets(
        doc,
        [
            "Course, unit, grade, and lesson count match the real unit",
            "Every road lesson has at least one question",
            "Each question has clear correct and incorrect feedback",
            "Match and sort items are short and readable on a phone",
            "You played the whole road once in preview or the published sample",
            "Publish zip is in review/sets/ and named correctly",
            "Helios embed uses the player link with the right ?set=",
        ],
    )
    add_back_to_contents(doc)

    add_heading(doc, "Common questions", 1, bookmark="faq")
    add_body(doc, "**Why did my review open on Lesson 2?**")
    add_body(
        doc,
        "You already finished Lesson 1 in that same browser tab. Close the tab, use **Start over**, or open a fresh link.",
    )
    add_body(doc, "**Where did my draft go?**")
    add_body(
        doc,
        "Drafts live in local browser storage on that computer. Another browser or computer will not see them. Publish and save the zip if you need a lasting copy.",
    )
    add_body(doc, "**Why are end-screen lesson names not links?**")
    add_body(
        doc,
        "By design. The list only reminds students which lessons to reopen in the course, so changing Course Builder URLs cannot break the interactive.",
    )
    add_body(doc, "**Do students see points or a percent score?**")
    add_body(
        doc,
        "No. This review is light. The focus is finishing the road and knowing which lessons to reopen.",
    )
    add_body(doc, "**Can I change the player design later?**")
    add_body(
        doc,
        "Yes, but that is a code change in review/index.html. After player edits, someone needs to run python tools/build_studio.py so the studio preview stays in sync.",
    )
    add_back_to_contents(doc)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print("Wrote", OUT)


if __name__ == "__main__":
    main()
