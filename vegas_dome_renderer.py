
import os
import time
import math
import sys

# ANSI Color codes for "Vegas LED" effects
GOLD = "\033[38;5;220m"
WHITE = "\033[97m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
RESET = "\033[0m"
BOLD = "\033[1m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_dome_frame(angle):
    # Simulated spherical/dome projection of ASCII art
    # Using math to create a "pulsing" and "curved" effect
    radius = 20
    output = []
    
    # Text to display on the dome
    text = "NASA LAUNCH DAY - NETWORKBUSTER SUITE - ARTEMIS II"
    
    for y in range(-radius, radius + 1, 2):
        line = ""
        for x in range(-radius * 2, radius * 2 + 1):
            dist = math.sqrt((x/2)**2 + y**2)
            if dist < radius:
                # Create a dynamic pulsing effect based on distance and time
                pulse = (dist - angle * 5) % 10
                if pulse < 2:
                    line += f"{GOLD}*{RESET}"
                elif pulse < 4:
                    line += f"{WHITE}.{RESET}"
                else:
                    line += " "
            else:
                line += " "
        output.append(line.center(80))
    return "\n".join(output)

def show_launch_countdown():
    for i in range(10, 0, -1):
        clear_screen()
        print(f"\n\n{GOLD}{BOLD}" + " T-MINUS ".center(80, "=") + f"{RESET}")
        print(f"\n{WHITE}{BOLD}" + f" {i} ".center(80) + f"{RESET}\n")
        print(f"{CYAN}" + "VEGAS DOME PREPARING FOR LUNAR INSERTION".center(80) + f"{RESET}")
        time.sleep(1)

from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)

DOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NASA Vegas Dome | Live Feed</title>
    <style>
        :root { --bg: #000; --gold: #ffcc00; --cyan: #00ffff; }
        body { background: var(--bg); color: #fff; font-family: 'Segoe UI', sans-serif; overflow: hidden; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
        .dome-container { width: 600px; height: 600px; border-radius: 50%; border: 4px solid var(--gold); position: relative; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle at center, #111 0%, #000 100%); box-shadow: 0 0 50px rgba(255, 204, 0, 0.3); }
        .text-overlay { position: absolute; text-align: center; width: 100%; z-index: 10; }
        .mission-title { font-size: 1.5rem; color: var(--gold); letter-spacing: 5px; text-transform: uppercase; margin-bottom: 10px; text-shadow: 0 0 10px var(--gold); }
        .status-box { background: rgba(0, 255, 255, 0.1); border: 1px solid var(--cyan); padding: 10px 20px; color: var(--cyan); display: inline-block; font-family: monospace; }
        .grid-lines { position: absolute; width: 100%; height: 100%; border-radius: 50%; background-image: linear-gradient(rgba(255,204,0,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,204,0,0.1) 1px, transparent 1px); background-size: 40px 40px; }
        @keyframes pulse { 0% { transform: scale(1); opacity: 0.8; } 50% { transform: scale(1.05); opacity: 1; } 100% { transform: scale(1); opacity: 0.8; } }
        .pulsing-orb { width: 200px; height: 200px; background: radial-gradient(circle, var(--gold) 0%, transparent 70%); border-radius: 50%; animation: pulse 4s infinite ease-in-out; filter: blur(20px); }
    </style>
</head>
<body>
    <div class="dome-container">
        <div class="grid-lines"></div>
        <div class="pulsing-orb"></div>
        <div class="text-overlay">
            <div class="mission-title">NASA VEGAS DOME</div>
            <div class="status-box">STATUS: MISSION_NOMINAL</div>
            <p style="margin-top: 20px; font-size: 0.8rem; color: #888;">COORDINATES: 36.1147° N, 115.1728° W</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(DOME_HTML)

def run_web_server():
    app.run(host='0.0.0.0', port=9000)

def run_dome_display():
    # Start web server in background
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    angle = 0
    try:
        while True:
            clear_screen()
            print(f"{GOLD}{BOLD}" + " NASA VEGAS DOME - EXTERIOR DISPLAY ".center(80, "=") + f"{RESET}")
            print(get_dome_frame(angle))
            print(f"\n{CYAN}{BOLD}" + " [ ARTEMIS MISSION STATUS: NOMINAL ] ".center(80) + f"{RESET}")
            print(f"{MAGENTA}" + " LIVE FROM LAS VEGAS STRIP ".center(80) + f"{RESET}")
            angle += 0.1
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n\n🛑 Dome display standby...")

if __name__ == "__main__":
    if "--launch" in sys.argv:
        show_launch_countdown()
    run_dome_display()
