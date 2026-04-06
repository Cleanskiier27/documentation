# Survival Mode Efficiency Protocol - NLRS

This document outlines the most efficient execution sequence for the NetworkBuster Lunar Recycling System (NLRS) during **Survival Mode** (Power < 10%) and the subsequent **Recovery & Re-Entry Phase**.

## 1. Stabilization Phase (Power < 10%)
Maintain system integrity before attempting high-energy tasks.
- **Thermal Lockdown:** Divert heat only to critical electronics to prevent terminal hardware freezing during the lunar night (-173°C).
- **Beacon Synchronization:** Establish a low-power communication heartbeat every 10 minutes to signal status to the habitat.

## 2. Recovery & Re-Entry Phase (Power 10% – 25%)
Restart systems in this specific order as power returns:
- **Core Logic Boot:** Start the **Universal Server** (`server-universal.js`). It is designed to run without optional dependencies, making it the most energy-efficient entry point.
- **Health Check (Self-Diagnostics):** Run `npm run admin:verify` or the `/api/health` endpoint. Verify system integrity before moving high-current actuators.

## 3. Build & Processing Phase (Power > 25% & Solar Peak)
Execute high-energy "High-Risk Operations" only during **Lunar Noon** (±3 Earth days).
- **Resource Warm-up:** Use solar thermal augmentation to pre-heat the regolith or processing chambers.
- **Execute Build Job:** Start `ai-training-pipeline.py`.
- **Sustainability Check:** Use the **Sustainability Predictor** to calculate power cost vs. current storage before starting to avoid mid-process shutdown.
- **Telemetry Monitoring:** Activate the **Real-Time Overlay**. Halt processing immediately if `security-monitor.js` triggers an "amber alert."

## 4. Cleanup & Data Egress (Post-Build)
- **Storage Sync:** Move telemetry and build logs to **Azure Blob Storage** (`backups` container) immediately after the build to prevent data loss.
- **Hibernation Check:** If power drops below 20%, halt all non-essential tasks and return to Stabilization Phase.

---
**Key Efficiency Rule:** Always prioritize **Thermal Management** over **Processing**. A processing error can be retried; a thermal failure (hardware freeze) is terminal.
