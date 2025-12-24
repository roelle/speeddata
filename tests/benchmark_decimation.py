"""Benchmark decimation algorithms for relay performance impact"""
import time
import numpy as np


def downsample(samples, factor):
    """Every Nth sample"""
    return samples[::factor]


def average(samples, factor):
    """Mean of windows"""
    return np.mean(samples.reshape(-1, factor), axis=1)


def min_max(samples, factor):
    """Min-max envelope"""
    reshaped = samples.reshape(-1, factor)
    mins = np.min(reshaped, axis=1)
    maxs = np.max(reshaped, axis=1)
    result = np.empty(len(mins) * 2)
    result[0::2] = mins
    result[1::2] = maxs
    return result


def rms(samples, factor):
    """Root-mean-square"""
    reshaped = samples.reshape(-1, factor)
    return np.sqrt(np.mean(reshaped ** 2, axis=1))


def benchmark_algorithm(name, func, samples, factor, iterations=100):
    """Benchmark a decimation algorithm"""
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(samples, factor)
        end = time.perf_counter()
        times.append(end - start)

    avg_time = np.mean(times) * 1000  # Convert to ms
    std_time = np.std(times) * 1000
    throughput = len(samples) / np.mean(times)  # samples/sec

    return {
        'name': name,
        'avg_ms': avg_time,
        'std_ms': std_time,
        'throughput': throughput,
        'output_size': len(result)
    }


if __name__ == '__main__':
    # Simulate 1 second of 5000 Hz data with 100 fields
    samples_per_sec = 5000
    num_fields = 100
    decimation_factor = 50  # 5000 Hz -> 100 Hz

    print("=" * 60)
    print("Relay Decimation Performance Benchmark")
    print("=" * 60)
    print(f"Input rate: {samples_per_sec} Hz")
    print(f"Number of fields: {num_fields}")
    print(f"Decimation factor: {decimation_factor}x")
    print(f"Target output rate: {samples_per_sec // decimation_factor} Hz")
    print()

    # Test single channel
    print("Single Channel Benchmark:")
    print("-" * 60)

    for field_idx in range(min(3, num_fields)):  # Test first 3 fields
        samples = np.random.randn(samples_per_sec)

        print(f"\nField {field_idx + 1}:")
        for algo_name, algo_func in [
            ('Downsample', downsample),
            ('Average', average),
            ('Min-Max', min_max),
            ('RMS', rms)
        ]:
            result = benchmark_algorithm(algo_name, algo_func, samples, decimation_factor)
            print(f"  {result['name']:12} {result['avg_ms']:6.3f}ms ± {result['std_ms']:5.3f}ms "
                  f"({result['throughput']:>12,.0f} samples/sec)")

    # Simulate full workload: 100 fields per sample, 5000 samples/sec
    print("\n" + "=" * 60)
    print("Full Workload Simulation (100 fields × 5000 Hz):")
    print("-" * 60)

    total_samples = samples_per_sec * num_fields  # 500,000 samples/sec
    all_samples = np.random.randn(total_samples)

    for algo_name, algo_func in [
        ('Downsample', downsample),
        ('Average', average),
        ('Min-Max', min_max),
        ('RMS', rms)
    ]:
        # Process all fields
        start_total = time.perf_counter()
        for field_offset in range(0, total_samples, samples_per_sec):
            field_samples = all_samples[field_offset:field_offset + samples_per_sec]
            _ = algo_func(field_samples, decimation_factor)
        end_total = time.perf_counter()

        total_time_ms = (end_total - start_total) * 1000
        overhead_pct = (total_time_ms / 1000) * 100  # % of 1 second

        print(f"{algo_name:12} {total_time_ms:7.2f}ms total ({overhead_pct:5.1f}% CPU overhead)")

    print("\n" + "=" * 60)
    print("Conclusion:")
    print("If CPU overhead < 10%, relay can handle decimation without bottleneck")
    print("If CPU overhead > 30%, relay hot loop performance risk is HIGH")
    print("=" * 60)
