/**
 * AuthGuard 3D Screen Motion, Scroll Parallax & Gyroscope Engine
 * Provides full-viewport 3D space warp, cursor depth parallax, and 3D card tilt physics.
 */
(function() {
    'use strict';

    // 1. FULL-VIEWPORT 3D WEBGL CYBER SPACE & SCROLL WARP
    function initGlobal3DSpace() {
        if (typeof THREE === 'undefined') return;

        let canvas = document.getElementById('global-3d-scene-canvas');
        if (!canvas) {
            canvas = document.createElement('canvas');
            canvas.id = 'global-3d-scene-canvas';
            document.body.prepend(canvas);
        }

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 30;

        const renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            alpha: true,
            antialias: true,
            powerPreference: 'high-performance'
        });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        // Starfield / Cyber Dust Field (350 floating particles)
        const particleCount = 350;
        const pGeo = new THREE.BufferGeometry();
        const pPositions = new Float32Array(particleCount * 3);
        const pColors = new Float32Array(particleCount * 3);

        const colorCyan = new THREE.Color(0x06b6d4);
        const colorPurple = new THREE.Color(0x8b5cf6);
        const colorEmerald = new THREE.Color(0x10b981);

        for (let i = 0; i < particleCount; i++) {
            const i3 = i * 3;
            pPositions[i3]     = (Math.random() - 0.5) * 80;
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
            size: 0.22,
            vertexColors: true,
            transparent: true,
            opacity: 0.65,
            blending: THREE.AdditiveBlending
        });
        const starField = new THREE.Points(pGeo, pMat);
        scene.add(starField);

        // Floating 3D Geometric Shards (Crystals, Polyhedra)
        const shardsGroup = new THREE.Group();
        scene.add(shardsGroup);

        const shardGeos = [
            new THREE.IcosahedronGeometry(0.7, 0),
            new THREE.OctahedronGeometry(0.6, 0),
            new THREE.TetrahedronGeometry(0.5, 0)
        ];

        const shardMats = [
            new THREE.MeshBasicMaterial({ color: 0x06b6d4, wireframe: true, transparent: true, opacity: 0.25 }),
            new THREE.MeshBasicMaterial({ color: 0x8b5cf6, wireframe: true, transparent: true, opacity: 0.25 }),
            new THREE.MeshBasicMaterial({ color: 0x10b981, wireframe: true, transparent: true, opacity: 0.25 })
        ];

        const shards = [];
        const shardCount = 14;

        for (let i = 0; i < shardCount; i++) {
            const geo = shardGeos[i % shardGeos.length];
            const mat = shardMats[i % shardMats.length];
            const mesh = new THREE.Mesh(geo, mat);

            mesh.position.set(
                (Math.random() - 0.5) * 55,
                (Math.random() - 0.5) * 55,
                (Math.random() - 0.5) * 35
            );

            mesh._rotSpeedX = (Math.random() - 0.5) * 0.015;
            mesh._rotSpeedY = (Math.random() - 0.5) * 0.015;
            mesh._baseY = mesh.position.y;
            mesh._floatOffset = Math.random() * Math.PI * 2;

            shardsGroup.add(mesh);
            shards.push(mesh);
        }

        // Mouse & Screen Movement State
        let mouseX = 0;
        let mouseY = 0;
        let targetCamX = 0;
        let targetCamY = 0;
        let currentCamX = 0;
        let currentCamY = 0;

        // Scroll Velocity State
        let lastScrollY = window.scrollY;
        let scrollVelocity = 0;
        let targetScrollWarp = 0;
        let currentScrollWarp = 0;

        // Cursor Movement Listener (Screen Parallax)
        window.addEventListener('mousemove', (e) => {
            mouseX = (e.clientX / window.innerWidth) * 2 - 1;
            mouseY = -(e.clientY / window.innerHeight) * 2 + 1;
            targetCamX = mouseX * 4.5;
            targetCamY = mouseY * 4.5;
        }, { passive: true });

        // Scroll Movement Listener (3D Screen Warp Flythrough)
        window.addEventListener('scroll', () => {
            const currentScroll = window.scrollY;
            const delta = currentScroll - lastScrollY;
            lastScrollY = currentScroll;
            scrollVelocity = delta * 0.05;
            targetScrollWarp += scrollVelocity;
        }, { passive: true });

        // Mobile Gyroscope / Device Tilt
        if (window.DeviceOrientationEvent) {
            window.addEventListener('deviceorientation', (e) => {
                if (e.gamma !== null && e.beta !== null) {
                    targetCamX = (e.gamma / 45) * 5;
                    targetCamY = ((e.beta - 45) / 45) * 5;
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
            camera.lookAt(0, 0, 0);

            // Smooth scroll warp decay
            targetScrollWarp *= 0.92;
            currentScrollWarp += (targetScrollWarp - currentScrollWarp) * 0.1;

            // Rotate starfield slowly and shift with scroll
            starField.rotation.y = elapsed * 0.02 + currentCamX * 0.01;
            starField.rotation.x = elapsed * 0.01 + currentCamY * 0.01;

            // Stream particles along Z on screen scroll
            const pos = pGeo.attributes.position.array;
            for (let i = 0; i < particleCount; i++) {
                const i3 = i * 3;
                pos[i3 + 2] += currentScrollWarp * 0.2;
                if (pos[i3 + 2] > 25) pos[i3 + 2] -= 50;
                if (pos[i3 + 2] < -25) pos[i3 + 2] += 50;
            }
            pGeo.attributes.position.needsUpdate = true;

            // Rotate and float 3D shards
            shards.forEach(mesh => {
                mesh.rotation.x += mesh._rotSpeedX;
                mesh.rotation.y += mesh._rotSpeedY;
                mesh.position.y = mesh._baseY + Math.sin(elapsed * 1.2 + mesh._floatOffset) * 0.8;
                mesh.position.z += currentScrollWarp * 0.15;
                if (mesh.position.z > 20) mesh.position.z -= 40;
                if (mesh.position.z < -20) mesh.position.z += 40;
            });

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

            let glare = card.querySelector('.tilt-3d-glare');
            if (!glare) {
                glare = document.createElement('div');
                glare.className = 'tilt-3d-glare';
                card.appendChild(glare);
            }

            card.addEventListener('mousemove', (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;

                const centerX = rect.width / 2;
                const centerY = rect.height / 2;

                const rotateX = ((y - centerY) / centerY) * -8;
                const rotateY = ((x - centerX) / centerX) * 8;

                card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) scale3d(1.02, 1.02, 1.02)`;

                const glareX = (x / rect.width) * 100;
                const glareY = (y / rect.height) * 100;
                glare.style.background = `radial-gradient(circle at ${glareX}% ${glareY}%, rgba(6, 182, 212, 0.25) 0%, transparent 65%)`;
                glare.style.opacity = '1';
            });

            card.addEventListener('mouseleave', () => {
                card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
                glare.style.opacity = '0';
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
