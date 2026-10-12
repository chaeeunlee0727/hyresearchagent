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

    route({ initial: true });
})();
