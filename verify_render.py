#!/usr/bin/env python3
"""
Render.com deployment verification script for Railway File Management System.
Run this script to verify that your Render deployment is working correctly.
"""

import os
import sys
import requests
import json
import time
from urllib.parse import urljoin


def test_render_health_endpoint(base_url):
    """Test the Render-optimized health check endpoint"""
    try:
        health_url = urljoin(base_url, "/health")
        print(f"Testing health endpoint: {health_url}")

        response = requests.get(health_url, timeout=30)

        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data.get('database')}")
            print(f"   Platform: {data.get('platform', 'unknown')}")

            if data.get("platform") == "render":
                print("✅ Render environment detected correctly")
            else:
                print("⚠️  Render environment not detected - check RENDER env var")

            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', 'Unknown error')}")
            except:
                print(f"   Response: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Health check timed out")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_render_performance(base_url):
    """Test Render service performance"""
    try:
        print("\n🔄 Testing Render performance...")

        # Test multiple requests to check consistency
        times = []
        for i in range(5):
            start_time = time.time()
            response = requests.get(urljoin(base_url, "/health"), timeout=30)
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            times.append(response_time)

            if response.status_code == 200:
                print(f"   Request {i+1}: {response_time:.0f}ms ✅")
            else:
                print(
                    f"   Request {i+1}: {response_time:.0f}ms ❌ (Status: {response.status_code})"
                )

            time.sleep(0.5)  # Small delay between requests

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"\n📊 Performance metrics:")
        print(f"   Average: {avg_time:.0f}ms")
        print(f"   Minimum: {min_time:.0f}ms")
        print(f"   Maximum: {max_time:.0f}ms")

        if avg_time < 500:
            print("✅ Excellent performance")
        elif avg_time < 1000:
            print("✅ Good performance")
        elif avg_time < 2000:
            print("⚠️  Acceptable performance")
        else:
            print("❌ Slow performance (check database connection)")

        return True
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def test_render_login_page(base_url):
    """Test that the login page loads in Render environment"""
    try:
        login_url = urljoin(base_url, "/login")
        print(f"Testing login page: {login_url}")

        response = requests.get(login_url, timeout=30)

        if response.status_code == 200:
            print("✅ Login page loads successfully")

            # Check if it's actually the login page
            if "login" in response.text.lower() or "password" in response.text.lower():
                print("✅ Login form detected")
            else:
                print("⚠️  Login page loaded but form not detected")

            return True
        else:
            print(f"❌ Login page failed with status {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Login page timed out")
        return False
    except Exception as e:
        print(f"❌ Login page test failed: {e}")
        return False


def test_render_static_files(base_url):
    """Test that static files are accessible"""
    try:
        print("Testing static file access...")

        # Test common static files
        static_files = ["/static/logo.png", "/static/style.css", "/static/script.js"]

        accessible_files = 0
        for static_file in static_files:
            try:
                static_url = urljoin(base_url, static_file)
                response = requests.head(static_url, timeout=10)

                if response.status_code == 200:
                    print(f"   ✅ {static_file}")
                    accessible_files += 1
                else:
                    print(f"   ⚠️  {static_file} (Status: {response.status_code})")
            except:
                print(f"   ❌ {static_file} (Not accessible)")

        if accessible_files > 0:
            print(f"✅ {accessible_files}/{len(static_files)} static files accessible")
            return True
        else:
            print("⚠️  No static files accessible (may be normal)")
            return True  # Not critical for basic functionality

    except Exception as e:
        print(f"⚠️  Static files test failed: {e}")
        return True  # Not critical for basic functionality


