"""
Network Tools Engine - Advanced Diagnostics & Discovery
Integrated network analysis tools for mobile and desktop interfaces
"""

import socket
import subprocess
import psutil
import platform
import time
from datetime import datetime
from typing import List, Dict, Optional

class NetworkScanner:
    """Discovers and analyzes network devices and services"""
    
    @staticmethod
    def get_local_ip() -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    @staticmethod
    def ping_host(host: str) -> Dict:
        """Ping a host and return latency metrics"""
        param = '-n' if platform.system().lower() == 'windows' else '-c'
        command = ['ping', param, '1', host]
        
        start_time = time.time()
        try:
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, timeout=2).decode()
            latency = (time.time() - start_time) * 1000
            return {
                "host": host,
                "status": "online",
                "latency_ms": round(latency, 2),
                "output": output.splitlines()[-1]
            }
        except Exception:
            return {
                "host": host,
                "status": "offline",
                "latency_ms": None,
                "error": "Timed out"
            }

    @staticmethod
    def scan_ports(host: str, ports: List[int]) -> List[Dict]:
        """Scan specific ports on a host"""
        results = []
        for port in ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            start = time.time()
            result = s.connect_ex((host, port))
            if result == 0:
                results.append({
                    "port": port,
                    "status": "open",
                    "service": socket.getservbyport(port) if port < 1024 else "custom",
                    "response_ms": round((time.time() - start) * 1000, 2)
                })
            s.close()
        return results

class BandwidthMonitor:
    """Analyzes network throughput and data usage"""
    
    @staticmethod
    def get_io_metrics() -> Dict:
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
            "timestamp": datetime.now().isoformat()
        }

class NetworkToolsEngine:
    """Main orchestrator for network operations"""
    
    def __init__(self):
        self.scanner = NetworkScanner()
        self.bandwidth = BandwidthMonitor()
        self.last_metrics = self.bandwidth.get_io_metrics()
        self.last_time = time.time()

    def get_realtime_throughput(self) -> Dict:
        """Calculate current upload/download speeds"""
        current_metrics = self.bandwidth.get_io_metrics()
        current_time = time.time()
        elapsed = current_time - self.last_time
        
        if elapsed <= 0: return {"up_kbps": 0, "down_kbps": 0}
        
        sent_diff = current_metrics["bytes_sent"] - self.last_metrics["bytes_sent"]
        recv_diff = current_metrics["bytes_recv"] - self.last_metrics["bytes_recv"]
        
        # Convert to KB/s
        up_kbps = (sent_diff / 1024) / elapsed
        down_kbps = (recv_diff / 1024) / elapsed
        
        self.last_metrics = current_metrics
        self.last_time = current_time
        
        return {
            "up_kbps": round(up_kbps, 2),
            "down_kbps": round(down_kbps, 2),
            "total_sent_mb": round(current_metrics["bytes_sent"] / (1024*1024), 2),
            "total_recv_mb": round(current_metrics["bytes_recv"] / (1024*1024), 2)
        }

    def run_full_diagnostic(self, target: Optional[str] = None) -> Dict:
        """Run a comprehensive network health check"""
        local_ip = self.scanner.get_local_ip()
        target = target or local_ip
        
        # 1. Ping test
        connectivity = self.scanner.ping_host(target)
        
        # 2. Critical Ports (NetworkBuster Services)
        critical_ports = [3000, 3001, 3002, 4000, 5000, 6000]
        port_scan = self.scanner.scan_ports(target, critical_ports)
        
        # 3. System Load
        load = {
            "cpu": psutil.cpu_percent(),
            "mem": psutil.virtual_memory().percent,
            "conns": len(psutil.net_connections())
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "local_ip": local_ip,
            "connectivity": connectivity,
            "services": port_scan,
            "system_load": load,
            "health_score": self._calculate_health(connectivity, port_scan, load)
        }

    def _calculate_health(self, conn, ports, load) -> int:
        score = 100
        if conn["status"] == "offline": score -= 50
        if len([p for p in ports if p["status"] == "open"]) < 3: score -= 20
        if load["cpu"] > 80: score -= 15
        if load["mem"] > 80: score -= 15
        return max(0, score)

# Singleton instance
nt_engine = NetworkToolsEngine()
