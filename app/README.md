# OSINT Phone Intelligence Platform - Frontend

A modern React + TypeScript frontend for the OSINT Phone Intelligence Platform.

## Features

- **Modern UI**: Built with React, TypeScript, and Tailwind CSS
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dark Theme**: Professional dark interface optimized for OSINT work
- **Real-time Results**: Live search and investigation results
- **Interactive Components**: Tabs, accordions, modals, and more
- **Accessibility**: ARIA-compliant components

## Tech Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Icons**: Lucide React
- **Notifications**: Sonner

## Installation

### Prerequisites

- Node.js 18 or higher
- npm or yarn

### Setup

1. Install dependencies:
```bash
npm install
```

2. Configure environment variables:
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

3. Start development server:
```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## Build for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | `http://localhost:5000/api` |

## Project Structure

```
src/
├── components/          # React components
│   ├── SearchForm.tsx
│   ├── PhoneAnalysisCard.tsx
│   ├── SocialMediaCard.tsx
│   ├── WebSearchCard.tsx
│   ├── RiskAnalysisCard.tsx
│   ├── LookupSourcesCard.tsx
│   └── DisclaimerModal.tsx
├── services/           # API services
│   └── api.ts
├── types/              # TypeScript types
│   └── index.ts
├── App.tsx             # Main application
├── App.css             # App-specific styles
├── index.css           # Global styles
└── main.tsx            # Entry point
```

## Components

### SearchForm
Main search interface with support for phone, username, and name queries.

### PhoneAnalysisCard
Displays detailed phone number analysis including carrier, location, and formatting.

### SocialMediaCard
Shows social media profile search results across multiple platforms.

### WebSearchCard
Displays web search results organized by query category.

### RiskAnalysisCard
Visualizes risk assessment with score, factors, and recommendations.

### LookupSourcesCard
Lists external lookup sources with status and direct links.

### DisclaimerModal
Legal disclaimer and terms of use modal.

## Development

### Adding New Components

1. Create component file in `src/components/`
2. Add types to `src/types/index.ts` if needed
3. Update `App.tsx` to use the component

### Styling

- Use Tailwind CSS utility classes
- Follow the existing color scheme (slate/blue/indigo)
- Use CSS variables for consistent theming

### API Integration

- Add new API methods to `src/services/api.ts`
- Use the existing error handling pattern
- Type all responses with TypeScript interfaces

## Build Configuration

### Vite Config

The `vite.config.ts` includes:
- Path aliases (`@/`)
- TypeScript support
- Tailwind CSS integration
- Production optimizations

### Tailwind Config

The `tailwind.config.js` extends the default config with:
- Custom colors for the dark theme
- shadcn/ui component styles
- Custom animations

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

- Code splitting with dynamic imports
- Lazy loading for heavy components
- Optimized images and assets
- Minimal bundle size

## License

MIT License - See LICENSE file for details.
