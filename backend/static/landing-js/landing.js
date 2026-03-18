/* ============================================================
   AgentDoc Landing Page - Single JS Bundle with GSAP Animations
   ============================================================ */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    'use strict';

    // Configuration
    const CONFIG = {
        demoUrl: '/app',
        animations: {
            duration: 1,
            stagger: 0.15,
            ease: 'power3.out'
        }
    };
    window.APP_CONFIG = CONFIG;

    // Check if GSAP is loaded
    if (typeof gsap === 'undefined') {
        console.warn('GSAP not loaded. Animations will be disabled.');
        document.body.style.opacity = '1';
        return;
    }

    // Register ScrollTrigger plugin
    gsap.registerPlugin(ScrollTrigger);

    // ============================================================
    // NAVIGATION FUNCTIONALITY
    // ============================================================
    
    // Navbar scroll effect
    function handleNavbarScroll() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;
        
        if (window.scrollY > 50) {
            gsap.to(navbar, {
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
                duration: 0.3,
                overwrite: true
            });
        } else {
            gsap.to(navbar, {
                boxShadow: '0 1px 0 rgba(59, 130, 246, 0.1)',
                duration: 0.3,
                overwrite: true
            });
        }
    }

    // Mobile menu toggle
    function setupMobileMenu() {
        const toggle = document.querySelector('.mobile-menu-toggle');
        const menu = document.querySelector('.nav-menu');
        
        if (!toggle || !menu) return;
        
        toggle.addEventListener('click', function() {
            menu.classList.toggle('active');
            
            const spans = this.querySelectorAll('span');
            if (menu.classList.contains('active')) {
                gsap.to(spans[0], { rotate: 45, y: 7, duration: 0.3 });
                gsap.to(spans[1], { opacity: 0, duration: 0.3 });
                gsap.to(spans[2], { rotate: -45, y: -7, duration: 0.3 });
            } else {
                gsap.to(spans[0], { rotate: 0, y: 0, duration: 0.3 });
                gsap.to(spans[1], { opacity: 1, duration: 0.3 });
                gsap.to(spans[2], { rotate: 0, y: 0, duration: 0.3 });
            }
        });
        
        menu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                menu.classList.remove('active');
                const spans = toggle.querySelectorAll('span');
                gsap.to(spans[0], { rotate: 0, y: 0, duration: 0.3 });
                gsap.to(spans[1], { opacity: 1, duration: 0.3 });
                gsap.to(spans[2], { rotate: 0, y: 0, duration: 0.3 });
            });
        });
    }

    // Smooth scroll for navigation links
    function setupSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    gsap.to(window, {
                        duration: 1,
                        scrollTo: {
                            y: target,
                            offsetY: 80
                        },
                        ease: 'power3.inOut'
                    });
                }
            });
        });
    }

    // ============================================================
    // HERO ANIMATIONS
    // ============================================================
    
    function initHeroAnimations() {
        // Entrance animations - staggered, clean
        const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
        
        tl.from('.hero-title', { duration: 0.9, y: 40, opacity: 0 })
          .from('.hero-subtitle', { duration: 0.8, y: 25, opacity: 0 }, '-=0.5')
          .from('.hero-buttons', { duration: 0.7, y: 20, opacity: 0 }, '-=0.4')
          .from('.stat-item', { duration: 0.6, y: 20, opacity: 0, stagger: 0.1 }, '-=0.3');
        
        // Document cards entrance
        gsap.from('.doc-card', {
            duration: 1,
            scale: 0.85,
            opacity: 0,
            stagger: 0.15,
            delay: 0.4,
            ease: 'back.out(1.5)'
        });
        
        // Floating animation - subtle, continuous
        gsap.to('.doc-1', {
            y: -18,
            rotation: -10,
            duration: 3.2,
            repeat: -1,
            yoyo: true,
            ease: 'sine.inOut'
        });
        
        gsap.to('.doc-2', {
            y: -12,
            rotation: 6,
            duration: 2.8,
            repeat: -1,
            yoyo: true,
            ease: 'sine.inOut',
            delay: 0.6
        });
        
        gsap.to('.doc-3', {
            y: -22,
            rotation: -3,
            duration: 3.6,
            repeat: -1,
            yoyo: true,
            ease: 'sine.inOut',
            delay: 1.1
        });
        
        // Stat counter - runs once when visible
        ScrollTrigger.create({
            trigger: '.hero-stats',
            start: 'top 85%',
            once: true,
            onEnter: () => {
                document.querySelectorAll('.stat-number').forEach(el => {
                    const original = el.textContent.trim();
                    const num = parseFloat(original);
                    if (isNaN(num)) return;
                    
                    const suffix = original.replace(String(num), '');
                    const obj = { val: 0 };
                    
                    gsap.to(obj, {
                        val: num,
                        duration: 2,
                        ease: 'power2.out',
                        onUpdate: function() {
                            const display = Number.isInteger(num)
                                ? Math.round(obj.val)
                                : obj.val.toFixed(1);
                            el.textContent = display + suffix;
                        },
                        onComplete: function() {
                            el.textContent = original;
                        }
                    });
                });
            }
        });
        
        // Parallax effect for hero background
        gsap.to('.hero::before', {
            scrollTrigger: {
                trigger: '.hero',
                start: 'top top',
                end: 'bottom top',
                scrub: true
            },
            y: 200,
            opacity: 0,
            ease: 'none'
        });
    }

    // ============================================================
    // DEMO SECTION ANIMATIONS
    // ============================================================
    
    function initDemoAnimations() {
        // Demo section animations with ScrollTrigger
        gsap.from('.demo-info', {
            scrollTrigger: {
                trigger: '.demo-section',
                start: 'top 85%',
                toggleActions: 'play none none none',
                once: true
            },
            duration: 0.9,
            x: -40,
            opacity: 0,
            ease: 'power3.out'
        });
        
        gsap.from('.demo-features', {
            scrollTrigger: {
                trigger: '.demo-section',
                start: 'top 85%',
                toggleActions: 'play none none none',
                once: true
            },
            duration: 0.9,
            x: 40,
            opacity: 0,
            delay: 0.15,
            ease: 'power3.out'
        });
    }

    // ============================================================
    // INTERACTIVE ANIMATIONS
    // ============================================================
    
    function initInteractiveAnimations() {
        // Button hover effects
        const buttons = document.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.addEventListener('mouseenter', function() {
                gsap.to(this, {
                    duration: 0.3,
                    scale: 1.05,
                    ease: 'power2.out'
                });
            });
            
            button.addEventListener('mouseleave', function() {
                gsap.to(this, {
                    duration: 0.3,
                    scale: 1,
                    ease: 'power2.out'
                });
            });
        });
    }

    // ============================================================
    // PAGE LOAD ANIMATION
    // ============================================================
    
    function initPageLoad() {
        // Fade in the body
        gsap.to('body', {
            duration: 0.5,
            opacity: 1,
            ease: 'power2.out',
            onComplete: () => {
                console.log('AgentDoc Landing Page - Loaded Successfully with GSAP Animations');
            }
        });
    }

    // ============================================================
    // INITIALIZE ALL
    // ============================================================
    
    // Set up event listeners
    window.addEventListener('scroll', handleNavbarScroll);
    
    // Initialize all animations and functionality
    setupMobileMenu();
    setupSmoothScroll();
    initHeroAnimations();
    initDemoAnimations();
    initInteractiveAnimations();
    initPageLoad();

    // Log configuration
    if (window.APP_CONFIG) {
        console.log('Configuration:', window.APP_CONFIG);
    }

    // Add ScrollTrigger utility for GSAP
    if (ScrollTrigger) {
        ScrollTrigger.config({
            limitCallbacks: true,
            ignoreMobileResize: true
        });
    }
});

// Fallback in case GSAP fails to load
window.addEventListener('load', function() {
    if (typeof gsap === 'undefined') {
        document.body.style.opacity = '1';
        console.warn('GSAP failed to load. Using fallback.');
    }
});