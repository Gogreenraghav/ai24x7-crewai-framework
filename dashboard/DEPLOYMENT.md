# 🚀 Deployment Guide

## Pre-Deployment Checklist

### ✅ Code Quality
- [x] All TypeScript types defined
- [x] No ESLint errors
- [x] Responsive design tested
- [x] WebSocket reconnection logic
- [x] Error handling implemented
- [x] Loading states for async operations

### ✅ Configuration
- [ ] Update backend URL in `lib/socket.ts` if needed
- [ ] Set environment variables (if any)
- [ ] Configure CORS on backend
- [ ] Set up SSL/TLS for production

### ✅ Build & Test
```bash
# Install dependencies
npm install

# Build for production
npm run build

# Test production build locally
npm start

# Check for build errors
npx tsc --noEmit
```

## Deployment Options

### 1. Vercel (Recommended for Next.js)

**Easiest deployment option with zero configuration**

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

**Or connect GitHub repo:**
1. Push code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import repository
4. Auto-deploys on every push!

**Environment Variables:**
- Add in Vercel dashboard if needed
- Example: `NEXT_PUBLIC_SOCKET_URL=https://your-backend.com`

### 2. Docker

Create `Dockerfile`:
```dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
```

Create `.dockerignore`:
```
node_modules
.next
.git
*.md
```

**Build and run:**
```bash
docker build -t crewai-dashboard .
docker run -p 3000:3000 crewai-dashboard
```

### 3. Static Export (if no server-side features needed)

Update `next.config.mjs`:
```javascript
const nextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
};
```

Build:
```bash
npm run build
# Output in ./out directory
```

Deploy `out/` folder to any static host (Netlify, GitHub Pages, S3, etc.)

### 4. Traditional Node Server

```bash
# Build
npm run build

# Start with PM2 (process manager)
npm i -g pm2
pm2 start npm --name "crewai-dashboard" -- start
pm2 save
pm2 startup
```

### 5. Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket support
    location /socket.io/ {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Backend Deployment

Your Python backend must be accessible from the dashboard.

### Option A: Same Server
```python
# Run backend on port 5000
python BACKEND_EXAMPLE.py
```

### Option B: Separate Server
```python
# Update CORS to allow dashboard domain
CORS(app, resources={r"/*": {"origins": "https://your-dashboard.com"}})
```

Update frontend URL in `lib/socket.ts`:
```typescript
const socket = io('https://your-backend.com:5000', {
  // config
});
```

### Option C: Serverless Backend
Use AWS Lambda, Google Cloud Functions, or Vercel Serverless Functions with Socket.IO support.

## Environment Variables

Create `.env.local` for development:
```bash
NEXT_PUBLIC_SOCKET_URL=http://localhost:5000
NEXT_PUBLIC_APP_NAME=CrewAI Dashboard
```

Update `lib/socket.ts`:
```typescript
const socket = io(process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:5000', {
  // config
});
```

## SSL/HTTPS Setup

For production, always use HTTPS:

1. **Vercel**: Automatic SSL
2. **Let's Encrypt**: Free SSL certificates
3. **Cloudflare**: Free SSL + CDN

Update WebSocket connection for HTTPS:
```typescript
const socket = io(process.env.NEXT_PUBLIC_SOCKET_URL || 'https://your-backend.com', {
  secure: true,
  // config
});
```

## Performance Optimization

### 1. Enable Compression
```javascript
// next.config.mjs
const nextConfig = {
  compress: true,
};
```

### 2. Image Optimization
Already configured with Next.js Image component (if needed)

### 3. Code Splitting
Automatically handled by Next.js

### 4. Caching Headers
```javascript
// next.config.mjs
const nextConfig = {
  async headers() {
    return [
      {
        source: '/static/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: 'public, max-age=31536000, immutable',
          },
        ],
      },
    ];
  },
};
```

## Monitoring & Debugging

### Production Logs
```bash
# PM2 logs
pm2 logs crewai-dashboard

# Docker logs
docker logs -f <container-id>

# Vercel logs
vercel logs
```

### Error Tracking
Consider adding:
- Sentry for error tracking
- LogRocket for session replay
- Google Analytics for usage stats

### Health Checks
Add a health endpoint if needed:
```typescript
// app/api/health/route.ts
export async function GET() {
  return Response.json({ status: 'ok' });
}
```

## Security Checklist

- [ ] HTTPS enabled
- [ ] CORS properly configured
- [ ] WebSocket authentication (if needed)
- [ ] Rate limiting on backend
- [ ] Input validation on project submissions
- [ ] No sensitive data in client code
- [ ] Environment variables for secrets
- [ ] Security headers configured

### Security Headers
```javascript
// next.config.mjs
const nextConfig = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          { key: 'X-Frame-Options', value: 'DENY' },
          { key: 'X-Content-Type-Options', value: 'nosniff' },
          { key: 'Referrer-Policy', value: 'origin-when-cross-origin' },
        ],
      },
    ];
  },
};
```

## Scaling Considerations

### Horizontal Scaling
- Use Redis for Socket.IO adapter
- Load balancer for multiple instances
- Sticky sessions for WebSocket

### Database
- Add PostgreSQL/MongoDB for task persistence
- Cache frequently accessed data
- Archive old tasks

### CDN
- Use Vercel Edge Network
- Or CloudFlare CDN
- Cache static assets

## Troubleshooting

**Build fails:**
```bash
# Clear cache
rm -rf .next node_modules
npm install
npm run build
```

**WebSocket won't connect:**
- Check CORS settings
- Verify backend is running
- Test with wscat: `npm i -g wscat && wscat -c ws://localhost:5000`

**Slow performance:**
- Enable production build
- Check Network tab for large payloads
- Profile with React DevTools

## Post-Deployment

1. **Test all features** in production
2. **Monitor logs** for errors
3. **Set up alerts** for downtime
4. **Document** any custom configuration
5. **Share** dashboard URL with team!

---

## Quick Deploy Commands

**Vercel:**
```bash
vercel --prod
```

**Docker:**
```bash
docker build -t crewai-dashboard . && docker run -p 3000:3000 crewai-dashboard
```

**PM2:**
```bash
npm run build && pm2 start npm --name crewai-dashboard -- start
```

---

**Your dashboard is ready for production!** 🎉
