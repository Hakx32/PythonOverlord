```python
import requests
import json
import subprocess
import os
import sys
import tempfile
import time
import tracemalloc
import statistics
import datetime


class BenchmarkEngine:
    """Benchmarks Python code and tracks performance"""
    
    def __init__(self):
        self.results = []
    
    def benchmark(self, code_string, runs=5, timeout=30):
        """Benchmark a piece of code by running it as subprocess"""
        times = []
        outputs = []
        errors = []
        
        for i in range(runs):
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py',
                delete=False, dir='.'
            ) as f:
                timed_code = f"""
import time
import tracemalloc

tracemalloc.start()
start = time.perf_counter()

# ---- USER CODE START ----
{code_string}
# ---- USER CODE END ----

end = time.perf_counter()
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"TIME:{{end - start}}")
print(f"MEMORY:{{peak / 1024 / 1024}}")
"""
                f.write(timed_code)
                f.flush()
                
                try:
                    result = subprocess.run(
                        ['python', f.name],
                        capture_output=True,
                        text=True,
                        timeout=timeout
                    )
                    
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if line.startswith("TIME:"):
                                times.append(float(line.split(":")[1]))
                        outputs.append(result.stdout)
                    else:
                        errors.append(result.stderr)
                        
                except subprocess.TimeoutExpired:
                    errors.append("TIMEOUT")
                finally:
                    os.unlink(f.name)
        
        if times:
            return {
                "success": True,
                "avg_time": statistics.mean(times),
                "min_time": min(times),
                "max_time": max(times),
                "runs": len(times),
                "errors": errors
            }
        else:
            return {
                "success": False,
                "avg_time": float('inf'),
                "min_time": float('inf'),
                "max_time": float('inf'),
                "runs": 0,
                "errors": errors
            }


class PythonOverlord:
    """AI-powered Python code optimizer"""
    
    def __init__(self, model="deepseek-coder-v2"):
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.benchmark = BenchmarkEngine()
        self.optimization_history = []
        self.best_solutions = {}
        self.results_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'results'
        )
        os.makedirs(self.results_dir, exist_ok=True)
    
    def ask_ai(self, prompt, temperature=0.7):
        """Send a prompt to our local AI"""
        print("🤖 AI is thinking...")
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 3000
            }
        }
        
        try:
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=120
            )
            return response.json()["response"]
        except Exception as e:
            print(f"❌ Error talking to AI: {e}")
            return None
    
    def extract_code(self, response):
        """Extract Python code from AI response"""
        if not response:
            return None
            
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0]
            return code.strip()
        elif "```" in response:
            code = response.split("```")[1].split("```")[0]
            return code.strip()
        return None
    
    def optimize(self, task, test_data_code="", iterations=5):
        """The main optimization loop"""
        
        print(f"\n{'='*60}")
        print(f"🐍👑 PYTHON OVERLORD - OPTIMIZATION SESSION")
        print(f"{'='*60}")
        print(f"📋 Task: {task}")
        print(f"🔄 Max Iterations: {iterations}")
        print(f"{'='*60}\n")
        
        best_time = float('inf')
        best_code = None
        best_version = 0
        all_attempts = []
        
        for i in range(iterations):
            print(f"\n{'─'*40}")
            print(f"🔄 ITERATION {i+1}/{iterations}")
            print(f"{'─'*40}")
            
            if i == 0:
                prompt = f"""You are an elite Python performance engineer.

TASK: {task}

TEST DATA SETUP:
{test_data_code}

Write a Python solution that is as FAST as possible.
Focus on performance and speed.
Include the test data setup in your code.
Print the result length or sum to verify correctness.

Return ONLY Python code in a ```python``` block.
No explanations. Just code."""

            else:
                history_text = "\n".join([
                    f"Version {a['version']}: {a['time']:.6f}s - {a['approach']}"
                    for a in all_attempts
                ])
                
                prompt = f"""You are an elite Python performance engineer.

TASK: {task}

TEST DATA SETUP:
{test_data_code}

PREVIOUS ATTEMPTS AND THEIR TIMES:
{history_text}

CURRENT BEST TIME: {best_time:.6f} seconds

You MUST beat {best_time:.6f} seconds!

Try a COMPLETELY DIFFERENT approach. Consider:
- NumPy vectorization
- Different algorithms
- Memory optimization
- Built-in function tricks
- List comprehensions vs generators
- Parallel processing
- Bitwise operations
- Cache optimization
- Reducing function call overhead
- Using arrays instead of lists
- Avoiding unnecessary copies
- Using map/filter instead of loops
- Struct packing
- Memory views
- Buffer protocol

Return ONLY Python code in a ```python``` block.
No explanations. Just code.
Include the test data setup.
Print the result length or sum to verify correctness."""

            # Ask AI for code
            response = self.ask_ai(prompt)
            code = self.extract_code(response)
            
            if not code:
                print("❌ AI didn't return valid code, skipping...")
                continue
            
            print(f"\n📝 Generated Code Preview:")
            print(f"{'─'*40}")
            preview = code[:500] + "..." if len(code) > 500 else code
            print(preview)
            print(f"{'─'*40}")
            
            # Benchmark it
            print(f"\n⏱️  Benchmarking...")
            result = self.benchmark.benchmark(code, runs=5, timeout=60)
            
            if result["success"]:
                avg_time = result["avg_time"]
                print(f"✅ Average Time: {avg_time:.6f}s")
                print(f"   Min Time:     {result['min_time']:.6f}s")
                print(f"   Max Time:     {result['max_time']:.6f}s")
                
                # Ask AI what approach it used
                approach_prompt = f"""In 10 words or less, what optimization technique```python
import requests
import json
import subprocess
import os
import sys
import tempfile
import time
import tracemalloc
import statistics
import datetime

class BenchmarkEngine:
    """Benchmarks Python code and tracks performance"""
    
    def __init__(self):
        self.results = []
    
    def benchmark(self, code_string, runs=5, timeout=30):
        """Benchmark a piece of code by running it as subprocess"""
        times = []
        outputs = []
        errors = []
        
        for i in range(runs):
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py',
                delete=False, dir='.'
            ) as f:
                # Wrap code with timing
                timed_code = f"""
