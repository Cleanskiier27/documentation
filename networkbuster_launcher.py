"""
NetworkBuster - All-in-One Launch Manager
Unified program to launch and manage all NetworkBuster services
Includes scheduled launch functionality
"""

import os
import sys
import subprocess
import time
import threading
import json
from datetime import datetime, timedelta
from pathlib import Path
import webbrowser
import schedule

import networkbuster_ascii_art

# Service configuration
SERVICES = [
    {
        'name': 'Web Server',
        'port': 3000,
        'command': 'node server-universal.js',
        'type': 'node',
        'critical': True,
        'startup_delay': 0
    },
    {
        'name': 'API Server',
        'port': 3001,
        'command': 'node server-universal.js',
        'cwd': 'api',
        'type': 'node',
        'critical': True,
        'startup_delay': 2
    },
    {
        'name': 'Audio Stream',
        'port': 3002,
        'command': 'node server-audio.js',
        'type': 'node',
        'critical': False,
        'startup_delay': 4
    },
    {
        'name': 'Mission Control',
        'port': 5000,
        'command': 'python nasa_home_base.py',
        'type': 'python',
        'critical': True,
        'startup_delay': 6
    },
    {
        'name': 'Network Map',
        'port': 6000,
        'command': 'python network_map_viewer.py',
        'type': 'python',
        'critical': False,
        'startup_delay': 8
    },
    {
        'name': 'Universal Launcher',
        'port': 7000,
        'command': 'python universal_launcher.py',
        'type': 'python',
        'critical': False,
        'startup_delay': 10
    },
    {
        'name': 'YouTube Trends',
        'port': 8001,
        'command': 'python youtube_trends_service.py',
        'type': 'python',
        'critical': False,
        'startup_delay': 11
    },
    {
        'name': 'API Tracer',
        'port': 8000,
        'command': 'python api_tracer.py',
        'type': 'python',
        'critical': False,
        'startup_delay': 12
    },
    {
        'name': 'Vegas Dome',
        'port': 9000,
        'command': 'python vegas_dome_renderer.py',
        'type': 'python',
        'critical': False,
        'startup_delay': 14
    },
    {
        'name': 'Test Center',
        'port': 4000,
        'command': 'python networkbuster_test_center.py',
        'type': 'python',
        'critical': False,
        'startup_delay': 16
    },
    {
        'name': 'Nexus One VM',
        'port': 9001,
        'command': 'python arch_matrix_vm.py',
        'type': 'python',
        'critical': False,
        'startup_delay': 18
    }
]

# Scheduled launch configuration
LAUNCH_DATE = datetime(2026, 1, 17, 9, 0, 0)  # January 17, 2026 at 9:00 AM
CONFIG_FILE = 'networkbuster_config.json'

