
import os
import time

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ANSI Color codes for "LED" effects
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

def get_networkbuster_logo():
    return f"""{GREEN}{BOLD}
    _   __     __                      __               __            
   / | / /__  / /__      ______  _____/ /_____  __  _______/ /____  _____
  /  |/ / _ \\/ __/ | /| / / __ \\/ ___/ //_/ __ \\/ / / / ___/ __/ _ \\/ ___/
 / /|  /  __/ /_ | |/ |/ / /_/ / /  / ,< / /_/ / /_/ (__  ) /_/  __/ /    
/_/ |_/\\___/\\__/ |__/|__/\\____/_/  /_/|_/\\____/\\__,_/____/\\__/\\___/_/     
                                                                          {RESET}"""

def get_artemis_logo():
    return f"""{CYAN}{BOLD}
          .                                            .
         / \\                                          / \\
        /   \\               ARTEMIS                  /   \\
       /_____\\              MISSION                 /_____\\
      |       |            INTEGRATION             |       |
      |   A   |             COMPLETE               |   A   |
      |_______|                                    |_______|
          |                                            |
    {RESET}"""

def get_led_arch_bundle():
    return f"""{BLUE}
    [ LED ARCHITECTURE BUNDLE - NETWORKBUSTER SUITE ]
    
    +-----------------------------------------------+
    |  {YELLOW}M-1{BLUE}  |  {GREEN}S-2{BLUE}  |  {YELLOW}M-3{BLUE}  |  {GREEN}S-4{BLUE}  |  {YELLOW}M-5{BLUE}  |  {GREEN}S-6{BLUE}  |
    | [::::] | [::::] | [::::] | [::::] | [::::] | [::::] |
    |  NODE  |  NODE  |  NODE  |  NODE  |  NODE  |  NODE  |
    +-----------------------------------------------+
    |  {CYAN}[ GATEWAY-ALPHA ]{BLUE}           {CYAN}[ GATEWAY-BETA ]{BLUE}  |
    |  STATUS: {GREEN}ONLINE{BLUE}               STATUS: {GREEN}ONLINE{BLUE}    |
    +-----------------------------------------------+
    |  {RED}[ ARTEMIS-CORE ]{BLUE}                               |
    |  PHASE: {YELLOW}LUNAR INSERTION{BLUE}                         |
    +-----------------------------------------------+
    {RESET}"""

def show_splash():
    clear_screen()
    print(get_networkbuster_logo())
    time.sleep(0.5)
    print(get_artemis_logo())
    time.sleep(0.5)
    print(get_led_arch_bundle())
    print(f"\n{BOLD}{GREEN}✓ NetworkBuster Full Suite v1.1.0 Loaded{RESET}")
    print(f"{BOLD}{CYAN}✓ Artemis Lunar Integration Active{RESET}")
    print(f"{BOLD}{YELLOW}✓ LED ASCII Architecture Bundle Ready{RESET}")

if __name__ == "__main__":
    show_splash()
