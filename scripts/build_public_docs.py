#!/usr/bin/env python3
"""Build TES public HTML from modular JSON + YAML i18n sources."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
STRUCTURE = ROOT / "docs/i18n/tes-public.structure.yml"
CONTENT = ROOT / "docs/i18n/tes-public.content.json"


def load_sources() -> tuple[dict, dict]:
    structure_text = STRUCTURE.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        structure = yaml.safe_load(structure_text)
    except ModuleNotFoundError:
        structure = json.loads(structure_text)
    content = json.loads(CONTENT.read_text(encoding="utf-8"))
    return structure, content


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def inline(text: str) -> str:
    parts = re.split(r"(`[^`]+`)", text)
    rendered: list[str] = []
    for part in parts:
        if part.startswith("`") and part.endswith("`"):
            rendered.append(f"<code>{esc(part[1:-1])}</code>")
            continue

        value = esc(part)
        value = re.sub(r"\*\*([^*]+)\*\*", lambda m: f"<strong>{m.group(1)}</strong>", value)
        value = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", lambda m: f"<em>{m.group(1)}</em>", value)

        def link(match: re.Match[str]) -> str:
            label = match.group(1)
            href = match.group(2)
            return f'<a href="{esc(href)}">{label}</a>'

        rendered.append(re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, value))
    return "".join(rendered)


def clean_html(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def read_fenced_block(source: str, fence: str = "text") -> str:
    path = (ROOT / source).resolve()
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"source outside repository: {source}") from exc
    text = path.read_text(encoding="utf-8")
    pattern = rf"```{re.escape(fence)}\n(.*?)\n```"
    match = re.search(pattern, text, re.S)
    if not match:
        raise ValueError(f"missing ```{fence}``` block in {source}")
    return match.group(1)


def lang_meta(structure: dict, lang: str) -> dict:
    for item in structure["languages"]:
        if item["code"] == lang:
            return item
    raise KeyError(lang)


def href_for(page: dict, href: str) -> str:
    if href.startswith(("http://", "https://", "#", "mailto:")):
        return href
    return f"{page['asset_prefix']}{href}"


def doc_slug_for(page: dict, href: str) -> str | None:
    if page.get("body_class") != "public-index":
        return None
    if href.startswith(("http://", "https://", "#", "mailto:", "/")):
        return None
    if not href.endswith(".md"):
        return None
    slug = href[:-3].lstrip("./")
    if not slug or slug.startswith("/") or "//" in slug or ".." in slug:
        return None
    if not re.match(r"^[A-Za-z0-9_./-]+$", slug):
        return None
    return slug


def render_doc_anchor(page: dict, item: dict, class_name: str) -> str:
    slug = doc_slug_for(page, item["href"])
    if slug:
        return (
            f'<a class="{class_name}" href="#/doc/{esc(slug)}" data-doc-link="{esc(slug)}">'
            f'{inline(item["label"])}</a>'
        )
    return f'<a class="{class_name}" href="{href_for(page, item["href"])}">{inline(item["label"])}</a>'


def render_block(block: dict, page: dict) -> str:
    kind = block["type"]
    if kind == "p":
        return f"<p>{inline(block['text'])}</p>"
    if kind == "note":
        return f'<aside class="note">{inline(block["text"])}</aside>'
    if kind == "aside":
        return (
            '<aside class="side-note">'
            f'<p class="side-note-title">{inline(block["title"])}</p>'
            f'<p>{inline(block["text"])}</p>'
            '</aside>'
        )
    if kind in {"list", "steps"}:
        tag = "ol" if kind == "steps" else "ul"
        items = "\n".join(f"<li>{inline(item)}</li>" for item in block["items"])
        return f'<{tag} class="{kind}">\n{items}\n</{tag}>'
    if kind == "code":
        return (
            f'<div class="pre-wrap" data-label="{esc(block.get("label", "code"))}">'
            f"<pre><code>{esc(block['text'])}</code></pre></div>"
        )
    if kind == "prompt_copy":
        text = read_fenced_block(block["source"], block.get("fence", "text"))
        label = esc(block.get("label", "prompt"))
        copy_label = esc(block.get("copy_label", "Copy"))
        copied_label = esc(block.get("copied_label", "Copied"))
        return (
            f'<div class="pre-wrap copy-wrap" data-label="{label}" data-copy-block>'
            '<div class="copy-toolbar">'
            f'<span>{label}</span>'
            f'<button type="button" class="copy-btn" data-copy-button data-copy-label="{copy_label}" '
            f'data-copied-label="{copied_label}">{copy_label}</button>'
            '</div>'
            f'<pre><code>{esc(text)}</code></pre></div>'
        )
    if kind == "table":
        headers = "".join(f"<th>{inline(head)}</th>" for head in block["headers"])
        rows = []
        for row in block["rows"]:
            rows.append("<tr>" + "".join(f"<td>{inline(cell)}</td>" for cell in row) + "</tr>")
        return f"<div class=\"table-wrap\"><table><thead><tr>{headers}</tr></thead><tbody>{''.join(rows)}</tbody></table></div>"
    if kind == "cards":
        cards = []
        for item in block["items"]:
            cards.append(
                "<article class=\"info-card\">"
                f"<h3>{inline(item['title'])}</h3>"
                f"<p>{inline(item['body'])}</p>"
                "</article>"
            )
        return f"<div class=\"card-grid\">{''.join(cards)}</div>"
    if kind == "source_map":
        groups = []
        for group in block["groups"]:
            items = []
            for item in group["items"]:
                body = f'<span class="source-link-body">{inline(item["body"])}</span>' if item.get("body") else ""
                meta = f'<span class="source-link-meta">{inline(item["meta"])}</span>' if item.get("meta") else ""
                items.append(
                    "<li>"
                    f'{render_doc_anchor(page, item, "source-link")}'
                    f"{body}{meta}"
                    "</li>"
                )
            groups.append(
                '<article class="source-group">'
                f'<h3>{inline(group["title"])}</h3>'
                f'<p>{inline(group["body"])}</p>'
                f'<ul>{"".join(items)}</ul>'
                '</article>'
            )
        return f'<div class="source-map">{"".join(groups)}</div>'
    if kind == "links":
        links = []
        for item in block["items"]:
            links.append(render_doc_anchor(page, item, "doc-link"))
        return f"<div class=\"link-grid\">{''.join(links)}</div>"
    raise ValueError(f"unknown block type: {kind}")


def render_section(section_key: str, section: dict, page: dict, lang: str) -> str:
    blocks = "\n".join(render_block(block, page) for block in section.get("blocks", []))
    section_id = f"{section_key}-{lang}"
    return f"""
        <section class="chapter" id="{section_id}" data-section-key="{section_key}">
          <div class="chapter-head">
            <span class="chapter-num">{esc(section["num"])}</span>
            <h2>{inline(section["title"])}</h2>
          </div>
          <div class="chapter-body">
            <p class="lede">{inline(section["lede"])}</p>
            {blocks}
          </div>
        </section>"""


def render_nav(page_key: str, page: dict, content: dict, lang: str) -> str:
    links = []
    for key in page["nav"]:
        section = content["sections"][key][lang]
        labels = " ".join(
            f'data-label-{code}="{esc(content["sections"][key][code]["title"])}"'
            for code in content["sections"][key]
        )
        hrefs = " ".join(
            f'data-href-{code}="#{esc(key)}-{esc(code)}"'
            for code in content["sections"][key]
        )
        links.append(
            f'<li><a href="#{key}-{lang}" data-nav="{key}" {labels} {hrefs}>'
            f'<span class="toc-num">{esc(section["num"])}</span>'
            f'<span class="toc-text">{inline(section["title"])}</span>'
            "</a></li>"
        )
    return "\n".join(links)


def render_lang_buttons(structure: dict, current: str) -> str:
    buttons = []
    for item in structure["languages"]:
        pressed = "true" if item["code"] == current else "false"
        buttons.append(
            f'<button type="button" class="lang-btn" data-lang-pick="{item["code"]}" aria-pressed="{pressed}">{item["label"]}</button>'
        )
    return "".join(buttons)


def render_brand_mark(text: str) -> str:
    if "·" not in text:
        return esc(text)
    left, right = [part.strip() for part in text.split("·", 1)]
    return f"{esc(left)}<em>·</em>{esc(right)}"


def render_lang_section(page_key: str, structure: dict, content: dict, lang: str) -> str:
    page = structure["pages"][page_key]
    hero = content["hero"][page_key][lang]
    meta = lang_meta(structure, lang)
    sections = "\n".join(
        render_section(key, content["sections"][key][lang], page, lang)
        for key in page["nav"]
    )
    hero_image = ""
    if page_key == "index":
        hero_image = (
            '<figure class="hero-visual">'
            f'<img src="{structure["assets"]["social_preview"]}" alt="{esc(content["meta"]["index"][lang]["og_description"])}">'
            "</figure>"
        )
    hero_facts = ""
    if hero.get("facts"):
        facts = "".join(
            '<div class="hero-fact">'
            f'<span>{inline(item["label"])}</span>'
            f'<strong>{inline(item["value"])}</strong>'
            '</div>'
            for item in hero["facts"]
        )
        hero_facts = f'<div class="hero-facts">{facts}</div>'
    hero_actions = ""
    if hero.get("primary") or hero.get("secondary"):
        primary = (
            f'<a class="btn btn-primary" href="#start">{inline(hero["primary"])}</a>'
            if hero.get("primary")
            else ""
        )
        secondary_href = "install/USER-MANUAL.html" if page_key == "index" else "../index.html"
        secondary = (
            f'<a class="btn" href="{esc(secondary_href)}">{inline(hero["secondary"])}</a>'
            if hero.get("secondary")
            else ""
        )
        hero_actions = f'<div class="hero-actions">{primary}{secondary}</div>'
    return f"""
      <section class="lang-section{' is-active' if lang == 'en' else ''}" data-lang="{lang}" lang="{meta['html_lang']}">
        <header class="masthead">
          <div class="language-row" role="radiogroup" aria-label="{esc(content['ui'][lang]['language'])}">
            {render_lang_buttons(structure, lang)}
            <span class="language-mark">— {inline(content["ui"][lang]["language_mark"])}</span>
          </div>
          <p class="eyebrow">{inline(hero["eyebrow"])}</p>
          <h1 class="display-h1">{inline(hero["title"])}</h1>
          <p class="lead">{inline(hero["lead"])}</p>
          {hero_actions}
          {hero_facts}
          {hero_image}
        </header>
        {sections}
      </section>"""


CSS = r"""
    :root {
      color-scheme: light;
      --paper: #f0f7f4;
      --paper-deep: #dcebea;
      --ink: #161215;
      --ink-soft: #3a302c;
      --ink-faint: #8b7d78;
      --rule: #b8cfca;
      --rule-soft: #d2e3df;
      --accent: #2f7f84;
      --accent-deep: #235f63;
      --accent-soft: #99e1d9;
      --warn: #b86a3a;
      --mono-bg: #161215;
      --mono-fg: #f0f7f4;
      --mono-muted: #b7c9c5;
      --font-display: "Fraunces", ui-serif, Georgia, "Times New Roman", serif;
      --font-body: "Newsreader", ui-serif, Georgia, "Times New Roman", serif;
      --font-mono: "JetBrains Mono", ui-monospace, "SF Mono", Menlo, monospace;
      --col-margin: 220px;
      --col-content: 760px;
      --col-aside: 280px;
      --gap: 32px;
      --speed-fast: 180ms;
      --speed-base: 320ms;
      --ease: cubic-bezier(0.22, 0.61, 0.36, 1);
    }

    *, *::before, *::after { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body {
      background: var(--paper);
      color: var(--ink);
      font-family: var(--font-body);
      font-size: 17px;
      font-weight: 400;
      line-height: 1.65;
      text-rendering: optimizeLegibility;
      -webkit-font-smoothing: antialiased;
    }
    body::before {
      background:
        radial-gradient(1200px 600px at 100% -10%, rgba(194, 65, 12, 0.06), transparent 60%),
        radial-gradient(800px 400px at -10% 30%, rgba(154, 52, 18, 0.04), transparent 60%);
      content: "";
      inset: 0;
      pointer-events: none;
      position: fixed;
      z-index: 0;
    }
    body.nav-open { overflow: hidden; }
    img, picture, svg { display: block; max-width: 100%; }
    button {
      background: none;
      border: 0;
      color: inherit;
      cursor: pointer;
      font: inherit;
      padding: 0;
    }
    a {
      color: var(--accent);
      text-decoration: none;
      text-decoration-color: transparent;
      text-decoration-thickness: 1px;
      text-underline-offset: 3px;
      transition: text-decoration-color var(--speed-fast) var(--ease);
    }
    a:hover { text-decoration: underline; }
    :focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }
    code {
      background: var(--paper-deep);
      border: 1px solid var(--rule-soft);
      border-radius: 3px;
      font-family: var(--font-mono);
      font-size: .86em;
      padding: 1px 5px;
      white-space: nowrap;
    }

    .skip {
      background: var(--ink);
      color: var(--paper);
      font-family: var(--font-mono);
      font-size: 12px;
      left: 12px;
      padding: 8px 12px;
      position: absolute;
      top: -100px;
      z-index: 100;
    }
    .skip:focus { top: 12px; }
    .layout, .page {
      display: grid;
      grid-template-columns: var(--col-margin) minmax(0, 1fr);
      min-height: 100vh;
      position: relative;
      z-index: 1;
    }
    .rail {
      border-right: 1px solid var(--rule-soft);
      display: flex;
      flex-direction: column;
      height: 100vh;
      position: sticky;
      top: 0;
    }
    .nav-bar {
      align-items: center;
      border-bottom: 1px solid var(--rule-soft);
      display: flex;
      flex-shrink: 0;
      gap: 16px;
      justify-content: space-between;
      padding: 24px 24px 20px;
    }
    .nav-toggle { display: none; }
    .rail-inner {
      flex: 1;
      overflow-y: auto;
      padding: 24px 24px 32px;
    }
    .rail-inner::-webkit-scrollbar { width: 6px; }
    .rail-inner::-webkit-scrollbar-thumb { background: var(--rule); border-radius: 3px; }
    .scrim {
      background: rgba(26, 24, 20, .32);
      inset: 64px 0 0;
      opacity: 0;
      pointer-events: none;
      position: fixed;
      transition: opacity var(--speed-base) var(--ease);
      z-index: 50;
    }
    .scrim.is-open {
      opacity: 1;
      pointer-events: auto;
    }
    .stage {
      max-width: calc(var(--col-content) + var(--col-aside) + var(--gap));
      padding: 56px 64px 96px;
      position: relative;
      width: 100%;
    }

    .brand { flex: 1; min-width: 0; }
    .brand-mark {
      align-items: baseline;
      color: var(--ink);
      display: inline-flex;
      font-family: var(--font-display);
      font-size: 19px;
      font-weight: 500;
      gap: 6px;
      letter-spacing: -.01em;
      line-height: 1;
    }
    .brand-mark em { color: var(--accent); font-style: normal; }
    .brand-meta {
      color: var(--ink-faint);
      display: block;
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 500;
      letter-spacing: .08em;
      margin-top: 6px;
      text-transform: uppercase;
      white-space: nowrap;
    }
    .toc { padding-top: 8px; }
    .toc-title {
      color: var(--ink-faint);
      font-family: var(--font-mono);
      font-size: 10px;
      letter-spacing: .14em;
      margin: 0 0 16px;
      text-transform: uppercase;
    }
    .toc ul { list-style: none; margin: 0; padding: 0; }
    .toc li { position: relative; }
    .toc a {
      align-items: baseline;
      color: var(--ink-soft);
      display: flex;
      font-family: var(--font-body);
      font-size: 14px;
      gap: 12px;
      line-height: 1.4;
      padding: 7px 0 7px 16px;
      position: relative;
      transition: color var(--speed-fast) var(--ease), padding-left var(--speed-fast) var(--ease);
    }
    .toc a::before {
      background: var(--accent);
      content: "";
      height: 0;
      left: 0;
      position: absolute;
      top: 50%;
      transform: translateY(-50%);
      transition: height var(--speed-fast) var(--ease);
      width: 2px;
    }
    .toc a:hover {
      color: var(--ink);
      padding-left: 22px;
      text-decoration: none;
    }
    .toc a[aria-current="true"] {
      color: var(--ink);
      font-weight: 500;
    }
    .toc a[aria-current="true"]::before { height: 18px; }
    .toc-num {
      color: var(--ink-faint);
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 500;
      letter-spacing: .04em;
      min-width: 22px;
    }
    .toc a[aria-current="true"] .toc-num { color: var(--accent); }
    .toc-text { color: inherit; font-family: inherit; font-size: inherit; }

    .lang-section { display: none; }
    .lang-section.is-active { display: block; }
    .language-row {
      align-items: center;
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
      margin-bottom: 34px;
    }
    .language-row::before {
      background: var(--accent);
      content: "";
      height: 1px;
      width: 46px;
    }
    .lang-btn {
      color: var(--ink-faint);
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 500;
      letter-spacing: .16em;
      text-transform: uppercase;
    }
    .lang-btn[aria-pressed="true"] { color: var(--accent); }
    .lang-btn + .lang-btn::before {
      color: var(--ink-faint);
      content: "·";
      margin-right: 15px;
    }
    .language-mark {
      color: var(--accent);
      font-family: var(--font-mono);
      font-size: 11px;
      letter-spacing: .18em;
      text-transform: uppercase;
    }
    .masthead {
      border-bottom: 1px solid var(--rule);
      margin: 0 0 56px;
      padding: 0 0 40px;
    }
    .eyebrow {
      color: var(--accent);
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 500;
      letter-spacing: .2em;
      margin: 0 0 30px;
      text-transform: uppercase;
    }
    .display-h1 {
      font-family: var(--font-display);
      font-size: clamp(48px, 6vw, 84px);
      font-variation-settings: "opsz" 144, "wght" 400, "SOFT" 50;
      letter-spacing: -.025em;
      line-height: .96;
      margin: 0 0 24px;
      max-width: 940px;
    }
    .display-h1 em {
      color: var(--accent);
      font-style: italic;
      font-variation-settings: "opsz" 144, "wght" 350, "SOFT" 80;
    }
    .lead {
      color: var(--ink-soft);
      font-family: var(--font-body);
      font-size: 21px;
      font-weight: 300;
      line-height: 1.5;
      margin: 0;
      max-width: 640px;
    }
    h2, h3 {
      font-family: var(--font-display);
      font-weight: 450;
      letter-spacing: -.015em;
      line-height: 1.1;
      margin: 0;
    }

    .hero-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 34px;
    }
    .btn {
      border: 1px solid var(--ink);
      color: var(--ink);
      display: inline-flex;
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      justify-content: center;
      letter-spacing: .16em;
      min-width: 150px;
      padding: 13px 18px;
      text-transform: uppercase;
    }
    .btn-primary {
      background: var(--ink);
      border-color: var(--ink);
      color: var(--paper);
    }
    .hero-facts {
      border-bottom: 1px solid var(--rule-soft);
      border-top: 1px solid var(--rule-soft);
      display: grid;
      gap: 24px;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      margin-top: 48px;
      padding: 24px 0;
    }
    .hero-fact span {
      color: var(--ink-faint);
      display: block;
      font-family: var(--font-mono);
      font-size: 10px;
      letter-spacing: .14em;
      margin-bottom: 7px;
      text-transform: uppercase;
    }
    .hero-fact strong { font-size: 18px; font-weight: 600; }
    .hero-visual {
      background: var(--mono-bg);
      border: 1px solid rgba(22,18,21,.2);
      margin: 42px 0 0;
    }
    .hero-visual img { width: 100%; }

    .chapter {
      margin: 0 0 64px;
      position: relative;
      scroll-margin-top: 92px;
    }
    .chapter-head {
      align-items: baseline;
      border-top: 1px solid var(--rule);
      display: grid;
      gap: 24px;
      grid-template-columns: 60px minmax(0, 1fr);
      margin: 0 0 24px;
      padding-top: 28px;
    }
    .chapter-num {
      color: var(--accent);
      font-family: var(--font-mono);
      font-size: 13px;
      font-weight: 500;
      letter-spacing: .04em;
    }
    .chapter h2 {
      font-size: clamp(28px, 3vw, 38px);
      font-variation-settings: "opsz" 96, "wght" 450;
    }
    .chapter-body {
      display: grid;
      gap: var(--gap);
      grid-template-columns: minmax(0, 1fr);
      padding-left: 84px;
    }
    .chapter-body > p,
    .chapter-body > ol,
    .chapter-body > ul,
    .chapter-body > .note,
    .chapter-body > .side-note {
      max-width: var(--col-content);
    }
    .chapter-body .lede {
      color: var(--ink);
      font-size: 17px;
      margin: 0;
    }
    .public-manual .chapter:first-of-type .lede::first-letter {
      color: var(--accent);
      float: left;
      font-family: var(--font-display);
      font-size: 64px;
      font-variation-settings: "opsz" 144, "wght" 500;
      line-height: .85;
      margin: 6px 10px -2px 0;
    }
    .chapter-body ol,
    .chapter-body ul {
      list-style: none;
      margin: 0;
      padding: 0;
    }
    .chapter-body ol { counter-reset: step; }
    .chapter-body ol li {
      counter-increment: step;
      margin: 0 0 14px;
      padding-left: 38px;
      position: relative;
    }
    .chapter-body ol li::before {
      color: var(--accent);
      content: counter(step, decimal-leading-zero);
      font-family: var(--font-mono);
      font-size: 12px;
      font-weight: 500;
      left: 0;
      letter-spacing: .04em;
      position: absolute;
      top: 4px;
    }
    .chapter-body ul li {
      margin: 0 0 8px;
      padding-left: 22px;
      position: relative;
    }
    .chapter-body ul li::before {
      background: var(--accent);
      content: "";
      height: 1px;
      left: 0;
      position: absolute;
      top: .85em;
      width: 12px;
    }
    .note {
      border-left: 3px solid var(--warn);
      color: var(--ink-soft);
      margin: 0 0 24px;
      padding: 8px 0 8px 18px;
    }
    .side-note {
      border-left: 3px solid var(--accent);
      margin: 4px 0 24px;
      padding: 14px 0 14px 22px;
    }
    .side-note-title {
      color: var(--accent);
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 500;
      letter-spacing: .16em;
      margin: 0 0 6px;
      text-transform: uppercase;
    }
    .side-note p { margin: 0; }
    .card-grid {
      display: grid;
      gap: 18px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      margin: 0 0 24px;
      max-width: calc(var(--col-content) + 120px);
    }
    .info-card {
      border-top: 3px solid var(--accent);
      padding: 16px 0 0;
    }
    .info-card h3 { font-size: 22px; margin-bottom: 8px; }
    .info-card p { color: var(--ink-soft); margin: 0; }
    .source-map {
      display: grid;
      gap: 28px;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      margin: 0 0 28px;
      max-width: calc(var(--col-content) + var(--col-aside));
    }
    .source-group {
      border-top: 1px solid var(--rule);
      padding-top: 18px;
    }
    .source-group h3 {
      font-size: 24px;
      margin: 0 0 8px;
    }
    .source-group > p {
      color: var(--ink-soft);
      font-size: 17px;
      line-height: 1.45;
      margin: 0 0 16px;
    }
    .source-group ul {
      list-style: none;
      margin: 0;
      padding: 0;
    }
    .source-group li {
      border-bottom: 1px solid var(--rule-soft);
      margin: 0;
      padding: 12px 0;
    }
    .chapter-body .source-group li {
      padding-left: 0;
    }
    .chapter-body .source-group li::before {
      content: none;
    }
    .source-link {
      color: var(--ink);
      display: inline-block;
      font-weight: 650;
      text-decoration: none;
    }
    .source-link::after {
      color: var(--accent);
      content: " ->";
      font-family: var(--font-mono);
      font-size: .72em;
      white-space: nowrap;
    }
    .source-link:hover {
      color: var(--accent);
      text-decoration: none;
    }
    .source-link-body,
    .source-link-meta {
      color: var(--ink-soft);
      display: block;
      font-size: 15px;
      line-height: 1.42;
      margin-top: 3px;
    }
    .source-link-meta {
      color: var(--ink-faint);
      font-family: var(--font-mono);
      font-size: 10px;
      letter-spacing: .12em;
      text-transform: uppercase;
    }
    .table-wrap {
      margin: 0 0 24px;
      max-width: calc(var(--col-content) + var(--col-aside));
      overflow-x: auto;
    }
    table { border-collapse: collapse; width: 100%; }
    th {
      border-bottom: 2px solid var(--ink);
      font-family: var(--font-mono);
      font-size: 12px;
      letter-spacing: .08em;
      padding: 10px 16px 10px 0;
      text-align: left;
      text-transform: uppercase;
    }
    td {
      border-bottom: 1px solid var(--rule-soft);
      padding: 14px 16px 14px 0;
      vertical-align: top;
    }
    td:first-child { white-space: nowrap; width: 1%; }
    .pre-wrap {
      background: var(--mono-bg);
      color: var(--mono-fg);
      margin: 0 0 24px;
      max-width: calc(var(--col-content) + var(--col-aside));
      overflow: hidden;
      position: relative;
    }
    .copy-wrap {
      border: 1px solid rgba(240, 247, 244, .12);
    }
    .pre-wrap::before {
      color: var(--accent-soft);
      content: attr(data-label);
      display: block;
      font-family: var(--font-mono);
      font-size: 10px;
      letter-spacing: .16em;
      padding: 14px 18px 0;
      text-transform: uppercase;
    }
    .copy-wrap::before { content: none; }
    .copy-toolbar {
      align-items: center;
      border-bottom: 1px solid rgba(240, 247, 244, .12);
      color: var(--accent-soft);
      display: flex;
      font-family: var(--font-mono);
      font-size: 10px;
      justify-content: space-between;
      letter-spacing: .16em;
      padding: 14px 18px;
      text-transform: uppercase;
    }
    .copy-btn {
      border: 1px solid rgba(240, 247, 244, .34);
      color: var(--mono-fg);
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 700;
      letter-spacing: .12em;
      padding: 7px 10px;
      text-transform: uppercase;
      transition: background var(--speed-fast) var(--ease), color var(--speed-fast) var(--ease);
    }
    .copy-btn:hover,
    .copy-btn:focus-visible {
      background: var(--mono-fg);
      color: var(--mono-bg);
      text-decoration: none;
    }
    .copy-wrap pre {
      max-height: 440px;
      overflow: auto;
      padding-top: 16px;
    }
    pre {
      font-family: var(--font-mono);
      font-size: 13px;
      line-height: 1.65;
      margin: 0;
      overflow-x: auto;
      padding: 14px 18px 18px;
      white-space: pre-wrap;
    }
    pre code { background: transparent; border: 0; color: inherit; padding: 0; white-space: inherit; }
    .link-grid {
      display: grid;
      gap: 10px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      margin: 0 0 24px;
      max-width: calc(var(--col-content) + 120px);
    }
    .doc-link {
      border: 1px solid var(--rule-soft);
      color: var(--ink);
      display: block;
      padding: 14px 16px;
    }
    .doc-link::after {
      color: var(--accent);
      content: " ->";
      font-family: var(--font-mono);
      font-size: .78em;
      white-space: nowrap;
    }
    body[data-view="landing"] #doc-view,
    #doc-view[hidden] {
      display: none;
    }
    body[data-view="doc"] .lang-section,
    body[data-view="doc"] .footer {
      display: none;
    }
    #doc-view {
      margin: 0 auto;
      max-width: calc(var(--col-content) + var(--col-aside) + var(--gap));
    }
    .doc-topbar {
      align-items: center;
      border-bottom: 1px solid var(--rule);
      display: flex;
      gap: 24px;
      justify-content: space-between;
      margin-bottom: 46px;
      padding-bottom: 20px;
    }
    .doc-back {
      align-items: center;
      color: var(--ink);
      display: inline-flex;
      font-family: var(--font-mono);
      font-size: 11px;
      gap: 8px;
      letter-spacing: .16em;
      text-transform: uppercase;
    }
    .doc-back:hover {
      color: var(--accent);
      text-decoration: none;
    }
    .doc-meta {
      color: var(--ink-faint);
      display: flex;
      flex-wrap: wrap;
      font-family: var(--font-mono);
      font-size: 11px;
      gap: 10px;
      letter-spacing: .16em;
      text-transform: uppercase;
    }
    .doc-source {
      color: var(--ink-faint);
      font-family: var(--font-mono);
      font-size: 10px;
      letter-spacing: .16em;
      margin: 0 0 28px;
      text-transform: uppercase;
    }
    #doc-content {
      counter-reset: doc-h2;
    }
    #doc-content h1 {
      font-family: var(--font-display);
      font-size: clamp(48px, 6vw, 72px);
      font-weight: 400;
      letter-spacing: -.025em;
      line-height: .98;
      margin: 0 0 22px;
      max-width: 880px;
    }
    #doc-content > .doc-lede {
      color: var(--ink-soft);
      font-size: 22px;
      font-weight: 300;
      line-height: 1.5;
      margin: 0 0 48px;
      max-width: 760px;
    }
    #doc-content h2 {
      border-top: 1px solid var(--rule);
      counter-increment: doc-h2;
      font-family: var(--font-display);
      font-size: clamp(30px, 3.2vw, 42px);
      font-weight: 450;
      letter-spacing: -.015em;
      line-height: 1.1;
      margin: 52px 0 20px;
      padding-top: 28px;
    }
    #doc-content h2::before {
      color: var(--accent);
      content: "§ " counter(doc-h2, decimal-leading-zero) "  ";
      font-family: var(--font-mono);
      font-size: 12px;
      font-weight: 500;
      letter-spacing: .08em;
    }
    #doc-content h3 {
      font-family: var(--font-display);
      font-size: 24px;
      font-weight: 500;
      margin: 32px 0 10px;
    }
    #doc-content h4 {
      font-family: var(--font-display);
      font-size: 18px;
      font-weight: 500;
      margin: 28px 0 8px;
    }
    #doc-content p {
      font-size: 17px;
      line-height: 1.7;
      margin: 0 0 16px;
      max-width: 64ch;
    }
    #doc-content ul,
    #doc-content ol {
      list-style: revert;
      margin: 0 0 18px;
      max-width: 64ch;
      padding-left: 28px;
    }
    #doc-content li {
      font-size: 17px;
      line-height: 1.7;
      margin: 0 0 6px;
    }
    #doc-content blockquote {
      border-left: 3px solid var(--accent);
      color: var(--ink-soft);
      font-family: var(--font-display);
      font-size: 19px;
      font-style: italic;
      line-height: 1.45;
      margin: 24px 0;
      max-width: 760px;
      padding: 4px 0 4px 24px;
    }
    #doc-content table {
      margin: 24px 0;
    }
    #doc-content code { font-size: 14px; }
    #doc-content pre {
      margin: 24px 0;
      max-width: calc(var(--col-content) + var(--col-aside));
    }
    #doc-content hr {
      border: 0;
      border-top: 1px solid var(--rule);
      margin: 56px 0;
    }
    .doc-toc {
      background: var(--paper-soft, var(--paper-deep));
      border: 1px solid var(--rule);
      margin: 0 0 48px;
      max-width: 760px;
      padding: 22px 28px;
    }
    .doc-toc-head {
      color: var(--ink-faint);
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 500;
      letter-spacing: .14em;
      margin: 0 0 12px;
      text-transform: uppercase;
    }
    .doc-toc ol {
      counter-reset: toc;
      list-style: none;
      margin: 0;
      padding: 0;
    }
    .doc-toc li {
      counter-increment: toc;
      font-size: 15px;
      line-height: 1.5;
      padding: 4px 0 4px 36px;
      position: relative;
    }
    .doc-toc li::before {
      color: var(--accent);
      content: counter(toc, decimal-leading-zero);
      font-family: var(--font-mono);
      font-size: 11px;
      left: 0;
      letter-spacing: .04em;
      position: absolute;
      top: 6px;
    }
    .doc-toc a { color: var(--ink-soft); }
    .doc-toc a:hover { color: var(--ink); }
    #doc-skeleton {
      padding: 32px 0;
    }
    .skeleton-line {
      background: linear-gradient(90deg, var(--paper-deep) 0%, var(--paper) 50%, var(--paper-deep) 100%);
      background-size: 200% 100%;
      height: 24px;
      margin-bottom: 16px;
    }
    .skeleton-line.title {
      height: 56px;
      margin-bottom: 32px;
      max-width: 70%;
    }
    .skeleton-line.short { max-width: 40%; }
    .skeleton-line.medium { max-width: 80%; }
    @keyframes skeleton-shine {
      from { background-position: 200% 0; }
      to { background-position: -200% 0; }
    }
    .skeleton-line { animation: skeleton-shine 1.6s linear infinite; }
    .doc-error {
      background: var(--paper-deep);
      border: 1px solid var(--warn);
      border-left-width: 4px;
      font-family: var(--font-mono);
      font-size: 13px;
      line-height: 1.6;
      margin: 32px 0;
      max-width: 760px;
      padding: 24px 28px;
    }
    .footer {
      border-top: 1px solid var(--rule);
      color: var(--ink-faint);
      margin: 64px 0 0;
      padding-top: 18px;
    }
    .footer-copy {
      color: var(--ink-soft);
      font-family: var(--font-body);
      font-size: 21px;
      font-weight: 300;
      letter-spacing: 0;
      line-height: 1.5;
      margin: 0 0 24px;
      max-width: var(--col-content);
      text-transform: none;
    }
    .footer-meta {
      display: flex;
      flex-wrap: wrap;
      font-family: var(--font-mono);
      font-size: 11px;
      gap: 16px;
      justify-content: space-between;
      letter-spacing: .06em;
      text-transform: uppercase;
    }

    .public-index .layout {
      display: block;
    }
    .public-index .rail {
      background: var(--paper);
      border-bottom: 0;
      border-right: 0;
      display: block;
      height: 72px;
      margin: 0;
      max-width: none;
      padding: 0;
      position: sticky;
      top: 0;
      width: 100%;
      z-index: 60;
    }
    .public-index .nav-bar {
      align-items: center;
      background: var(--paper);
      border-bottom: 1px solid var(--rule-soft);
      display: flex;
      height: 72px;
      justify-content: space-between;
      margin: 0 auto;
      max-width: calc(var(--col-content) + var(--col-aside) + var(--gap));
      padding: 0 64px;
      position: relative;
      z-index: 70;
      width: 100%;
    }
    .public-index .rail-inner {
      background: var(--paper);
      border-bottom: 1px solid var(--rule);
      inset: 72px 0 auto;
      max-height: calc(100vh - 72px);
      overflow-y: auto;
      padding: 34px max(28px, calc((100vw - 1072px) / 2)) 38px;
      position: fixed;
      transform: translateY(-110%);
      transition: transform var(--speed-base) var(--ease);
      z-index: 55;
    }
    .public-index .rail-inner.is-open { transform: translateY(0); }
    .public-index .scrim { inset: 72px 0 0; }
    .public-index .toc { padding-top: 8px; }
    .public-index .toc-title { display: block; }
    .public-index .toc-num { display: inline-block; }
    .public-index .toc ul {
      display: grid;
      gap: 10px 34px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    }
    .public-index .toc a {
      display: flex;
      font-family: var(--font-body);
      font-size: 15px;
      letter-spacing: 0;
      padding: 7px 0 7px 16px;
      text-transform: none;
    }
    .public-index .toc a::before { display: block; }
    .public-index .toc a:hover { padding-left: 22px; }
    .public-index .nav-toggle {
      align-items: center;
      background: var(--paper);
      border: 1px solid var(--ink);
      border-radius: 0;
      color: var(--ink);
      display: inline-flex;
      height: 40px;
      justify-content: center;
      padding: 0;
      transition: background var(--speed-fast) var(--ease), color var(--speed-fast) var(--ease);
      width: 56px;
    }
    .public-index .nav-toggle:hover,
    .public-index .nav-toggle[aria-expanded="true"] {
      background: var(--ink);
      color: var(--paper);
    }
    .public-index .nav-toggle span {
      background: currentColor;
      display: block;
      height: 1.5px;
      position: relative;
      transition: transform var(--speed-base) var(--ease), opacity var(--speed-fast) var(--ease);
      width: 22px;
    }
    .public-index .nav-toggle span::before,
    .public-index .nav-toggle span::after {
      background: currentColor;
      content: "";
      display: block;
      height: 1.5px;
      left: 0;
      position: absolute;
      transition: transform var(--speed-base) var(--ease);
      width: 22px;
    }
    .public-index .nav-toggle span::before { top: -7px; }
    .public-index .nav-toggle span::after { top: 7px; }
    .public-index .nav-toggle[aria-expanded="true"] span { background: transparent; }
    .public-index .nav-toggle[aria-expanded="true"] span::before { transform: translateY(7px) rotate(45deg); }
    .public-index .nav-toggle[aria-expanded="true"] span::after { transform: translateY(-7px) rotate(-45deg); }
    .public-index .stage {
      margin: 0 auto;
      max-width: calc(var(--col-content) + var(--col-aside) + var(--gap));
      padding-top: 72px;
      width: calc(100% - 128px);
    }
    .public-index .masthead { padding-bottom: 84px; }

    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after {
        animation-duration: .01ms !important;
        scroll-behavior: auto !important;
        transition-duration: .01ms !important;
      }
    }
    @media (max-width: 1180px) {
      :root { --col-margin: 200px; }
      .stage { padding: 48px 48px 80px; }
      .chapter-body { padding-left: 0; }
      .chapter-head { grid-template-columns: 48px minmax(0, 1fr); }
      .public-index .stage { width: calc(100% - 96px); }
      .public-index .nav-bar { padding: 0 48px; }
    }
    @media (max-width: 960px) {
      .layout, .page {
        display: grid;
        grid-template-columns: minmax(0, 1fr);
      }
      .rail,
      .public-index .rail {
        background: var(--paper);
        border-bottom: 1px solid var(--rule-soft);
        border-right: 0;
        display: block;
        height: auto;
        margin: 0;
        max-width: none;
        padding: 0;
        position: sticky;
        top: 0;
        width: 100%;
        z-index: 60;
      }
      .nav-bar,
      .public-index .nav-bar {
        align-items: center;
        background: var(--paper);
        border-bottom: 0;
        display: flex;
        height: 64px;
        padding: 0 20px;
        position: relative;
        z-index: 70;
      }
      .nav-bar .brand-meta { display: none; }
      .rail-inner,
      .public-index .rail-inner {
        background: var(--paper);
        border-bottom: 1px solid var(--rule);
        inset: 64px 0 auto;
        max-height: calc(100vh - 64px);
        overflow-y: auto;
        padding: 28px 28px 32px;
        position: fixed;
        transform: translateY(-110%);
        transition: transform var(--speed-base) var(--ease);
        z-index: 55;
      }
      .public-index .scrim { inset: 64px 0 0; }
      .rail-inner.is-open { transform: translateY(0); }
      .public-index .toc,
      .toc { padding-top: 8px; }
      .public-index .toc-title,
      .public-index .toc-num { display: inline-block; }
      .public-index .toc-title { display: block; }
      .public-index .toc ul {
        display: block;
      }
      .public-index .toc a {
        display: flex;
        font-family: var(--font-body);
        font-size: 15px;
        letter-spacing: 0;
        padding: 7px 0 7px 16px;
        text-transform: none;
      }
      .public-index .toc a::before { display: block; }
      .public-index .toc a:hover { padding-left: 22px; }
      .nav-toggle {
        align-items: center;
        background: var(--paper);
        border: 1px solid var(--ink);
        border-radius: 0;
        color: var(--ink);
        display: inline-flex;
        height: 40px;
        justify-content: center;
        padding: 0;
        transition: background var(--speed-fast) var(--ease), color var(--speed-fast) var(--ease);
        width: 56px;
      }
      .nav-toggle:hover,
      .nav-toggle[aria-expanded="true"] {
        background: var(--ink);
        color: var(--paper);
      }
      .nav-toggle span {
        background: currentColor;
        display: block;
        height: 1.5px;
        position: relative;
        transition: transform var(--speed-base) var(--ease), opacity var(--speed-fast) var(--ease);
        width: 22px;
      }
      .nav-toggle span::before,
      .nav-toggle span::after {
        background: currentColor;
        content: "";
        display: block;
        height: 1.5px;
        left: 0;
        position: absolute;
        transition: transform var(--speed-base) var(--ease);
        width: 22px;
      }
      .nav-toggle span::before { top: -7px; }
      .nav-toggle span::after { top: 7px; }
      .nav-toggle[aria-expanded="true"] span { background: transparent; }
      .nav-toggle[aria-expanded="true"] span::before { transform: translateY(7px) rotate(45deg); }
      .nav-toggle[aria-expanded="true"] span::after { transform: translateY(-7px) rotate(-45deg); }
      .stage,
      .public-index .stage {
        padding: 32px 24px 64px;
        width: 100%;
      }
      .masthead {
        margin-bottom: 40px;
        padding-bottom: 28px;
      }
      .chapter { margin-bottom: 48px; }
      .chapter-head {
        gap: 16px;
        grid-template-columns: 36px minmax(0, 1fr);
        padding-top: 22px;
      }
      .hero-facts { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .source-map { grid-template-columns: 1fr; }
      code { white-space: normal; }
    }
    @media (max-width: 560px) {
      .stage,
      .public-index .stage {
        padding: 24px 18px 56px;
      }
      .display-h1 {
        font-size: 44px;
        line-height: .98;
      }
      .lead { font-size: 18px; }
      .chapter h2 { font-size: 26px; }
      .chapter-body ol li { padding-left: 32px; }
      .language-mark {
        display: block;
        flex-basis: 100%;
        margin-top: 8px;
      }
      .hero-facts { grid-template-columns: 1fr; }
      th { font-size: 11px; padding-right: 12px; }
      td { padding-right: 12px; }
      pre { font-size: 12px; }
      .copy-toolbar {
        align-items: flex-start;
        flex-direction: column;
        gap: 10px;
      }
    }
"""


JS = r"""
    (() => {
      const supported = __SUPPORTED__;
      const uiLabels = __UI_LABELS__;
      const storageKey = "tes-public-lang";
      const pageHomeTitle = document.title;
      const pageHomeDescription = document.querySelector("meta[name='description']")?.getAttribute("content") || "";
      const ogTitle = document.querySelector("meta[property='og:title']");
      const ogDescription = document.querySelector("meta[property='og:description']");
      const docView = document.getElementById("doc-view");
      const docContent = document.getElementById("doc-content");
      const docToc = document.getElementById("doc-toc");
      const docSource = document.getElementById("doc-source");
      const docMeta = document.getElementById("doc-meta");
      const docBack = document.querySelector("[data-doc-back]");
      const sections = document.querySelectorAll(".lang-section");
      const buttons = document.querySelectorAll("[data-lang-pick]");
      const navLinks = document.querySelectorAll("[data-nav]");
      const tocTitle = document.querySelector("[data-ui='contents']");
      const navToggle = document.querySelector(".nav-toggle");
      const railInner = document.getElementById("rail-inner");
      const scrim = document.getElementById("scrim");
      const mobileQuery = window.matchMedia("(max-width: 960px)");
      const html = document.documentElement;

      function datasetKey(lang) {
        return `label${lang.charAt(0).toUpperCase()}${lang.slice(1)}`;
      }

      function setLang(lang, scrollTop = true) {
        if (!supported.includes(lang)) lang = "en";
        sections.forEach((section) => section.classList.toggle("is-active", section.dataset.lang === lang));
        buttons.forEach((button) => button.setAttribute("aria-pressed", button.dataset.langPick === lang ? "true" : "false"));
        navLinks.forEach((link) => {
          const label = link.dataset[datasetKey(lang)] || link.dataset.labelEn;
          const target = link.querySelector(".toc-text");
          if (label && target) target.textContent = label;
          link.setAttribute("href", link.dataset[`href${lang.charAt(0).toUpperCase()}${lang.slice(1)}`] || link.dataset.hrefEn);
        });
        if (tocTitle) tocTitle.textContent = (uiLabels[lang] || uiLabels.en).contents;
        const footerCopy = document.querySelector("[data-ui='footer-copy']");
        if (footerCopy && (uiLabels[lang] || uiLabels.en).footerCopy) {
          footerCopy.textContent = (uiLabels[lang] || uiLabels.en).footerCopy;
        }
        html.lang = lang === "pt" ? "pt-BR" : lang;
        try { localStorage.setItem(storageKey, lang); } catch (_) {}
        if (scrollTop && document.body.dataset.view !== "doc") window.scrollTo({ top: 0, behavior: "smooth" });
        if (document.body.dataset.view !== "doc") bindScrollSpy();
      }

      buttons.forEach((button) => button.addEventListener("click", () => setLang(button.dataset.langPick)));

      function fallbackCopy(text) {
        const textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.top = "-1000px";
        document.body.appendChild(textarea);
        textarea.select();
        let ok = false;
        try { ok = document.execCommand("copy"); } catch (_) { ok = false; }
        textarea.remove();
        return ok;
      }

      async function copyText(text) {
        if (navigator.clipboard?.writeText && window.isSecureContext) {
          try {
            await navigator.clipboard.writeText(text);
            return true;
          } catch (_) {}
        }
        return fallbackCopy(text);
      }

      document.querySelectorAll("[data-copy-button]").forEach((button) => {
        const block = button.closest("[data-copy-block]");
        const code = block?.querySelector("pre code");
        if (!code) return;
        const copyLabel = button.dataset.copyLabel || button.textContent || "Copy";
        const copiedLabel = button.dataset.copiedLabel || "Copied";
        button.addEventListener("click", async () => {
          const ok = await copyText(code.textContent || "");
          if (!ok) return;
          button.textContent = copiedLabel;
          window.setTimeout(() => { button.textContent = copyLabel; }, 1800);
        });
      });

      function openNav() {
        if (!navToggle || !railInner || !scrim) return;
        navToggle.setAttribute("aria-expanded", "true");
        railInner.classList.add("is-open");
        scrim.classList.add("is-open");
        document.body.classList.add("nav-open");
      }

      function closeNav() {
        if (!navToggle || !railInner || !scrim) return;
        navToggle.setAttribute("aria-expanded", "false");
        railInner.classList.remove("is-open");
        scrim.classList.remove("is-open");
        document.body.classList.remove("nav-open");
      }

      if (navToggle && railInner && scrim) {
        navToggle.addEventListener("click", () => {
          if (navToggle.getAttribute("aria-expanded") === "true") closeNav();
          else openNav();
        });
        scrim.addEventListener("click", closeNav);
        navLinks.forEach((link) => link.addEventListener("click", () => {
          setActiveNav(link.dataset.nav);
          closeNav();
          window.setTimeout(scheduleScrollSpy, 180);
        }));
        document.addEventListener("keydown", (event) => {
          if (event.key === "Escape") closeNav();
        });
        mobileQuery.addEventListener("change", (event) => {
          if (!event.matches) closeNav();
        });
      }

      let activeSectionKey = "";
      let scrollSpyPending = false;
      let activeDocSlug = "";

      function setActiveNav(sectionKey) {
        if (!sectionKey || sectionKey === activeSectionKey) return;
        activeSectionKey = sectionKey;
        navLinks.forEach((link) => {
          if (link.dataset.nav === sectionKey) {
            link.setAttribute("aria-current", "true");
          } else {
            link.removeAttribute("aria-current");
          }
        });
      }

      function updateScrollSpy() {
        if (document.body.dataset.view === "doc") return;
        const active = document.querySelector(".lang-section.is-active");
        if (!active) return;
        const chapters = Array.from(active.querySelectorAll(".chapter"));
        if (!chapters.length) return;
        const marker = Math.min(window.innerHeight * 0.36, 260);
        let current = chapters[0];
        chapters.forEach((chapter) => {
          if (chapter.getBoundingClientRect().top <= marker) current = chapter;
        });
        setActiveNav(current.dataset.sectionKey);
      }

      function scheduleScrollSpy() {
        if (scrollSpyPending) return;
        scrollSpyPending = true;
        window.requestAnimationFrame(() => {
          scrollSpyPending = false;
          updateScrollSpy();
        });
      }

      function bindScrollSpy() {
        activeSectionKey = "";
        scheduleScrollSpy();
      }

      function setView(view) {
        document.body.dataset.view = view;
        if (docView) docView.hidden = view !== "doc";
        if (view === "landing") {
          activeDocSlug = "";
          document.title = pageHomeTitle;
          if (ogTitle) ogTitle.setAttribute("content", pageHomeTitle);
          if (ogDescription) ogDescription.setAttribute("content", pageHomeDescription);
          bindScrollSpy();
        } else {
          closeNav();
          navLinks.forEach((link) => link.removeAttribute("aria-current"));
        }
      }

      function cleanDocSlug(slug) {
        if (!slug) return "";
        const decoded = decodeURIComponent(String(slug)).replace(/^\.\//, "").replace(/\.md$/, "");
        if (!decoded || decoded.startsWith("/") || decoded.includes("//") || decoded.includes("..")) return "";
        if (!/^[A-Za-z0-9_./-]+$/.test(decoded)) return "";
        return decoded;
      }

      function docSlugFromHref(rawHref, baseSlug = "") {
        if (!docView || !rawHref) return "";
        if (/^(https?:|mailto:|#|\/)/.test(rawHref)) return "";
        const hrefPath = rawHref.split("#")[0].split("?")[0];
        if (!hrefPath.endsWith(".md")) return "";
        const baseParts = baseSlug ? baseSlug.split("/").slice(0, -1) : [];
        const parts = hrefPath.split("/");
        const resolved = [];
        [...baseParts, ...parts].forEach((part) => {
          if (!part || part === ".") return;
          if (part === "..") resolved.pop();
          else resolved.push(part);
        });
        return cleanDocSlug(resolved.join("/"));
      }

      function docSlugFromHash() {
        const match = window.location.hash.match(/^#\/doc\/(.+)$/);
        return match ? cleanDocSlug(match[1]) : "";
      }

      function normalizeDocLinks(root = document) {
        if (!docView) return;
        root.querySelectorAll("a[href]").forEach((link) => {
          const raw = link.getAttribute("href") || "";
          const slug = docSlugFromHref(raw, activeDocSlug);
          if (!slug) return;
          link.setAttribute("href", `#/doc/${slug}`);
          link.dataset.docLink = slug;
        });
      }

      function escapeHtml(value) {
        return String(value)
          .replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;")
          .replaceAll('"', "&quot;")
          .replaceAll("'", "&#39;");
      }

      function parseFrontmatter(markdown) {
        if (!markdown.startsWith("---\n")) return { attrs: {}, body: markdown };
        const end = markdown.indexOf("\n---", 4);
        if (end === -1) return { attrs: {}, body: markdown };
        const attrs = {};
        markdown.slice(4, end).split("\n").forEach((line) => {
          const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
          if (match) attrs[match[1]] = match[2].replace(/^['"]|['"]$/g, "");
        });
        return { attrs, body: markdown.slice(end + 4).trimStart() };
      }

      function renderMarkdown(markdown) {
        if (window.marked?.parse) {
          window.marked.setOptions({ breaks: false, gfm: true });
          return window.marked.parse(markdown);
        }
        return `<pre><code>${escapeHtml(markdown)}</code></pre>`;
      }

      function sanitizeHtml(unsafe) {
        if (window.DOMPurify?.sanitize) {
          return window.DOMPurify.sanitize(unsafe, {
            ADD_ATTR: ["target", "rel"],
          });
        }
        const template = document.createElement("template");
        template.innerHTML = unsafe;
        template.content.querySelectorAll("script, iframe, object, embed, link, style").forEach((node) => node.remove());
        template.content.querySelectorAll("*").forEach((node) => {
          [...node.attributes].forEach((attr) => {
            if (/^on/i.test(attr.name) || /^javascript:/i.test(attr.value)) node.removeAttribute(attr.name);
          });
        });
        return template.innerHTML;
      }

      function slugifyHeading(text, fallback) {
        const slug = text.toLowerCase().trim()
          .replace(/<[^>]+>/g, "")
          .normalize("NFD").replace(/[\u0300-\u036f]/g, "")
          .replace(/[^a-z0-9]+/g, "-")
          .replace(/^-+|-+$/g, "");
        return slug || fallback;
      }

      function buildDocToc() {
        if (!docToc || !docContent) return;
        const headings = Array.from(docContent.querySelectorAll("h2"));
        if (!headings.length) {
          docToc.hidden = true;
          docToc.innerHTML = "";
          return;
        }
        const items = headings.map((heading, index) => {
          if (!heading.id) heading.id = slugifyHeading(heading.textContent || "", `section-${index + 1}`);
          return `<li><a href="#${heading.id}">${escapeHtml(heading.textContent || "")}</a></li>`;
        }).join("");
        docToc.hidden = false;
        docToc.innerHTML = `<p class="doc-toc-head">On this page</p><ol>${items}</ol>`;
      }

      function prepareDocArticle() {
        if (!docContent) return;
        const firstParagraph = docContent.querySelector("h1 + p");
        if (firstParagraph) firstParagraph.classList.add("doc-lede");
        normalizeDocLinks(docContent);
        docContent.querySelectorAll("a[href^='http']").forEach((link) => {
          link.setAttribute("target", "_blank");
          link.setAttribute("rel", "noreferrer");
        });
        buildDocToc();
      }

      function setDocMeta(attrs, slug) {
        if (!docMeta) return;
        const parts = [attrs.status, attrs.evidence_level, attrs.tver].filter(Boolean);
        docMeta.innerHTML = parts.length ? parts.map((part) => `<span>${escapeHtml(part)}</span>`).join("") : `<span>${escapeHtml(slug)}.md</span>`;
      }

      function setSourceLink(slug) {
        if (!docSource) return;
        docSource.innerHTML = `Source: <a href="${escapeHtml(slug)}.md">${escapeHtml(slug)}.md</a>`;
      }

      function renderDocError(slug, message) {
        if (docContent) {
          docContent.innerHTML = `<div class="doc-error"><h1>Document unavailable</h1><p>${escapeHtml(message)}</p></div>`;
        }
        if (docToc) docToc.hidden = true;
        setSourceLink(slug);
        setDocMeta({}, slug);
      }

      function renderDocSkeleton(slug) {
        if (docContent) {
          docContent.innerHTML = `<div class="doc-skeleton" aria-label="Loading document">
            <span></span><span></span><span></span><span></span>
          </div>`;
        }
        if (docToc) docToc.hidden = true;
        setSourceLink(slug);
        setDocMeta({}, slug);
      }

      async function loadDoc(slug) {
        if (!docView || !docContent) return;
        if (!slug) {
          setView("landing");
          return;
        }
        setView("doc");
        activeDocSlug = slug;
        renderDocSkeleton(slug);
        try {
          const response = await fetch(`${slug}.md`, { cache: "no-cache" });
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const markdown = await response.text();
          const parsed = parseFrontmatter(markdown);
          const rendered = sanitizeHtml(renderMarkdown(parsed.body));
          docContent.innerHTML = rendered;
          prepareDocArticle();
          const title = docContent.querySelector("h1")?.textContent?.trim() || `${slug}.md`;
          const lead = docContent.querySelector(".doc-lede")?.textContent?.trim() || pageHomeDescription;
          document.title = `${title} - Tilly Engineer Skills`;
          if (ogTitle) ogTitle.setAttribute("content", document.title);
          if (ogDescription) ogDescription.setAttribute("content", lead);
          setSourceLink(slug);
          setDocMeta(parsed.attrs, slug);
          window.scrollTo({ top: 0, behavior: "auto" });
        } catch (error) {
          renderDocError(slug, `Could not render ${slug}.md in this local view.`);
        }
      }

      function handleDocRoute() {
        if (!docView) return false;
        const slug = docSlugFromHash();
        if (!slug) {
          setView("landing");
          return false;
        }
        loadDoc(slug);
        return true;
      }

      if (docBack) {
        docBack.addEventListener("click", (event) => {
          event.preventDefault();
          history.pushState("", "", `${window.location.pathname}${window.location.search}`);
          setView("landing");
        });
      }

      window.addEventListener("scroll", scheduleScrollSpy, { passive: true });
      window.addEventListener("resize", scheduleScrollSpy);
      window.addEventListener("hashchange", () => {
        handleDocRoute();
        window.setTimeout(scheduleScrollSpy, 80);
      });

      let initial = "en";
      try {
        const stored = localStorage.getItem(storageKey);
        if (supported.includes(stored)) initial = stored;
      } catch (_) {}
      if (!supported.includes(initial)) initial = (navigator.language || "en").slice(0, 2).toLowerCase();
      setLang(initial, false);
      normalizeDocLinks();
      handleDocRoute();
    })();
"""


def render_page(page_key: str, structure: dict, content: dict) -> str:
    page = structure["pages"][page_key]
    meta = content["meta"][page_key]["en"]
    supported = [item["code"] for item in structure["languages"]]
    nav = render_nav(page_key, page, content, "en")
    sections = "\n".join(render_lang_section(page_key, structure, content, item["code"]) for item in structure["languages"])
    ui = content["ui"]["en"]
    brand_meta = ui["manual_meta"] if page_key == "manual" else ui["release_meta"]
    ui_labels = {
        lang: {
            "brand": values["brand"],
            "contents": values["contents"],
            "footerCopy": content["hero"][page_key][lang]["lead"] if page_key == "index" else "",
        }
        for lang, values in content["ui"].items()
    }
    footer_copy = ""
    if page_key == "index":
        footer_copy = (
            '<p class="footer-copy" data-ui="footer-copy">'
            f'{inline(content["hero"][page_key]["en"]["lead"])}'
            '</p>'
        )
    doc_view = ""
    if page_key == "index":
        doc_view = """
      <article class="doc-view" id="doc-view" hidden aria-live="polite">
        <div class="doc-topbar">
          <a class="doc-back" href="./" data-doc-back>Back to overview</a>
          <div class="doc-meta" id="doc-meta"></div>
        </div>
        <p class="doc-source" id="doc-source"></p>
        <aside class="doc-toc" id="doc-toc" hidden></aside>
        <div class="doc-content" id="doc-content"></div>
      </article>
        """
    image = structure["assets"]["social_preview_absolute"]
    script = (
        JS
        .replace("__SUPPORTED__", json.dumps(supported))
        .replace("__UI_LABELS__", json.dumps(ui_labels, ensure_ascii=False))
    )
    doc_scripts = ""
    if page_key == "index":
        doc_scripts = """
  <script src="https://cdn.jsdelivr.net/npm/dompurify@3.0.11/dist/purify.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js"></script>
        """
    return clean_html(f"""<!doctype html>
<!-- Generated by scripts/build_public_docs.py from docs/i18n/tes-public.structure.yml and docs/i18n/tes-public.content.json. -->
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>{esc(meta["title"])}</title>
  <meta name="description" content="{esc(meta["description"])}">
  <link rel="canonical" href="{esc(page["canonical"])}">
  <meta property="og:title" content="{esc(meta["title"])}">
  <meta property="og:description" content="{esc(meta["og_description"])}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{esc(page["canonical"])}">
  <meta property="og:image" content="{esc(image)}">
  <meta property="og:image:type" content="image/webp">
  <meta property="og:image:width" content="1731">
  <meta property="og:image:height" content="909">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="{esc(image)}">
  <meta name="theme-color" content="#f0f7f4">
  <link rel="icon" href="{page['asset_prefix']}assets/logo-tesc-icon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT@9..144,300..900,30..100&family=Newsreader:opsz,wght@6..72,300..700&family=JetBrains+Mono:wght@400;500;700&display=swap">
  <style>{CSS}</style>
</head>
<body class="{esc(page["body_class"])}" data-view="landing">
  <a class="skip" href="#content">{esc(ui["skip"])}</a>
  <div class="layout page">
    <aside class="rail">
      <header class="nav-bar">
        <div class="brand">
          <span class="brand-mark" data-ui="brand">{render_brand_mark(ui["brand"])}</span>
          <span class="brand-meta">{esc(brand_meta)}</span>
        </div>
        <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="rail-inner" aria-label="Open navigation">
          <span></span>
        </button>
      </header>
      <div class="rail-inner" id="rail-inner">
        <nav class="toc" aria-label="{esc(ui["contents"])}">
          <p class="toc-title" data-ui="contents">{esc(ui["contents"])}</p>
          <ul>{nav}</ul>
        </nav>
      </div>
    </aside>
    <div class="scrim" id="scrim" aria-hidden="true"></div>
    <main class="stage" id="content">
      {doc_view}
      {sections}
      <footer class="footer">
        {footer_copy}
        <div class="footer-meta">
          <span>{esc(ui["version"])} - {esc(ui["source_note"])}</span>
          <span><a href="https://github.com/murillodutt/tilly-engineer-skills">{esc(ui["github"])}</a></span>
        </div>
      </footer>
    </main>
  </div>
  {doc_scripts}
  <script>{script}</script>
</body>
</html>
""")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    structure, content = load_sources()
    failures: list[str] = []
    for page_key, page in structure["pages"].items():
        output = ROOT / page["output"]
        rendered = render_page(page_key, structure, content)
        if args.check:
            if not output.exists() or output.read_text(encoding="utf-8") != rendered:
                failures.append(page["output"])
        else:
            output.write_text(rendered, encoding="utf-8")

    if failures:
        print("[public-docs] FAIL")
        for path in failures:
            print(f"out of date: {path}")
        return 1
    print("[public-docs] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
