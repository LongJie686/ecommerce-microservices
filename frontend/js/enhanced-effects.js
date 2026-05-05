/**
 * 电商数据分析系统 - 增强视觉效果
 * 包含：鼠标光效、粒子背景、3D卡片、流光边框、磁性按钮等
 */

(function() {
    'use strict';

    // ==================== 配置项 ====================
    const CONFIG = {
        particles: {
            count: 80,
            connectionDistance: 100,
            mouseDistance: 150,
            speed: 0.5
        },
        magnetic: {
            strength: 0.3
        }
    };

    // ==================== 鼠标跟随光效 ====================
    class CursorGlow {
        constructor() {
            this.primary = document.getElementById('cursor-glow');
            this.secondary = document.getElementById('cursor-glow-secondary');
            this.mouseX = 0;
            this.mouseY = 0;
            this.glowX = 0;
            this.glowY = 0;
            this.glow2X = 0;
            this.glow2Y = 0;

            if (this.primary) {
                this.init();
            }
        }

        init() {
            document.addEventListener('mousemove', (e) => {
                this.mouseX = e.clientX;
                this.mouseY = e.clientY;
            });

            this.animate();
            this.initHoverEffects();
        }

        animate() {
            // 主光效平滑跟随
            this.glowX += (this.mouseX - this.glowX) * 0.1;
            this.glowY += (this.mouseY - this.glowY) * 0.1;

            if (this.primary) {
                this.primary.style.left = this.glowX + 'px';
                this.primary.style.top = this.glowY + 'px';
            }

            // 副光效延迟跟随
            this.glow2X += (this.mouseX - this.glow2X) * 0.05;
            this.glow2Y += (this.mouseY - this.glow2Y) * 0.05;

            if (this.secondary) {
                this.secondary.style.left = this.glow2X + 'px';
                this.secondary.style.top = this.glow2Y + 'px';
            }

            requestAnimationFrame(() => this.animate());
        }

        initHoverEffects() {
            const cards = document.querySelectorAll('.stat-card, .action-card, .glass-panel');
            cards.forEach(card => {
                card.addEventListener('mouseenter', () => {
                    if (this.primary) this.primary.style.opacity = '0.5';
                });
                card.addEventListener('mouseleave', () => {
                    if (this.primary) this.primary.style.opacity = '1';
                });
            });
        }
    }

    // ==================== 粒子背景系统 ====================
    class ParticleSystem {
        constructor() {
            this.canvas = document.getElementById('particles-canvas');
            if (!this.canvas) return;

            this.ctx = this.canvas.getContext('2d');
            this.particles = [];
            this.animationId = null;
            this.frameCount = 0;
            this.isActive = true;

            this.init();
        }

        init() {
            this.resize();
            window.addEventListener('resize', () => this.resize());

            this.createParticles();
            this.animate();

            // 页面可见性控制
            document.addEventListener('visibilitychange', () => {
                if (document.hidden) {
                    this.pause();
                } else {
                    this.resume();
                }
            });
        }

        resize() {
            this.canvas.width = window.innerWidth;
            this.canvas.height = window.innerHeight;
        }

        createParticles() {
            for (let i = 0; i < CONFIG.particles.count; i++) {
                this.particles.push({
                    x: Math.random() * this.canvas.width,
                    y: Math.random() * this.canvas.height,
                    vx: (Math.random() - 0.5) * CONFIG.particles.speed,
                    vy: (Math.random() - 0.5) * CONFIG.particles.speed,
                    radius: Math.random() * 2 + 1,
                    color: Math.random() > 0.5
                        ? 'rgba(0, 255, 136, 0.5)'
                        : 'rgba(0, 243, 255, 0.5)'
                });
            }
        }

        animate() {
            if (!this.isActive) return;

            this.frameCount++;

            // 每2帧渲染一次，降低性能消耗
            if (this.frameCount % 2 === 0) {
                this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

                this.particles.forEach((p, i) => {
                    // 更新位置
                    p.x += p.vx;
                    p.y += p.vy;

                    // 边界检测
                    if (p.x < 0 || p.x > this.canvas.width) p.vx *= -1;
                    if (p.y < 0 || p.y > this.canvas.height) p.vy *= -1;

                    // 绘制粒子
                    this.ctx.beginPath();
                    this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                    this.ctx.fillStyle = p.color;
                    this.ctx.fill();

                    // 绘制连线（优化性能）
                    if (i % 3 === 0) {
                        this.drawConnections(p, i);
                    }
                });
            }

            this.animationId = requestAnimationFrame(() => this.animate());
        }

        drawConnections(p, startIndex) {
            for (let j = startIndex + 1; j < this.particles.length; j += 2) {
                const dx = this.particles[j].x - p.x;
                const dy = this.particles[j].y - p.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < CONFIG.particles.connectionDistance) {
                    this.ctx.beginPath();
                    this.ctx.moveTo(p.x, p.y);
                    this.ctx.lineTo(this.particles[j].x, this.particles[j].y);
                    this.ctx.strokeStyle = `rgba(0, 243, 255, ${0.2 * (1 - dist / CONFIG.particles.connectionDistance)})`;
                    this.ctx.lineWidth = 0.5;
                    this.ctx.stroke();
                }
            }
        }

        pause() {
            this.isActive = false;
            if (this.animationId) {
                cancelAnimationFrame(this.animationId);
            }
        }

        resume() {
            if (!this.isActive) {
                this.isActive = true;
                this.animate();
            }
        }
    }

    // ==================== 3D 卡片倾斜效果 - 全新设计 ====================
    class TiltCards {
        constructor() {
            this.cards = document.querySelectorAll('.tilt-card');
            this.init();
        }

        init() {
            this.cards.forEach(card => {
                const shine = card.querySelector('.card-shine');
                const content = card.querySelector('.card-content');

                // 鼠标进入 - 弹性放大入场
                card.addEventListener('mouseenter', (e) => {
                    card.classList.remove('fade-in-up');
                    card.style.opacity = '';

                    // 弹性入场动画
                    this.animateEntry(card, content);
                });

                // 鼠标移动 - 3D 倾斜跟随
                card.addEventListener('mousemove', (e) => {
                    this.handleMouseMove(e, card, shine, content);
                });

                // 鼠标离开 - 弹性复位
                card.addEventListener('mouseleave', () => {
                    this.handleMouseLeave(card, shine, content);
                });
            });
        }

        animateEntry(card, content) {
            // 第一阶段：快速弹起
            card.style.transition = 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)';
            card.style.transform = 'perspective(1000px) translateZ(-30px) scale3d(0.95, 0.95, 0.95)';

            setTimeout(() => {
                // 第二阶段：回弹放大
                card.style.transition = 'transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                card.style.transform = 'perspective(1000px) translateZ(20px) scale3d(1.03, 1.03, 1.03)';

                // 内容层视差效果
                if (content) {
                    content.style.transition = 'transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                    content.style.transform = 'translateZ(30px) scale(0.98)';
                }
            }, 150);
        }

        handleMouseMove(e, card, shine, content) {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            // 计算旋转角度 (限制最大角度)
            const maxRotate = 12;
            const rotateX = Math.max(-maxRotate, Math.min(maxRotate, (y - centerY) / (centerY / maxRotate)));
            const rotateY = Math.max(-maxRotate, Math.min(maxRotate, (centerX - x) / (centerX / maxRotate)));

            // 计算光泽位置
            const percentX = (x / rect.width) * 100;
            const percentY = (y / rect.height) * 100;

            // 计算磁吸偏移 (卡片跟随鼠标轻微移动)
            const magnetX = (x - centerX) / centerX * 8;
            const magnetY = (y - centerY) / centerY * 8;

            // 应用变换 - 无过渡实现实时跟随
            card.style.transition = 'none';
            card.style.transform = `
                perspective(1000px)
                rotateX(${-rotateX}deg)
                rotateY(${rotateY}deg)
                translateX(${magnetX}px)
                translateY(${magnetY}px)
                translateZ(30px)
                scale3d(1.05, 1.05, 1.05)
            `;

            // 边框发光效果
            card.style.borderColor = 'rgba(0, 243, 255, 0.6)';

            // 动态阴影 (根据倾斜角度调整)
            const shadowX = -rotateY * 2;
            const shadowY = rotateX * 2;
            card.style.boxShadow = `
                ${shadowX}px ${shadowY + 20}px 40px rgba(0, 0, 0, 0.4),
                ${shadowX}px ${shadowY + 10}px 20px rgba(0, 243, 255, 0.15),
                0 0 60px rgba(0, 243, 255, 0.2),
                inset 0 1px 0 rgba(255, 255, 255, 0.2)
            `;

            // 光泽层跟随鼠标
            if (shine) {
                shine.style.transition = 'none';
                shine.style.background = `
                    radial-gradient(
                        circle at ${percentX}% ${percentY}%,
                        rgba(255,255,255,0.4) 0%,
                        rgba(0, 243, 255, 0.1) 25%,
                        transparent 50%
                    )
                `;
                shine.style.opacity = '1';
            }

            // 内容层视差 - 与卡片反向移动
            if (content) {
                content.style.transition = 'none';
                content.style.transform = `
                    translateX(${-magnetX * 0.5}px)
                    translateY(${-magnetY * 0.5}px)
                    translateZ(40px)
                `;
            }
        }

        handleMouseLeave(card, shine, content) {
            // 弹性复位动画
            card.style.transition = 'all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateX(0) translateY(0) translateZ(0) scale3d(1, 1, 1)';
            card.style.borderColor = '';
            card.style.boxShadow = '';

            if (shine) {
                shine.style.transition = 'opacity 0.3s ease';
                shine.style.opacity = '0';
            }

            if (content) {
                content.style.transition = 'transform 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55)';
                content.style.transform = 'translateZ(0) translateX(0) translateY(0)';
            }

            // 清除内联样式
            setTimeout(() => {
                card.style.transition = '';
                card.style.transform = '';
                card.style.borderColor = '';
                card.style.boxShadow = '';
                if (content) {
                    content.style.transition = '';
                    content.style.transform = '';
                }
            }, 500);
        }
    }

    // ==================== 磁性按钮效果 ====================
    class MagneticButtons {
        constructor() {
            // 只选择按钮和特定元素，完全排除所有导航菜单项
            this.buttons = document.querySelectorAll('.magnetic-btn, .header-icon, .ai-toggle, .btn-primary, .btn-secondary');
            this.init();
        }

        init() {
            this.buttons.forEach(btn => {
                btn.addEventListener('mousemove', (e) => {
                    this.handleMouseMove(e, btn);
                });

                btn.addEventListener('mouseleave', () => {
                    this.handleMouseLeave(btn);
                });

                btn.addEventListener('click', (e) => {
                    this.createRipple(e, btn);
                });
            });
        }

        handleMouseMove(e, btn) {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            btn.style.transform = `translate(${x * CONFIG.magnetic.strength}px, ${y * CONFIG.magnetic.strength}px)`;
        }

        handleMouseLeave(btn) {
            btn.style.transform = 'translate(0, 0)';
        }

        createRipple(e, btn) {
            const rect = btn.getBoundingClientRect();
            const ripple = document.createElement('span');
            ripple.className = 'ripple';
            ripple.style.left = (e.clientX - rect.left) + 'px';
            ripple.style.top = (e.clientY - rect.top) + 'px';
            btn.appendChild(ripple);

            setTimeout(() => ripple.remove(), 600);
        }
    }

    // ==================== 滚动动画 ====================
    class ScrollAnimations {
        constructor() {
            this.elements = document.querySelectorAll('.stat-card, .action-card, .glass-panel');
            this.observer = null;
            this.init();
        }

        init() {
            if ('IntersectionObserver' in window) {
                this.observer = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('fade-in-up');
                            // 动画完成后移除动画类和内联样式，避免与3D tilt效果冲突
                            setTimeout(() => {
                                entry.target.classList.remove('fade-in-up');
                                entry.target.style.opacity = '';
                                entry.target.style.transform = '';
                                entry.target.style.transition = '';
                            }, 600);
                            this.observer.unobserve(entry.target);
                        }
                    });
                }, {
                    threshold: 0.1
                });

                this.elements.forEach(el => {
                    el.style.opacity = '0';
                    el.style.transform = 'translateY(20px)';
                    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                    this.observer.observe(el);
                });
            }
        }
    }

    // ==================== 打字机效果 ====================
    class TypeWriter {
        constructor(element, text, speed = 100) {
            this.element = element;
            this.text = text;
            this.speed = speed;
            this.index = 0;
        }

        type() {
            if (this.index < this.text.length) {
                this.element.textContent += this.text.charAt(this.index);
                this.index++;
                setTimeout(() => this.type(), this.speed);
            }
        }

        start() {
            this.element.textContent = '';
            this.type();
        }
    }

    // ==================== 霓虹文字效果 ====================
    class NeonText {
        constructor(selector) {
            this.elements = document.querySelectorAll(selector);
            this.init();
        }

        init() {
            this.elements.forEach(el => {
                el.addEventListener('mouseenter', () => {
                    el.style.animation = 'neonPulse 0.5s ease-in-out infinite';
                });
                el.addEventListener('mouseleave', () => {
                    el.style.animation = '';
                });
            });
        }
    }

    // ==================== 点击粒子 & 长按火星效果 ====================
    function initClickParticles() {
        const flameColors = [
            { r: 0,   g: 255, b: 0   },
            { r: 0,   g: 243, b: 255 },
            { r: 255, g: 255, b: 0   },
            { r: 255, g: 68,  b: 0   },
            { r: 255, g: 0,   b: 255 },
            { r: 0,   g: 0,   b: 0   }
        ];

        function interpolateColor(c1, c2, t) {
            return {
                r: Math.round(c1.r + (c2.r - c1.r) * t),
                g: Math.round(c1.g + (c2.g - c1.g) * t),
                b: Math.round(c1.b + (c2.b - c1.b) * t)
            };
        }

        function getFlameColor(ms) {
            const stage = Math.floor(ms / 1000);
            const t = (ms % 1000) / 1000;
            const c1 = flameColors[Math.min(stage, flameColors.length - 1)];
            const c2 = flameColors[Math.min(stage + 1, flameColors.length - 1)];
            return interpolateColor(c1, c2, t);
        }

        function rgba(c, a) { return `rgba(${c.r},${c.g},${c.b},${a})`; }

        function spawnParticle(x, y, color) {
            const p = document.createElement('div');
            const c = color || { r: 0, g: 243, b: 255 };
            p.style.cssText = `position:fixed;left:${x}px;top:${y}px;width:5px;height:5px;
                border-radius:50%;pointer-events:none;z-index:99999;
                background:radial-gradient(circle,${rgba(c,1)} 0%,${rgba(c,0.6)} 50%,transparent 100%);
                box-shadow:0 0 8px ${rgba(c,1)},0 0 16px ${rgba(c,0.5)};
                transition:transform 0.8s cubic-bezier(.4,0,.2,1),opacity 0.8s ease;`;
            document.body.appendChild(p);
            const angle = Math.random() * Math.PI * 2;
            const v = 60 + Math.random() * 110;
            setTimeout(() => {
                p.style.transform = `translate(${Math.cos(angle)*v}px,${Math.sin(angle)*v}px) scale(0)`;
                p.style.opacity = '0';
            }, 10);
            setTimeout(() => p.remove(), 820);
        }

        // 普通点击 - 青色粒子
        document.addEventListener('click', function(e) {
            for (let i = 0; i < 4; i++) {
                setTimeout(() => spawnParticle(e.clientX, e.clientY), i * 40);
            }
        });

        // 长按 - 火星变色效果
        let timer = null, interval = null, mx = 0, my = 0, t0 = 0;

        document.addEventListener('mousedown', function(e) {
            if (['INPUT','TEXTAREA','BUTTON','SELECT'].includes(e.target.tagName)) return;
            mx = e.clientX; my = e.clientY; t0 = Date.now();
            timer = setTimeout(() => {
                let cnt = 0;
                interval = setInterval(() => {
                    const ms = Date.now() - t0;
                    const n = 2 + Math.floor(cnt / 5);
                    for (let i = 0; i < n; i++) {
                        setTimeout(() => spawnParticle(
                            mx + (Math.random()-0.5)*30,
                            my + (Math.random()-0.5)*30,
                            getFlameColor(ms)
                        ), i * 15);
                    }
                    cnt++;
                }, 60);
            }, 300);
        });

        document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });

        function stopLongPress() {
            clearTimeout(timer);
            clearInterval(interval);
            interval = null;
        }
        document.addEventListener('mouseup', stopLongPress);
        document.addEventListener('mouseleave', stopLongPress);
    }

    // ==================== 初始化所有效果 ====================
    function init() {
        // 检查是否支持必要的特性
        if (!window.requestAnimationFrame) {
            console.warn('浏览器不支持 requestAnimationFrame，部分效果可能无法正常运行');
            return;
        }

        // 初始化各个效果
        new CursorGlow();
        new ParticleSystem();
        new TiltCards();
        new MagneticButtons();
        new ScrollAnimations();
        new NeonText('.neon-text, .neon-text-blue');
        initClickParticles();

        console.log('[Enhanced Effects] 所有效果已初始化');
    }

    // DOM 加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // 暴露到全局
    window.EnhancedEffects = {
        CursorGlow,
        ParticleSystem,
        TiltCards,
        MagneticButtons,
        ScrollAnimations,
        TypeWriter,
        NeonText,
        CONFIG
    };

})();