# hyresearchagent

LLM Wiki Part 4 수업 자료. 검증된 연구 절차(논문 읽기, 실험 로그 정리)를 재사용 가능한 Skill로 다시 쓰는 방법을 다룬다. GitHub Pages로 `index.html`을 배포한다.

## 구성

| 경로 | 내용 |
|---|---|
| `index.html` | 빌드 결과물. 직접 고치지 않는다 |
| `src/pages/*.html` | 페이지별 본문 원본 (복습 R, 세팅 00, 01~06장, 정리) |
| `build.py` | `src/pages/` + `styles.css` + `app.js` → `index.html` |
| `styles.css`, `app.js` | 공통 스타일, 라우팅·Q&A·복사 버튼 스크립트 |
| `실습파일/` | 실행 계약 템플릿, 두 Skill의 계약·SKILL.md 완성본, 생성 프롬프트, 테스트 기록표, 선정 기준표, 품질 체크리스트, Part 4 템플릿 다섯 파일 |
| `강의교안/` | 클립별 강의 PDF |
| `전체 스크립트.md`, `정리본.md` | 강의 전사본과 정리본 |
| `legacy/content_v1/` | 이전 버전(정리본 기반 JSON 콘텐츠). 현재 빌드에서 쓰지 않음 |

## 빌드

```bash
python build.py
```

페이지 순서와 제목은 `build.py`의 `PAGES`에서, 본문은 `src/pages/<page_id>.html`에서 고친다. 각 페이지 파일은 `<div class="prose">` 안에 들어갈 HTML 조각이고, `<!-- toc -->` 앞부분은 목차 위에, 뒷부분의 `<h2>`는 자동으로 번호 id와 목차 항목이 붙는다.

## 수업 자료의 규칙

- 규칙 파일 이름은 `AGENTS.md` (루트, `llm_wiki/`, `llm_wiki/research/`). Part 3의 `CLAUDE.md`·`README.md`에 해당한다.
- Skill 저장 위치는 `.agents/skills/<이름>/SKILL.md`.
- Q&A는 답을 입력해야 해설이 열린다. 입력한 답은 브라우저 localStorage에 남는다.
- 장마다 개념 설명 뒤에 실습이 바로 이어지고, 실습 블록은 목표 → 요청문 → 확인할 것 → 실패하면 순서다.