import time
import tracemalloc

tracemalloc.start()
start = time.perf_counter()

# ---- USER CODE START ----
{code_string}
# ---- USER CODE END ----

end = time.perf_counter()
current, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"TIME:{{end - start}}")
print(f"MEMORY:{{peak / 1024 / 1024}}")
"""
                f.write(timed_code)
                f.flush()
                
                try:
                    result = subprocess.run(
                        ['python', f.name],
                        capture_output=True,
                        text=True,
                        timeout=timeout
                    )
                    
                    if result.returncode == 0:
                        for line in result.stdout.split('\n'):
                            if line.startswith("TIME:"):
                                times.append(float(line.split(":")[1]))
                            outputs.append(result.stdout)
                    else:
                        errors.append(result.stderr)
                        
                except subprocess.TimeoutExpired:
                    errors.append("TIMEOUT")
                finally:
                    os.unlink(f.name)
        
        if times:
            return {
                "success": True,
                "avg_time": statistics.mean(times),
                "min_time": min(times),
                "max_time": max(times),
                "runs": len(times),
                "errors": errors
            }
        else:
            return {
                "success": False,
                "avg_time": float('inf'),
                "min_time": float('inf'),
                "max_time": float('inf'),
                "runs": 0,
                "errors": errors
            }


class PythonOverlord:
    """AI-powered Python code optimizer"""
    
    def __init__(self, model="deepseek-coder-v2"):
        self.model = model
        self.ollama_url = "http://localhost:11434/api/generate"
        self.benchmark = BenchmarkEngine()
        self.optimization_history = []
        self.best_solutions = {}
        self.results_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'results'
        )
        os.makedirs(self.results_dir, exist_ok=True)
    
    def ask_ai(self, prompt, temperature=0.7):
        """Send a prompt to our local AI"""
        print("🤖 AI is thinking...")
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 3000
            }
        }
        
        try:
            response = requests.post(
                self.ollama_url, 
                json=payload,
                timeout=120
            )
            return response.json()["response"]
        except Exception as e:
            print(f"❌ Error talking to AI: {e}")
            return None
    
    def extract_code(self, response):
        """Extract Python code from AI response"""
        if not response:
            return None
            
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0]
            return code.strip()
        elif "```" in response:
            code = response.split("```")[1].split("```")[0]
            return code.strip()
        return None
    
    def optimize(self, task, test_data_code="", iterations=5):
        """
        The main optimization loop!
        
        task: What we want to optimize (e.g., "sort a list of 1 million integers")
        test_data_code: Python code that generates test data
        iterations: How many optimization attempts
        """
        
        print(f"\n{'='*60}")
        print(f"🐍👑 PYTHON OVERLORD - OPTIMIZATION SESSION")
        print(f"{'='*60}")
        print(f"📋 Task: {task}")
        print(f"🔄 Max Iterations: {iterations}")
        print(f"{'='*60}\n")
        
        best_time = float('inf')
        best_code = None
        best_version = 0
        all_attempts = []
        
        for i in range(iterations):
            print(f"\n{'─'*40}")
            print(f"🔄 ITERATION {i+1}/{iterations}")
            print(f"{'─'*40}")
            
            if i == 0:
                # First attempt - just solve the problem
                prompt = f"""You are an elite Python performance engineer.

