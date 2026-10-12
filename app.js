(() => {
    const pages = [...document.querySelectorAll('[data-page]')];
    const links = [...document.querySelectorAll('[data-route]')];
    const sidebar = document.querySelector('.sidebar');
    const scrim = document.querySelector('.scrim');
    const menu = document.querySelector('.menu-button');
    const progress = document.querySelector('.progress span');
    const backTop = document.querySelector('.back-top');
    const lightbox = document.querySelector('.lightbox');
    const lightboxImage = lightbox.querySelector('img');
    const DEFAULT = '#review';

    function pageForHash(hash) {
        const id = decodeURIComponent((hash || DEFAULT).slice(1));
        return pages.find(page => id === page.id || id.startsWith(page.id + '--')) || pages[0];
    }
    function closeMenu() {
        sidebar.classList.remove('is-open'); scrim.classList.remove('is-open');
        menu.setAttribute('aria-expanded', 'false'); menu.setAttribute('aria-label', '목차 열기');
    }
    function route({ initial = false } = {}) {
        const hash = location.hash || DEFAULT;
        const page = pageForHash(hash);
        pages.forEach(item => item.classList.toggle('is-visible', item === page));
        links.forEach(link => link.classList.toggle('is-active', link.dataset.route === page.dataset.page));
        document.title = page.querySelector('h1').textContent + ' · LLM Wiki Part 4';
        closeMenu();
        requestAnimationFrame(() => {
            const target = document.getElementById(decodeURIComponent(hash.slice(1)));
            if (target && target !== page) target.scrollIntoView({ block: 'start' });
            else if (!initial) window.scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
            page.focus({ preventScroll: true });
            updateProgress();
        });
    }
    function updateProgress() {
        const page = document.querySelector('.page.is-visible');
        if (!page) return;
        const start = page.offsetTop;
        const max = Math.max(page.offsetHeight - innerHeight, 1);
        const value = Math.max(0, Math.min(1, (scrollY - start) / max));
        progress.style.width = (value * 100) + '%';
        backTop.classList.toggle('is-visible', scrollY > 650);
    }
    addEventListener('hashchange', () => route());
    addEventListener('scroll', updateProgress, { passive: true });
    addEventListener('resize', updateProgress);
    menu.addEventListener('click', () => {
        const open = sidebar.classList.toggle('is-open'); scrim.classList.toggle('is-open', open);
        menu.setAttribute('aria-expanded', String(open)); menu.setAttribute('aria-label', open ? '목차 닫기' : '목차 열기');
    });
    scrim.addEventListener('click', closeMenu);
    backTop.addEventListener('click', () => window.scrollTo({ top: 0, behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' }));
    document.querySelectorAll('.image-button').forEach(button => button.addEventListener('click', () => {
        const image = button.querySelector('img'); lightboxImage.src = image.src; lightboxImage.alt = image.alt; lightbox.showModal();
    }));
    lightbox.querySelector('.lightbox-close').addEventListener('click', () => lightbox.close());
    lightbox.addEventListener('click', event => { if (event.target === lightbox) lightbox.close(); });
    addEventListener('keydown', event => { if (event.key === 'Escape') closeMenu(); });

    // ---- Q&A: the model answer opens only after the reader writes something.
    const store = (() => { try { return localStorage; } catch (_) { return null; } })();
    document.querySelectorAll('.qa').forEach(box => {
        const input = box.querySelector('.qa-input');
        const answer = box.querySelector('.qa-answer');
        const mine = box.querySelector('.qa-mine');
        const hint = box.querySelector('.qa-hint');
        const button = box.querySelector('.qa-submit');
        const reset = box.querySelector('.qa-reset');
        const key = 'part4-qa:' + box.id;
        function reveal(text) {
            mine.textContent = text;
            answer.hidden = false;
            box.classList.add('is-answered');
            input.disabled = true;
            if (store) store.setItem(key, text);
        }
        function submit() {
            const text = input.value.trim();
            if (text.length < 2) {
                hint.textContent = '답을 먼저 적어야 해설이 열립니다. 짧아도 괜찮습니다.';
                box.classList.remove('shake'); void box.offsetWidth; box.classList.add('shake');
                input.focus();
                return;
            }
            reveal(text);
        }
        input.addEventListener('keydown', event => {
            if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); submit(); }
        });
        if (button) button.addEventListener('click', submit);
        if (reset) reset.addEventListener('click', () => {
            answer.hidden = true; box.classList.remove('is-answered'); input.disabled = false; input.value = ''; input.focus();
            if (store) store.removeItem(key);
        });
        const saved = store && store.getItem(key);
        if (saved) { input.value = saved; reveal(saved); }
    });

    // ---- copy buttons on prompt blocks
    document.querySelectorAll('pre.prompt').forEach(pre => {
        const btn = document.createElement('button');
        btn.type = 'button'; btn.className = 'copy-button'; btn.textContent = '복사';
        btn.addEventListener('click', async () => {
            const text = pre.querySelector('code').innerText;
            try { await navigator.clipboard.writeText(text); btn.textContent = '복사됨'; }
            catch (_) { btn.textContent = '복사 실패'; }
            setTimeout(() => { btn.textContent = '복사'; }, 1600);
        });
        pre.appendChild(btn);
    });

    // ---- clickable checklists (state kept per page + position)
    document.querySelectorAll('.page').forEach(page => {
        const lists = page.querySelectorAll('ul.check-list:not(.forbid)');
        lists.forEach((list, li) => {
            list.querySelectorAll('li').forEach((item, ii) => {
                const key = `part4-check:${page.id}:${li}:${ii}`;
                item.tabIndex = 0; item.setAttribute('role', 'checkbox');
                const set = on => { item.classList.toggle('is-done', on); item.setAttribute('aria-checked', String(on)); if (store) { on ? store.setItem(key, '1') : store.removeItem(key); } updateCounter(page); };
                item.addEventListener('click', () => set(!item.classList.contains('is-done')));
                item.addEventListener('keydown', e => { if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); set(!item.classList.contains('is-done')); } });
                if (store && store.getItem(key)) set(true);
            });
        });
        updateCounter(page);
    });
    function updateCounter(page) {
        const items = page.querySelectorAll('ul.check-list:not(.forbid) li');
        if (!items.length) return;
        let badge = page.querySelector('.check-counter');
        if (!badge) { badge = document.createElement('span'); badge.className = 'check-counter'; page.querySelector('.hero-meta').appendChild(badge); }
        const done = [...items].filter(i => i.classList.contains('is-done')).length;
        badge.textContent = `확인 ${done}/${items.length}`;
        badge.classList.toggle('is-complete', done === items.length);
    }

    // ---- drills: pick one option per item, reveal verdict
    document.querySelectorAll('.drill').forEach(drill => {
        const items = drill.querySelectorAll('.drill-item');
        const score = drill.querySelector('.drill-score');
        function tally() {
            if (!score) return;
            const answered = [...items].filter(i => i.dataset.state).length;
            const right = [...items].filter(i => i.dataset.state === 'right').length;
            score.textContent = answered ? `${items.length}개 중 ${answered}개 답함 · ${right}개 맞음` : '';
        }
        items.forEach(item => {
            const answer = item.dataset.answer;
            item.querySelectorAll('.drill-opt').forEach(btn => btn.addEventListener('click', () => {
                if (item.dataset.state) return;
                const ok = btn.dataset.value === answer;
                item.dataset.state = ok ? 'right' : 'wrong';
                btn.classList.add(ok ? 'is-right' : 'is-wrong');
                item.querySelectorAll('.drill-opt').forEach(b => { b.disabled = true; if (b.dataset.value === answer) b.classList.add('is-answer'); });
                item.querySelector('.drill-why').hidden = false;
                tally();
            }));
        });
        const reset = drill.querySelector('.drill-reset');
        if (reset) reset.addEventListener('click', () => {
            items.forEach(item => { delete item.dataset.state; item.querySelectorAll('.drill-opt').forEach(b => { b.disabled = false; b.className = 'drill-opt'; }); item.querySelector('.drill-why').hidden = true; });
            tally();
        });
    });

    // ---- rater: 5 criteria -> verdict (chapter 01)
    document.querySelectorAll('.rater').forEach(rater => {
        const rows = rater.querySelectorAll('.rater-row');
        const out = rater.querySelector('.rater-out');
        const val = { '상': 2, '중': 1, '하': 0 };
        function update() {
            const picks = [...rows].map(r => r.querySelector('.is-picked')?.dataset.value);
            if (picks.some(p => !p)) { out.textContent = '다섯 기준을 모두 고르면 판정이 나옵니다.'; out.className = 'rater-out'; return; }
            const human = picks[4];
            let plus = picks.slice(0, 4).reduce((a, p) => a + val[p], 0);
            let text, cls;
            if (human === '상') { text = '연구자 판단으로 남깁니다. 절차 중간에 매번 가치 판단이 들어가면 입력을 반복할 수 없고 결과를 대조할 기준도 흔들립니다.'; cls = 'is-no'; }
            else if (plus >= 7 && human === '하') { text = 'Skill 후보 1순위감입니다. 입력·출력이 안정적이고 검증 기준이 있습니다. 02장으로 바로 갈 수 있습니다.'; cls = 'is-yes'; }
            else if (plus >= 5) { text = 'Skill 후보지만 설계가 더 필요합니다. "중"으로 고른 기준(특히 입력 안정성·검증 가능성)에서 입력 게이트와 중지 조건을 더 자세히 적어야 합니다.'; cls = 'is-maybe'; }
            else { text = '아직 Skill로 만들기 어렵습니다. 업무 이름이 넓어서 여러 일이 섞여 있지 않은지 먼저 봅니다. 쪼개면 일부는 1순위가 될 수 있습니다.'; cls = 'is-no'; }
            out.textContent = text; out.className = 'rater-out ' + cls;
        }
        rows.forEach(row => row.querySelectorAll('.rater-opt').forEach(btn => btn.addEventListener('click', () => {
            row.querySelectorAll('.rater-opt').forEach(b => b.classList.remove('is-picked'));
            btn.classList.add('is-picked'); update();
        })));
        update();
    });

    route({ initial: true });
})();
