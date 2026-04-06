---
layout: home

hero:
  name: "NetworkBuster"
  text: "Mission Documentation"
  tagline: "Artemis Navigation · Lunar Recycling System · Full-Stack Infrastructure"
  image:
    src: /hero-bg.svg
    alt: NetworkBuster
  actions:
    - theme: brand
      text: 🚀 Executive Summary
      link: /01-executive-summary
    - theme: alt
      text: 📋 Quick Reference
      link: /12-quick-reference
    - theme: alt
      text: 🌐 Launch Dashboard
      link: http://localhost:3000

features:
  - icon: 🛠
    title: Hidden Tools & Scripts
    details: All automation helpers, custom scripts, and server launchers powering the NetworkBuster stack.
    link: /02-hidden-tools
  - icon: ☁️
    title: Azure Infrastructure
    details: Full cloud deployment architecture, resource groups, app services, and configuration details.
    link: /04-azure-infrastructure
  - icon: 🔧
    title: API & Server Config
    details: Express.js server setup, routes, health checks, and audio streaming endpoints.
    link: /08-api-server
  - icon: 🎛
    title: Frontend Applications
    details: React dashboards, control panels, equalizers, and the Lunar Recycling UI.
    link: /09-frontend-apps
  - icon: 🔒
    title: Security Audit
    details: Comprehensive vulnerability assessment and exposed secret remediation guide.
    link: /11-security-audit
  - icon: ⚡
    title: Quick Reference
    details: Command cheat sheet for all servers, APIs, Docker, Azure CLI, and Git hooks.
    link: /12-quick-reference

---

<style>
:root {
  --vp-home-hero-name-color: transparent;
  --vp-home-hero-name-background: linear-gradient(135deg, #6c63ff 0%, #3ecfcf 50%, #f87171 100%);
  --vp-home-hero-image-background-image: radial-gradient(ellipse at center, rgba(108,99,255,0.3) 0%, rgba(62,207,207,0.1) 60%, transparent 100%);
  --vp-home-hero-image-filter: blur(60px);
  --vp-c-brand-1: #6c63ff;
  --vp-c-brand-2: #3ecfcf;
  --vp-c-brand-3: #f87171;
}
.VPFeature .title {
  font-family: 'Outfit', sans-serif;
}
</style>
