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
