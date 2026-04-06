import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'NetworkBuster Docs',
  description: 'Comprehensive documentation for the NetworkBuster Lunar Recycling System',
  lang: 'en-US',

  head: [
    ['link', { rel: 'preconnect', href: 'https://fonts.googleapis.com' }],
    ['link', { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' }],
    ['link', { href: 'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap', rel: 'stylesheet' }],
    ['meta', { name: 'theme-color', content: '#6c63ff' }],
  ],

  themeConfig: {
    logo: { light: '/logo-light.svg', dark: '/logo-dark.svg', alt: 'NetworkBuster' },
    siteTitle: 'NetworkBuster',

    nav: [
      { text: '🚀 Overview', link: '/01-executive-summary' },
      { text: '🔧 Infrastructure', link: '/04-azure-infrastructure' },
      { text: '🔒 Security', link: '/11-security-audit' },
      { text: '📅 Schedule', link: '/13-schedule' },
      { text: '📋 Quick Reference', link: '/12-quick-reference' },
      {
        text: '🌐 Live Apps',
        items: [
          { text: 'Main Dashboard', link: 'http://localhost:3000', target: '_blank' },
          { text: 'API Server', link: 'http://localhost:3001', target: '_blank' },
          { text: 'Audio Lab', link: 'http://localhost:3002/audio-lab', target: '_blank' },
        ]
      }
    ],

    sidebar: [
      {
        text: '📑 Getting Started',
        items: [
          { text: 'Index & Table of Contents', link: '/00-index' },
          { text: '01 · Executive Summary', link: '/01-executive-summary' },
        ]
      },
      {
        text: '🛠 Tools & Automation',
        items: [
          { text: '02 · Hidden Tools & Scripts', link: '/02-hidden-tools' },
          { text: '07 · Git Hooks & Automation', link: '/07-git-hooks' },
          { text: '05 · CI/CD Pipelines', link: '/05-cicd-pipelines' },
        ]
      },
      {
        text: '☁️ Cloud & Infrastructure',
        items: [
          { text: '04 · Azure Infrastructure', link: '/04-azure-infrastructure' },
          { text: '06 · Docker Configuration', link: '/06-docker-config' },
          { text: '10 · Deployment Status', link: '/10-deployment-status' },
        ]
      },
      {
        text: '⚙️ Application',
        items: [
          { text: '08 · API & Server Config', link: '/08-api-server' },
          { text: '09 · Frontend Applications', link: '/09-frontend-apps' },
        ]
      },
      {
        text: '🔐 Security & Secrets',
        items: [
          { text: '03 · Exposed Secrets', link: '/03-exposed-secrets' },
          { text: '11 · Security Audit', link: '/11-security-audit' },
        ]
      },
      {
        text: '📋 Reference',
        items: [
          { text: '12 · Quick Reference', link: '/12-quick-reference' },
          { text: '13 · Mission Schedule', link: '/13-schedule' },
        ]
      },
    ],

    search: {
      provider: 'local',
      options: {
        placeholder: 'Search NetworkBuster docs...',
      }
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com/networkbuster' }
    ],

    footer: {
      message: 'NetworkBuster Lunar Recycling System',
      copyright: 'Built with VitePress · Artemis Navigation Online'
    },

    editLink: false,
  },

  markdown: {
    lineNumbers: true,
    theme: { light: 'github-light', dark: 'one-dark-pro' }
  }
})
