#!/usr/bin/env python3
"""
NetworkBuster Quick Admin Commands
Fast access to common admin operations
"""

import ctypes
import subprocess
import sys
import os
from pathlib import Path

PROJECT_PATH = Path(__file__).parent.resolve()


def is_admin():
    """Check if running as administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_elevated(func):
    """Decorator to run function with admin privileges."""
    def wrapper(*args, **kwargs):
        if not is_admin():
            print("↑ Elevating to Administrator...")
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable,
                f'"{__file__}" {func.__name__}',
                str(PROJECT_PATH), 1
            )
            return
        return func(*args, **kwargs)
    return wrapper


def ps(cmd, show=True):
    """Run PowerShell command."""
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", cmd],
        capture_output=True, text=True
    )
    if show and result.stdout:
        print(result.stdout)
    if result.stderr:
        print(f"Error: {result.stderr}")
    return result


def cmd(command, show=True):
    """Run CMD command."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if show and result.stdout:
        print(result.stdout)
    return result


# ============================================================
# Quick Commands
# ============================================================

def start_servers():
    """Start all NetworkBuster servers."""
    print("🚀 Starting NetworkBuster servers...")
    os.chdir(PROJECT_PATH)
    subprocess.Popen(
        ["node", "start-servers.js"],
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    print("✓ Servers starting in new window")


def stop_servers():
    """Stop all Node.js processes."""
    print("🛑 Stopping Node.js processes...")
    ps("Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force")
    print("✓ All Node.js processes stopped")


def restart_servers():
    """Restart all servers."""
    stop_servers()
    import time
    time.sleep(2)
    start_servers()


def check_ports():
    """Check server port status."""
    print("\n🔌 Port Status:")
    print("-" * 40)
    for port in [3000, 3001, 3002, 3003]:
        result = ps(f"Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue", show=False)
        status = "🟢 ACTIVE" if result.stdout.strip() else "⚪ FREE"
        print(f"  Port {port}: {status}")


def kill_port(port):
    """Kill process using a specific port."""
    print(f"🔪 Killing process on port {port}...")
    ps(f'''
$conn = Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue
if ($conn) {{
    Stop-Process -Id $conn.OwningProcess -Force
    Write-Output "Killed process on port {port}"
}} else {{
    Write-Output "No process found on port {port}"
}}
''')


@run_elevated
def set_execution_policy():
    """Set PowerShell execution policy to RemoteSigned."""
    print("🔧 Setting execution policy...")
    ps("Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force")
    print("✓ Execution policy set to RemoteSigned")


@run_elevated
def open_firewall():
    """Open firewall ports for NetworkBuster."""
    print("🔥 Opening firewall ports...")
    ports = [
        (3000, "NetworkBuster-Web"),
        (3001, "NetworkBuster-API"),
        (3002, "NetworkBuster-Audio"),
        (3003, "NetworkBuster-Auth")
    ]
    for port, name in ports:
        ps(f'New-NetFirewallRule -DisplayName "{name}" -Direction Inbound -Protocol TCP -LocalPort {port} -Action Allow -ErrorAction SilentlyContinue')
        print(f"  ✓ Port {port} ({name})")
    print("✓ Firewall configured")


@run_elevated  
def flush_dns():
    """Flush DNS cache."""
    print("🌐 Flushing DNS cache...")
    cmd("ipconfig /flushdns")
    print("✓ DNS cache flushed")


def show_ip():
    """Show IP addresses."""
    print("\n🌐 Network Information:")
    print("-" * 40)
    ps("Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.InterfaceAlias -notlike '*Loopback*'} | Select-Object InterfaceAlias, IPAddress | Format-Table")


def disk_status():
    """Show disk space status."""
    print("\n💾 Disk Status:")
    print("-" * 40)
    ps("Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{N='Used(GB)';E={[math]::Round($_.Used/1GB,1)}}, @{N='Free(GB)';E={[math]::Round($_.Free/1GB,1)}} | Format-Table")


def node_status():
    """Show Node.js process status."""
    print("\n📦 Node.js Processes:")
    print("-" * 40)
    ps("Get-Process node -ErrorAction SilentlyContinue | Select-Object Id, CPU, @{N='Memory(MB)';E={[math]::Round($_.WorkingSet64/1MB,1)}} | Format-Table")


def clear_logs():
    """Clear log files."""
    print("🧹 Clearing logs...")
    log_dir = PROJECT_PATH / "logs"
    if log_dir.exists():
        for f in log_dir.glob("*.log"):
            f.unlink()
            print(f"  Deleted: {f.name}")
    print("✓ Logs cleared")


def open_project():
    """Open project in VS Code."""
    print("📂 Opening project in VS Code...")
    subprocess.Popen(["code", str(PROJECT_PATH)])


def open_dashboard():
    """Open dashboard in browser."""
    print("🌐 Opening dashboard...")
    import webbrowser
    webbrowser.open("http://localhost:3000")


def open_bi_magic():
    """Launch Business Intelligence Magic Hub."""
    print("🔮 Launching Business Intelligence Magic...")
    subprocess.run([sys.executable, "business_intelligence.py"])


def open_multi_node_magic():
    """Launch Multi-Node Orchestrator."""
    print("🛰️ Launching Multi-Node Orchestrator...")
    subprocess.run([sys.executable, "multi_node_curl.py"])


# ============================================================
# Main Menu
# ============================================================

COMMANDS = {
    "1": ("Start Servers", start_services),
    "2": ("Stop Servers", stop_services),
    "3": ("Restart Servers", restart_servers),
    "4": ("Check Ports", check_ports),
    "5": ("Show IP Info", show_ip),
    "6": ("Disk Status", disk_status),
    "7": ("Node.js Status", node_status),
    "8": ("Set Execution Policy*", set_execution_policy),
    "9": ("Open Firewall Ports*", open_firewall),
    "10": ("Flush DNS*", flush_dns),
    "11": ("Clear Logs", clear_logs),
    "12": ("Open VS Code", open_project),
    "13": ("Open Dashboard", open_dashboard),
    "14": ("Business Magic Hub", open_bi_magic),
    "15": ("Multi-Node Magic Hub", open_multi_node_magic),
    "k": ("Kill Port (enter port)", lambda: kill_port(input("Port: "))),
}



def main():
    """Main menu."""
    # Handle command-line function calls
    if len(sys.argv) > 1:
        func_name = sys.argv[1]
        for _, (_, func) in COMMANDS.items():
            if func.__name__ == func_name:
                func()
                return
    
    print("=" * 50)
    print("  NetworkBuster Quick Admin")
    print("=" * 50)
    print(f"  Admin: {'✓ Yes' if is_admin() else '✗ No (some options need elevation)'}")
    print("  * = Requires Admin")
    print()
    
    while True:
        print("\n📋 Quick Commands:")
        for key, (name, _) in COMMANDS.items():
            print(f"  [{key}] {name}")
        print("  [q] Quit")
        print()
        
        choice = input("Command: ").strip().lower()
        
        if choice == "q":
            print("👋 Goodbye!")
            break
        elif choice in COMMANDS:
            print()
            COMMANDS[choice][1]()
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()
