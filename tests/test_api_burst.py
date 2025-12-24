"""
Test burst request handling for Pivot REST API
Validates synchronous API behavior under concurrent load
"""
import requests
import time
import concurrent.futures
from datetime import datetime, timedelta


API_URL = 'http://localhost:8000/api/v1/pivot/export'


def make_export_request(request_id, channels, duration='PT30S'):
    """Make a single export request and measure timing"""
    start_time = time.time()

    try:
        response = requests.get(API_URL, params={
            'start': '2025-01-23T14:00:00Z',
            'duration': duration,
            'channels': ','.join(channels)
        }, timeout=120)

        end_time = time.time()
        elapsed = end_time - start_time

        return {
            'request_id': request_id,
            'status_code': response.status_code,
            'elapsed_sec': elapsed,
            'file_size': len(response.content) if response.status_code == 200 else 0,
            'start_time': start_time,
            'end_time': end_time,
            'error': None
        }
    except Exception as e:
        end_time = time.time()
        return {
            'request_id': request_id,
            'status_code': None,
            'elapsed_sec': end_time - start_time,
            'file_size': 0,
            'start_time': start_time,
            'end_time': end_time,
            'error': str(e)
        }


def test_single_request():
    """Baseline: single request performance"""
    print("=" * 60)
    print("Test 1: Single Request Baseline")
    print("=" * 60)

    result = make_export_request(1, ['ch1', 'ch2'], 'PT30S')

    print(f"Status: {result['status_code']}")
    print(f"Elapsed: {result['elapsed_sec']:.2f} seconds")
    print(f"File size: {result['file_size']:,} bytes")

    if result['error']:
        print(f"Error: {result['error']}")

    return result


def test_burst_requests(num_concurrent=3):
    """Test burst of concurrent requests"""
    print("\n" + "=" * 60)
    print(f"Test 2: Burst of {num_concurrent} Concurrent Requests")
    print("=" * 60)

    # Submit all requests simultaneously
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = [
            executor.submit(make_export_request, i+1, [f'ch{i+1}', f'ch{i+2}'], 'PT30S')
            for i in range(num_concurrent)
        ]

        results = [f.result() for f in futures]

    # Analyze results
    print(f"\nResults (submitted simultaneously):")
    print("-" * 60)

    for r in sorted(results, key=lambda x: x['start_time']):
        status = "✓" if r['status_code'] == 200 else "✗"
        print(f"Request {r['request_id']}: {status} {r['elapsed_sec']:.2f}s "
              f"(size: {r['file_size']:,} bytes)")
        if r['error']:
            print(f"  Error: {r['error']}")

    # Calculate metrics
    all_successful = all(r['status_code'] == 200 for r in results)
    avg_elapsed = sum(r['elapsed_sec'] for r in results) / len(results)
    max_elapsed = max(r['elapsed_sec'] for r in results)
    min_elapsed = min(r['elapsed_sec'] for r in results)

    # Check for serialization (requests processed sequentially)
    start_times = sorted([r['start_time'] for r in results])
    end_times = sorted([r['end_time'] for r in results])

    # If serialized, each request starts after previous ends
    serialized = all(
        start_times[i] >= end_times[i-1] - 0.1  # 100ms tolerance
        for i in range(1, len(start_times))
    )

    print("\n" + "-" * 60)
    print("Burst Analysis:")
    print(f"  All successful: {all_successful}")
    print(f"  Avg elapsed: {avg_elapsed:.2f}s")
    print(f"  Min elapsed: {min_elapsed:.2f}s")
    print(f"  Max elapsed: {max_elapsed:.2f}s")
    print(f"  Processing: {'SERIALIZED' if serialized else 'PARALLEL'}")

    if serialized:
        print(f"  ⚠ Requests processed sequentially (expected for sync API)")
        print(f"  Last request waited ~{max_elapsed - min_elapsed:.1f}s")
    else:
        print(f"  ✓ Requests processed in parallel (Flask threading working)")

    return results, all_successful


def test_limit_validation():
    """Test that API enforces limits"""
    print("\n" + "=" * 60)
    print("Test 3: Limit Validation")
    print("=" * 60)

    # Test channel limit (max 20)
    print("\nTesting channel limit (21 channels, max=20)...")
    result = make_export_request(1, [f'ch{i}' for i in range(21)], 'PT30S')
    print(f"Status: {result['status_code']} (expected 413)")
    assert result['status_code'] == 413, "Should reject >20 channels"

    # Test duration limit (max 5 minutes)
    print("\nTesting duration limit (6 minutes, max=5)...")
    result = make_export_request(1, ['ch1'], 'PT6M')
    print(f"Status: {result['status_code']} (expected 413)")
    assert result['status_code'] == 413, "Should reject >5 minute duration"

    print("\n✓ All limits enforced correctly")


if __name__ == '__main__':
    print("Pivot REST API Burst Test")
    print("Make sure API server is running: python pivot/python/api_server.py")
    print()

    input("Press Enter to start tests...")

    # Run tests
    baseline = test_single_request()
    burst_results, burst_success = test_burst_requests(num_concurrent=3)
    test_limit_validation()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Baseline single request: {baseline['elapsed_sec']:.2f}s")
    print(f"Burst test (3 concurrent): {'PASSED' if burst_success else 'FAILED'}")
    print(f"Limit validation: PASSED")

    if burst_success:
        print("\n✓ Synchronous API handles bursts correctly")
        print("  (Sequential processing is expected behavior)")
    else:
        print("\n✗ Burst test failed - check errors above")
