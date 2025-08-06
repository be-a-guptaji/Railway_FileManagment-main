#!/usr/bin/env python3
"""
Vercel deployment verification script for Railway File Management System.
Run this script to verify that your Vercel deployment is working correctly.
"""

import os
import sys
import requests
import json
import time
from urllib.parse import urljoin


def test_vercel_health_endpoint(base_url):
    """Test the Vercel-optimized health check endpoint"""
    try:
        health_url = urljoin(base_url, "/health")
        print(f"Testing health endpoint: {health_url}")

        response = requests.get(
            health_url, timeout=25
        )  # Shorter timeout for serverless

        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data.get('database')}")
            print(f"   Platform: {data.get('platform', 'unknown')}")

            if data.get("platform") == "vercel":
                print("✅ Vercel environment detected correctly")
            else:
                print("⚠️  Vercel environment not detected - check VERCEL env var")

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
        print(
            "❌ Health check timed out (this may indicate serverless cold start issues)"
        )
        return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_serverless_performance(base_url):
    """Test serverless function performance"""
    try:
        print("\n🔄 Testing serverless performance...")

        # Test multiple requests to check cold start vs warm start
        times = []
        for i in range(3):
            start_time = time.time()
            response = requests.get(urljoin(base_url, "/health"), timeout=25)
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            times.append(response_time)

            if response.status_code == 200:
                print(f"   Request {i+1}: {response_time:.0f}ms ✅")
            else:
                print(
                    f"   Request {i+1}: {response_time:.0f}ms ❌ (Status: {response.status_code})"
                )

            time.sleep(1)  # Small delay between requests

        avg_time = sum(times) / len(times)
        print(f"\n📊 Average response time: {avg_time:.0f}ms")

        if avg_time < 1000:
            print("✅ Good performance")
        elif avg_time < 3000:
            print("⚠️  Acceptable performance (may have cold starts)")
        else:
            print("❌ Slow performance (check database connection)")

        return True
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def test_vercel_login_page(base_url):
    """Test that the login page loads in Vercel environment"""
    try:
        login_url = urljoin(base_url, "/login")
        print(f"Testing login page: {login_url}")

        response = requests.get(login_url, timeout=25)

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


def test_vercel_environment(base_url):
    """Test Vercel-specific environment features"""
    try:
        print("\n🔍 Testing Vercel environment features...")

        # Test if serverless functions are working
        health_response = requests.get(urljoin(base_url, "/health"), timeout=25)

        if health_response.status_code == 200:
            data = health_response.json()

            # Check platform detection
            if data.get("platform") == "vercel":
                print("✅ Vercel platform detection working")
            else:
                print("❌ Vercel platform not detected")
                return False

            # Check database connection
            if data.get("database") == "connected":
                print("✅ Database connection working")
            else:
                print("❌ Database connection failed")
                return False

            return True
        else:
            print("❌ Environment test failed")
            return False

    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False


def check_vercel_limitations(base_url):
    """Check for common Vercel limitations"""
    print("\n⚠️  Checking Vercel limitations...")

    limitations = [
        "📁 File uploads are stored in /tmp (ephemeral storage)",
        "⏱️  Function timeout is 30 seconds maximum",
        "🔄 Cold starts may cause initial delays",
        "💾 Database connections are created per request",
        "📤 Large file operations may timeout",
    ]

    for limitation in limitations:
        print(f"   {limitation}")

    print("\n💡 Recommendations:")
    print("   - Use external file storage (AWS S3, Cloudinary, etc.)")
    print("   - Keep operations under 30 seconds")
    print("   - Optimize database queries")
    print("   - Consider connection pooling")


def main():
    """Main verification function for Vercel deployment"""
    print("🚀 Railway File Management System - Vercel Deployment Verification")
    print("=" * 70)

    # Get the base URL
    base_url = input(
        "Enter your Vercel app URL (e.g., https://your-app.vercel.app): "
    ).strip()

    if not base_url:
        print("❌ No URL provided")
        sys.exit(1)

    if not base_url.startswith(("http://", "https://")):
        base_url = "https://" + base_url

    print(f"\n🔍 Testing Vercel deployment at: {base_url}")
    print("-" * 50)

    # Run Vercel-specific tests
    tests_passed = 0
    total_tests = 4

    if test_vercel_health_endpoint(base_url):
        tests_passed += 1

    if test_vercel_login_page(base_url):
        tests_passed += 1

    if test_serverless_performance(base_url):
        tests_passed += 1

    if test_vercel_environment(base_url):
        tests_passed += 1

    # Show Vercel limitations
    check_vercel_limitations(base_url)

    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All tests passed! Your Vercel deployment is working correctly.")
        print("\n📝 Next steps:")
        print("1. Log in with your admin credentials")
        print("2. Test file upload/download (remember: files are ephemeral)")
        print("3. Consider implementing cloud storage for production")
        print("4. Monitor function execution times")
    elif tests_passed >= 2:
        print("⚠️  Most tests passed, but some issues detected.")
        print("\n🔧 Check the failed tests above and:")
        print("1. Verify environment variables in Vercel dashboard")
        print("2. Check database connection string")
        print("3. Monitor Vercel function logs")
    else:
        print("❌ Multiple tests failed. Check the issues above.")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check Vercel deployment logs")
        print("2. Verify all environment variables are set")
        print("3. Ensure external database is accessible")
        print("4. Check that api/index.py is properly configured")

    print(f"\n🌐 Your Vercel application: {base_url}")
    print("📚 Vercel dashboard: https://vercel.com/dashboard")


if __name__ == "__main__":
    main()
