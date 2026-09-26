#!/usr/bin/env python3
"""Assemble Part 4 site HTML from chapter JSON files (content/ch1.json ..)."""
import json, re, html, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PAGES = [
    # (page_id, num, kicker, title)
    ("overview", "00", "전체 흐름", "Part 4. 검증된 절차를 스킬로 다시 쓰기"),
    ("chapter-01", "01", "판단", "반복 업무에서 스킬이 맞는 일 찾기"),
    ("chapter-02", "02", "설계", "페이퍼 리딩 스킬: 실행 계약부터 검증까지"),
    ("chapter-03", "03", "재사용", "실험 로그 스킬과 품질 체크리스트"),
]

SECTIONS_CSS = []

def md_to_html(md):
    """Minimal markdown -> HTML for the prose blocks used here."""
    lines = md.split("\n")
    out = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            lang = line[3:].strip()
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            cls = f' class="language-{lang}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(buf))}</code></pre>")
            continue
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            rows = [r for r in rows if not all(set(c) <= set("-: ") for c in r)]
            t = ["<div class=\"table-scroll\"><table>", "<thead><tr>"]
            t += [f"<th>{inline(c)}</th>" for c in rows[0]]
            t += ["</tr></thead><tbody>"]
            for r in rows[1:]:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("\n".join(t))
            continue
        if line.startswith("- ") or line.startswith("* "):
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or lines[i].startswith("* ")):
                items.append(lines[i][2:]); i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue
        if re.match(r"^\d+\. ", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(re.sub(r"^\d+\. ", "", lines[i])); i += 1
            out.append("<ol>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ol>")
            continue
        if line.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].startswith("> "):
                buf.append(lines[i][2:]); i += 1
            out.append("<blockquote><p>" + "</p><p>".join(inline(b) for b in buf) + "</p></blockquote>")
            continue
        if line.strip() == "":
            i += 1; continue
        # paragraph (may span blank-line separated)
        buf = [line]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#|```|\||- |\* |\d+\. |> )", lines[i]):
            buf.append(lines[i]); i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")
    return "\n".join(out)

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"`([^`]+?)`", r"<code>\1</code>", s)
    return s

def slug(pid, idx):
    return f"{pid}--section-{idx}"

def build_page(pid, num, kicker, title, sections_md, pager_prev, pager_next):
    body = []
    body.append(f'<article class="page" id="{pid}" data-page="{pid}" tabindex="-1">')
    body.append(f'<header class="page-hero"><div class="hero-meta"><span>{kicker}</span><span>{num}</span></div><h1>{html.escape(title)}</h1></header>')
    body.append('<div class="prose">')
    # first section paragraphs go before TOC if first section has no heading marker
    secs = sections_md
    # TOC
    if secs:
        toc = ['<nav class="on-this-page" aria-label="이 페이지의 내용"><p>이 페이지에서 다루는 내용</p><ol>']
        for idx, s in enumerate(secs, 1):
            toc.append(f'<li><a href="#{slug(pid, idx)}">{inline(s["title"])}</a></li>')
        toc.append("</ol></nav>")
        body.append("\n".join(toc))
    for idx, s in enumerate(secs, 1):
        sid = slug(pid, idx)
        body.append('<section class="content-section">')
        body.append(f'<h2 id="{sid}">{inline(s["title"])}<a class="heading-anchor" href="#{sid}" aria-label="이 제목으로 이동">#</a></h2>')
        body.append(md_to_html(s["body"]))
        body.append("</section>")
    body.append("</div>")
    pager = ['<nav class="page-pager" aria-label="앞뒤 페이지">']
    if pager_prev:
        pager.append(f'<a href="#{pager_prev[0]}"><span>이전</span>{html.escape(pager_prev[1])}</a>')
    else:
        pager.append("<span></span>")
    if pager_next:
        pager.append(f'<a href="#{pager_next[0]}"><span>다음</span>{html.escape(pager_next[1])}</a>')
    body.append("\n".join(pager) + "</nav></article>")
    return "\n".join(body)

