import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'NetworkBuster',
  description: 'Mission Documentation — Artemis Navigation · Lunar Recycling System · Full-Stack Infrastructure',
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: '🚀 Summary', link: '/01-executive-summary' },
      {
        text: '▶ Start: Connected Servers',
        items: [
          { text: 'Web Dashboard (3000)', link: 'http://localhost:3000' },
          { text: 'Web Status /api/status', link: 'http://localhost:3000/api/status' },
          { text: 'API Health (3001)', link: 'http://localhost:3001/api/health' },
          { text: 'API Root (3001)', link: 'http://localhost:3001' },
          { text: 'Audio Lab (3002)', link: 'http://localhost:3002/audio-lab' },
          { text: 'Audio Health (3002)', link: 'http://localhost:3002/api/health' },
          { text: 'Docs (80)', link: 'http://localhost:80' }
        ]
      },
      { text: '🛡 Triage: Drone Recursion', link: '/14-triage-drone-recursion' }
    ],
    sidebar: [
      { text: 'Overview', link: '/00-index' },
      { text: 'Executive Summary', link: '/01-executive-summary' },
      { text: 'Hidden Tools & Scripts', link: '/02-hidden-tools' },
      { text: 'Azure Infrastructure', link: '/04-azure-infrastructure' },
      { text: 'CI/CD Pipelines', link: '/05-cicd-pipelines' },
      { text: 'Docker Config', link: '/06-docker-config' },
      { text: 'Git Hooks', link: '/07-git-hooks' },
      { text: 'API Server', link: '/08-api-server' },
      { text: 'Frontend Apps', link: '/09-frontend-apps' },
      { text: 'Deployment Status', link: '/10-deployment-status' },
      { text: 'Security Audit', link: '/11-security-audit' },
      { text: 'Quick Reference', link: '/12-quick-reference' },
      { text: 'Schedule', link: '/13-schedule' },
      {
        text: '🛡 Triage',
        items: [
          { text: 'Drone Recursion Bug Patch', link: '/14-triage-drone-recursion' }
        ]
      }
    ],
    socialLinks: []
  }
})