class NetworkBusterManager:
    def __init__(self):
        self.processes = {}
        self.running = False
        self.config = self.load_config()
    
    def apply_production_optimizations(self):
        """Apply max power optimizations for production"""
        networkbuster_ascii_art.show_splash()
        print("\n🔥 APPLYING MAX POWER PRODUCTION OPTIMIZATIONS...")
        print("="*60)
        
        try:
            # High Performance Power Plan
            print("⚡ Setting Ultimate Performance power plan...")
            subprocess.run('powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c', 
                          shell=True, capture_output=True)
            
            # Disable CPU throttling
            print("🚀 Disabling CPU throttling...")
            subprocess.run('powercfg /setacvalueindex scheme_current sub_processor PROCTHROTTLEMAX 100', 
                          shell=True, capture_output=True)
            subprocess.run('powercfg /setactive scheme_current', shell=True, capture_output=True)
            
            # Optimize network stack
            print("🌐 Maximizing network throughput...")
            subprocess.run('netsh int tcp set global autotuninglevel=experimental', 
                          shell=True, capture_output=True)
            subprocess.run('netsh int tcp set global chimney=enabled', 
                          shell=True, capture_output=True)
            subprocess.run('netsh int tcp set global rss=enabled', 
                          shell=True, capture_output=True)
            
            # Set process priority to realtime
            print("🎯 Setting realtime process priority...")
            import psutil
            p = psutil.Process()
            p.nice(psutil.REALTIME_PRIORITY_CLASS)
            
            print("✅ Max power production optimizations applied!")
            print("="*60 + "\n")
            
        except Exception as e:
            print(f"⚠️  Some optimizations require admin privileges: {e}")
            print("   Run with administrator for full power mode\n")
        
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        return {
            'auto_launch': True,
            'scheduled_launch_date': LAUNCH_DATE.isoformat(),
            'last_launch': None,
            'launch_count': 0,
            'enabled_services': [s['name'] for s in SERVICES]
        }
    
    def save_config(self):
        """Save configuration to file"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def check_port(self, port):
        """Check if port is in use"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    
    def start_service(self, service):
        """Start a single service"""
        if service['name'] not in self.config['enabled_services']:
            print(f"⏭️  Skipping {service['name']} (disabled)")
            return None
        
        print(f"\n🚀 Starting {service['name']} on port {service['port']}...")
        
        # Check if already running
        if self.check_port(service['port']):
            print(f"   ⚠️  Port {service['port']} already in use")
            return None
        
        # Build command
        env = os.environ.copy()
        env['SERVICE_NAME'] = service['name']
        if service['name'] == 'API Server':
            env['PORT'] = '3001'
        
        if service['type'] == 'python':
            cmd = f"python {service['command']}"
            if sys.platform == 'win32':
                cmd = f".venv\\Scripts\\python.exe {service['command']}"
        else:
            cmd = service['command']
        
        # Set working directory
        cwd = service.get('cwd', os.getcwd())
        if not os.path.isabs(cwd):
            cwd = os.path.join(os.getcwd(), cwd)
        
        try:
            # Start process
            if sys.platform == 'win32':
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    cwd=cwd,
                    env=env,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:
                process = subprocess.Popen(
                    cmd,
                    shell=True,
                    cwd=cwd,
                    env=env
                )
            
            # Wait a bit for startup
            time.sleep(2)
            
            # Verify it started
            if self.check_port(service['port']):
                print(f"   ✅ {service['name']} started successfully")
                self.processes[service['name']] = {
                    'process': process,
                    'service': service,
                    'started': datetime.now().isoformat()
                }
                return process
            else:
                print(f"   ❌ {service['name']} failed to start")
                return None
                
        except Exception as e:
            print(f"   ❌ Error starting {service['name']}: {e}")
            return None
    
    def start_all_services(self):
        """Start all services in order with max power production mode"""
        print("""
╔════════════════════════════════════════════════════════════╗
║  NetworkBuster All-in-One Launch Manager                 ║
║  MAX POWER PRODUCTION MODE                                ║
║  Starting all services...                                 ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        # Apply max power production optimizations
        self.apply_production_optimizations()
        
        self.running = True
        started = 0
        failed = 0
        
        for service in SERVICES:
            # Apply startup delay
            if service['startup_delay'] > 0:
                time.sleep(service['startup_delay'])
            
            result = self.start_service(service)
            
            if result:
                started += 1
            else:
                failed += 1
                if service['critical']:
                    print(f"\n⚠️  Critical service {service['name']} failed to start!")
        
        # Update config
        self.config['last_launch'] = datetime.now().isoformat()
        self.config['launch_count'] += 1
        self.save_config()
        
        # Summary
        print("\n" + "="*60)
        print("📊 LAUNCH SUMMARY")
        print("="*60)
        print(f"✅ Started: {started} services")
        print(f"❌ Failed: {failed} services")
        print(f"🕐 Launch time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📈 Total launches: {self.config['launch_count']}")
        
        # Open main dashboard
        if started > 0:
            print("\n🌐 Opening Universal Launcher dashboard...")
            time.sleep(3)
            webbrowser.open('http://localhost:7000')
        
        return started, failed
    
    def stop_all_services(self):
        """Stop all running services"""
        print("\n🛑 Stopping all services...")
        
        for name, info in self.processes.items():
            try:
                print(f"   Stopping {name}...")
                info['process'].terminate()
                info['process'].wait(timeout=5)
                print(f"   ✅ {name} stopped")
            except:
                try:
                    info['process'].kill()
                    print(f"   ⚠️  {name} force killed")
                except:
                    print(f"   ❌ Failed to stop {name}")
        
        self.processes = {}
        self.running = False
        print("\n✅ All services stopped")
    
    def check_scheduled_launch(self):
        """Check if it's time for scheduled launch"""
        scheduled_date = datetime.fromisoformat(self.config['scheduled_launch_date'])
        now = datetime.now()
        
        if now >= scheduled_date and not self.running:
            print(f"\n⏰ SCHEDULED LAUNCH TRIGGERED!")
            print(f"   Scheduled for: {scheduled_date}")
            print(f"   Current time: {now}")
            self.start_all_services()
            return True
        
        return False
    
    def countdown_to_launch(self):
        """Display countdown to scheduled launch"""
        scheduled_date = datetime.fromisoformat(self.config['scheduled_launch_date'])
        now = datetime.now()
        
        if now >= scheduled_date:
            return "LAUNCH TIME REACHED!"
        
        delta = scheduled_date - now
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"{days}d {hours}h {minutes}m {seconds}s"
    
    def get_status(self):
        """Get status of all services"""
        status = {
            'running': self.running,
            'services': {},
            'scheduled_launch': self.config['scheduled_launch_date'],
            'countdown': self.countdown_to_launch()
        }
        
        for service in SERVICES:
            is_running = self.check_port(service['port'])
            status['services'][service['name']] = {
                'port': service['port'],
                'running': is_running,
                'critical': service['critical'],
                'url': f"http://localhost:{service['port']}"
            }
        
        return status
    
    def create_startup_script(self):
        """Create startup script for Windows"""
        script_path = Path('networkbuster_startup.bat')
        
        script_content = f"""@echo off
echo ========================================
echo NetworkBuster All-in-One Launcher
echo ========================================
echo.

cd /d "%~dp0"

REM Activate virtual environment
call .venv\\Scripts\\activate.bat

REM Launch NetworkBuster
python networkbuster_launcher.py --start

echo.
echo Press any key to exit...
pause > nul
"""
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        print(f"✅ Startup script created: {script_path}")
        return script_path
    
    def create_scheduled_task(self):
        """Create Windows scheduled task with admin privileges and thumbnail extraction"""
        task_name = "NetworkBuster_ScheduledLaunch"
        scheduled_date = datetime.fromisoformat(self.config['scheduled_launch_date'])
        
        # Create task XML with elevated privileges for overclocking and thumbnail extraction
        task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>NetworkBuster Scheduled Launch - Administrator Mode with Thumbnail Extraction</Description>
    <Author>NetworkBuster</Author>
  </RegistrationInfo>
  <Triggers>
    <TimeTrigger>
      <StartBoundary>{scheduled_date.isoformat()}</StartBoundary>
      <Enabled>true</Enabled>
    </TimeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>4</Priority>
  </Settings>
  <Actions>
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-ExecutionPolicy Bypass -WindowStyle Normal -File "{os.path.join(os.getcwd(), 'run_launcher_admin.ps1')}"</Arguments>
      <WorkingDirectory>{os.getcwd()}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""
        
        # Save XML
        xml_path = Path('networkbuster_task.xml')
        with open(xml_path, 'w', encoding='utf-16') as f:
            f.write(task_xml)
        
        # Create scheduled task with admin privileges
        try:
            cmd = f'schtasks /Create /TN "{task_name}" /XML "{xml_path}" /F'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Scheduled task created: {task_name}")
                print(f"   Launch date: {scheduled_date.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Run level: Administrator (for overclocking)")
                print(f"   Priority: High")
                return True
            else:
                print(f"⚠️  Failed to create scheduled task.")
                print(f"   Error: {result.stderr}")
                print(f"   Tip: Run PowerShell as Administrator")
                return False
        except Exception as e:
            print(f"⚠️  Failed to create scheduled task: {e}")
            print(f"   Run PowerShell as Administrator for overclocking features")
            return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='NetworkBuster All-in-One Launch Manager')
    parser.add_argument('--start', action='store_true', help='Start all services')
    parser.add_argument('--stop', action='store_true', help='Stop all services')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--schedule', action='store_true', help='Create scheduled launch')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    manager = NetworkBusterManager()
    
    if args.start:
        manager.start_all_services()
        
        # Keep running and check for scheduled launches
        print("\n🔄 Manager running. Press Ctrl+C to stop all services...")
        try:
            while True:
                time.sleep(60)
                manager.check_scheduled_launch()
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping all services...")
            manager.stop_all_services()
    
    elif args.stop:
        manager.stop_all_services()
    
    elif args.status:
        status = manager.get_status()
        print("\n📊 NETWORKBUSTER STATUS")
        print("="*60)
        print(f"System Running: {status['running']}")
        print(f"Scheduled Launch: {status['scheduled_launch']}")
        print(f"Countdown: {status['countdown']}")
        print("\nServices:")
        for name, info in status['services'].items():
            status_icon = "✅" if info['running'] else "❌"
            critical = " [CRITICAL]" if info['critical'] else ""
            print(f"  {status_icon} {name:20} Port {info['port']}{critical}")
    
    elif args.schedule:
        print("\n⏰ SCHEDULED LAUNCH SETUP")
        print("="*60)
        print(f"Launch Date: {manager.config['scheduled_launch_date']}")
        print(f"Countdown: {manager.countdown_to_launch()}")
        print("\n📋 Creating startup script...")
        manager.create_startup_script()
        print("\n📅 Creating scheduled task...")
        manager.create_scheduled_task()
    
    else:
        # Interactive mode
        print("""
╔════════════════════════════════════════════════════════════╗
║  NetworkBuster All-in-One Launch Manager                 ║
║  Package all services into unified launcher              ║
╚════════════════════════════════════════════════════════════╝
        """)
        
        print("\n📦 PACKAGE INFORMATION")
        print("="*60)
        print(f"Total Services: {len(SERVICES)}")
        print(f"Critical Services: {sum(1 for s in SERVICES if s['critical'])}")
        print(f"Port Range: 3000-8000")
        print(f"Launch Count: {manager.config['launch_count']}")
        
        print("\n⏰ SCHEDULED LAUNCH")
        print("="*60)
        scheduled_date = datetime.fromisoformat(manager.config['scheduled_launch_date'])
        print(f"Scheduled Date: {scheduled_date.strftime('%A, %B %d, %Y at %I:%M %p')}")
        print(f"Countdown: {manager.countdown_to_launch()}")
        
        print("\n📋 SERVICES")
        print("="*60)
        for service in SERVICES:
            critical = " [CRITICAL]" if service['critical'] else ""
            print(f"  • {service['name']:20} Port {service['port']}{critical}")
        
        print("\n🎮 OPTIONS")
        print("="*60)
        print("1. Start all services now")
        print("2. Show status")
        print("3. Create scheduled launch")
        print("4. Configure services")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            manager.start_all_services()
            print("\n🔄 Manager running. Press Ctrl+C to stop all services...")
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                manager.stop_all_services()
        
        elif choice == '2':
            status = manager.get_status()
            print("\n📊 STATUS")
            print("="*60)
            for name, info in status['services'].items():
                status_icon = "✅ ONLINE" if info['running'] else "❌ OFFLINE"
                print(f"{name:20} {status_icon:15} {info['url']}")
        
        elif choice == '3':
            print("\n⏰ Creating scheduled launch...")
            manager.create_startup_script()
            manager.create_scheduled_task()
            print("\n✅ Scheduled launch configured!")
        
        elif choice == '4':
            print("\n⚙️  Service Configuration")
            print("="*60)
            for i, service in enumerate(SERVICES, 1):
                enabled = "✅" if service['name'] in manager.config['enabled_services'] else "❌"
                print(f"{i}. {enabled} {service['name']}")
            
            print("\nEnter service numbers to toggle (comma-separated) or 'done':")
            toggle = input().strip()
            
            if toggle.lower() != 'done':
                for num in toggle.split(','):
                    try:
                        idx = int(num.strip()) - 1
                        service = SERVICES[idx]
                        if service['name'] in manager.config['enabled_services']:
                            manager.config['enabled_services'].remove(service['name'])
                            print(f"❌ Disabled {service['name']}")
                        else:
                            manager.config['enabled_services'].append(service['name'])
                            print(f"✅ Enabled {service['name']}")
                    except:
                        pass
                
                manager.save_config()
                print("\n✅ Configuration saved!")

if __name__ == '__main__':
    main()
