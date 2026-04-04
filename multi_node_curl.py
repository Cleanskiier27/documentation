#!/usr/bin/env python3
"""
NetworkBuster Multi-Node Orchestrator
Automated curl interactions and TCP/DNS listener management across multiple nodes.
"""

import subprocess
import sys
import os
import json
import time
from concurrent.futures import ThreadPoolExecutor

# Define standard nodes/ports
NODES = {
    "Web/Proxy": 3000,
    "Backend": 3001,
    "Audio": 3002,
    "AI Command": 4000,
    "Mission Control": 5000,
    "Network Map": 6000,
    "Launcher": 7000,
    "BI Magic": 4000 # Integrated with AI
}

class DNSManager:
    """Manages TCP listeners/firewall rules for DNS-like tasks."""
    
    @staticmethod
    def open_listener(port):
        print(f"🔓 Opening TCP Listener on port {port}...")
        rule_name = f"NetworkBuster_TCP_{port}"
        cmd = f'powershell -Command "New-NetFirewallRule -DisplayName \\"NetworkBuster TCP {port}\\" -Direction Inbound -LocalPort {port} -Protocol TCP -Action Allow -Name {rule_name}"'
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            return True
        except:
            return False

    @staticmethod
    def close_listener(port):
        print(f"🔒 Closing TCP Listener on port {port}...")
        rule_name = f"NetworkBuster_TCP_{port}"
        cmd = f'powershell -Command "Remove-NetFirewallRule -Name {rule_name}"'
        try:
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            return True
        except:
            return False

class CurlNode:
    """Automated curl interactions for a specific node."""
    
    def __init__(self, name, port):
        self.name = name
        self.port = port
        self.base_url = f"http://localhost:{port}"

    def test_health(self):
        print(f"🛰️  Pinging {self.name} Node (:{self.port})...")
        # Try /api/health or /health
        for endpoint in ["/api/health", "/health", "/"]:
            cmd = ["curl", "-s", "-o", "nul", "-w", "%{http_code}", f"{self.base_url}{endpoint}"]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.stdout == "200":
                    print(f"   ✅ {self.name} node is ALIVE")
                    return True
            except:
                pass
        print(f"   ❌ {self.name} node is UNREACHABLE")
        return False

def orchestrate_nodes():
    print("╔" + "═" * 58 + "╗")
    print("║" + "  NETWORKBUSTER MULTI-NODE ORCHESTRATOR  ".center(58) + "║")
    print("╚" + "═" * 58 + "╝")
    
    # 1. Setup Listeners (DNS Logic)
    print("\n[STEP 1] Initializing TCP Listeners...")
    dns = DNSManager()
    for port in [53, 80, 443]: # Standard DNS/Web ports for "DNS magic"
        dns.open_listener(port)

    # 2. Parallel Health Check
    print("\n[STEP 2] Multi-Node Status Verification...")
    nodes = [CurlNode(name, port) for name, port in NODES.items()]
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(lambda n: n.test_health(), nodes)

    # 3. Custom Audio Server Shortcut Action
    print("\n[STEP 3] Triggering Audio Server Shortcut...")
    subprocess.run(["curl", "-s", "http://localhost:3002/open"], capture_output=True)
    print("   ✅ Audio Lab shortcut sent")

    print("\n✨ Orchestration Complete. Systems are interlinked.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        dns = DNSManager()
        for port in [53, 80, 443]: dns.close_listener(port)
    else:
        orchestrate_nodes()
