
        document.addEventListener('DOMContentLoaded', () => {


            // ===== DETECT TOUCH DEVICE =====
            // Disable heavy desktop effects on touch/coarse-pointer devices
            const isTouch = window.matchMedia('(pointer: coarse)').matches ||
                            ('ontouchstart' in window) ||
                            (navigator.maxTouchPoints > 0);

            // Detect high-refresh-rate screen (90/120 Hz)
            // We pass this to JS animations so they can scale timing
            let deviceFPS = 60;
            (function detectFPS() {
                let last = 0, count = 0;
                function tick(ts) {
                    if (last) count++;
                    if (ts - last < 1000) { requestAnimationFrame(tick); }
                    else { deviceFPS = Math.min(Math.round(count / ((ts - last) / 1000)), 120); }
                    last = ts;
                }
                requestAnimationFrame(tick);
            })();

            // ===== SCROLL PROGRESS BAR — rAF throttled =====
            const progressBar = document.getElementById('scroll-progress');
            let _scrollRAF = null;
            window.addEventListener('scroll', () => {
                if (_scrollRAF) return;
                _scrollRAF = requestAnimationFrame(() => {
                    const scrollTop = window.scrollY;
                    const docHeight = document.documentElement.scrollHeight - window.innerHeight;
                    const pct = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
                    progressBar.style.width = pct + '%';
                    _scrollRAF = null;
                });
            }, { passive: true });

            // ===== CURSOR SPOTLIGHT — disabled on touch =====
            const spotlight = document.getElementById('cursor-spotlight');
            if (isTouch) {
                if (spotlight) spotlight.style.display = 'none';
            } else {
                let _spotX = 0, _spotY = 0, _spotRAF = false;
                document.addEventListener('mousemove', e => {
                    _spotX = e.clientX; _spotY = e.clientY;
                    if (!_spotRAF) {
                        _spotRAF = true;
                        requestAnimationFrame(() => {
                            spotlight.style.left = _spotX + 'px';
                            spotlight.style.top  = _spotY + 'px';
                            _spotRAF = false;
                        });
                    }
                });
            }

            // ===== TYPEWRITER EFFECT =====
            const words = ['Voice Clones', 'Deepfake Images', 'AI-Written Text', 'Synthetic Videos', 'Fake Profiles', 'AI Audio'];
            let wIdx = 0, cIdx = 0, deleting = false;
            const twEl = document.getElementById('typewriter-word');
            function typeLoop() {
                const current = words[wIdx];
                if (!deleting) {
                    twEl.textContent = current.substring(0, cIdx + 1);
                    cIdx++;
                    if (cIdx === current.length) { deleting = true; setTimeout(typeLoop, 1800); return; }
                } else {
                    twEl.textContent = current.substring(0, cIdx - 1);
                    cIdx--;
                    if (cIdx === 0) { deleting = false; wIdx = (wIdx + 1) % words.length; }
                }
                setTimeout(typeLoop, deleting ? 60 : 100);
            }
            typeLoop();

            // ===== HERO LIVE COUNTERS =====
            function animateHeroCounter(el, target, suffix, duration) {
                let start = 0, startTime = null;
                function step(ts) {
                    if (!startTime) startTime = ts;
                    const prog = Math.min((ts - startTime) / duration, 1);
                    const ease = 1 - Math.pow(1 - prog, 3);
                    const val = Math.floor(ease * target);
                    el.textContent = val.toLocaleString() + suffix;
                    if (prog < 1) requestAnimationFrame(step);
                }
                requestAnimationFrame(step);
            }
            let heroCountersDone = false;
            const heroObserver = new IntersectionObserver(entries => {
                if (entries[0].isIntersecting && !heroCountersDone) {
                    heroCountersDone = true;
                    animateHeroCounter(document.getElementById('hc-detections'), 47392841, '', 2500);
                    setTimeout(() => { document.getElementById('hc-accuracy').textContent = '99.2%'; }, 1200);
                    animateHeroCounter(document.getElementById('hc-users'), 128400, '', 2200);
                    animateHeroCounter(document.getElementById('hc-countries'), 47, '+', 1800);
                }
            }, { threshold: 0.3 });
            heroObserver.observe(document.querySelector('.hero-counter-strip'));

            // Tick the detection counter up every 3s to feel live
            setInterval(() => {
                const el = document.getElementById('hc-detections');
                if (heroCountersDone && el) {
                    const cur = parseInt(el.textContent.replace(/,/g,'')) || 47392841;
                    el.textContent = (cur + Math.floor(Math.random() * 5 + 1)).toLocaleString();
                }
            }, 3000);

            // ===== TRUST SCORE GAUGE =====
            const trustSection = document.querySelector('.trust-section');
            let trustDone = false;
            const trustObs = new IntersectionObserver(entries => {
                if (entries[0].isIntersecting && !trustDone) {
                    trustDone = true;
                    // Animate gauge (circumference = 2π*90 ≈ 565)
                    const circumference = 565;
                    const pct = 98.5;
                    const offset = circumference - (pct / 100) * circumference;
                    const gaugeFill = document.getElementById('gauge-fill');
                    const gaugePercent = document.getElementById('gauge-percent');
                    gaugeFill.style.strokeDashoffset = offset;
                    // Animate number
                    let g = 0, gTimer = setInterval(() => {
                        g += 2;
                        if (g >= pct) { g = pct; clearInterval(gTimer); }
                        gaugePercent.textContent = g.toFixed(1) + '%';
                    }, 40);
                    // Animate bars
                    document.querySelectorAll('.trust-bar-fill').forEach(bar => {
                        const w = bar.dataset.width;
                        setTimeout(() => { bar.style.width = w + '%'; }, 300);
                    });
                }
            }, { threshold: 0.3 });
            if (trustSection) trustObs.observe(trustSection);

            // ===== FAQ LIVE SEARCH =====
            const faqSearch = document.getElementById('faq-search');
            const faqNoResults = document.getElementById('faq-no-results');
            if (faqSearch) {
                faqSearch.addEventListener('input', () => {
                    const q = faqSearch.value.toLowerCase().trim();
                    let visible = 0;
                    document.querySelectorAll('.faq-item').forEach(item => {
                        const text = item.textContent.toLowerCase();
                        const match = !q || text.includes(q);
                        item.classList.toggle('hidden', !match);
                        if (match) visible++;
                    });
                    faqNoResults.style.display = visible === 0 ? 'block' : 'none';
                });
            }

            // ===== CONFETTI =====
            window.launchConfetti = function() {
                const canvas = document.getElementById('confetti-canvas');
                const ctx2 = canvas.getContext('2d');
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
                const pieces = Array.from({ length: 120 }, () => ({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height - canvas.height,
                    r: Math.random() * 6 + 4,
                    d: Math.random() * 120 + 80,
                    color: ['#06b6d4','#8b5cf6','#10b981','#f59e0b','#f43f5e'][Math.floor(Math.random()*5)],
                    tilt: Math.random() * 10 - 5,
                    tiltSpeed: Math.random() * 0.07 + 0.05,
                    angle: 0
                }));
                let frame = 0, done = false;
                function drawConfetti() {
                    ctx2.clearRect(0, 0, canvas.width, canvas.height);
                    pieces.forEach(p => {
                        p.angle += p.tiltSpeed;
                        p.y += Math.cos(p.d + frame) + 2;
                        p.x += Math.sin(frame / 4) * 0.6;
                        p.tilt = Math.sin(p.angle) * 12;
                        ctx2.beginPath();
                        ctx2.lineWidth = p.r / 2;
                        ctx2.strokeStyle = p.color;
                        ctx2.moveTo(p.x + p.tilt + p.r / 4, p.y);
                        ctx2.lineTo(p.x + p.tilt, p.y + p.tilt + p.r / 4);
                        ctx2.stroke();
                    });
                    frame++;
                    if (frame < 180) requestAnimationFrame(drawConfetti);
                    else { ctx2.clearRect(0, 0, canvas.width, canvas.height); }
                }
                drawConfetti();
            };

            // ===== ACTIVITY TOAST FEED =====
            const activityToast = document.getElementById('activity-toast');
            const activityMain = document.getElementById('activity-toast-main');
            const activitySub = document.getElementById('activity-toast-sub');
            const activityIcons = ['🌍','🌎','🌏'];
            const countries = ['🇺🇸','🇬🇧','🇮🇳','🇩🇪','🇧🇷','🇯🇵','🇰🇷','🇫🇷','🇦🇺','🇨🇦'];
            const detectionTypes = ['AI Voice Clone Detected','Deepfake Image Caught','ChatGPT Essay Flagged','MidJourney Image Found','Synthetic Profile Blocked','AI Video Intercepted'];
            function showActivityToast() {
                const type = detectionTypes[Math.floor(Math.random() * detectionTypes.length)];
                const flag = countries[Math.floor(Math.random() * countries.length)];
                const icon = activityIcons[Math.floor(Math.random() * activityIcons.length)];
                document.querySelector('.activity-toast-icon').textContent = icon;
                activityMain.textContent = type;
                activitySub.textContent = `User from ${flag} · just now`;
                activityToast.classList.add('show');
                setTimeout(() => activityToast.classList.remove('show'), 4000);
            }
            setTimeout(() => { showActivityToast(); setInterval(showActivityToast, 9000); }, 5000);



            // Tilt Cards — disabled on touch, rAF-throttled on desktop
            if (!isTouch) {
                document.querySelectorAll('.tilt-card').forEach(card => {
                    let _tiltRAF = false;
                    let _tx = 0, _ty = 0;
                    card.addEventListener('mousemove', (e) => {
                        const rect = card.getBoundingClientRect();
                        _tx = e.clientX - rect.left;
                        _ty = e.clientY - rect.top;
                        if (!_tiltRAF) {
                            _tiltRAF = true;
                            requestAnimationFrame(() => {
                                const rect2 = card.getBoundingClientRect();
                                const rotateX = ((_ty - rect2.height/2) / (rect2.height/2)) * -12;
                                const rotateY = ((_tx - rect2.width/2)  / (rect2.width/2))  *  12;
                                card.style.transform = `translateY(-8px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
                                const glare = card.querySelector('.card-glare');
                                if (glare) glare.style.background = `radial-gradient(circle at ${_tx}px ${_ty}px, rgba(255,255,255,0.13), transparent 60%)`;
                                _tiltRAF = false;
                            });
                        }
                    });
                    card.addEventListener('mouseleave', () => {
                        card.style.transform = 'translateY(0) rotateX(0) rotateY(0)';
                        const glare = card.querySelector('.card-glare');
                        if (glare) { glare.style.background = 'radial-gradient(circle at 50% 50%, rgba(255,255,255,0.13), transparent 60%)'; glare.style.opacity = '0'; }
                    });
                    card.addEventListener('mouseenter', () => {
                        const glare = card.querySelector('.card-glare');
                        if (glare) glare.style.opacity = '1';
                    });
                });
            }

            // Scroll Reveal
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) { entry.target.classList.add('visible'); observer.unobserve(entry.target); }
                });
            }, { threshold: 0.15 });
            document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

            // Animated Counters — rAF-based, no setInterval
            const counterObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const el = entry.target;
                        const target = parseInt(el.dataset.target);
                        const suffix = target === 99 ? '%' : target === 6 ? '+' : '';
                        let startTs = null;
                        const duration = 1400; // ms
                        function step(ts) {
                            if (!startTs) startTs = ts;
                            const progress = Math.min((ts - startTs) / duration, 1);
                            const ease = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
                            el.textContent = Math.floor(ease * target) + suffix;
                            if (progress < 1) requestAnimationFrame(step);
                            else el.textContent = target + suffix;
                        }
                        requestAnimationFrame(step);
                        counterObserver.unobserve(el);
                    }
                });
            }, { threshold: 0.5 });
            document.querySelectorAll('.stat-number[data-target]').forEach(el => counterObserver.observe(el));

            // Navbar scroll effect — rAF throttled
            let _navRAF = null;
            window.addEventListener('scroll', () => {
                if (_navRAF) return;
                _navRAF = requestAnimationFrame(() => {
                    document.getElementById('navbar').classList.toggle('scrolled', window.scrollY > 50);
                    document.getElementById('back-to-top').classList.toggle('show', window.scrollY > 400);
                    _navRAF = null;
                });
            }, { passive: true });

            // Back to top
            document.getElementById('back-to-top').addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

            // FAQ Accordion
            document.querySelectorAll('.faq-question').forEach(btn => {
                btn.addEventListener('click', () => {
                    const item = btn.parentElement;
                    const isOpen = item.classList.contains('open');
                    document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
                    if (!isOpen) item.classList.add('open');
                });
            });

            // Newsletter Form with confetti
            document.getElementById('newsletter-form').addEventListener('submit', (e) => {
                e.preventDefault();
                showToast('success', '🎉 Thanks for subscribing! You\'ll receive updates soon.');
                if (window.launchConfetti) window.launchConfetti();
                e.target.reset();
            });

            // Hall of Fakes Feed Logic
            const feedContainer = document.getElementById('live-feed');
            const fakeTypes = ['Deepfake Video', 'AI Voice Clone', 'ChatGPT Essay', 'MidJourney Image', 'Synthetic Profile Pic'];
            const fakeSources = ['Twitter', 'Reddit', 'News Site', 'Dating App', 'University Portal'];
            
            function createFeedItem() {
                const type = fakeTypes[Math.floor(Math.random() * fakeTypes.length)];
                const source = fakeSources[Math.floor(Math.random() * fakeSources.length)];
                const confidence = (85 + Math.random() * 14.9).toFixed(1);
                
                const item = document.createElement('div');
                item.style.padding = '14px 20px';
                item.style.background = 'rgba(239, 68, 68, 0.05)';
                item.style.border = '1px solid rgba(239, 68, 68, 0.2)';
                item.style.borderLeft = '4px solid #ef4444';
                item.style.borderRadius = '8px';
                item.style.display = 'flex';
                item.style.justifyContent = 'space-between';
                item.style.alignItems = 'center';
                
                item.innerHTML = `
                    <div>
                        <div style="font-weight: 600; font-size: 14px; color: var(--text-primary); margin-bottom: 4px;">
                            <i class="fa-solid fa-triangle-exclamation" style="color: #ef4444; margin-right: 6px;"></i> ${type} Detected
                        </div>
                        <div style="font-size: 12px; color: var(--text-secondary);">Source: ${source} • Just now</div>
                    </div>
                    <div style="text-align: right;">
                        <div style="color: #ef4444; font-weight: 700; font-size: 15px;">${confidence}% AI</div>
                        <div style="font-size: 11px; color: var(--text-secondary); text-transform: uppercase;">Confidence</div>
                    </div>
                `;
                return item;
            }

            // Initialize feed
            for(let i=0; i<6; i++) feedContainer.appendChild(createFeedItem());
            
            // Auto scroll and add new
            setInterval(() => {
                const newItem = createFeedItem();
                newItem.style.opacity = '0';
                newItem.style.transform = 'translateY(-20px)';
                newItem.style.transition = 'all 0.5s ease';
                feedContainer.insertBefore(newItem, feedContainer.firstChild);
                
                // Trigger animation
                setTimeout(() => {
                    newItem.style.opacity = '1';
                    newItem.style.transform = 'translateY(0)';
                }, 50);

                if(feedContainer.children.length > 10) {
                    feedContainer.removeChild(feedContainer.lastChild);
                }
            }, 3000);
            
            // ===== MOBILE SLIDE-OVER DRAWER =====
            const hamburger = document.getElementById('hamburgerMenu');
            const drawer = document.getElementById('mobile-drawer');
            const drawerOverlay = document.getElementById('mobile-drawer-overlay');
            const drawerCloseBtn = document.getElementById('drawer-close-btn');

            function openDrawer() {
                drawerOverlay.style.display = 'block';
                requestAnimationFrame(() => {
                    drawerOverlay.classList.add('open');
                    drawer.classList.add('open');
                });
                document.body.style.overflow = 'hidden'; // prevent scroll behind
            }
            function closeDrawer() {
                drawerOverlay.classList.remove('open');
                drawer.classList.remove('open');
                document.body.style.overflow = '';
                setTimeout(() => { drawerOverlay.style.display = 'none'; }, 400);
                const icon = hamburger?.querySelector('i');
                if (icon) { icon.classList.remove('fa-xmark'); icon.classList.add('fa-bars'); }
            }

            if (hamburger) {
                hamburger.addEventListener('click', () => {
                    if (drawer.classList.contains('open')) { closeDrawer(); }
                    else {
                        openDrawer();
                        const icon = hamburger.querySelector('i');
                        if (icon) { icon.classList.remove('fa-bars'); icon.classList.add('fa-xmark'); }
                    }
                });
            }
            if (drawerCloseBtn) drawerCloseBtn.addEventListener('click', closeDrawer);
            if (drawerOverlay) drawerOverlay.addEventListener('click', closeDrawer);

            // Close drawer on nav link click (smooth scroll)
            document.querySelectorAll('.drawer-nav-item[href^="#"]').forEach(link => {
                link.addEventListener('click', () => {
                    closeDrawer();
                });
            });

            // Swipe right to close gesture
            let _dTouchX = 0;
            if (drawer) {
                drawer.addEventListener('touchstart', e => { _dTouchX = e.touches[0].clientX; }, { passive: true });
                drawer.addEventListener('touchend', e => {
                    if (e.changedTouches[0].clientX - _dTouchX > 60) closeDrawer();
                }, { passive: true });
            }
        });

        // ===== MAGNETIC BUTTONS =====
        document.querySelectorAll('.btn-primary, .btn-secondary, .login-btn').forEach(btn => {
            btn.addEventListener('mousemove', e => {
                const rect = btn.getBoundingClientRect();
                const x = e.clientX - rect.left - rect.width / 2;
                const y = e.clientY - rect.top - rect.height / 2;
                btn.style.transform = `translate(${x * 0.25}px, ${y * 0.25}px)`;
            });
            btn.addEventListener('mouseleave', () => {
                btn.style.transform = '';
                btn.style.transition = 'transform 0.4s cubic-bezier(0.16,1,0.3,1)';
                setTimeout(() => btn.style.transition = '', 400);
            });
        });

        // ===== TEXT SCRAMBLE =====
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%';
        function scrambleText(el, finalText, duration = 1200) {
            let frame = 0, totalFrames = Math.ceil(duration / 16);
            const timer = setInterval(() => {
                const progress = frame / totalFrames;
                el.textContent = finalText.split('').map((c, i) => {
                    if (c === ' ') return ' ';
                    if (i / finalText.length < progress) return c;
                    return chars[Math.floor(Math.random() * chars.length)];
                }).join('');
                frame++;
                if (frame > totalFrames) { el.textContent = finalText; clearInterval(timer); }
            }, 16);
        }
        // Trigger scramble on section headings when they enter viewport
        const scrambleObs = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    const orig = el.dataset.original || el.textContent;
                    el.dataset.original = orig;
                    scrambleText(el, orig);
                    scrambleObs.unobserve(el);
                }
            });
        }, { threshold: 0.5 });
        document.querySelectorAll('.section-title').forEach(el => {
            el.dataset.original = el.textContent;
            scrambleObs.observe(el);
        });

        // ===== HOLOGRAPHIC SHEEN =====
        document.querySelectorAll('.nav-card').forEach(card => {
            if (!card.querySelector('.holo-sheen')) {
                const sheen = document.createElement('div');
                sheen.className = 'holo-sheen';
                card.appendChild(sheen);
            }
        });

        // ===== NEON GLOW ON REVEAL =====
        const neonObserver = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('neon-glow-enter');
                    neonObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });
        document.querySelectorAll('.feature-card, .testimonial-card, .step-card, .timeline-content').forEach(el => neonObserver.observe(el));

        // ===== DEMO SLIDER =====
        const demoSlider = document.getElementById('demo-slider');
        const sliderHandle = document.getElementById('slider-handle');
        const sliderClip = document.getElementById('slider-clip');
        if (demoSlider && sliderHandle && sliderClip) {
            let dragging = false;
            function setSlider(x) {
                const rect = demoSlider.getBoundingClientRect();
                let pct = Math.max(5, Math.min(95, ((x - rect.left) / rect.width) * 100));
                sliderHandle.style.left = pct + '%';
                sliderClip.style.width = pct + '%';
            }
            sliderHandle.addEventListener('mousedown', e => { dragging = true; e.preventDefault(); });
            demoSlider.addEventListener('touchstart', e => { dragging = true; }, { passive: true });
            document.addEventListener('mousemove', e => { if (dragging) setSlider(e.clientX); });
            document.addEventListener('touchmove', e => { if (dragging && e.touches[0]) setSlider(e.touches[0].clientX); }, { passive: true });
            document.addEventListener('mouseup', () => dragging = false);
            document.addEventListener('touchend', () => dragging = false);
            demoSlider.addEventListener('click', e => setSlider(e.clientX));
            // Init at 50%
            sliderClip.style.width = '50%';
        }

        // ===== TRY IT LIVE =====
        const tryBtn = document.getElementById('try-btn');
        const tryTextarea = document.getElementById('try-textarea');
        if (tryBtn && tryTextarea) {
            tryBtn.addEventListener('click', () => {
                const text = tryTextarea.value.trim();
                if (!text || text.length < 20) {
                    showToast('info', 'Please enter at least 20 characters to analyze.');
                    return;
                }
                tryBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';
                tryBtn.disabled = true;
                setTimeout(() => {
                    // Heuristic mock scoring
                    const aiWords = ['utilize','leverage','furthermore','moreover','facilitate','optimal','comprehensive','implement','ensure','paradigm'];
                    const lower = text.toLowerCase();
                    const matches = aiWords.filter(w => lower.includes(w)).length;
                    const baseScore = Math.min(95, 30 + matches * 10 + (text.length > 200 ? 10 : 0));
                    const score = baseScore + Math.floor(Math.random() * 8 - 4);
                    const clipped = Math.max(5, Math.min(98, score));
                    const bar = document.getElementById('try-bar');
                    const scoreEl = document.getElementById('try-score-val');
                    const verdict = document.getElementById('try-verdict');
                    const result = document.getElementById('try-result');
                    bar.style.background = clipped > 60 ? 'linear-gradient(90deg,#f59e0b,#ef4444)' : 'linear-gradient(90deg,#10b981,#06b6d4)';
                    scoreEl.style.color = clipped > 60 ? '#ef4444' : '#10b981';
                    scoreEl.textContent = clipped + '%';
                    verdict.textContent = clipped > 75 ? '⚠️ High probability of AI-generated content. Patterns suggest structured, low-variation writing typical of LLMs like ChatGPT or Claude.'
                        : clipped > 45 ? '⚡ Mixed signals detected. The text shows some AI-like patterns but also natural human variation. Manual review recommended.'
                        : '✅ Likely human-written. The text exhibits natural perplexity, burstiness, and organic sentence variation.';
                    result.classList.add('show');
                    setTimeout(() => { bar.style.width = clipped + '%'; }, 50);
                    tryBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Analyze Now';
                    tryBtn.disabled = false;
                }, 1800);
            });
        }

        // ===== COOKIE BANNER =====
        if (!localStorage.getItem('cookie_consent')) {
            setTimeout(() => document.getElementById('cookie-banner').classList.add('show'), 2500);
        }
        document.getElementById('cookie-accept').addEventListener('click', () => {
            localStorage.setItem('cookie_consent', 'accepted');
            document.getElementById('cookie-banner').classList.remove('show');
            showToast('success', '🍪 Preferences saved. Thank you!');
        });
        document.getElementById('cookie-decline').addEventListener('click', () => {
            localStorage.setItem('cookie_consent', 'declined');
            document.getElementById('cookie-banner').classList.remove('show');
        });

        // ===== MILESTONE POPUP =====
        const milestones = [47400000, 47500000, 47600000, 50000000];
        const milestoneLabels = ['🎯 47.4M threats blocked!', '🔥 47.5M detections reached!', '⚡ 47.6M scans complete!', '🏆 50 Million milestone!'];
        let milestoneFired = new Set();
        function checkMilestone(count) {
            milestones.forEach((m, i) => {
                if (count >= m && !milestoneFired.has(m)) {
                    milestoneFired.add(m);
                    const popup = document.getElementById('milestone-popup');
                    document.getElementById('milestone-text').textContent = milestoneLabels[i];
                    popup.classList.add('show');
                    if(window.launchConfetti) window.launchConfetti();
                    setTimeout(() => popup.classList.remove('show'), 4000);
                }
            });
        }

        // ===== KEYBOARD SHORTCUTS =====
        const shortcutsModal = document.getElementById('shortcuts-modal');
        document.addEventListener('keydown', e => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
            const key = e.key.toLowerCase();
            if (key === '?' || (e.key === '/' && e.shiftKey)) {
                shortcutsModal.classList.toggle('show'); return;
            }
            if (key === 'escape') { shortcutsModal.classList.remove('show'); document.getElementById('chat-panel').classList.remove('show'); document.getElementById('ctx-menu').classList.remove('show'); return; }
            if (key === 'v') { window.location.href = 'voice-ui/index.html'; }
            if (key === 'i') { window.location.href = 'deepfake-ui/index.html'; }
            if (key === 't') { window.location.href = 'text-ui/index.html'; }
            if (key === 'w') { window.location.href = 'video-ui/index.html'; }
            if (key === 'd') { window.location.href = 'dashboard-ui/index.html'; }
            if (key === 'm') { 
                const tt = document.querySelector('.theme-toggle');
                if (tt) tt.click(); 
            }
            if (e.key === 'Home') { window.scrollTo({ top: 0, behavior: 'smooth' }); }
        });
        shortcutsModal.addEventListener('click', e => { if(e.target === shortcutsModal) shortcutsModal.classList.remove('show'); });


        // ===== CUSTOM CONTEXT MENU =====
        const ctxMenu = document.getElementById('ctx-menu');
        document.addEventListener('contextmenu', e => {
            e.preventDefault();
            const x = Math.min(e.clientX, window.innerWidth - 200);
            const y = Math.min(e.clientY, window.innerHeight - 240);
            ctxMenu.style.left = x + 'px';
            ctxMenu.style.top = y + 'px';
            ctxMenu.classList.add('show');
        });
        document.addEventListener('click', () => ctxMenu.classList.remove('show'));
        document.getElementById('ctx-detect').addEventListener('click', () => { document.querySelector('#tools').scrollIntoView({behavior:'smooth'}); });
        document.getElementById('ctx-voice').addEventListener('click', () => { window.location.href = 'voice-ui/index.html'; });
        document.getElementById('ctx-image').addEventListener('click', () => { window.location.href = 'deepfake-ui/index.html'; });
        document.getElementById('ctx-dashboard').addEventListener('click', () => { window.location.href = 'dashboard-ui/index.html'; });
        document.getElementById('ctx-shortcuts').addEventListener('click', () => shortcutsModal.classList.add('show'));
        document.getElementById('ctx-top').addEventListener('click', () => window.scrollTo({top:0,behavior:'smooth'}));

        // ===== PAGE TRANSITIONS =====
        const transitionEl = document.getElementById('page-transition');
        document.querySelectorAll('a[href]:not([href^="#"]):not([href^="http"]):not([href^="mailto"])').forEach(link => {
            link.addEventListener('click', e => {
                const href = link.getAttribute('href');
                if (!href || href.startsWith('#')) return;
                e.preventDefault();
                transitionEl.classList.add('active');
                setTimeout(() => { window.location.href = href; }, 300);
            });
        });

        // ===== CUSTOM CURSOR — rAF-driven, disabled on touch =====
        const cursor = document.getElementById('custom-cursor');
        if (isTouch) {
            // On touch devices: hide custom cursor, restore system cursor
            if (cursor) cursor.style.display = 'none';
            // Remove the global cursor:none rule that was injected via CSS
            const styleEl = document.createElement('style');
            styleEl.textContent = '*, *::before, *::after { cursor: auto !important; }';
            document.head.appendChild(styleEl);
        } else {
            let _curX = 0, _curY = 0, _curRAF = false;
            let _curFrameCount = 0;
            document.addEventListener('mousemove', e => {
                _curX = e.clientX; _curY = e.clientY;
                if (!_curRAF) {
                    _curRAF = true;
                    requestAnimationFrame(() => {
                        cursor.style.left = _curX + 'px';
                        cursor.style.top  = _curY + 'px';
                        // Spawn trail every 4 frames instead of every 3 mousemoves
                        // (frequency scales naturally with mousemove rate)
                        if (_curFrameCount++ % 4 === 0) {
                            const t = document.createElement('div');
                            t.className = 'cursor-trail';
                            t.style.cssText = `left:${_curX}px;top:${_curY}px`;
                            document.body.appendChild(t);
                            setTimeout(() => t.remove(), 500);
                        }
                        const el = document.elementFromPoint(_curX, _curY);
                        cursor.classList.toggle('hovering',
                            el && (el.tagName === 'A' || el.tagName === 'BUTTON' ||
                                   el.closest('a,button,[data-tip]') !== null));
                        _curRAF = false;
                    });
                }
            });
            document.addEventListener('mousedown', () => cursor.classList.add('clicking'));
            document.addEventListener('mouseup',   () => cursor.classList.remove('clicking'));
            document.addEventListener('mouseleave', () => cursor.style.opacity = '0');
            document.addEventListener('mouseenter', () => cursor.style.opacity = '1');
        }

        // ===== KONAMI CODE EASTER EGG =====
        const konamiCode = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a'];
        let konamiIdx = 0;
        document.addEventListener('keydown', e => {
            if (e.key === konamiCode[konamiIdx]) {
                konamiIdx++;
                if (konamiIdx === konamiCode.length) {
                    konamiIdx = 0;
                    // Rain shields down the screen
                    for (let i = 0; i < 30; i++) {
                        setTimeout(() => {
                            const shield = document.createElement('div');
                            shield.style.cssText = `position:fixed;top:-60px;left:${Math.random()*100}vw;font-size:${24+Math.random()*32}px;z-index:99999;pointer-events:none;animation:burstFly 2s ease-in forwards;--dx:${(Math.random()-0.5)*100}px;--dy:${window.innerHeight+100}px;`;
                            shield.textContent = '🛡️';
                            document.body.appendChild(shield);
                            setTimeout(() => shield.remove(), 2100);
                        }, i * 80);
                    }
                    showToast('success', '🛡️ KONAMI CODE! AuthGuard Mode Activated!');
                    if (window.launchConfetti) window.launchConfetti();
                }
            } else { konamiIdx = 0; }
        });

        // ===== SOUND EFFECTS (Web Audio API) =====
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        let audioCtx = null;
        let soundEnabled = localStorage.getItem('sound_enabled') !== 'false';
        function playSound(type) {
            if (!soundEnabled) return;
            try {
                if (!audioCtx) audioCtx = new AudioCtx();
                const o = audioCtx.createOscillator();
                const g = audioCtx.createGain();
                o.connect(g); g.connect(audioCtx.destination);
                if (type === 'click') { o.frequency.value = 800; g.gain.setValueAtTime(0.05, audioCtx.currentTime); g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.1); }
                else if (type === 'success') { o.frequency.value = 523; o.frequency.setValueAtTime(659, audioCtx.currentTime + 0.1); g.gain.setValueAtTime(0.06, audioCtx.currentTime); g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.3); }
                else if (type === 'error') { o.frequency.value = 220; g.gain.setValueAtTime(0.06, audioCtx.currentTime); g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.2); }
                else if (type === 'hover') { o.frequency.value = 1200; g.gain.setValueAtTime(0.02, audioCtx.currentTime); g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.05); }
                o.start(); o.stop(audioCtx.currentTime + 0.4);
            } catch(e) {}
        }
        document.querySelectorAll('button, a').forEach(el => el.addEventListener('click', () => playSound('click')));
        document.querySelectorAll('.btn-primary, .btn-secondary').forEach(el => el.addEventListener('mouseenter', () => playSound('hover')));

        // ===== ACHIEVEMENTS =====
        const achievementContainer = document.getElementById('achievement-container');
        const unlockedAch = new Set(JSON.parse(localStorage.getItem('achievements') || '[]'));
        const achievements = {
            firstScroll: { icon: '📜', title: 'Achievement Unlocked', name: 'Explorer', sub: 'You scrolled the page!' },
            nightOwl: { icon: '🌙', title: 'Achievement Unlocked', name: 'Night Owl', sub: 'Toggled dark mode' },
            konamiKing: { icon: '🕹️', title: 'Achievement Unlocked', name: 'Konami King', sub: 'Found the Easter egg!' },
        };
        function unlockAchievement(key) {
            if (unlockedAch.has(key)) return;
            unlockedAch.add(key); localStorage.setItem('achievements', JSON.stringify([...unlockedAch]));
            const a = achievements[key]; if (!a) return;
            const popup = document.createElement('div');
            popup.className = 'achievement-popup';
            popup.innerHTML = `<div class="ach-icon">${a.icon}</div><div><div class="ach-title">${a.title}</div><div class="ach-name">${a.name}</div><div class="ach-sub">${a.sub}</div></div>`;
            achievementContainer.appendChild(popup);
            playSound('success');
            requestAnimationFrame(() => { requestAnimationFrame(() => popup.classList.add('show')); });
            setTimeout(() => { popup.classList.remove('show'); setTimeout(() => popup.remove(), 400); }, 4000);
        }
        window.addEventListener('scroll', () => { if (window.scrollY > 100) unlockAchievement('firstScroll'); }, { once: true });

        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => unlockAchievement('nightOwl'));
        }

        // ===== SECTION DOT NAV — rAF throttled =====
        const dotNavItems = document.querySelectorAll('.dot-nav-item');
        const sections = ['body', '#tools', '#about', '#pricing-home', '.quiz-section', '#faq', '#testimonials'];
        let _dotNavRAF = null;
        function updateDotNav() {
            const scrollY = window.scrollY + window.innerHeight / 2;
            sections.forEach((sel, i) => {
                const el = sel === 'body' ? document.body : document.querySelector(sel);
                if (!el) return;
                const top = el === document.body ? 0 : el.getBoundingClientRect().top + window.scrollY;
                const bot = top + (el.offsetHeight || 200);
                dotNavItems[i]?.classList.toggle('active', scrollY >= top && scrollY < bot);
            });
        }
        window.addEventListener('scroll', () => {
            if (_dotNavRAF) return;
            _dotNavRAF = requestAnimationFrame(() => { updateDotNav(); _dotNavRAF = null; });
        }, { passive: true });
        dotNavItems.forEach((dot, i) => {
            dot.addEventListener('click', () => {
                const sel = sections[i];
                const el = sel === 'body' ? document.body : document.querySelector(sel);
                if (el) el.scrollIntoView({ behavior: 'smooth' });
            });
        });

        // ===== BACK TO TOP CIRCLE — rAF throttled =====
        const bttBtn = document.getElementById('back-to-top');
        const bttProgress = document.getElementById('btt-progress');
        const circumference = 2 * Math.PI * 20;
        let _bttRAF = null;
        window.addEventListener('scroll', () => {
            if (_bttRAF) return;
            _bttRAF = requestAnimationFrame(() => {
                const pct = window.scrollY / (document.documentElement.scrollHeight - window.innerHeight);
                bttProgress.style.strokeDashoffset = circumference - pct * circumference;
                bttBtn.classList.toggle('show', window.scrollY > 300);
                _bttRAF = null;
            });
        }, { passive: true });
        bttBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));



        // ===== API DOCS TABS =====
        document.querySelectorAll('.api-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                document.querySelectorAll('.api-tab').forEach(t => t.classList.remove('active'));
                document.querySelectorAll('.api-panel').forEach(p => p.classList.remove('active'));
                tab.classList.add('active');
                document.getElementById('api-' + tab.dataset.tab)?.classList.add('active');
            });
        });
        document.querySelectorAll('.api-copy-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const code = btn.closest('.api-panel').querySelector('pre').innerText;
                navigator.clipboard.writeText(code).then(() => { btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!'; setTimeout(() => btn.innerHTML = '<i class="fa-solid fa-copy"></i> Copy', 2000); });
            });
        });

        // ===== 3D TILT CARDS — rAF-throttled, disabled on touch =====
        if (!isTouch) {
            document.querySelectorAll('.nav-card, .feature-card, .testimonial-card').forEach(card => {
                card.classList.add('tilt-card');
                let _tx = 0.5, _ty = 0.5, _tRaf = false;
                card.addEventListener('mousemove', e => {
                    const r = card.getBoundingClientRect();
                    _tx = (e.clientX - r.left) / r.width - 0.5;
                    _ty = (e.clientY - r.top)  / r.height - 0.5;
                    if (!_tRaf) {
                        _tRaf = true;
                        requestAnimationFrame(() => {
                            card.style.transform = `perspective(700px) rotateY(${_tx * 10}deg) rotateX(${-_ty * 10}deg) translateZ(8px)`;
                            _tRaf = false;
                        });
                    }
                });
                card.addEventListener('mouseleave', () => { card.style.transform = ''; });
            });
        }

        // ===== ANIMATED GRADIENT BORDER on Featured Cards =====
        document.querySelectorAll('.pricing-card.popular, .trust-section').forEach(el => el.classList.add('gradient-border'));

        // ===== DRAG & DROP FILE ZONE =====
        const dragOverlay = document.getElementById('drag-overlay');
        let dragCounter = 0;
        document.addEventListener('dragenter', e => { e.preventDefault(); dragCounter++; dragOverlay.classList.add('show'); });
        document.addEventListener('dragleave', () => { dragCounter--; if (dragCounter <= 0) { dragCounter = 0; dragOverlay.classList.remove('show'); } });
        document.addEventListener('dragover', e => e.preventDefault());
        document.addEventListener('drop', e => {
            e.preventDefault(); dragCounter = 0; dragOverlay.classList.remove('show');
            const file = e.dataTransfer.files[0];
            if (file) {
                showToast('info', `⚡ Scanning ${file.name}...`);
                setTimeout(() => {
                    const isAI = Math.random() > 0.45;
                    showToast(isAI ? 'error' : 'success', isAI ? `🤖 AI content detected in ${file.name} (96.1%)` : `✅ ${file.name} appears authentic (94.7%)`);
                }, 2200);
            }
        });



        // ===== WAVE 5 JS =====
        



        // Magnetic Buttons — disabled on touch, rAF-throttled on desktop
        if (!isTouch) {
            document.querySelectorAll('.btn-primary, .btn-secondary, .nav-links a').forEach(btn => {
                btn.classList.add('magnetic');
                let _mx = 0, _my = 0, _mRaf = false;
                btn.addEventListener('mousemove', e => {
                    const rect = btn.getBoundingClientRect();
                    _mx = e.clientX - rect.left - rect.width / 2;
                    _my = e.clientY - rect.top  - rect.height / 2;
                    if (!_mRaf) {
                        _mRaf = true;
                        requestAnimationFrame(() => {
                            btn.style.transform = `translate(${_mx * 0.18}px, ${_my * 0.18}px)`;
                            _mRaf = false;
                        });
                    }
                });
                btn.addEventListener('mouseleave', () => { btn.style.transform = ''; });
            });

            // Spotlight Cards — disabled on touch
            document.querySelectorAll('.feature-card, .tool-card, .pricing-card').forEach(card => {
                card.classList.add('spotlight-card');
                let _sx = 0, _sy = 0, _sRaf = false;
                card.addEventListener('mousemove', e => {
                    const rect = card.getBoundingClientRect();
                    _sx = e.clientX - rect.left;
                    _sy = e.clientY - rect.top;
                    if (!_sRaf) {
                        _sRaf = true;
                        requestAnimationFrame(() => {
                            card.style.setProperty('--x', `${_sx}px`);
                            card.style.setProperty('--y', `${_sy}px`);
                            _sRaf = false;
                        });
                    }
                });
            });
        }

        // Social Proof Toasts
        const spNames = ['Alex in NY', 'Maria in Madrid', 'Team Alpha', 'User_992', 'SecureCorp'];
        const spActions = ['scanned a video', 'upgraded to Pro', 'intercepted a voice clone', 'completed the IQ Quiz'];
        setInterval(() => {
            if(Math.random() > 0.6) {
                const container = document.getElementById('social-proof-container');
                if(!container) return;
                const t = document.createElement('div');
                t.className = 'social-proof-toast';
                t.innerHTML = `<i class="fa-solid fa-shield-check sp-icon"></i><div><div class="sp-text">${spNames[Math.floor(Math.random()*spNames.length)]} ${spActions[Math.floor(Math.random()*spActions.length)]}</div><div class="sp-time">Just now</div></div>`;
                container.appendChild(t);
                requestAnimationFrame(() => requestAnimationFrame(() => t.classList.add('show')));
                setTimeout(() => { t.classList.remove('show'); setTimeout(() => t.remove(), 400); }, 4000);
            }
        }, 8000);

        // News Sidebar
        document.getElementById('news-toggle')?.addEventListener('click', () => {
            document.getElementById('news-sidebar').classList.toggle('show');
        });




        // ===== TIMELINE ANIMATION =====
        const timelineObs = new IntersectionObserver(entries => {
            entries.forEach((entry, i) => {
                if (entry.isIntersecting) {
                    setTimeout(() => entry.target.classList.add('visible'), i * 150);
                    timelineObs.unobserve(entry.target);
                }
            });
        }, { threshold: 0.3 });
        document.querySelectorAll('.timeline-item').forEach(item => timelineObs.observe(item));

        // ===== RIPPLE EFFECT — disabled on touch (tap already has native feedback) =====
        if (!isTouch) {
            document.addEventListener('click', e => {
                const r = document.createElement('div');
                r.className = 'ripple-circle';
                const size = 80;
                r.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX - size/2}px;top:${e.clientY - size/2}px`;
                document.body.appendChild(r);
                setTimeout(() => r.remove(), 700);
            });
        }


        // ===== LIVE USER COUNT =====
        const liveCountEl = document.getElementById('live-count');
        if (liveCountEl) {
        let liveBase = 1200 + Math.floor(Math.random() * 200);
        setInterval(() => {
            liveBase += Math.floor(Math.random() * 7) - 3;
            liveBase = Math.max(900, Math.min(2000, liveBase));
            liveCountEl.textContent = liveBase.toLocaleString();
        }, 4000);
        }

        // ===== SMART SEARCH =====
        const searchData = [
            { icon: '🎙️', title: 'Voice Detection', sub: 'Detect AI-generated voice clones', url: 'voice-ui/index.html' },
            { icon: '🖼️', title: 'Deepfake Image', sub: 'Detect AI-generated images', url: 'deepfake-ui/index.html' },
            { icon: '📝', title: 'Text Detection', sub: 'Detect ChatGPT / Claude text', url: 'text-ui/index.html' },
            { icon: '🎥', title: 'Video Detection', sub: 'Detect synthetic video content', url: 'video-ui/index.html' },
            { icon: '📄', title: 'Document Scanner', sub: 'Scan PDFs and documents', url: 'document-ui/index.html' },
            { icon: '📱', title: 'Social Media Check', sub: 'Verify social profiles', url: 'social-ui/index.html' },
            { icon: '📊', title: 'Pro Dashboard', sub: 'View your scan history', url: 'dashboard-ui/index.html' },
            { icon: '💰', title: 'Pricing', sub: 'View plans and pricing', url: 'pricing.html' },
            { icon: '🔐', title: 'Login / Sign Up', sub: 'Create or access your account', url: 'login.html' },
            { icon: '❓', title: 'FAQ', sub: 'Frequently asked questions', url: '#faq' },
        ];
        const searchModal = document.getElementById('smart-search-modal');
        const searchInput = document.getElementById('smart-search-input');
        const searchResults = document.getElementById('search-results');
        function renderSearch(query) {
            const q = query.toLowerCase();
            const matches = q ? searchData.filter(d => d.title.toLowerCase().includes(q) || d.sub.toLowerCase().includes(q)) : searchData;
            searchResults.innerHTML = matches.map(d =>
                `<div class="search-result-item" onclick="window.location.href='${d.url}'"><div class="search-result-icon">${d.icon}</div><div><div class="search-result-title">${d.title}</div><div class="search-result-sub">${d.sub}</div></div></div>`
            ).join('') || '<div style="padding:20px;text-align:center;color:var(--text-secondary);font-size:13px">No results found</div>';
        }
        renderSearch('');
        searchInput.addEventListener('input', e => renderSearch(e.target.value));
        document.addEventListener('keydown', e => {
            if ((e.key === '/') && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
                e.preventDefault();
                searchModal.classList.add('show');
                searchInput.focus();
            }
        });
        searchModal.addEventListener('click', e => { if(e.target === searchModal) { searchModal.classList.remove('show'); searchInput.value = ''; renderSearch(''); } });

        // ===== OFFLINE DETECTION =====
        const offlineBanner = document.getElementById('offline-banner');
        window.addEventListener('offline', () => offlineBanner.classList.add('show'));
        window.addEventListener('online', () => { offlineBanner.classList.remove('show'); showToast('success', '✅ Back online!'); });

        // ===== WELCOME BACK ANIMATION =====
        const storedName = localStorage.getItem('user_name');
        if (storedName) {
            const heroP = document.querySelector('.landing-header p');
            if (heroP) {
                const greeting = document.createElement('div');
                greeting.style.cssText = 'font-size:14px;color:var(--accent-cyan);font-weight:600;margin-bottom:8px;animation:slideUpFadeIn 0.8s ease forwards;opacity:0';
                greeting.innerHTML = `👋 Welcome back, <strong>${storedName.split(' ')[0]}</strong>!`;
                heroP.parentNode.insertBefore(greeting, heroP);
            }
        }

        // ===== PRICING TOGGLE =====
        const pricingToggle = document.getElementById('pricing-toggle-sw');
        let isYearly = false;
        if (pricingToggle) {
            pricingToggle.addEventListener('click', () => {
                isYearly = !isYearly;
                pricingToggle.classList.toggle('yearly', isYearly);
                document.getElementById('pt-monthly').classList.toggle('active', !isYearly);
                document.getElementById('pt-yearly').classList.toggle('active', isYearly);
                document.getElementById('price-pro').textContent = isYearly ? '11' : '19';
                document.getElementById('price-ent').textContent = isYearly ? '59' : '99';
                document.getElementById('period-pro').textContent = isYearly ? 'per month, billed yearly' : 'per month';
                document.getElementById('period-ent').textContent = isYearly ? 'per month, billed yearly' : 'per month';
            });
        }

        // ===== VOICE RECORDING DEMO =====
        const voiceBtn = document.getElementById('voice-record-btn');
        const voiceBtnText = document.getElementById('voice-btn-text');
        if (voiceBtn) {
            let recording = false, recTimer = null, secs = 5;
            voiceBtn.addEventListener('click', () => {
                if (recording) return;
                recording = true;
                secs = 5;
                voiceBtn.classList.add('recording');
                voiceBtn.innerHTML = `<div class="voice-bars">${'<div class="voice-bar"></div>'.repeat(5)}</div> <span id="voice-btn-text">Recording... ${secs}s</span>`;
                recTimer = setInterval(() => {
                    secs--;
                    const t = voiceBtn.querySelector('span');
                    if(t) t.textContent = `Recording... ${secs}s`;
                    if (secs <= 0) {
                        clearInterval(recTimer);
                        voiceBtn.classList.remove('recording');
                        voiceBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> <span>Analyzing...</span>';
                        setTimeout(() => {
                            recording = false;
                            const result = Math.random() > 0.5 ? 'Human' : 'AI Voice Clone';
                            const color = result === 'Human' ? '#10b981' : '#ef4444';
                            showToast(result === 'Human' ? 'success' : 'error', `Result: ${result} detected with 98.2% confidence`);
                            voiceBtn.innerHTML = '<i class="fa-solid fa-microphone"></i> <span id="voice-btn-text">Record 5s Demo</span>';
                        }, 1500);
                    }
                }, 1000);
            });
        }

        // ===== SHARE RESULT CARD =====
        const shareModal = document.getElementById('share-modal');
        window.showShareCard = function(score, label) {
            document.getElementById('share-score-display').textContent = score;
            document.getElementById('share-score-label').textContent = label;
            shareModal.classList.add('show');
        };
        document.getElementById('share-close')?.addEventListener('click', () => shareModal.classList.remove('show'));
        document.getElementById('share-twitter')?.addEventListener('click', () => {
            const score = document.getElementById('share-score-display').textContent;
            window.open(`https://twitter.com/intent/tweet?text=I+just+tested+this+text+on+AuthGuard+AI+Detection+and+got+${encodeURIComponent(score)}+AI+probability!+Check+yours+at+https://authguard.vercel.app`, '_blank');
        });
        document.getElementById('share-copy')?.addEventListener('click', () => {
            navigator.clipboard.writeText('https://authguard.vercel.app').then(() => showToast('success', '🔗 Link copied to clipboard!'));
        });
        // Hook into try-it-live
        const origTryBtn = document.getElementById('try-btn');
        if (origTryBtn) {
            const origHandler = origTryBtn.onclick;
            origTryBtn.addEventListener('click', () => {
                setTimeout(() => {
                    const scoreEl = document.getElementById('try-score-val');
                    if (scoreEl && scoreEl.textContent && scoreEl.textContent !== '—') {
                        const shareBtn = document.createElement('button');
                        shareBtn.className = 'try-btn';
                        shareBtn.style.cssText = 'background:rgba(255,255,255,0.05);border:1px solid var(--border-color);margin-left:10px';
                        shareBtn.innerHTML = '<i class="fa-solid fa-share-nodes"></i> Share Result';
                        shareBtn.onclick = () => showShareCard(scoreEl.textContent, 'AI Probability Score');
                        const existing = document.getElementById('share-result-btn');
                        if (!existing) { shareBtn.id = 'share-result-btn'; origTryBtn.parentNode.appendChild(shareBtn); }
                    }
                }, 2500);
            });
        }

        // ===== DETECTION IQ QUIZ =====
        const quizQuestions = [
            { q: 'ChatGPT tends to use which of these patterns more often?', opts: ['Short, choppy sentences with typos', 'Structured paragraphs with smooth transitions', 'All-caps emphasis', 'Excessive punctuation!!!'], ans: 1 },
            { q: 'What is the key telltale sign of an AI voice clone?', opts: ['It speaks too slowly', 'Perfect pitch and zero background noise', 'Heavy accent', 'Too many pauses'], ans: 1 },
            { q: 'Deepfake images often fail on which body part?', opts: ['Elbows', 'Knees', 'Hands and fingers', 'Ears'], ans: 2 },
            { q: 'Which metric do AI text detectors primarily analyze?', opts: ['Word count', 'Perplexity and burstiness', 'Sentence length only', 'Number of adverbs'], ans: 1 },
            { q: 'What is "burstiness" in AI text detection?', opts: ['How often the AI crashes', 'Variation in sentence complexity (humans vary more)', 'The speed of text generation', 'Number of exclamation marks'], ans: 1 },
            { q: 'EXIF metadata in images can help detect fakes because:', opts: ['AI tools always add fake GPS data', 'AI-generated images often have no or inconsistent camera metadata', 'Real photos never have EXIF data', 'EXIF data is encrypted'], ans: 1 },
            { q: 'Which deepfake video technique replaces a person\'s face in video?', opts: ['Neural Style Transfer', 'Face Swap (GAN-based)', 'JPEG Compression', 'Optical Flow'], ans: 1 },
            { q: 'What does "hallucination" mean in AI context?', opts: ['The AI becomes self-aware', 'The AI generates plausible but incorrect facts', 'A display glitch', 'Memory overflow error'], ans: 1 },
            { q: 'ElevenLabs is known for creating:', opts: ['Image deepfakes', 'AI-generated voices', 'Synthetic video', 'Bot social profiles'], ans: 1 },
            { q: 'Which is the MOST reliable way to verify if a voice is real?', opts: ['Ask them to say something random', 'Check frequency analysis and breath patterns', 'Compare to old recordings', 'Both B and C'], ans: 3 }
        ];
        let quizIdx = 0, quizCorrect = 0, quizAnswered = false;
        function startQuiz() {
            quizIdx = 0; quizCorrect = 0; quizAnswered = false;
            document.getElementById('quiz-result-card').classList.remove('show');
            document.getElementById('quiz-content').style.display = 'block';
            loadQuizQ();
        }
        function loadQuizQ() {
            if (quizIdx >= quizQuestions.length) { showQuizResult(); return; }
            const qd = quizQuestions[quizIdx];
            document.getElementById('quiz-q').textContent = `Q${quizIdx+1}. ${qd.q}`;
            document.getElementById('quiz-progress-fill').style.width = ((quizIdx/quizQuestions.length)*100)+'%';
            const optsEl = document.getElementById('quiz-options');
            optsEl.innerHTML = '';
            qd.opts.forEach((opt, i) => {
                const btn = document.createElement('button');
                btn.className = 'quiz-option'; btn.textContent = opt;
                btn.addEventListener('click', () => {
                    if (quizAnswered) return;
                    quizAnswered = true;
                    if (i === qd.ans) { quizCorrect++; btn.classList.add('correct'); }
                    else { btn.classList.add('wrong'); optsEl.children[qd.ans].classList.add('correct'); }
                    setTimeout(() => { quizIdx++; quizAnswered = false; loadQuizQ(); }, 900);
                });
                optsEl.appendChild(btn);
            });
        }
        function showQuizResult() {
            document.getElementById('quiz-content').style.display = 'none';
            document.getElementById('quiz-progress-fill').style.width = '100%';
            const iqScores = [70,85,95,105,112,120,128,135,142,155,165];
            const iq = iqScores[quizCorrect];
            const labels = ['Needs Practice 📚','Getting There 🔍','Average Detector 👀','Good Eye 🎯','Sharp Detector ⚡','Expert Detector 🌟','AI Whisperer 🧠','Detection Master 🏆','Elite Analyst 💎','Supreme Guardian 🛡️','Legendary 🔱'];
            document.getElementById('quiz-iq-num').textContent = iq;
            document.getElementById('quiz-iq-label').textContent = labels[quizCorrect];
            document.getElementById('quiz-iq-sub').textContent = `You got ${quizCorrect}/10 correct. ${quizCorrect >= 8 ? 'Outstanding work! You have elite detection skills.' : quizCorrect >= 5 ? 'Good job! Keep practicing to sharpen your skills.' : 'Keep learning — the AI threat landscape is evolving fast.'}`;
            document.getElementById('quiz-result-card').classList.add('show');
        }
        window.shareQuizResult = function() { showShareCard(document.getElementById('quiz-iq-num').textContent + ' IQ', 'My AuthGuard Detection IQ Score'); };
        startQuiz();

        // ===== DAILY CHALLENGE =====
        const dailyChallenges = [
            { q: 'Which company made ElevenLabs, a popular AI voice tool?', opts: ['Google', 'OpenAI', 'ElevenLabs Inc.', 'Meta'], ans: 2 },
            { q: 'MidJourney is primarily used to generate:', opts: ['AI voices', 'AI images', 'AI text', 'AI video'], ans: 1 },
            { q: 'Which AI model is behind ChatGPT?', opts: ['BERT', 'GPT-4 (OpenAI)', 'LLaMA', 'Gemini'], ans: 1 },
            { q: 'Deepfake videos are primarily created using:', opts: ['Photoshop filters', 'GANs (Generative Adversarial Networks)', 'Video compression', 'CGI rendering'], ans: 1 },
            { q: 'What does "GAN" stand for?', opts: ['General AI Network', 'Generative Adversarial Network', 'Global Artificial Node', 'Graphic Animation Node'], ans: 1 },
            { q: 'Which is NOT an AI text generator?', opts: ['ChatGPT', 'Claude', 'Photoshop', 'Gemini'], ans: 2 },
            { q: 'AI voice clones can be created from as little as how much audio?', opts: ['1 hour', '30 minutes', '3-5 seconds (modern tools)', '24 hours'], ans: 2 }
        ];
        const today = new Date().getDay();
        const todayChallenge = dailyChallenges[today % dailyChallenges.length];
        let dailyAnswered = localStorage.getItem('daily_answered_' + new Date().toDateString());
        document.getElementById('daily-num').textContent = today + 1;
        document.getElementById('daily-q').textContent = todayChallenge.q;
        const dailyOpts = document.getElementById('daily-opts');
        todayChallenge.opts.forEach((opt, i) => {
            const btn = document.createElement('button');
            btn.className = 'daily-option';
            btn.textContent = opt;
            if (dailyAnswered) {
                btn.disabled = true;
                if (i === todayChallenge.ans) btn.classList.add('correct');
            }
            btn.addEventListener('click', () => {
                if (dailyAnswered) return;
                dailyAnswered = 'yes';
                localStorage.setItem('daily_answered_' + new Date().toDateString(), 'yes');
                const streak = parseInt(localStorage.getItem('daily_streak') || '0') + 1;
                localStorage.setItem('daily_streak', streak);
                document.getElementById('streak-count').textContent = streak;
                if (i === todayChallenge.ans) { btn.classList.add('correct'); showToast('success', '🔥 Correct! Streak: ' + streak + ' days'); }
                else { btn.classList.add('wrong'); dailyOpts.children[todayChallenge.ans].classList.add('correct'); showToast('error', '❌ Not quite! Come back tomorrow.'); }
                dailyOpts.querySelectorAll('.daily-option').forEach(b => b.disabled = true);
            });
            dailyOpts.appendChild(btn);
        });
        document.getElementById('streak-count').textContent = localStorage.getItem('daily_streak') || '0';
        // Daily countdown timer
        function updateDailyTimer() {
            const now = new Date(); const midnight = new Date(); midnight.setHours(24,0,0,0);
            const diff = midnight - now;
            const h = String(Math.floor(diff/3600000)).padStart(2,'0');
            const m = String(Math.floor((diff%3600000)/60000)).padStart(2,'0');
            const s = String(Math.floor((diff%60000)/1000)).padStart(2,'0');
            const el = document.getElementById('daily-timer');
            if (el) el.textContent = `${h}:${m}:${s}`;
        }
        setInterval(updateDailyTimer, 1000); updateDailyTimer();

        // ===== MATRIX RAIN — rAF-driven, skips frames on mobile for perf =====
        const matrixCanvas = document.getElementById('matrix-canvas');
        if (matrixCanvas && !isTouch) {
            // Only run on desktop — too expensive on mobile GPU
            const mCtx = matrixCanvas.getContext('2d');
            function resizeMatrix() {
                matrixCanvas.width  = matrixCanvas.offsetWidth;
                matrixCanvas.height = matrixCanvas.offsetHeight;
            }
            resizeMatrix();
            window.addEventListener('resize', resizeMatrix, { passive: true });
            const cols = Math.floor(matrixCanvas.width / 14);
            const drops = Array(cols).fill(1);
            let _matrixLast = 0;
            const MATRIX_INTERVAL = 1000 / 24; // target 24 fps for matrix rain
            function drawMatrix(ts) {
                requestAnimationFrame(drawMatrix);
                if (ts - _matrixLast < MATRIX_INTERVAL) return;
                _matrixLast = ts;
                mCtx.fillStyle = 'rgba(0,0,0,0.05)';
                mCtx.fillRect(0, 0, matrixCanvas.width, matrixCanvas.height);
                mCtx.fillStyle = '#06b6d4';
                mCtx.font = '12px monospace';
                drops.forEach((y, i) => {
                    const char = Math.random() > 0.5 ? '1' : '0';
                    mCtx.fillText(char, i * 14, y * 14);
                    if (y * 14 > matrixCanvas.height && Math.random() > 0.975) drops[i] = 0;
                    drops[i]++;
                });
            }
            requestAnimationFrame(drawMatrix);
        } else if (matrixCanvas && isTouch) {
            // Hide the canvas section on mobile — saves GPU memory
            const matrixSection = matrixCanvas.closest('.matrix-section');
            if (matrixSection) matrixSection.style.display = 'none';
        }

    