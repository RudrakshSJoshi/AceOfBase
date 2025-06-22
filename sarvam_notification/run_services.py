"""
Notification System Service Launcher
===================================

This script automatically starts all 4 services in separate PowerShell windows:
1. Call Service (Port 8001)
2. Speech Service (Port 8002) 
3. Orchestrator Service (Port 8000)
4. API Gateway (Port 8080)

Each service runs in its own PowerShell window with virtual environment activated.
"""

import subprocess
import sys
import os
import time
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class ServiceLauncher:
    def __init__(self):
        self.project_dir = Path.cwd()
        self.venv_path = self.project_dir / "myenv"
        self.services = [
            {
                "name": "Call Service",
                "file": "call_service.py",
                "port": 8001,
                "description": "Handles voice calls via Twilio"
            },
            {
                "name": "Speech Service", 
                "file": "speech_service.py",
                "port": 8002,
                "description": "Text-to-speech notifications"
            },
            {
                "name": "Orchestrator Service",
                "file": "orchestrator.py", 
                "port": 8000,
                "description": "Coordinates speech and call services"
            },
            {
                "name": "API Gateway",
                "file": "gateway.py",
                "port": 8080,
                "description": "Main API entry point"
            }
        ]
    
    def print_header(self, text: str):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")
    
    def print_success(self, text: str):
        print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")
    
    def print_error(self, text: str):
        print(f"{Colors.RED}❌ {text}{Colors.RESET}")
    
    def print_info(self, text: str):
        print(f"{Colors.CYAN}ℹ️  {text}{Colors.RESET}")
    
    def print_warning(self, text: str):
        print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

    def check_prerequisites(self):
        """Check if all required files and virtual environment exist"""
        self.print_header("CHECKING PREREQUISITES")
        
        # Check virtual environment
        if not self.venv_path.exists():
            self.print_error(f"Virtual environment not found at: {self.venv_path}")
            self.print_info("Please create virtual environment first:")
            self.print_info("python -m venv myenv")
            return False
        else:
            self.print_success(f"Virtual environment found: {self.venv_path}")
        
        # Check activation script
        activate_script = self.venv_path / "Scripts" / "activate.ps1"
        if not activate_script.exists():
            activate_script = self.venv_path / "Scripts" / "Activate.ps1"
        
        if not activate_script.exists():
            self.print_error("Virtual environment activation script not found")
            return False
        else:
            self.print_success("Virtual environment activation script found")
        
        # Check service files
        missing_files = []
        for service in self.services:
            service_file = self.project_dir / service["file"]
            if service_file.exists():
                self.print_success(f"Found: {service['file']}")
                service["file_path"] = service_file
            else:
                missing_files.append(service["file"])
                self.print_error(f"Missing: {service['file']}")
        
        if missing_files:
            self.print_error(f"Missing service files: {', '.join(missing_files)}")
            self.print_info("Please ensure all service files are in the current directory")
            return False
        
        return True

    def create_powershell_command(self, service):
        """Create PowerShell command to run a service"""
        # PowerShell command that:
        # 1. Changes to project directory
        # 2. Activates virtual environment  
        # 3. Runs the Python service
        # 4. Keeps window open on error
        
        ps_command = f'''
        cd "{self.project_dir}";
        Write-Host "Starting {service['name']}..." -ForegroundColor Green;
        Write-Host "Port: {service['port']}" -ForegroundColor Cyan;
        Write-Host "Description: {service['description']}" -ForegroundColor Yellow;
        Write-Host "Activating virtual environment..." -ForegroundColor White;
        .\\myenv\\Scripts\\Activate.ps1;
        Write-Host "Running {service['file']}..." -ForegroundColor White;
        python {service['file']};
        Write-Host "Service stopped. Press any key to close..." -ForegroundColor Red;
        Read-Host;
        '''
        
        return ps_command

    def launch_service(self, service):
        """Launch a single service in a new PowerShell window"""
        try:
            ps_command = self.create_powershell_command(service)
            
            # Launch PowerShell with the command
            subprocess.Popen([
                "powershell.exe",
                "-ExecutionPolicy", "Bypass",
                "-WindowStyle", "Normal",
                "-Command", ps_command
            ], creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            self.print_success(f"Launched {service['name']} in new PowerShell window")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to launch {service['name']}: {str(e)}")
            return False

    def launch_all_services(self):
        """Launch all services in separate PowerShell windows"""
        self.print_header("LAUNCHING SERVICES")
        
        launched_count = 0
        
        for i, service in enumerate(self.services):
            self.print_info(f"Launching {service['name']} ({i+1}/{len(self.services)})...")
            
            if self.launch_service(service):
                launched_count += 1
                # Small delay between launches
                time.sleep(2)
            else:
                self.print_error(f"Failed to launch {service['name']}")
        
        return launched_count

    def show_service_info(self):
        """Display information about all services"""
        self.print_header("SERVICE INFORMATION")
        
        for service in self.services:
            print(f"{Colors.WHITE}{service['name']}{Colors.RESET}")
            print(f"  File: {service['file']}")
            print(f"  Port: {service['port']}")
            print(f"  URL:  http://localhost:{service['port']}")
            print(f"  Description: {service['description']}")
            print()

    def show_next_steps(self):
        """Show what to do after services are launched"""
        self.print_header("NEXT STEPS")
        
        print(f"{Colors.WHITE}1. Wait for all services to start (check PowerShell windows){Colors.RESET}")
        print(f"{Colors.WHITE}2. Test the system:{Colors.RESET}")
        print(f"   {Colors.CYAN}# Test all services health{Colors.RESET}")
        print(f"   {Colors.YELLOW}Invoke-RestMethod -Uri 'http://localhost:8080/services/health' -Method Get{Colors.RESET}")
        print()
        print(f"   {Colors.CYAN}# Send a test notification{Colors.RESET}")
        print(f"   {Colors.YELLOW}$body = '{{\"message\": \"Test notification\", \"priority\": \"medium\"}}'{Colors.RESET}")
        print(f"   {Colors.YELLOW}Invoke-RestMethod -Uri 'http://localhost:8080/api/v1/notifications' -Method Post -Body $body -ContentType 'application/json'{Colors.RESET}")
        print()
        print(f"{Colors.WHITE}3. Access service documentation:{Colors.RESET}")
        for service in self.services:
            print(f"   {Colors.CYAN}{service['name']}: http://localhost:{service['port']}/docs{Colors.RESET}")
        print()
        print(f"{Colors.WHITE}4. Run integration tests:{Colors.RESET}")
        print(f"   {Colors.YELLOW}python integration_test.py{Colors.RESET}")

    def run(self):
        """Main execution method"""
        self.print_header("NOTIFICATION SYSTEM SERVICE LAUNCHER")
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.print_error("Prerequisites check failed. Cannot continue.")
            input("Press Enter to exit...")
            return False
        
        # Show service information
        self.show_service_info()
        
        # Confirm launch
        print(f"{Colors.YELLOW}This will open 4 PowerShell windows, one for each service.{Colors.RESET}")
        confirm = input(f"{Colors.WHITE}Continue? (Y/n): {Colors.RESET}").strip().lower()
        if confirm and confirm not in ['y', 'yes']:
            print(f"{Colors.YELLOW}Launch cancelled.{Colors.RESET}")
            return False
        
        # Launch services
        launched_count = self.launch_all_services()
        
        # Summary
        self.print_header("LAUNCH SUMMARY")
        if launched_count == len(self.services):
            self.print_success(f"Successfully launched all {launched_count} services!")
            self.show_next_steps()
        else:
            self.print_warning(f"Launched {launched_count}/{len(self.services)} services")
            self.print_info("Check PowerShell windows for any error messages")
        
        input(f"\n{Colors.WHITE}Press Enter to exit...{Colors.RESET}")
        return launched_count == len(self.services)

def main():
    """Main entry point"""
    try:
        launcher = ServiceLauncher()
        success = launcher.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Launch interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error: {str(e)}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()