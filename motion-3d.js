/**
 * AuthGuard 3D Screen Motion, Scroll Parallax & Gyroscope Engine
 * Provides a clean Infinite 3D Cyber Horizon Wave, ambient nebula dust, and 3D card tilt physics.
 */
(function() {
    'use strict';

    // 1. FULL-VIEWPORT 3D INFINITE CYBER HORIZON & AMBIENT NEBULA ENGINE
    function initGlobal3DSpace() {
        if (typeof THREE === 'undefined') return;

        let canvas = document.getElementById('global-3d-scene-canvas');
        if (!canvas) {
            canvas = document.createElement('canvas');
            canvas.id = 'global-3d-scene-canvas';
            document.body.prepend(canvas);
        }

        const scene = new THREE.Scene();
        // Deep space atmospheric fog for infinite horizon falloff
        scene.fog = new THREE.FogExp2(0x0a0c16, 0.022);

        const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 2, 28);

        const renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            alpha: true,
            antialias: true,
            powerPreference: 'high-performance'
        });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // 1.1 Ambient Glowing Stardust Field (240 micro-particles)
        const particleCount = 240;
        const pGeo = new THREE.BufferGeometry();
        const pPositions = new Float32Array(particleCount * 3);
        const pColors = new Float32Array(particleCount * 3);

        const colorCyan = new THREE.Color(0x06b6d4);
        const colorPurple = new THREE.Color(0x8b5cf6);
        const colorEmerald = new THREE.Color(0x10b981);

        for (let i = 0; i < particleCount; i++) {
            const i3 = i * 3;
            pPositions[i3]     = (Math.random() - 0.5) * 90;
            pPositions[i3 + 1] = (Math.random() - 0.5) * 80;
            pPositions[i3 + 2] = (Math.random() - 0.5) * 60;

            const rand = Math.random();
            const col = rand > 0.6 ? colorCyan : (rand > 0.3 ? colorPurple : colorEmerald);
            pColors[i3]     = col.r;
            pColors[i3 + 1] = col.g;
            pColors[i3 + 2] = col.b;
        }

        pGeo.setAttribute('position', new THREE.BufferAttribute(pPositions, 3));
        pGeo.setAttribute('color', new THREE.BufferAttribute(pColors, 3));

        const pMat = new THREE.PointsMaterial({
            size: 0.18,
            vertexColors: true,
            transparent: true,
            opacity: 0.55,
            blending: THREE.AdditiveBlending
        });
        const starField = new THREE.Points(pGeo, pMat);
        scene.add(starField);

        // 1.2 Infinite 3D Cyber Horizon Wave (Tron / Futuristic Grid Ground)
        const gridCols = 42;
        const gridRows = 42;
        const gridGeo = new THREE.PlaneGeometry(130, 110, gridCols - 1, gridRows - 1);
        gridGeo.rotateX(-Math.PI / 2.15);

        const gridMat = new THREE.MeshBasicMaterial({
            color: 0x06b6d4,
            wireframe: true,
            transparent: true,
            opacity: 0.16
        });
        const gridMesh = new THREE.Mesh(gridGeo, gridMat);
        gridMesh.position.set(0, -15, -12);
        scene.add(gridMesh);

        // Base original position cache for grid wave calculation
        const baseGridPos = gridGeo.attributes.position.array.slice();

        // Mouse & Screen Movement State
        let mouseX = 0;
        let mouseY = 0;
        let targetCamX = 0;
        let targetCamY = 2;
        let currentCamX = 0;
        let currentCamY = 2;

        // Scroll Velocity State
        let lastScrollY = window.scrollY;
        let scrollVelocity = 0;
        let targetScrollWarp = 0;
        let currentScrollWarp = 0;

        // Cursor Movement Listener (Screen Parallax)
        window.addEventListener('mousemove', (e) => {
            mouseX = (e.clientX / window.innerWidth) * 2 - 1;
            mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
            targetCamX = mouseX * 3.5;
            targetCamY = 2 + mouseY * 2.5;
        }, { passive: true });

        // Scroll Movement Listener (3D Screen Warp Flythrough)
        window.addEventListener('scroll', () => {
            const currentScroll = window.scrollY;
            const delta = currentScroll - lastScrollY;
            lastScrollY = currentScroll;
            scrollVelocity = delta * 0.04;
            targetScrollWarp += scrollVelocity;
        }, { passive: true });

        // Mobile Gyroscope / Device Tilt
        if (window.DeviceOrientationEvent) {
            window.addEventListener('deviceorientation', (e) => {
                if (e.gamma !== null && e.beta !== null) {
                    targetCamX = (e.gamma / 45) * 3.5;
                    targetCamY = 2 + ((e.beta - 45) / 45) * 2.5;
                }
            }, { passive: true });
        }

        // Window Resize
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // Main 3D Animation Loop
        let clock = new THREE.Clock();
        function animateSpace() {
            requestAnimationFrame(animateSpace);
            const elapsed = clock.getElapsedTime();

            // Smooth camera lerp towards mouse / gyroscope target
            currentCamX += (targetCamX - currentCamX) * 0.04;
            currentCamY += (targetCamY - currentCamY) * 0.04;
            camera.position.x = currentCamX;
            camera.position.y = currentCamY;
            camera.lookAt(0, -4, 0);

            // Smooth scroll warp decay
            targetScrollWarp *= 0.92;
            currentScrollWarp += (targetScrollWarp - currentScrollWarp) * 0.1;

            // Rotate starfield slowly and shift with scroll
            starField.rotation.y = elapsed * 0.015 + currentCamX * 0.01;
            starField.rotation.x = elapsed * 0.008;

            // Stream particles along Z on screen scroll
            const pos = pGeo.attributes.position.array;
            for (let i = 0; i < particleCount; i++) {
                const i3 = i * 3;
                pos[i3 + 2] += currentScrollWarp * 0.2;
                if (pos[i3 + 2] > 25) pos[i3 + 2] -= 50;
                if (pos[i3 + 2] < -25) pos[i3 + 2] += 50;
            }
            pGeo.attributes.position.needsUpdate = true;

            // Undulating 3D Cyber Horizon Wave Ground
            const gPos = gridGeo.attributes.position.array;
            for (let i = 0; i < gridGeo.attributes.position.count; i++) {
                const i3 = i * 3;
                const bx = baseGridPos[i3];
                const bz = baseGridPos[i3 + 2];
                const wave = Math.sin(bx * 0.10 + elapsed * 1.2) * Math.cos(bz * 0.08 + elapsed * 0.9) * 1.35;
                gPos[i3 + 1] = baseGridPos[i3 + 1] + wave;
            }
            gridGeo.attributes.position.needsUpdate = true;

            renderer.render(scene, camera);
        }
        animateSpace();
    }

    // 2. 3D INTERACTIVE CARD PARALLAX TILT & SPECULAR GLARE
    function init3DCardTilt() {
        const cardSelectors = [
            '.tilt-3d',
            '.feature-card',
            '.step-card',
            '.tool-card',
            '.interactive-arena-card',
            '.threat-map-card',
            '.stat-item',
            '.pricing-card',
            '.hero-3d-card',
            '.info-card',
            '.result-card'
        ];

        const cards = document.querySelectorAll(cardSelectors.join(', '));

        cards.forEach(card => {
            card.classList.add('tilt-3d');

            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                const centerX = rect.width / 2;
                const centerY = rect.height / 2;

                const rotateX = ((y - centerY) / centerY) * -6;
                const rotateY = ((x - centerX) / centerX) * 6;

                card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale3d(1.01, 1.01, 1.01)`;
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
            });
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            initGlobal3DSpace();
            init3DCardTilt();
        });
    } else {
        initGlobal3DSpace();
        init3DCardTilt();
    }
})();
