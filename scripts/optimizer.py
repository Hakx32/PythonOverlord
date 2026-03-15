
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
    def __init__(self):
        self.results = []
    
    def benchmark(self, code_string, runs=5, timeout=30):
        times = []
        outputs = []
        errors = []
        
        for i in range(runs):
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py',
                delete=False, dir='.'
            ) as f:
                timed_code = (
                    "import time\n"
                    "import tracemalloc\n\n"
                    "tracemalloc.start()\n"
                    "start = time.perf_counter()\n\n"
                    + code_string + "\n\n"
                    "end = time.perf_counter()\n"
                    "current, peak = tracemalloc.get_traced_memory()\n"
                    "tracemalloc.stop()\n\n"
                    "print('TIME:' + str(end - start))\n"
                    "print('MEMORY:' + str(peak / 1024 / 1024))\n"
                )
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
        print("AI is thinking...")
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
            print("Error talking to AI: " + str(e))
            return None
    
    def extract_code(self, response):
        if not response:
            return None
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0]
            return code.strip()
        elif "```" in response:
            code = response.split("```")[1].split("```")[0]
            return code.strip()
        return None
    
    def format_time(self, t):
        return str(round(t, 6))
    def optimize(self, task, test_data_code="", iterations=5):
        print("\n" + "=" * 60)
        print("PYTHON OVERLORD - OPTIMIZATION SESSION")
        print("=" * 60)
        print("Task: " + task)
        print("Max Iterations: " + str(iterations))
        print("=" * 60 + "\n")
        
        best_time = float('inf')
        best_code = None
        best_version = 0
        all_attempts = []
        
        for i in range(iterations):
            print("\n" + "-" * 40)
            print("ITERATION " + str(i + 1) + "/" + str(iterations))
            print("-" * 40)
            
            if i == 0:
                prompt = (
                    "You are an elite Python performance engineer.\n\n"
                    "TASK: " + task + "\n\n"
                    "TEST DATA SETUP:\n"
                    + test_data_code + "\n\n"
                    "Write a Python solution that is as FAST as possible.\n"
                    "Focus on performance and speed.\n"
                    "Include the test data setup in your code.\n"
                    "Print the result length or sum to verify correctness.\n\n"
                    "Return ONLY Python code in a ```python``` block.\n"
                    "No explanations. Just code."
                )
            else:
                history_parts = []
                for a in all_attempts:
                    line = ("Version " + str(a["version"]) + ": "
                            + self.format_time(a["time"]) + "s - "
                            + a["approach"])
                    history_parts.append(line)
                history_text = "\n".join(history_parts)
                best_time_str = self.format_time(best_time)
                
                prompt = (
                    "You are an elite Python performance engineer.\n\n"
                    "TASK: " + task + "\n\n"
                    "TEST DATA SETUP:\n"
                    + test_data_code + "\n\n"
                    "PREVIOUS ATTEMPTS AND THEIR TIMES:\n"
                    + history_text + "\n\n"
                    "CURRENT BEST TIME: " + best_time_str + " seconds\n\n"
                    "You MUST beat " + best_time_str + " seconds!\n\n"
                    "Try a COMPLETELY DIFFERENT approach. Consider:\n"
                    "- NumPy vectorization\n"
                    "- Different algorithms\n"
                    "- Memory optimization\n"
                    "- Built-in function tricks\n"
                    "- List comprehensions vs generators\n"
                    "- Parallel processing\n"
                    "- Bitwise operations\n"
                    "- Cache optimization\n"
                    "- Reducing function call overhead\n"
                    "- Using arrays instead of lists\n"
                    "- Avoiding unnecessary copies\n\n"
                    "Return ONLY Python code in a ```python``` block.\n"
                    "No explanations. Just code.\n"
                    "Include the test data setup.\n"
                    "Print the result length or sum to verify correctness."
                )
            
            response = self.ask_ai(prompt)
            code = self.extract_code(response)
            
            if not code:
                print("AI didn't return valid code, skipping...")
                continue
            
            print("\nGenerated Code Preview:")
            print("-" * 40)
            if len(code) > 500:
                print(code[:500] + "...")
            else:
                print(code)
            print("-" * 40)
            
            print("\nBenchmarking...")
            result = self.benchmark.benchmark(code, runs=5, timeout=60)
            
            if result["success"]:
                avg_time = result["avg_time"]
                print("Avg Time: " + self.format_time(avg_time) + "s")
                print("Min Time: " + self.format_time(result["min_time"]) + "s")
                print("Max Time: " + self.format_time(result["max_time"]) + "s")
                
                approach_prompt = (
                    "In 10 words or less, what optimization "
                    "technique does this code use?\n\n"
                    + code[:500]
                )
                approach = self.ask_ai(approach_prompt, temperature=0.1)
                if not approach:
                    approach = "Unknown approach"
                approach = approach.strip()[:100]
                
                attempt = {
                    "version": i + 1,
                    "time": avg_time,
                    "approach": approach,
                    "code": code
                }
                all_attempts.append(attempt)
                
                if avg_time < best_time:
                    if best_time != float('inf'):
                        improvement = ((best_time - avg_time) / best_time) * 100
                        print("\nNEW BEST!")
                        print("Improved by " + str(round(improvement, 1)) + "%!")
                    else:
                        print("\nFirst benchmark set: " + self.format_time(avg_time) + "s")
                    best_time = avg_time
                    best_code = code
                    best_version = i + 1
                else:
                    diff = ((avg_time - best_time) / best_time) * 100
                    print("\nSlower by " + str(round(diff, 1)) + "% - Best is still Version " + str(best_version))
            else:
                print("Code failed to run!")
                for error in result["errors"][:3]:
                    print("Error: " + error[:200])
                all_attempts.append({
                    "version": i + 1,
                    "time": float('inf'),
                    "approach": "FAILED",
                    "code": code
                })
        
        print("\n" + "=" * 60)
        print("OPTIMIZATION COMPLETE")
        print("=" * 60)
        print("Best Version: " + str(best_version))
        print("Best Time: " + self.format_time(best_time) + "s")
        print("Total Attempts: " + str(len(all_attempts)))
        
        successful = [a for a in all_attempts if a["time"] != float('inf')]
        if len(successful) > 1:
            worst = max(a["time"] for a in successful)
            improvement = ((worst - best_time) / worst) * 100
            print("Total Improvement: " + str(round(improvement, 1)) + "%")
        
        print("\nAll Attempts:")
        for a in all_attempts:
            if a["version"] == best_version:
                marker = "WINNER "
            else:
                marker = "       "
            if a["time"] == float('inf'):
                print(marker + "V" + str(a["version"]) + ": FAILED - " + a["approach"])
            else:
                print(marker + "V" + str(a["version"]) + ": " + self.format_time(a["time"]) + "s - " + a["approach"])
        
        self.save_results(task, all_attempts, best_code, best_version)
        return best_code, best_time, all_attempts
    def save_results(self, task, attempts, best_code, best_version):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.results_dir, "optimization_" + timestamp + ".json")
        
        attempt_data = []
        for a in attempts:
            t = a["time"]
            if t == float('inf'):
                t = "FAILED"
            attempt_data.append({
                "version": a["version"],
                "time": t,
                "approach": a["approach"],
                "code": a["code"]
            })
        
        data = {
            "task": task,
            "timestamp": timestamp,
            "best_version": best_version,
            "attempts": attempt_data,
            "best_code": best_code
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print("\nResults saved to: " + filename)
        
        if best_code:
            code_file = os.path.join(
                self.results_dir,
                "best_solution_" + timestamp + ".py"
            )
            with open(code_file, 'w') as f:
                f.write("# Task: " + task + "\n")
                f.write("# Best Version: " + str(best_version) + "\n")
                f.write("# Generated: " + timestamp + "\n\n")
                f.write(best_code)
            print("Best code saved to: " + code_file)


if __name__ == "__main__":
    
    print("")
    print("=" * 50)
    print("")
    print("   PYTHON OVERLORD v1.0")
    print("   AI-Powered Code Optimizer")
    print("   Making Python Unreasonably Fast")
    print("")
    print("=" * 50)
    print("")
    
    overlord = PythonOverlord(model="deepseek-coder-v2")
    
    task = "Sort a list of 1 million random integers as fast as possible"
    
    test_data = (
        "import random\n"
        "random.seed(42)\n"
        "data = [random.randint(0, 10000000) for _ in range(1000000)]\n"
    )
    
    best_code, best_time, attempts = overlord.optimize(
        task=task,
        test_data_code=test_data,
        iterations=5
    )
    
    print("\n\nFINAL BEST CODE:")
    print("=" * 60)
    print(best_code)
    print("=" * 60)