TASK: {task}

TEST DATA SETUP:
{test_data_code}

Write a Python solution that is as FAST as possible.
Focus on performance and speed.
Include the test data setup in your code.
Print the result length or sum to verify correctness.

Return ONLY Python code in a ```python``` block.
No explanations. Just code."""

            else:
                # Subsequent attempts - try to beat the best
                history_text = "\n".join([
                    f"Version {a['version']}: {a['time']:.6f}s - {a['approach']}"
                    for a in all_attempts
                ])
                
                prompt = f"""You are an elite Python performance engineer.

TASK: {task}

TEST DATA SETUP:
{test_data_code}

PREVIOUS ATTEMPTS AND THEIR TIMES:
{history_text}

CURRENT BEST TIME: {best_time:.6f} seconds

You MUST beat {best_time:.6f} seconds!

Try a COMPLETELY DIFFERENT approach. Consider:
- NumPy vectorization
- Different algorithms
- Memory optimization
- Cython-like tricks
- Built-in function tricks
- List comprehensions vs generators
- Parallel processing
- Bitwise operations
- Cache optimization
- Reducing function call overhead
- Using arrays instead of lists
- Avoiding unnecessary copies

Return ONLY Python code in a ```python``` block.
No explanations. Just code.
Include the test data setup in your code.
Print the result length or sum to verify correctness."""

            # Ask AI for code
            response = self.ask_ai(prompt)
            code = self.extract_code(response)
            
            if not code:
                print("❌ AI didn't return valid code, skipping...")
                continue
            
            print(f"\n📝 Generated Code:")
            print(f"{'─'*40}")
            print(code[:500] + "..." if len(code) > 500 else code)
            print(f"{'─'*40}")
            
            # Benchmark it
            print(f"\n⏱️ Benchmarking...")

  # Ask AI what approach it used
                approach_prompt = f"""In 10 words or less, what optimization technique does this code use?