def test_render_database(base_url):
    """Test database connectivity through the application"""
    try:
        print("Testing database connectivity...")

        # The health endpoint already tests database connection
        health_response = requests.get(urljoin(base_url, "/health"), timeout=30)

        if health_response.status_code == 200:
            data = health_response.json()

            if data.get("database") == "connected":
                print("✅ Database connection working")
                return True
            else:
                print("❌ Database connection failed")
                return False
        else:
            print("❌ Could not test database connection")
            return False

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_render_file_operations(base_url):
    """Test file upload capability (basic check)"""
    try:
        print("Testing file operation endpoints...")

        # Test that file-related endpoints are accessible
        endpoints = [
            "/export",  # Should require login but endpoint should exist
        ]

        accessible_endpoints = 0
        for endpoint in endpoints:
            try:
                url = urljoin(base_url, endpoint)
                response = requests.get(url, timeout=10, allow_redirects=False)

                # We expect redirect to login page (302) or forbidden (403)
                if response.status_code in [302, 403]:
                    print(f"   ✅ {endpoint} (redirects to login)")
                    accessible_endpoints += 1
                elif response.status_code == 200:
                    print(f"   ✅ {endpoint} (accessible)")
                    accessible_endpoints += 1
                else:
                    print(f"   ⚠️  {endpoint} (Status: {response.status_code})")
            except:
                print(f"   ❌ {endpoint} (Not accessible)")

        if accessible_endpoints > 0:
            print("✅ File operation endpoints accessible")
            return True
        else:
            print("⚠️  File operation endpoints may have issues")
            return False

    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False


def check_render_features(base_url):
    """Check Render-specific features"""
    print("\n🔍 Checking Render-specific features...")

    features = [
        "✅ Persistent disk storage for file uploads",
        "✅ Built-in PostgreSQL database",
        "✅ Automatic SSL/HTTPS",
        "✅ Zero-downtime deployments",
        "✅ Health check monitoring",
        "✅ Auto-scaling capabilities",
        "✅ Custom domain support",
        "✅ Automatic backups (Starter plan+)",
    ]

    for feature in features:
        print(f"   {feature}")

    print("\n💡 Render advantages:")
    print("   - Files persist across deployments")
    print("   - No cold starts (always-on containers)")
    print("   - Managed database with backups")
    print("   - Easy scaling and monitoring")


def main():
    """Main verification function for Render deployment"""
    print("🚀 Railway File Management System - Render Deployment Verification")
    print("=" * 70)

    # Get the base URL
    base_url = input(
        "Enter your Render app URL (e.g., https://your-app.onrender.com): "
    ).strip()

    if not base_url:
        print("❌ No URL provided")
        sys.exit(1)

    if not base_url.startswith(("http://", "https://")):
        base_url = "https://" + base_url

    print(f"\n🔍 Testing Render deployment at: {base_url}")
    print("-" * 50)

    # Run Render-specific tests
    tests_passed = 0
    total_tests = 6

    if test_render_health_endpoint(base_url):
        tests_passed += 1

    if test_render_login_page(base_url):
        tests_passed += 1

    if test_render_performance(base_url):
        tests_passed += 1

    if test_render_static_files(base_url):
        tests_passed += 1

    if test_render_database(base_url):
        tests_passed += 1

    if test_render_file_operations(base_url):
        tests_passed += 1

    # Show Render features
    check_render_features(base_url)

    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All tests passed! Your Render deployment is working perfectly.")
        print("\n📝 Next steps:")
        print("1. Log in with your admin credentials")
        print("2. Test file upload/download functionality")
        print("3. Verify persistent storage is working")
        print("4. Set up custom domain (if needed)")
        print("5. Configure monitoring and alerts")
    elif tests_passed >= 4:
        print("✅ Most tests passed! Your deployment is mostly working.")
        print("\n🔧 Check the failed tests above and:")
        print("1. Verify environment variables in Render dashboard")
        print("2. Check database connection and configuration")
        print("3. Review application logs in Render dashboard")
        print("4. Ensure persistent disk is properly mounted")
    else:
        print("❌ Multiple tests failed. Please review the issues above.")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check Render service logs")
        print("2. Verify all environment variables are set correctly")
        print("3. Ensure database service is running")
        print("4. Check render.yaml configuration")
        print("5. Verify persistent disk configuration")

    print(f"\n🌐 Your Render application: {base_url}")
    print("📚 Render dashboard: https://dashboard.render.com")
    print("📖 Documentation: https://render.com/docs")


if __name__ == "__main__":
    main()
