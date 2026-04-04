#!/usr/bin/env python3
"""
NetworkBuster Business Intelligence (BI) Magic
Executive dashboard for financial monitoring, resource optimization, and growth tracking.
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime
import psutil

# Import existing engines for real-time data
try:
    from mission_control_engine import engine as mc_engine
except ImportError:
    mc_engine = None

PROJECT_PATH = Path(__file__).parent.resolve()

class BusinessIntelligence:
    def __init__(self):
        self.budget_data = self._parse_budget_file()
        self.start_time = datetime.now()
        
    def _parse_budget_file(self):
        """Parse BUDGET_AND_DETAILS.md for baseline financial data."""
        budget_path = PROJECT_PATH / "BUDGET_AND_DETAILS.md"
        data = {
            "azure_core": 69.77,
            "frontend": 28.95,
            "dev_tools": 21.00,
            "optional_ai": 70.00,
            "team_cost_min": 61209,
            "team_cost_max": 95084
        }
        
        if budget_path.exists():
            content = budget_path.read_text(encoding='utf-8')
            # Try to extract grand total
            total_match = re.search(r"TOTAL AZURE.*?\*\*?\$([\d.]+)", content)
            if total_match:
                data["azure_core"] = float(total_match.group(1))
            
            frontend_match = re.search(r"TOTAL FRONTEND.*?\*\*?\$([\d.]+)", content)
            if frontend_match:
                data["frontend"] = float(frontend_match.group(1))
                
            team_match = re.search(r"Total Monthly Team Cost: \$([\d,]+)-([\d,]+)", content)
            if team_match:
                data["team_cost_min"] = float(team_match.group(1).replace(',', ''))
                data["team_cost_max"] = float(team_match.group(2).replace(',', ''))
                
        return data

    def get_realtime_metrics(self):
        """Calculate real-time business metrics based on system usage."""
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        
        # Calculate eco-score and power draw if engine is available
        eco_data = {}
        if mc_engine:
            active_services = self._count_active_services()
            eco_data = mc_engine.eco.calculate_eco_score(cpu, mem, active_services)
        else:
            # Fallback calculation
            power = 15.0 + (cpu * 0.8) + (mem * 0.2)
            eco_data = {
                "power_draw_watts": round(power, 2),
                "eco_score": round(max(0, 100 - (power / 1.5)), 1)
            }
            
        # Estimate real-time infrastructure cost (simulated)
        # Base cost + usage-based scaling
        usage_multiplier = 1.0 + (cpu / 100.0) * 0.5 # Up to 50% increase under heavy load
        estimated_monthly_infra = self.budget_data["azure_core"] * usage_multiplier
        
        return {
            "system": {"cpu": cpu, "mem": mem},
            "eco": eco_data,
            "financial": {
                "estimated_monthly_infra": round(estimated_monthly_infra, 2),
                "daily_burn_rate": round(estimated_monthly_infra / 30, 2),
                "projected_annual": round(estimated_monthly_infra * 12, 2)
            }
        }

    def _count_active_services(self):
        """Count active NetworkBuster services."""
        ports = [3000, 3001, 3002, 3003, 4000, 5000, 6000, 7000, 8000]
        count = 0
        for conn in psutil.net_connections():
            if conn.laddr.port in ports and conn.status == 'LISTEN':
                count += 1
        return count

    def get_business_recommendations(self, metrics):
        """AI-driven business recommendations."""
        recs = []
        infra_cost = metrics["financial"]["estimated_monthly_infra"]
        cpu = metrics["system"]["cpu"]
        eco_score = metrics["eco"]["eco_score"]
        
        # Recommendation 1: Cost Optimization
        if cpu < 20 and infra_cost > self.budget_data["azure_core"]:
            recs.append({
                "category": "COST",
                "priority": "HIGH",
                "msg": "Infrastructure is over-provisioned for current load. Scale down Container App instances to save ~$20/mo."
            })
            
        # Recommendation 2: Spot Instances
        if cpu > 60:
            recs.append({
                "category": "OPTIMIZATION",
                "priority": "MEDIUM",
                "msg": "High sustained load detected. Consider Azure Spot Instances for training pipelines to reduce costs by 60%."
            })
            
        # Recommendation 3: Eco Sustainability
        if eco_score < 70:
            recs.append({
                "category": "ESG",
                "priority": "LOW",
                "msg": "Eco Score is dipping. Consolidate background services to improve carbon footprint and brand image."
            })
            
        # Recommendation 4: Team Allocation (Static based on budget)
        recs.append({
            "category": "STRATEGY",
            "priority": "MEDIUM",
            "msg": f"Monthly team burn is ${self.budget_data['team_cost_min']:,.0f}. Ensure DevOps/Infra is prioritized for Year 2 growth."
        })
        
        return recs

    def show_dashboard(self):
        """Display the Executive Dashboard."""
        metrics = self.get_realtime_metrics()
        recs = self.get_business_recommendations(metrics)
        
        os.system('cls' if os.name == 'nt' else 'clear')
        print("╔" + "═" * 78 + "╗")
        print("║" + "  NETWORKBUSTER EXECUTIVE BUSINESS INTELLIGENCE  ".center(78) + "║")
        print("╠" + "═" * 78 + "╣")
        
        # Financial Health
        print(f"║ 💰 FINANCIAL HEALTH OVERVIEW{' ' * 49}║")
        fin = metrics["financial"]
        print(f"║    Monthly Projected Infra:  ${fin['estimated_monthly_infra']:<10} (Target: ${self.budget_data['azure_core']}){' ' * 19}║")
        print(f"║    Daily Burn Rate:           ${fin['daily_burn_rate']:<10}{' ' * 41}║")
        print(f"║    Projected Annual:          ${fin['projected_annual']:<10}{' ' * 41}║")
        print(f"║    Estimated Team Burn:       ${self.budget_data['team_cost_min']:,.0f} - ${self.budget_data['team_cost_max']:,.0f}/mo{' ' * 23}║")
        
        print("╠" + "═" * 78 + "╣")
        
        # Resource & Eco Health
        print(f"║ ⚡ RESOURCE & SUSTAINABILITY{' ' * 49}║")
        sys_m = metrics["system"]
        eco = metrics["eco"]
        print(f"║    CPU Usage: {sys_m['cpu']:>5}% | MEM Usage: {sys_m['mem']:>5}%{' ' * 41}║")
        print(f"║    Power Draw: {eco['power_draw_watts']:>6} W | Eco Score: {eco['eco_score']:>5}/100{' ' * 38}║")
        
        print("╠" + "═" * 78 + "╣")
        
        # AI Recommendations
        print(f"║ 🔮 AI BUSINESS MAGIC RECOMMENDATIONS{' ' * 40}║")
        for r in recs:
            color = "" # Terminal colors omitted for compatibility
            priority_tag = f"[{r['priority']}]"
            category_tag = f"[{r['category']}]"
            msg = r['msg']
            # Wrap message
            wrapped_msg = [msg[i:i+60] for i in range(0, len(msg), 60)]
            print(f"║    {category_tag:<14} {priority_tag:<10} {wrapped_msg[0]:<50}║")
            for extra in wrapped_msg[1:]:
                print(f"║    {' ' * 25} {extra:<50}║")
                
        print("╚" + "═" * 78 + "╝")
        print(f"\n   Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   [R] Refresh | [Q] Exit Magic Hub")

def main():
    bi = BusinessIntelligence()
    while True:
        bi.show_dashboard()
        choice = input("\n   Command: ").strip().lower()
        if choice == 'q':
            break
        # Auto-refresh loop could be added here

if __name__ == "__main__":
    main()
