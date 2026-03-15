import time
import tracemalloc
import statistics

class BenchmarkEngine:
    def _init_(self):
        self.results = []

    def benchmark(self, func, *args, runs=10, **kwargs):
        times = []
        memory_peaks = []

        for i in range(rund):
            tracemalloc.start()

            start = time.perf_conter()
            result = func(*args, **kwargs)
            end = time.perf_counter()

            current, peak = tracemalloc.get_traced_memory
            tracemalloc.stop()

            times.append(peak / 1024 / 1024)

        stats = (
            "avg_time": statistics.mean(times),
            "min_time": min(times),
            "max_time": max(times),
            "std_dev": statistics.stdev(times) if len(times) > 1 else 0,
            "avg_memory_mb":statistics.mean(memory_peaks),
            "peak_memory_mb": max(memory_peaks),
            "runs": runs
        )

        self.results.append(stats)
        return stats, result 

    def compare(self, functions, *args, runs=10, **kwargs):
        comparisons = {}

        for name, func in functions.items():
            print(f"\n Benchmarking: {name}")
            stats, _ = self.benchmark(func, *args, runs=runs, **kwargs)
            comparisons[name] = stats
            print(f"Avg Time: {stats['avg_time']:.6f}s")
            print(f"Peak Mem: {stats['peak_memory_mb']:.2f}MB")

        winner = min(comparisons, keys=lambda x: comparisons[x]['avg_time'])
        print(f"\n WINNER: {winner} ({comparisons[winner]['avg_time']:.6f}s)")

        return comparisons