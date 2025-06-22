"""
Notification System Integration Test Client
==========================================

This script tests the complete notification system end-to-end:
- API Gateway (Port 8080)
- Orchestrator (Port 8000)  
- Speech Service (Port 8002)
- Call Service (Port 8001)

Run this after starting all services to verify integration.
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, List
import uuid

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class NotificationTestClient:
    def __init__(self):
        self.base_urls = {
            'gateway': 'http://localhost:8080',
            'orchestrator': 'http://localhost:8000',
            'speech': 'http://localhost:8002',
            'call': 'http://localhost:8001'
        }
        self.test_phone = "+1234567890"  # Replace with your test number
        self.results = []
        
    def print_header(self, text: str):
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.RESET}\n")
    
    def print_test(self, text: str):
        print(f"{Colors.YELLOW}🧪 {text}{Colors.RESET}")
    
    def print_success(self, text: str):
        print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")
    
    def print_error(self, text: str):
        print(f"{Colors.RED}❌ {text}{Colors.RESET}")
    
    def print_info(self, text: str):
        print(f"{Colors.CYAN}ℹ️  {text}{Colors.RESET}")

    def test_service_health(self, service_name: str, url: str) -> bool:
        """Test individual service health"""
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"{service_name.title()} Service: {data.get('status', 'unknown')}")
                return True
            else:
                self.print_error(f"{service_name.title()} Service: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"{service_name.title()} Service: {str(e)}")
            return False

    def test_all_services_health(self) -> bool:
        """Test health of all services"""
        self.print_header("HEALTH CHECKS")
        
        all_healthy = True
        for service_name, url in self.base_urls.items():
            if not self.test_service_health(service_name, url):
                all_healthy = False
        
        # Test gateway's service health endpoint
        self.print_test("Testing Gateway's Service Health Check...")
        try:
            response = requests.get(f"{self.base_urls['gateway']}/services/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_success("Gateway Service Health Check: OK")
                self.print_info(f"Services Status: {json.dumps(data.get('services', {}), indent=2)}")
            else:
                self.print_error(f"Gateway Service Health Check: HTTP {response.status_code}")
                all_healthy = False
        except Exception as e:
            self.print_error(f"Gateway Service Health Check: {str(e)}")
            all_healthy = False
        
        return all_healthy

    def test_individual_services(self) -> List[Dict]:
        """Test each service individually"""
        self.print_header("INDIVIDUAL SERVICE TESTS")
        
        test_results = []
        
        # Test Speech Service
        self.print_test("Testing Speech Service...")
        try:
            response = requests.post(
                f"{self.base_urls['speech']}/speak",
                json={"message": "Speech service integration test", "priority": "medium"},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Speech Service: {data.get('status')} via {data.get('method')}")
                test_results.append({"service": "speech", "status": "success", "data": data})
            else:
                self.print_error(f"Speech Service: HTTP {response.status_code}")
                test_results.append({"service": "speech", "status": "failed", "error": f"HTTP {response.status_code}"})
        except Exception as e:
            self.print_error(f"Speech Service: {str(e)}")
            test_results.append({"service": "speech", "status": "failed", "error": str(e)})
        
        # Test Call Service
        self.print_test("Testing Call Service...")
        try:
            response = requests.post(
                f"{self.base_urls['call']}/call",
                json={
                    "phone_number": self.test_phone,
                    "message": "Call service integration test",
                    "priority": "high"
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Call Service: {data.get('status')}")
                if data.get('call_sid'):
                    self.print_info(f"Call SID: {data.get('call_sid')}")
                test_results.append({"service": "call", "status": "success", "data": data})
            else:
                self.print_error(f"Call Service: HTTP {response.status_code}")
                test_results.append({"service": "call", "status": "failed", "error": f"HTTP {response.status_code}"})
        except Exception as e:
            self.print_error(f"Call Service: {str(e)}")
            test_results.append({"service": "call", "status": "failed", "error": str(e)})
        
        # Test Orchestrator
        self.print_test("Testing Orchestrator Service...")
        try:
            response = requests.post(
                f"{self.base_urls['orchestrator']}/process",
                json={
                    "id": f"test-{uuid.uuid4()}",
                    "message": "Orchestrator integration test",
                    "priority": "medium"
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"Orchestrator: {data.get('status')}")
                self.print_info(f"Results: Speech={data.get('results', {}).get('speech', {}).get('status')}")
                test_results.append({"service": "orchestrator", "status": "success", "data": data})
            else:
                self.print_error(f"Orchestrator: HTTP {response.status_code}")
                test_results.append({"service": "orchestrator", "status": "failed", "error": f"HTTP {response.status_code}"})
        except Exception as e:
            self.print_error(f"Orchestrator: {str(e)}")
            test_results.append({"service": "orchestrator", "status": "failed", "error": str(e)})
        
        return test_results

    def test_end_to_end_scenarios(self) -> List[Dict]:
        """Test complete end-to-end scenarios"""
        self.print_header("END-TO-END INTEGRATION TESTS")
        
        scenarios = [
            {
                "name": "Low Priority Notification",
                "data": {
                    "message": "Low priority test - disk space warning",
                    "priority": "low",
                    "source": "integration_test"
                },
                "expected_services": ["speech"]
            },
            {
                "name": "Medium Priority Notification", 
                "data": {
                    "message": "Medium priority test - CPU usage high",
                    "priority": "medium",
                    "source": "integration_test"
                },
                "expected_services": ["speech"]
            },
            {
                "name": "High Priority Notification",
                "data": {
                    "message": "High priority test - server failure detected",
                    "priority": "high",
                    "phone_number": self.test_phone,
                    "source": "integration_test"
                },
                "expected_services": ["speech", "call"]
            },
            {
                "name": "Critical Priority Notification",
                "data": {
                    "message": "Critical priority test - system down",
                    "priority": "critical",
                    "source": "integration_test"
                },
                "expected_services": ["speech", "call"]
            }
        ]
        
        results = []
        
        for scenario in scenarios:
            self.print_test(f"Testing: {scenario['name']}")
            
            try:
                # Create notification via Gateway
                response = requests.post(
                    f"{self.base_urls['gateway']}/api/v1/notifications",
                    json=scenario['data'],
                    timeout=30
                )
                
                if response.status_code == 200:
                    notification_data = response.json()
                    notification_id = notification_data.get('id')
                    
                    self.print_success(f"Notification created: {notification_id}")
                    self.print_info(f"Status: {notification_data.get('status')}")
                    
                    # Wait a moment for processing
                    time.sleep(2)
                    
                    # Retrieve notification details
                    detail_response = requests.get(
                        f"{self.base_urls['gateway']}/api/v1/notifications/{notification_id}",
                        timeout=10
                    )
                    
                    if detail_response.status_code == 200:
                        details = detail_response.json()
                        results.append({
                            "scenario": scenario['name'],
                            "status": "success",
                            "notification_id": notification_id,
                            "data": details
                        })
                        
                        # Check results
                        notification_results = details.get('results', {})
                        
                        if 'speech' in scenario['expected_services']:
                            speech_status = notification_results.get('speech', {}).get('status')
                            if speech_status == 'success':
                                self.print_success("✓ Speech notification delivered")
                            else:
                                self.print_error(f"✗ Speech notification failed: {speech_status}")
                        
                        if 'call' in scenario['expected_services']:
                            call_status = notification_results.get('call', {}).get('status') if notification_results.get('call') else None
                            if call_status == 'success':
                                self.print_success("✓ Call notification delivered")
                            elif call_status:
                                self.print_error(f"✗ Call notification failed: {call_status}")
                            else:
                                self.print_error("✗ Call notification not attempted")
                    else:
                        self.print_error(f"Failed to retrieve notification details: HTTP {detail_response.status_code}")
                        results.append({
                            "scenario": scenario['name'],
                            "status": "partial",
                            "error": "Could not retrieve details"
                        })
                else:
                    self.print_error(f"Failed to create notification: HTTP {response.status_code}")
                    results.append({
                        "scenario": scenario['name'],
                        "status": "failed",
                        "error": f"HTTP {response.status_code}"
                    })
                    
            except Exception as e:
                self.print_error(f"Scenario failed: {str(e)}")
                results.append({
                    "scenario": scenario['name'],
                    "status": "failed",
                    "error": str(e)
                })
            
            print()  # Add spacing between scenarios
        
        return results

    def test_notification_retrieval(self):
        """Test notification listing and retrieval"""
        self.print_header("NOTIFICATION RETRIEVAL TESTS")
        
        self.print_test("Testing notification listing...")
        try:
            response = requests.get(f"{self.base_urls['gateway']}/api/v1/notifications", timeout=10)
            if response.status_code == 200:
                data = response.json()
                notifications = data.get('notifications', [])
                self.print_success(f"Retrieved {len(notifications)} notifications")
                
                if notifications:
                    latest = notifications[-1]
                    self.print_info(f"Latest notification: {latest.get('id')} - {latest.get('priority')} - {latest.get('status')}")
                else:
                    self.print_info("No notifications found")
            else:
                self.print_error(f"Failed to list notifications: HTTP {response.status_code}")
        except Exception as e:
            self.print_error(f"Notification listing failed: {str(e)}")

    def generate_report(self):
        """Generate final test report"""
        self.print_header("INTEGRATION TEST REPORT")
        
        print(f"{Colors.WHITE}Test completed at: {datetime.now().isoformat()}{Colors.RESET}")
        print(f"{Colors.WHITE}Services tested:{Colors.RESET}")
        for service_name, url in self.base_urls.items():
            print(f"  • {service_name.title()}: {url}")
        
        print(f"\n{Colors.WHITE}Test phone number: {self.test_phone}{Colors.RESET}")
        print(f"{Colors.YELLOW}Note: Update the test_phone variable with your actual number for call testing{Colors.RESET}")
        
        print(f"\n{Colors.WHITE}Expected behavior:{Colors.RESET}")
        print("  • Low/Medium priority: Speech notification only")
        print("  • High/Critical priority: Speech + Phone call")
        print("  • All notifications stored and retrievable via API")

def main():
    """Main test execution"""
    print(f"{Colors.BOLD}{Colors.GREEN}")
    print("🚀 NOTIFICATION SYSTEM INTEGRATION TEST")
    print("=====================================")
    print(f"{Colors.RESET}")
    
    # Initialize test client
    client = NotificationTestClient()
    
    # Update test phone number
    print(f"{Colors.YELLOW}Current test phone number: {client.test_phone}{Colors.RESET}")
    user_input = input(f"{Colors.WHITE}Press Enter to use this number, or type a new number: {Colors.RESET}").strip()
    if user_input:
        client.test_phone = user_input
        print(f"{Colors.GREEN}Updated test phone number to: {client.test_phone}{Colors.RESET}")
    
    try:
        # Step 1: Health checks
        if not client.test_all_services_health():
            print(f"\n{Colors.RED}❌ Some services are not healthy. Please check your services before continuing.{Colors.RESET}")
            response = input(f"{Colors.WHITE}Continue anyway? (y/N): {Colors.RESET}").strip().lower()
            if response != 'y':
                sys.exit(1)
        
        # Step 2: Individual service tests
        individual_results = client.test_individual_services()
        
        # Step 3: End-to-end integration tests
        e2e_results = client.test_end_to_end_scenarios()
        
        # Step 4: Test notification retrieval
        client.test_notification_retrieval()
        
        # Step 5: Generate report
        client.generate_report()
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 Integration test completed!{Colors.RESET}")
        print(f"{Colors.CYAN}Check your speakers for speech notifications and phone for calls.{Colors.RESET}")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}Test failed with error: {str(e)}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()