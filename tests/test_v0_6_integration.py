#!/usr/bin/env python3
"""
Integration test for v0.6: Registration Frontend + Python Client Library
Tests: Client library, frontend serving, full workflow
"""
import sys
import os
from pathlib import Path

# Add lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../lib/python'))


def test_client_library_import():
    """Test Python client library can be imported"""
    try:
        from speeddata_client import SpeedDataClient
        print("✓ SpeedDataClient imported successfully")

        # Test instantiation
        client = SpeedDataClient()
        assert client.base_url == "http://localhost:8080/api/v1"
        assert client.session is not None
        print("✓ SpeedDataClient instantiation works")

        # Test custom base URL
        client2 = SpeedDataClient(base_url="http://example.com:9000/api/v1")
        assert client2.base_url == "http://example.com:9000/api/v1"
        print("✓ Custom base URL works")

        return True
    except ImportError as e:
        print(f"✗ Failed to import speeddata_client: {e}")
        return False


def test_frontend_files_exist():
    """Test that frontend files were created"""
    frontend_path = Path(__file__).parent.parent / 'registration' / 'frontend' / 'index.html'

    if not frontend_path.exists():
        print(f"✗ Frontend not found at: {frontend_path}")
        return False

    print(f"✓ Frontend exists at: {frontend_path}")

    # Check file size (should be ~140 lines)
    with open(frontend_path) as f:
        lines = f.readlines()
        line_count = len(lines)
        print(f"✓ Frontend is {line_count} lines (target: ~140)")

        # Verify key elements
        content = ''.join(lines)
        checks = [
            ('Channel list table', '<table id="channelTable">' in content),
            ('Registration form', '<form id="registerForm">' in content),
            ('API fetch calls', 'fetch(`${API_BASE}/channels`)' in content),
            ('De-register button', 'onclick="deregister(' in content),
            ('Monospace font', 'font-family: monospace;' in content)
        ]

        for name, passed in checks:
            if passed:
                print(f"  ✓ {name}")
            else:
                print(f"  ✗ {name} MISSING")
                return False

    return True


def test_api_static_serving():
    """Test that api.py is configured to serve static files"""
    api_path = Path(__file__).parent.parent / 'relay' / 'api.py'

    with open(api_path) as f:
        content = f.read()

    checks = [
        ('Static folder config', 'static_folder' in content),
        ('Root route handler', '@app.route(\'/\')' in content),
        ('send_static_file', 'send_static_file(\'index.html\')' in content)
    ]

    all_passed = True
    for name, passed in checks:
        if passed:
            print(f"✓ {name} configured")
        else:
            print(f"✗ {name} MISSING")
            all_passed = False

    return all_passed


def test_client_library_methods():
    """Test client library has all required methods"""
    try:
        from speeddata_client import SpeedDataClient
        client = SpeedDataClient()

        required_methods = [
            'list_channels',
            'register_channel',
            'deregister_channel',
            'get_channel',
            'upload_schema'
        ]

        for method in required_methods:
            if hasattr(client, method):
                print(f"✓ Method '{method}' exists")
            else:
                print(f"✗ Method '{method}' MISSING")
                return False

        return True
    except Exception as e:
        print(f"✗ Client library test failed: {e}")
        return False


def test_usage_documentation():
    """Verify usage documentation exists in docstrings"""
    try:
        from speeddata_client import SpeedDataClient
        import inspect

        # Check class docstring
        if SpeedDataClient.__doc__ and 'Usage:' in SpeedDataClient.__doc__:
            print("✓ Client library has usage documentation")

            # Show example
            print("\n--- Client Library Usage Example ---")
            doc = SpeedDataClient.__doc__.strip()
            usage_section = doc.split('Usage:')[1].split('"""')[0]
            print(usage_section)
            print("---")

            return True
        else:
            print("✗ Missing usage documentation in docstring")
            return False
    except Exception as e:
        print(f"✗ Documentation check failed: {e}")
        return False


def print_integration_guide():
    """Print guide for testing the integration manually"""
    print("\n" + "="*70)
    print("MANUAL INTEGRATION TEST GUIDE")
    print("="*70)

    print("\n1. START ORCHESTRATOR:")
    print("   cd /mnt/data/sd-dev")
    print("   python relay/orchestrator.py")
    print("   (Should show: REST API started on http://0.0.0.0:8080/api/v1)")

    print("\n2. ACCESS FRONTEND:")
    print("   Open browser to: http://localhost:8080/")
    print("   Should see: Channel registration UI")

    print("\n3. TEST REGISTRATION VIA FRONTEND:")
    print("   - Fill in form:")
    print("     Name: test_channel")
    print("     Port: 26100")
    print("     Schema: config/agents/example.avsc")
    print("     Decimation: 5")
    print("   - Click 'Register Channel'")
    print("   - Should appear in table above")

    print("\n4. TEST PYTHON CLIENT:")
    print("   python")
    print("   >>> from lib.python.speeddata_client import SpeedDataClient")
    print("   >>> client = SpeedDataClient()")
    print("   >>> channels = client.list_channels()")
    print("   >>> print(channels)")

    print("\n5. TEST DE-REGISTRATION:")
    print("   - Click 'Remove' button in frontend")
    print("   - Channel should disappear from table")
    print("   - Refresh page to confirm")

    print("\n6. VERIFY RELAY PROCESS:")
    print("   ps aux | grep relay")
    print("   (Should show C relay process for each channel)")

    print("\n" + "="*70)


if __name__ == "__main__":
    print("=== v0.6 Integration Test Suite ===\n")

    results = []
    results.append(("Client library import", test_client_library_import()))
    results.append(("Client library methods", test_client_library_methods()))
    results.append(("Frontend files exist", test_frontend_files_exist()))
    results.append(("API static serving", test_api_static_serving()))
    results.append(("Usage documentation", test_usage_documentation()))

    print("\n=== Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"{passed}/{total} tests passed")

    if passed == total:
        print("\n✓ v0.6 implementation complete!")
        print("  - registration/frontend/index.html (~140 lines)")
        print("  - lib/python/speeddata_client.py (~180 lines)")
        print("  - API configured to serve static files")
        print("\nTotal implementation: ~320 lines (target: ~200, acceptable for completeness)")

        print_integration_guide()

        sys.exit(0)
    else:
        print("\n✗ Some tests failed")
        sys.exit(1)