def main():
    chapters = {}
    for pid, _, _, _ in PAGES:
        key = pid.replace("chapter-", "ch").replace("overview", "ch0")
        path = os.path.join(ROOT, "content", f"{pid}.json")
        if os.path.exists(path):
            chapters[pid] = json.load(open(path))
    # chapters[pid] = {"title":..., "sections":[{"title","body"}...]}
    arts = []
    titles = {p[0]: p[3] for p in PAGES}
    for i, (pid, num, kicker, title) in enumerate(PAGES):
        if pid == "overview":
            continue
        data = chapters.get(pid) or {"title": title, "sections": []}
        prev = (PAGES[i-1][0], PAGES[i-1][3]) if i > 0 else None
        nxt = (PAGES[i+1][0], PAGES[i+1][3]) if i+1 < len(PAGES) else None
        arts.append(build_page(pid, num, kicker, data.get("title", title), data["sections"], prev, nxt))
    overview = chapters.get("overview")
    if overview:
        arts.insert(0, build_page("overview", "00", "전체 흐름", PAGES[0][3], overview["sections"], None, (PAGES[1][0], PAGES[1][3])))
    nav_items = []
    for i, (pid, num, kicker, title) in enumerate(PAGES):
        nav_items.append(
            f'<a class="nav-item{" is-active" if i==0 else ""}" href="#{pid}" data-route="{pid}"><span class="nav-dot" aria-hidden="true"></span><span class="nav-copy"><span class="nav-kicker">{kicker}</span><span class="nav-title">{html.escape(titles[pid])}</span></span><span class="nav-num">{num}</span></a>')
    css = open(os.path.join(ROOT, "styles.css")).read()
    js = open(os.path.join(ROOT, "app.js")).read()
    js = js.replace("document.title = page.querySelector('h1').textContent + ' · LLM Wiki Part 3';",
                    "document.title = page.querySelector('h1').textContent + ' · LLM Wiki Part 4';")
    doc = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="검증된 절차를 재사용 가능한 스킬로 만드는 Claude Code 스킬 제작 교재 (Part 4)">
<meta name="theme-color" content="#ffffff">
<title>Part 4. 검증된 절차를 스킬로 다시 쓰는 LLM Wiki</title>
<style>
{css}
</style>
</head>
<body>
<a class="skip-link" href="#main-content">본문으로 건너뛰기</a>
<div class="progress" aria-hidden="true"><span></span></div>
<header class="site-header"><strong>LLM Wiki · Part 4</strong><button class="menu-button" type="button" aria-label="목차 열기" aria-expanded="false">☰</button></header>
<aside class="sidebar" aria-label="문서 목차">
    <a class="brand" href="#overview"><strong>LLM Wiki · Part 4</strong><span>검증된 절차를 스킬로 다시 쓰는 연구 흐름</span></a>
    <p class="trail-label">Research trail</p>
    <nav class="nav-list">{''.join(nav_items)}</nav>
    <div class="sidebar-note"><strong>읽는 순서</strong>처음이라면 01~03장을 차례로 읽으세요. 01장에서 판단 기준을 만들고, 02장에서 페이퍼 리딩 스킬을 설계·구현·검증한 뒤, 03장에서 실험 로그 스킬과 품질 체크리스트로 마무리합니다.</div>
</aside>
<div class="scrim" aria-hidden="true"></div>
<div class="shell"><main class="main" id="main-content">
{''.join(arts)}
</main></div>
<dialog class="lightbox"><div class="lightbox-inner"><button class="lightbox-close" type="button" aria-label="닫기">×</button><img src="" alt=""></div></dialog>
<button class="back-top" type="button" aria-label="맨 위로">↑</button>
{js}
</body>
</html>"""
    out = os.path.join(ROOT, "index.html")
    open(out, "w").write(doc)
    print("wrote", out, len(doc), "chars")

if __name__ == "__main__":
    main()
