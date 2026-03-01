"""
Performance testing script for packaged DocManager application.
Measures memory usage, CPU usage, startup time, and response times.
"""

import time
import psutil
import requests
import subprocess
import sys
from datetime import datetime


class PerformanceTester:
    def __init__(self, backend_url="http://localhost:8443"):
        self.backend_url = backend_url
        self.process = None
        self.results = {
            "startup_time": None,
            "memory_usage_mb": [],
            "cpu_usage_percent": [],
            "api_response_times_ms": [],
            "errors": []
        }
    
    def start_backend(self, executable_path):
        """Start backend and measure startup time."""
        print("🚀 Starting backend server...")
        start_time = time.time()
        
        try:
            self.process = subprocess.Popen(
                [executable_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to be ready
            max_wait = 30
            waited = 0
            while waited < max_wait:
                try:
                    response = requests.get(f"{self.backend_url}/", timeout=1)
                    if response.status_code == 200:
                        break
                except:
                    pass
                time.sleep(1)
                waited += 1
            
            startup_time = time.time() - start_time
            self.results["startup_time"] = startup_time
            print(f"   ✅ Startup time: {startup_time:.2f}s")
            return True
            
        except Exception as e:
            self.results["errors"].append(f"Startup failed: {e}")
            print(f"   ❌ Startup failed: {e}")
            return False
    
    def measure_memory_usage(self):
        """Measure current memory usage."""
        if not self.process:
            return None
        
        try:
            proc = psutil.Process(self.process.pid)
            memory_mb = proc.memory_info().rss / 1024 / 1024
            self.results["memory_usage_mb"].append(memory_mb)
            return memory_mb
        except:
            return None
    
    def measure_cpu_usage(self, duration=5):
        """Measure CPU usage over a period."""
        if not self.process:
            return None
        
        try:
            proc = psutil.Process(self.process.pid)
            cpu_percent = proc.cpu_percent(interval=duration)
            self.results["cpu_usage_percent"].append(cpu_percent)
            return cpu_percent
        except:
            return None
    
    def test_api_response_time(self, endpoint="/"):
        """Test API response time."""
        try:
            start = time.time()
            response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
            duration_ms = (time.time() - start) * 1000
            
            if response.status_code == 200:
                self.results["api_response_times_ms"].append(duration_ms)
                return duration_ms
            else:
                self.results["errors"].append(f"API returned {response.status_code}")
                return None
        except Exception as e:
            self.results["errors"].append(f"API test failed: {e}")
            return None
    
    def run_full_test(self, executable_path, test_duration=30):
        """Run complete performance test suite."""
        print("\n" + "="*60)
        print("📊 DocManager Performance Test")
        print("="*60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Test Duration: {test_duration}s")
        print()
        
        # Start backend
        if not self.start_backend(executable_path):
            return False
        
        # Let it stabilize
        print("\n⏳ Waiting for stabilization (5s)...")
        time.sleep(5)
        
        # Measure idle performance
        print("\n📈 Measuring idle performance...")
        idle_memory = self.measure_memory_usage()
        print(f"   Memory (Idle): {idle_memory:.1f} MB")
        
        idle_cpu = self.measure_cpu_usage(duration=3)
        print(f"   CPU (Idle): {idle_cpu:.1f}%")
        
        # Test API response times
        print("\n🔥 Testing API response times...")
        for i in range(10):
            response_time = self.test_api_response_time("/")
            if response_time:
                print(f"   Request {i+1}: {response_time:.2f} ms")
            time.sleep(0.5)
        
        # Monitor during activity
        print(f"\n🏃 Monitoring under load ({test_duration}s)...")
        end_time = time.time() + test_duration
        sample_count = 0
        
        while time.time() < end_time:
            memory = self.measure_memory_usage()
            if memory and sample_count % 5 == 0:
                print(f"   Memory: {memory:.1f} MB")
            
            # Make some API calls
            self.test_api_response_time("/")
            time.sleep(2)
            sample_count += 1
        
        # Final CPU measurement
        active_cpu = self.measure_cpu_usage(duration=3)
        print(f"   CPU (Active): {active_cpu:.1f}%")
        
        # Print summary
        self.print_summary()
        
        # Stop backend
        self.stop_backend()
        
        return True
    
    def print_summary(self):
        """Print performance summary."""
        print("\n" + "="*60)
        print("📊 PERFORMANCE SUMMARY")
        print("="*60)
        
        # Startup
        if self.results["startup_time"]:
            print(f"\n🚀 Startup Time: {self.results['startup_time']:.2f}s")
            if self.results["startup_time"] < 10:
                print("   ✅ EXCELLENT (< 10s)")
            elif self.results["startup_time"] < 20:
                print("   ⚠️  ACCEPTABLE (< 20s)")
            else:
                print("   ❌ SLOW (> 20s)")
        
        # Memory
        if self.results["memory_usage_mb"]:
            avg_memory = sum(self.results["memory_usage_mb"]) / len(self.results["memory_usage_mb"])
            max_memory = max(self.results["memory_usage_mb"])
            print(f"\n💾 Memory Usage:")
            print(f"   Average: {avg_memory:.1f} MB")
            print(f"   Peak: {max_memory:.1f} MB")
            if max_memory < 200:
                print("   ✅ EXCELLENT (< 200 MB)")
            elif max_memory < 500:
                print("   ✅ GOOD (< 500 MB)")
            else:
                print("   ⚠️  HIGH (> 500 MB)")
        
        # CPU
        if self.results["cpu_usage_percent"]:
            avg_cpu = sum(self.results["cpu_usage_percent"]) / len(self.results["cpu_usage_percent"])
            print(f"\n🔥 CPU Usage:")
            print(f"   Average: {avg_cpu:.1f}%")
            if avg_cpu < 5:
                print("   ✅ EXCELLENT (< 5%)")
            elif avg_cpu < 10:
                print("   ✅ GOOD (< 10%)")
            else:
                print("   ⚠️  HIGH (> 10%)")
        
        # API Response
        if self.results["api_response_times_ms"]:
            avg_response = sum(self.results["api_response_times_ms"]) / len(self.results["api_response_times_ms"])
            max_response = max(self.results["api_response_times_ms"])
            print(f"\n⚡ API Response Time:")
            print(f"   Average: {avg_response:.2f} ms")
            print(f"   Slowest: {max_response:.2f} ms")
            if avg_response < 100:
                print("   ✅ EXCELLENT (< 100ms)")
            elif avg_response < 200:
                print("   ✅ GOOD (< 200ms)")
            else:
                print("   ⚠️  SLOW (> 200ms)")
        
        # Errors
        if self.results["errors"]:
            print(f"\n❌ Errors: {len(self.results['errors'])}")
            for error in self.results["errors"][:5]:
                print(f"   - {error}")
        else:
            print("\n✅ No errors detected")
        
        print("\n" + "="*60)
    
    def stop_backend(self):
        """Stop backend process."""
        if self.process:
            print("\n🛑 Stopping backend...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except:
                self.process.kill()
            print("   ✅ Backend stopped")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_performance.py <path_to_executable>")
        sys.exit(1)
    
    executable = sys.argv[1]
    tester = PerformanceTester()
    success = tester.run_full_test(executable, test_duration=30)
    
    sys.exit(0 if success else 1)
