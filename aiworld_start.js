const fs = require('fs');
const path = require('path');

const baseUrl = process.env.AIWORLD_HOST || 'http://localhost';
const universalPort = process.env.UNIVERSAL_API_PORT || '8080';
const universalUrl = `${baseUrl.replace(/\/$/, '')}:${universalPort}`;

const payload = {
  app: 'AI World - NetworkBuster',
  host: baseUrl,
  universalApi: universalUrl,
  endpoints: {
    api: `${baseUrl}:8000`,
    web: `${baseUrl}:3000`,
    mesh: `${baseUrl}:9000`,
    map: `${baseUrl}:8100`,
    analytics: `${baseUrl}:8200`,
    telemetry: `${baseUrl}:8300`,
    universalApi: universalUrl,
  },
  wifi7: {
    mode: process.env.WIFI7_MESH_MODE || 'overlay',
    interface: process.env.WIFI7_MESH_INTERFACE || 'mesh0',
    ssid: process.env.WIFI7_MESH_SSID || 'AI-World-Mesh',
    channel: process.env.WIFI7_MESH_CHANNEL || '6'
  }
};

const outFile = path.join(__dirname, 'aiworld-config.json');
fs.writeFileSync(outFile, JSON.stringify(payload, null, 2));
console.log(`Saved launch config to ${outFile}`);
console.log(JSON.stringify(payload, null, 2));
