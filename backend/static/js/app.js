// Main application
const App = {
    async init() {
        // Initialize authentication (async to fetch CSRF token)
        await Auth.init();
        
        // Setup routing
        this.setupRouting();
        
        // Handle initial route
        await this.handleRoute();
    },
    
    setupRouting() {
        // Listen for hash changes
        window.addEventListener('hashchange', () => {
            this.handleRoute();
        });
        
        // Setup navigation links
        document.querySelectorAll('[data-page]').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.dataset.page;
                window.location.hash = `#${page}`;
            });
        });
        
        // Setup auth page toggles
        this.setupAuthToggles();
    },
    
    setupAuthToggles() {
        // Toggle between login and signup
        const showSignupLinks = document.querySelectorAll('.show-signup');
        const showLoginLinks = document.querySelectorAll('.show-login');
        
        showSignupLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.hash = '#signup';
            });
        });
        
        showLoginLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.hash = '#login';
            });
        });
    },
    
    async handleRoute() {
        const hash = window.location.hash.slice(1) || 'login';
        
        // Check authentication for protected routes
        if (hash !== 'login' && hash !== 'signup' && !Auth.isAuthenticated()) {
            window.location.hash = '#login';
            return;
        }
        
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        
        // Show requested page
        const page = document.getElementById(`${hash}Page`);
        if (page) {
            page.classList.add('active');
            
            // Initialize page-specific functionality
            await this.initializePage(hash);
        } else {
            // Default to login
            window.location.hash = '#login';
        }
    },
    
    async initializePage(pageName) {
        switch (pageName) {
            case 'dashboard':
                await Dashboard.init();
                break;
            case 'documents':
                await Documents.init();
                break;
            case 'reviews':
                const user = Auth.getUser();
                if (user && (user.role === 'reviewer' || user.role === 'admin')) {
                    await Reviews.init();
                } else {
                    alert('You do not have permission to access reviews');
                    window.location.hash = '#dashboard';
                }
                break;
        }
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await App.init();
    } catch (error) {
        console.error('App initialization failed:', error);
        // Show error to user
        document.body.innerHTML = `
            <div style="padding: 2rem; text-align: center; font-family: sans-serif;">
                <h1>Application Error</h1>
                <p>Failed to initialize the application. Please refresh the page.</p>
                <p style="color: red; font-size: 0.9rem;">${error.message}</p>
            </div>
        `;
    }
});
