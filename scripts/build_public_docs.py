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

        def link(match: re.Match[str]) -> str:
            label = match.group(1)
            href = match.group(2)
            return f'<a href="{esc(href)}">{label}</a>'

        rendered.append(re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, value))
    return "".join(rendered)


def clean_html(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines()) + "\n"


def lang_meta(structure: dict, lang: str) -> dict:
    for item in structure["languages"]:
        if item["code"] == lang:
            return item
    raise KeyError(lang)


def href_for(page: dict, href: str) -> str:
    if href.startswith(("http://", "https://", "#", "mailto:")):
        return href
    return f"{page['asset_prefix']}{href}"


def render_block(block: dict, page: dict) -> str:
    kind = block["type"]
    if kind == "p":
        return f"<p>{inline(block['text'])}</p>"
    if kind == "note":
        return f'<aside class="note">{inline(block["text"])}</aside>'
    if kind in {"list", "steps"}:
        tag = "ol" if kind == "steps" else "ul"
        items = "\n".join(f"<li>{inline(item)}</li>" for item in block["items"])
        return f'<{tag} class="{kind}">\n{items}\n</{tag}>'
    if kind == "code":
        return (
            f'<div class="pre-wrap" data-label="{esc(block.get("label", "code"))}">'
            f"<pre><code>{esc(block['text'])}</code></pre></div>"
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
    if kind == "links":
        links = []
        for item in block["items"]:
            links.append(f'<a class="doc-link" href="{href_for(page, item["href"])}">{inline(item["label"])}</a>')
        return f"<div class=\"link-grid\">{''.join(links)}</div>"
    raise ValueError(f"unknown block type: {kind}")


def render_section(section_key: str, section: dict, page: dict) -> str:
    blocks = "\n".join(render_block(block, page) for block in section.get("blocks", []))
    return f"""
        <section class="chapter" id="{section_key}">
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
        links.append(
            f'<li><a href="#{key}" data-nav="{key}" {labels}>'
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


def render_lang_section(page_key: str, structure: dict, content: dict, lang: str) -> str:
    page = structure["pages"][page_key]
    hero = content["hero"][page_key][lang]
    meta = lang_meta(structure, lang)
    sections = "\n".join(
        render_section(key, content["sections"][key][lang], page)
        for key in page["nav"]
    )
    hero_image = ""
    if page_key == "index":
        hero_image = (
            '<figure class="hero-visual">'
            f'<img src="{structure["assets"]["social_preview"]}" alt="{esc(content["meta"]["index"][lang]["og_description"])}">'
            "</figure>"
        )
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
          </div>
          <p class="eyebrow">{inline(hero["eyebrow"])}</p>
          <h1>{inline(hero["title"])}</h1>
          <p class="lead">{inline(hero["lead"])}</p>
          {hero_actions}
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
      --ink-faint: #776c68;
      --rule: #b8cfca;
      --rule-soft: #d2e3df;
      --accent: #2f7f84;
      --accent-soft: #99e1d9;
      --warn: #b86a3a;
      --mono-bg: #161215;
      --mono-fg: #f0f7f4;
      --font-display: ui-serif, Georgia, "Times New Roman", serif;
      --font-body: ui-serif, Georgia, "Times New Roman", serif;
      --font-mono: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace;
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body {
      background: var(--paper);
      color: var(--ink);
      font-family: var(--font-body);
      font-size: 17px;
      line-height: 1.65;
      text-rendering: optimizeLegibility;
      -webkit-font-smoothing: antialiased;
    }
    body::before {
      background:
        radial-gradient(1000px 500px at 100% 0%, rgba(47,127,132,.08), transparent 60%),
        radial-gradient(760px 420px at 0% 30%, rgba(184,106,58,.05), transparent 60%);
      content: "";
      inset: 0;
      pointer-events: none;
      position: fixed;
      z-index: 0;
    }
    a { color: var(--accent); text-decoration: none; }
    a:hover { text-decoration: underline; text-underline-offset: 3px; }
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
      left: 12px;
      padding: 8px 12px;
      position: absolute;
      top: -100px;
      z-index: 10;
    }
    .skip:focus { top: 12px; }
    .layout {
      display: grid;
      grid-template-columns: 260px minmax(0, 1fr);
      min-height: 100vh;
      position: relative;
      z-index: 1;
    }
    .rail {
      border-right: 1px solid var(--rule-soft);
      height: 100vh;
      padding: 28px 24px;
      position: sticky;
      top: 0;
    }
    .brand {
      font-family: var(--font-mono);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: .12em;
      margin-bottom: 32px;
      text-transform: uppercase;
    }
    .toc-title {
      color: var(--ink-faint);
      font-family: var(--font-mono);
      font-size: 11px;
      letter-spacing: .1em;
      margin: 0 0 12px;
      text-transform: uppercase;
    }
    .toc ul { list-style: none; margin: 0; padding: 0; }
    .toc a {
      border-left: 2px solid transparent;
      color: var(--ink-soft);
      display: grid;
      font-size: 15px;
      gap: 10px;
      grid-template-columns: 30px 1fr;
      margin: 2px 0;
      padding: 7px 0 7px 10px;
    }
    .toc a[aria-current="true"] {
      border-left-color: var(--accent);
      color: var(--ink);
    }
    .toc-num { color: var(--accent); font-family: var(--font-mono); font-size: 12px; }
    .toc-text { color: inherit; font-family: inherit; font-size: inherit; }
    .stage {
      margin: 0 auto;
      max-width: 1120px;
      padding: 56px clamp(24px, 6vw, 72px) 96px;
      width: 100%;
    }
    .lang-section { display: none; }
    .lang-section.is-active { display: block; }
    .language-row { display: flex; gap: 8px; margin-bottom: 28px; }
    .lang-btn {
      background: transparent;
      border: 1px solid var(--rule);
      border-radius: 999px;
      color: var(--ink-soft);
      cursor: pointer;
      font-family: var(--font-mono);
      font-size: 12px;
      padding: 6px 10px;
    }
    .lang-btn[aria-pressed="true"] {
      background: var(--ink);
      border-color: var(--ink);
      color: var(--paper);
    }
    .masthead { padding-bottom: 40px; }
    .eyebrow {
      color: var(--accent);
      font-family: var(--font-mono);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: .12em;
      margin: 0 0 18px;
      text-transform: uppercase;
    }
    h1, h2, h3 {
      font-family: var(--font-display);
      font-weight: 500;
      letter-spacing: 0;
      line-height: 1.06;
      margin: 0;
    }
    h1 {
      font-size: clamp(48px, 8vw, 96px);
      max-width: 900px;
    }
    .lead {
      color: var(--ink-soft);
      font-size: clamp(21px, 2.4vw, 30px);
      line-height: 1.38;
      margin: 24px 0 0;
      max-width: 820px;
    }
    .hero-actions {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 28px;
    }
    .btn {
      border: 1px solid var(--rule);
      color: var(--ink);
      display: inline-flex;
      font-family: var(--font-mono);
      font-size: 13px;
      font-weight: 700;
      justify-content: center;
      min-width: 156px;
      padding: 11px 14px;
      text-transform: uppercase;
    }
    .btn-primary {
      background: var(--ink);
      border-color: var(--ink);
      color: var(--paper);
    }
    .hero-visual {
      background: var(--mono-bg);
      border: 1px solid rgba(22,18,21,.2);
      margin: 36px 0 0;
    }
    .hero-visual img { display: block; width: 100%; }
    .chapter {
      border-top: 1px solid var(--rule-soft);
      padding: 44px 0 8px;
    }
    .chapter-head {
      display: grid;
      gap: 20px;
      grid-template-columns: 64px minmax(0, 1fr);
      margin-bottom: 22px;
    }
    .chapter-num {
      color: var(--accent);
      font-family: var(--font-mono);
      font-size: 13px;
      font-weight: 700;
      padding-top: 8px;
    }
    h2 { font-size: clamp(32px, 4vw, 54px); }
    .chapter-body { margin-left: 84px; max-width: 900px; }
    .chapter-body > p,
    .chapter-body > ul,
    .chapter-body > ol,
    .note { max-width: 780px; }
    .chapter-body .lede {
      color: var(--ink-soft);
      font-size: 22px;
      margin: 0 0 24px;
    }
    ul, ol { padding-left: 22px; }
    li { margin: 0 0 8px; }
    .card-grid {
      display: grid;
      gap: 14px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      margin: 24px 0;
    }
    .info-card {
      border-top: 3px solid var(--accent);
      padding: 16px 0 0;
    }
    .info-card h3 { font-size: 22px; margin-bottom: 8px; }
    .info-card p { color: var(--ink-soft); margin: 0; }
    .table-wrap { margin: 24px 0; overflow-x: auto; }
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
    td { border-bottom: 1px solid var(--rule-soft); padding: 14px 16px 14px 0; vertical-align: top; }
    .pre-wrap {
      background: var(--mono-bg);
      border-radius: 6px;
      color: var(--mono-fg);
      margin: 24px 0;
      overflow: hidden;
    }
    .pre-wrap::before {
      color: var(--accent-soft);
      content: attr(data-label);
      display: block;
      font-family: var(--font-mono);
      font-size: 11px;
      letter-spacing: .08em;
      padding: 14px 18px 0;
      text-transform: uppercase;
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
    .note {
      border-left: 3px solid var(--warn);
      color: var(--ink-soft);
      margin: 24px 0;
      padding: 8px 0 8px 18px;
    }
    .link-grid {
      display: grid;
      gap: 10px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      margin: 24px 0;
    }
    .doc-link {
      border: 1px solid var(--rule-soft);
      color: var(--ink);
      display: block;
      padding: 14px 16px;
    }
    .footer {
      border-top: 1px solid var(--rule-soft);
      color: var(--ink-faint);
      display: flex;
      flex-wrap: wrap;
      font-family: var(--font-mono);
      font-size: 12px;
      gap: 12px;
      justify-content: space-between;
      margin-top: 56px;
      padding-top: 22px;
    }
    @media (max-width: 860px) {
      .layout { display: block; }
      .rail {
        background: rgba(240,247,244,.96);
        border-bottom: 1px solid var(--rule-soft);
        border-right: 0;
        height: auto;
        position: relative;
      }
      .toc ul { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
      .stage { padding-top: 36px; }
      .chapter-head { grid-template-columns: 1fr; gap: 8px; }
      .chapter-body { margin-left: 0; }
      code { white-space: normal; }
    }
"""


JS = r"""
    (() => {
      const supported = __SUPPORTED__;
      const uiLabels = __UI_LABELS__;
      const storageKey = "tes-public-lang";
      const sections = document.querySelectorAll(".lang-section");
      const buttons = document.querySelectorAll("[data-lang-pick]");
      const navLinks = document.querySelectorAll("[data-nav]");
      const tocTitle = document.querySelector("[data-ui='contents']");
      const brand = document.querySelector("[data-ui='brand']");
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
        });
        if (tocTitle) tocTitle.textContent = (uiLabels[lang] || uiLabels.en).contents;
        if (brand) brand.textContent = (uiLabels[lang] || uiLabels.en).brand;
        html.lang = lang === "pt" ? "pt-BR" : lang;
        try { localStorage.setItem(storageKey, lang); } catch (_) {}
        if (scrollTop) window.scrollTo({ top: 0, behavior: "smooth" });
        bindScrollSpy();
      }

      buttons.forEach((button) => button.addEventListener("click", () => setLang(button.dataset.langPick)));

      let observer;
      function bindScrollSpy() {
        if (observer) observer.disconnect();
        const active = document.querySelector(".lang-section.is-active");
        if (!active) return;
        observer = new IntersectionObserver((entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            navLinks.forEach((link) => {
              const activeLink = link.dataset.nav === entry.target.id;
              link.toggleAttribute("aria-current", activeLink);
            });
          });
        }, { rootMargin: "-28% 0px -62% 0px", threshold: 0 });
        active.querySelectorAll(".chapter").forEach((chapter) => observer.observe(chapter));
      }

      let initial = "en";
      try {
        const stored = localStorage.getItem(storageKey);
        if (supported.includes(stored)) initial = stored;
      } catch (_) {}
      if (!supported.includes(initial)) initial = (navigator.language || "en").slice(0, 2).toLowerCase();
      setLang(initial, false);
    })();
"""


def render_page(page_key: str, structure: dict, content: dict) -> str:
    page = structure["pages"][page_key]
    meta = content["meta"][page_key]["en"]
    supported = [item["code"] for item in structure["languages"]]
    nav = render_nav(page_key, page, content, "en")
    sections = "\n".join(render_lang_section(page_key, structure, content, item["code"]) for item in structure["languages"])
    ui = content["ui"]["en"]
    ui_labels = {
        lang: {"brand": values["brand"], "contents": values["contents"]}
        for lang, values in content["ui"].items()
    }
    image = structure["assets"]["social_preview_absolute"]
    script = (
        JS
        .replace("__SUPPORTED__", json.dumps(supported))
        .replace("__UI_LABELS__", json.dumps(ui_labels, ensure_ascii=False))
    )
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
  <style>{CSS}</style>
</head>
<body class="{esc(page["body_class"])}">
  <a class="skip" href="#content">{esc(ui["skip"])}</a>
  <div class="layout">
    <aside class="rail">
      <div class="brand" data-ui="brand">{esc(ui["brand"])}</div>
      <nav class="toc" aria-label="{esc(ui["contents"])}">
        <p class="toc-title" data-ui="contents">{esc(ui["contents"])}</p>
        <ul>{nav}</ul>
      </nav>
    </aside>
    <main class="stage" id="content">
      {sections}
      <footer class="footer">
        <span>{esc(ui["version"])} - {esc(ui["source_note"])}</span>
        <span><a href="https://github.com/murillodutt/tilly-engineer-skills">{esc(ui["github"])}</a></span>
      </footer>
    </main>
  </div>
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
