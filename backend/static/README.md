# AgentDoc Landing Page

A modern, animated landing page for the AgentDoc Agentic AI Document Intelligence System built with pure HTML5, CSS3, and JavaScript with GSAP animations.

## Features

- **Pure Web Technologies**: No frameworks - just HTML5, CSS3, and vanilla JavaScript
- **GSAP Animations**: Smooth, professional animations using GreenSock Animation Platform
- **Modular Architecture**: Organized CSS and JS files for maintainability
- **Responsive Design**: Mobile-first approach that works on all devices
- **5-Agent Workflow**: Streamlined to essential agents (Classification, Extraction, Validation, Routing, Audit)
- **Render-Ready**: Configured for free deployment on Render

## Project Structure

```
landing-page/
├── index.html              # Main HTML structure
├── css/
│   ├── reset.css          # CSS reset
│   ├── variables.css      # CSS custom properties
│   ├── layout.css         # Layout and grid systems
│   ├── components.css     # Reusable components
│   ├── sections.css       # Section-specific styles
│   └── responsive.css     # Media queries
├── js/
│   ├── config.js          # Configuration
│   ├── navigation.js      # Navigation functionality
│   ├── main.js            # Main initialization
│   └── animations/
│       ├── hero.js        # Hero section animations
│       ├── sections.js    # Section scroll animations
│       └── interactions.js # Interactive animations
└── README.md              # This file
```

## 5-Agent Workflow

The landing page highlights the streamlined 5-agent system:

1. **Classification Agent**: Identifies document type with confidence scoring
2. **Extraction Agent**: Extracts structured data using AI-powered OCR
3. **Validation Agent**: Validates against business rules and semantic checks
4. **Routing Agent**: Routes to auto-approve, review, or exception handling
5. **Audit Agent**: Creates immutable audit trail for compliance

## Local Development

### Quick Start

1. Open `index.html` in a modern web browser:
   ```bash
   # Windows
   start index.html
   ```

2. Or use a local server (recommended):
   ```bash
   # Python
   python -m http.server 8080
   
   # Node.js
   npx serve
   ```

3. Navigate to `http://localhost:8080`

### Configuration

Edit `js/config.js` to customize:

```javascript
const CONFIG = {
    demoUrl: 'YOUR_DEMO_URL',
    animations: {
        duration: 1,
        stagger: 0.15,
        ease: 'power3.out'
    }
};
```

## Deployment on Render (Free Tier)

### Option 1: Static Site

1. Create a new Static Site on Render
2. Connect your GitHub repository
3. Set build settings:
   - **Build Command**: (leave empty)
   - **Publish Directory**: `landing-page`
4. Deploy!

### Option 2: Manual Deploy

1. Install Render CLI:
   ```bash
   npm install -g render-cli
   ```

2. Deploy:
   ```bash
   render deploy
   ```

### Environment Variables

No environment variables needed for the landing page. It's purely static HTML/CSS/JS.

## Customization

### Colors

Edit `css/variables.css`:

```css
:root {
    --primary: #3b82f6;
    --secondary: #8b5cf6;
    --dark: #0f172a;
}
```

### Content

Edit text directly in `index.html`

### Animations

Modify GSAP timelines in `js/animations/` files

## Technologies Used

- **HTML5**: Semantic markup
- **CSS3**: Modern styling with Grid, Flexbox, custom properties
- **JavaScript (ES6+)**: Modular architecture
- **GSAP 3.12.5**: Professional animation library
- **ScrollTrigger**: Scroll-based animations

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- Lightweight: ~60KB total (excluding GSAP CDN)
- Fast load times
- Optimized animations with hardware acceleration
- Smooth 60fps animations

## File Organization

### CSS Files
- `reset.css`: Browser normalization
- `variables.css`: Design tokens and CSS custom properties
- `layout.css`: Grid systems and spacing
- `components.css`: Buttons, cards, navigation
- `sections.css`: Section-specific styles
- `responsive.css`: Mobile breakpoints

### JS Files
- `config.js`: Application configuration
- `navigation.js`: Menu and scroll behavior
- `main.js`: Initialization and error handling
- `animations/hero.js`: Hero section animations
- `animations/sections.js`: Scroll-triggered animations
- `animations/interactions.js`: Hover and click effects

## Key Features Highlighted

1. **5-Agent System**: Classification → Extraction → Validation → Routing → Audit
2. **Structured Extraction**: From messy documents
3. **Intelligent Validation**: Business rules + semantic understanding
4. **Smart Routing**: Risk-based workflow decisions
5. **Human-in-the-Loop**: Seamless reviewer collaboration
6. **Semantic Search**: Vector-based document retrieval

## Responsive Breakpoints

- Desktop: 1200px+
- Tablet: 768px - 1199px
- Mobile: < 768px

## License

Part of the AgentDoc project - Agentic AI Document Intelligence System
