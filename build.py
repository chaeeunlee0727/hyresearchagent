#!/usr/bin/env python3
"""Assemble index.html from hand-written page fragments in src/pages/.

Each fragment is the inner HTML of one page (everything that goes inside
<div class="prose">). Page order, numbering and titles live in PAGES below.
Run:  python build.py
"""
import html
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src", "pages")

# (page_id, num, kicker, title, nav_title)
PAGES = [
    ("review",     "R",  "복습",   "Part 3 되짚기: 우리가 이미 가진 것",            "Part 3 되짚기"),
    ("setup",      "00", "준비",   "수업 흐름과 작업공간 세팅",                      "수업 흐름과 세팅"),
    ("chapter-01", "01", "판단",   "어떤 업무를 Skill로 만들 것인가",                "Skill로 만들 업무 고르기"),
    ("chapter-02", "02", "설계",   "실행 경계를 정하고 실행 계약을 쓴다",            "실행 경계와 실행 계약"),
    ("chapter-03", "03", "구현",   "실행 계약을 SKILL.md로 옮긴다",                  "계약을 SKILL.md로"),
    ("chapter-04", "04", "검증",   "정상·누락·재실행, 세 시나리오로 시험한다",       "세 시나리오 테스트"),
    ("chapter-05", "05", "재사용", "같은 패턴으로 실험 로그 Skill을 만든다",         "실험 로그 Skill"),
    ("chapter-06", "06", "점검",   "품질 체크리스트와 수정 루프",                    "품질 체크리스트"),
    ("wrapup",     "끝", "정리",   "가져가는 것과 다음 단계",                        "정리와 다음 단계"),
]

HEADING_RE = re.compile(r'<h2(?P<attrs>[^>]*)>(?P<text>.*?)</h2>', re.S)


def number_headings(pid, body):
    """Give every <h2> a stable id and an anchor link; collect a TOC."""
    toc = []
    idx = 0

    def repl(m):
        nonlocal idx
        idx += 1
        attrs = m.group("attrs")
        text = m.group("text").strip()
        sid = f"{pid}--section-{idx}"
        if 'id="' in attrs:
            sid = re.search(r'id="([^"]+)"', attrs).group(1)
        else:
            attrs = f' id="{sid}"' + attrs
        plain = re.sub(r"<[^>]+>", "", text)
        toc.append((sid, plain))
        return (f'<h2{attrs}>{text}<a class="heading-anchor" href="#{sid}" '
                f'aria-label="이 제목으로 이동">#</a></h2>')

    body = HEADING_RE.sub(repl, body)
    return body, toc


def build_page(i):
    pid, num, kicker, title, _ = PAGES[i]
    path = os.path.join(SRC, f"{pid}.html")
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    # Optional lead block: everything before the first <!-- toc --> marker
    # is rendered above the "on this page" box.
    lead, _, rest = raw.partition("<!-- toc -->")
    if not rest:
        lead, rest = "", raw
    rest, toc = number_headings(pid, rest)
    lead, _ = number_headings(pid, lead)
    # Wrap each <h2>...(until next h2) in a section so CSS can draw dividers.
    parts = re.split(r'(?=<h2[ >])', rest)
    rest = parts[0] + "".join(f'<section class="content-section">\n{p.strip()}\n</section>' for p in parts[1:] if p.strip())

    out = [f'<article class="page" id="{pid}" data-page="{pid}" tabindex="-1">']
    out.append(f'<header class="page-hero"><div class="hero-meta"><span>{kicker}</span>'
               f'<span>{num}</span></div><h1>{html.escape(title)}</h1></header>')
    out.append('<div class="prose">')
    out.append(lead)
    if toc:
        out.append('<nav class="on-this-page" aria-label="이 페이지의 내용"><p>이 페이지에서 다루는 내용</p><ol>')
        out += [f'<li><a href="#{sid}">{html.escape(t)}</a></li>' for sid, t in toc]
        out.append('</ol></nav>')
    out.append(rest)
    out.append('</div>')
    pager = ['<nav class="page-pager" aria-label="앞뒤 페이지">']
    if i > 0:
        p = PAGES[i - 1]
        pager.append(f'<a href="#{p[0]}"><span>이전</span>{p[1]}. {html.escape(p[4])}</a>')
    else:
        pager.append('<span></span>')
    if i + 1 < len(PAGES):
        n = PAGES[i + 1]
        pager.append(f'<a href="#{n[0]}"><span>다음</span>{n[1]}. {html.escape(n[4])}</a>')
    pager.append('</nav>')
    out.append("".join(pager))
    out.append('</article>')
    return "\n".join(out)


def main():
    arts = [build_page(i) for i in range(len(PAGES))]
    nav = []
    for i, (pid, num, kicker, _, nav_title) in enumerate(PAGES):
        active = " is-active" if i == 0 else ""
        nav.append(f'<a class="nav-item{active}" href="#{pid}" data-route="{pid}">'
                   f'<span class="nav-dot" aria-hidden="true"></span>'
                   f'<span class="nav-copy"><span class="nav-kicker">{kicker}</span>'
                   f'<span class="nav-title">{html.escape(nav_title)}</span></span>'
                   f'<span class="nav-num">{num}</span></a>')
    with open(os.path.join(ROOT, "styles.css"), encoding="utf-8") as f:
        css = f.read()
    with open(os.path.join(ROOT, "app.js"), encoding="utf-8") as f:
        js = f.read()
    doc = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="검증된 연구 절차를 재사용 가능한 Skill로 다시 쓰는 LLM Wiki Part 4 수업 자료">
<meta name="theme-color" content="#ffffff">
<title>Part 4. 검증된 절차를 Skill로 다시 쓰는 LLM Wiki</title>
<style>
{css}
</style>
</head>
<body>
<a class="skip-link" href="#main-content">본문으로 건너뛰기</a>
<div class="progress" aria-hidden="true"><span></span></div>
<header class="site-header"><strong>LLM Wiki · Part 4</strong><button class="menu-button" type="button" aria-label="목차 열기" aria-expanded="false">☰</button></header>
<aside class="sidebar" aria-label="문서 목차">
    <a class="brand" href="#review"><strong>LLM Wiki · Part 4</strong><span>검증된 절차를 Skill로 다시 쓰기</span></a>
    <p class="trail-label">Lesson trail</p>
    <nav class="nav-list">{''.join(nav)}</nav>
    <div class="sidebar-note"><strong>읽는 순서</strong>복습과 세팅을 마친 뒤 01~06을 차례로 진행합니다. 장마다 개념 설명 뒤에 바로 실습이 이어지고, 각 실습의 산출물이 다음 장의 재료가 됩니다.</div>
</aside>
<div class="scrim" aria-hidden="true"></div>
<div class="shell"><main class="main" id="main-content">
{''.join(arts)}
</main></div>
<dialog class="lightbox"><div class="lightbox-inner"><button class="lightbox-close" type="button" aria-label="닫기">×</button><img src="" alt=""></div></dialog>
<button class="back-top" type="button" aria-label="맨 위로">↑</button>
<script>
{js}
</script>
</body>
</html>"""
    out = os.path.join(ROOT, "index.html")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write(doc)
    print("wrote", out, len(doc), "chars,", len(PAGES), "pages")


if __name__ == "__main__":
    main()