{code[:500]}"""
                approach = self.ask_ai(approach_prompt, temperature=0.1)
                if not approach:
                    approach = "Unknown approach"
                approach = approach.strip()[:100]
                
                # Track this attempt
                attempt = {
                    "version": i + 1,
                    "time": avg_time,
                    "approach": approach,
                    "code": code
                }
                all_attempts.append(attempt)
                
                # Check if this is the new best
                if avg_time < best_time:
                    improvement = ((best_time - avg_time) / best_time * 100) if best_time != float('inf') else 0
                    best_time = avg_time
                    best_code = code
                    best_version = i + 1
                    
                    if improvement > 0:
                        print(f"\n🏆🏆🏆 NEW BEST! 🏆🏆🏆")
                        print(f"📈 Improved by {improvement:.1f}%!")
                    else:
                        print(f"\n🏆 First benchmark set: {avg_time:.6f}s")
                else:
                    diff = ((avg_time - best_time) / best_time * 100)
                    print(f"\n❌ Slower by {diff:.1f}% - Best is still Version {best_version}")
            
            else:
                print(f"❌ Code failed to run!")
                for error in result["errors"][:3]:
                    print(f"   Error: {error[:200]}")
                
                all_attempts.append({
                    "version": i + 1,
                    "time": float('inf'),
                    "approach": "FAILED",
                    "code": code
                })
        
        # Final Report
        print(f"\n{'='*60}")
        print(f"🏁 OPTIMIZATION COMPLETE")
        print(f"{'='*60}")
        print(f"🏆 Best Version: {best_version}")
        print(f"⏱️  Best Time: {best_time:.6f}s")
        print(f"🔄 Total Attempts: {len(all_attempts)}")
        
        successful = [a for a in all_attempts if a['time'] != float('inf')]
        if len(successful) > 1:
            worst = max(a['time'] for a in successful)
            improvement = ((worst - best_time) / worst * 100)
            print(f"📈 Total Improvement: {improvement:.1f}%")
        
        print(f"\n📊 All Attempts:")
        for a in all_attempts:
            marker = "👑" if a['version'] == best_version else "  "
            if a['time'] == float('inf'):
                print(f"  {marker} V{a['version']}: FAILED - {a['approach']}")
            else:
                print(f"  {marker} V{a['version']}: {a['time']:.6f}s - {a['approach']}")
        
        # Save results
        self.save_results(task, all_attempts, best_code, best_version)
        
        return best_code, best_time, all_attempts
    
    def save_results(self, task, attempts, best_code, best_version):
        """Save optimization results to file"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.results_dir, f"optimization_{timestamp}.json")
        
        data = {
            "task": task,
            "timestamp": timestamp,
            "best_version": best_version,
            "attempts": [
                {
                    "version": a["version"],
                    "time": a["time"] if a["time"] != float('inf') else "FAILED",
                    "approach": a["approach"],
                    "code": a["code"]
                }
                for a in attempts
            ],
            "best_code": best_code
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
        
        # Also save best code as standalone file
        if best_code:
            code_file = os.path.join(self.results_dir, f"best_solution_{timestamp}.py")
            with open(code_file, 'w') as f:
                f.write(f"# Task: {task}\n")
                f.write(f"# Best Version: {best_version}\n")
                f.write(f"# Generated: {timestamp}\n\n")
                f.write(best_code)
            print(f"📝 Best code saved to: {code_file}")


# ============================================
#           MAIN RUNNER
# ============================================

if __name__ == "__main__":
    
    print("""
    ╔══════════════════════════════════════╗
    ║                                      ║
    ║   🐍👑 PYTHON OVERLORD v1.0         ║
    ║                                      ║
    ║   AI-Powered Code Optimizer          ║
    ║   "Making Python Unreasonably Fast"  ║
    ║                                      ║
    ╚══════════════════════════════════════╝
    """)
    
    # Initialize the Overlord
    overlord = PythonOverlord(model="deepseek-coder-v2")
    
    # ==========================================
    # TEST CHALLENGE 1: Sort 1 Million Integers
    # ==========================================
    
    task = "Sort a list of 1 million random integers as fast as possible"
    
    test_data = """
import random
random.seed(42)
data = [random.randint(0, 10_000_000) for _ in range(1_000_000)]
"""
    
    best_code, best_time, attempts = overlord.optimize(
        task=task,
        test_data_code=test_data,
        iterations=5
    )
    
    print(f"\n\n🎯 FINAL BEST CODE:")
    print(f"{'='*60}")
    print(best_code)
    print(f"{'='*60}")
