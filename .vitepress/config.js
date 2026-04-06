// Config file for VitePress
module.exports = {
  title: 'Your Documentation Title',
  description: 'Documentation for your project.',
  themeConfig: {
    nav: [
      {
        text: '▶ Start: Connected Servers',
        items: [
          { text: 'Web Dashboard', link: 'http://localhost:3000' },
          { text: 'Web Status', link: 'http://localhost:3000/api/status' },
          { text: 'API Health', link: 'http://localhost:3001/api/health' },
          { text: 'API Root', link: 'http://localhost:3001' },
          { text: 'Audio Lab', link: 'http://localhost:3002/audio-lab' },
          { text: 'Audio Health', link: 'http://localhost:3002/api/health' },
          { text: 'Docs', link: 'http://localhost:80' }
        ]
      },
      {
        text: '🌕 Deep Lunar Tracking',
        items: [
          { text: 'Orbit Sim Health', link: 'http://localhost:3003/api/orbit/health' },
          { text: 'Orbit Sim Position', link: 'http://localhost:3003/api/orbit/position?t=0' },
          { text: 'Orbit Sim UI', link: 'http://localhost:3003' }
        ]
      }
      // ... other nav items
      
    ]
  }
};