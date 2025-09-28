# Tender Extraction Frontend

Modern React frontend for the Government Tender Extraction System with a beautiful, responsive interface.

## Features

- **Modern UI**: Clean, professional interface with TailwindCSS styling
- **Document Upload**: Drag-and-drop file upload with progress indicators
- **Real-time Processing**: Live updates during document processing
- **Results Display**: Beautiful presentation of extracted tender data
- **Evaluation Metrics**: Visual feedback on extraction accuracy
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Architecture

### Core Components

- **DocumentUpload**: File upload with drag-and-drop functionality
- **ExtractionResults**: Display extracted tender data in organized cards
- **EvaluationMetrics**: Show accuracy metrics and discrepancies
- **Home**: Main landing page with upload interface
- **Results**: Results page with extracted data and evaluation

### Styling

- **TailwindCSS**: Utility-first CSS framework for rapid styling
- **Gradient Design**: Modern gradient backgrounds and accents
- **Glass Morphism**: Subtle glass effects for depth
- **Responsive Grid**: Adaptive layouts for all screen sizes

## Setup

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start
```

The application will be available at `http://localhost:3000`.

## Development

### Available Scripts

```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Run linting
npm run lint

# Format code
npm run format
```

### Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── DocumentUpload.tsx
│   ├── ExtractionResults.tsx
│   └── EvaluationMetrics.tsx
├── pages/              # Page components
│   ├── Home.tsx
│   └── Results.tsx
├── services/           # API integration
│   └── api.ts
├── __tests__/          # Test files
└── App.tsx            # Main application component
```

## API Integration

### Services

The frontend communicates with the backend through the `api.ts` service:

- **Document Upload**: Upload files and receive processing status
- **Real-time Updates**: WebSocket connection for live progress
- **Results Retrieval**: Fetch extracted data and evaluation metrics

### WebSocket Connection

Real-time updates are handled through WebSocket connections:

```typescript
// Connect to processing updates
const ws = connectWebSocket(documentId, (update) => {
  setProcessingStatus(update.status);
  setProgress(update.progress);
});
```

## Styling Guide

### Design System

The application uses a consistent design system:

- **Colors**: Blue gradient primary, gray neutrals, success/error states
- **Typography**: Clean, readable fonts with proper hierarchy
- **Spacing**: Consistent padding and margins using TailwindCSS
- **Components**: Reusable styled components with consistent behavior

### TailwindCSS Classes

Key utility classes used throughout the application:

```css
/* Gradients */
bg-gradient-to-r from-blue-600 to-purple-600
bg-gradient-to-br from-blue-50 to-indigo-100

/* Glass morphism */
backdrop-blur-sm bg-white/80

/* Animations */
animate-spin
transition-all duration-300

/* Responsive design */
md:grid-cols-2 lg:grid-cols-3
```

## Testing

### Running Tests

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage
```

### Test Structure

- **Component Tests**: Test individual component behavior
- **Integration Tests**: Test API communication
- **User Interaction Tests**: Test user workflows

## Deployment

### Build for Production

```bash
# Create production build
npm run build

# Serve the build locally
npx serve -s build
```

### Environment Configuration

Configure API endpoints in `.env`:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

### Deployment Options

1. **Static Hosting**: Deploy to Netlify, Vercel, or GitHub Pages
2. **CDN**: Use AWS CloudFront or similar CDN
3. **Container**: Docker deployment with nginx

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Performance

### Optimization Features

- **Code Splitting**: Lazy loading of components
- **Image Optimization**: Efficient image handling
- **Bundle Analysis**: Webpack bundle analyzer
- **Caching**: Proper cache headers for static assets

### Performance Monitoring

The application includes performance monitoring:

- **Loading Times**: Track component load times
- **API Response Times**: Monitor backend communication
- **User Interactions**: Track user engagement metrics

## Accessibility

### Features

- **Keyboard Navigation**: Full keyboard support
- **Screen Reader Support**: Proper ARIA labels
- **Color Contrast**: WCAG compliant color schemes
- **Focus Management**: Clear focus indicators

### Testing Accessibility

```bash
# Run accessibility tests
npm run test:a11y

# Manual testing with screen readers
# Use VoiceOver (macOS) or NVDA (Windows)
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend CORS is configured for frontend domain
2. **WebSocket Connection**: Check WebSocket URL configuration
3. **Build Failures**: Clear node_modules and reinstall dependencies
4. **Styling Issues**: Ensure TailwindCSS is properly configured

### Debug Mode

Enable debug logging:

```javascript
// In browser console
localStorage.setItem('debug', 'true');
```

## Contributing

### Code Style

- Use TypeScript for type safety
- Follow React best practices
- Use functional components with hooks
- Implement proper error boundaries

### Git Workflow

1. Create feature branch
2. Make changes with tests
3. Run linting and tests
4. Submit pull request

## License

This project is part of the Government Tender Extraction System.
