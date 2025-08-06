#!/usr/bin/env python3
"""
Deployment verification script for Railway File Management System.
Run this script to verify that your deployment is working correctly.
"""

import os
import sys
import requests
import json
from urllib.parse import urljoin


def test_health_endpoint(base_url):
    """Test the health check endpoint"""
    try:
        health_url = urljoin(base_url, "/health")
        response = requests.get(health_url, timeout=30)

        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   Database: {data.get('database')}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_login_page(base_url):
    """Test that the login page loads"""
    try:
        login_url = urljoin(base_url, "/login")
        response = requests.get(login_url, timeout=30)

        if response.status_code == 200:
            print("✅ Login page loads successfully")
            return True
        else:
            print(f"❌ Login page failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login page test failed: {e}")
        return False


def test_static_files(base_url):
    """Test that static files are accessible"""
    try:
        # Test a common static file
        static_url = urljoin(base_url, "/static/logo.png")
        response = requests.head(static_url, timeout=30)

        if response.status_code == 200:
            print("✅ Static files are accessible")
            return True
        else:
            print(
                f"⚠️  Static files may not be accessible (status {response.status_code})"
            )
            return True  # Not critical for basic functionality
    except Exception as e:
        print(f"⚠️  Static files test failed: {e}")
        return True  # Not critical for basic functionality


def main():
    """Main verification function"""
    print("🚀 Railway File Management System - Deployment Verification")
    print("=" * 60)

    # Get the base URL
    base_url = input(
        "Enter your Railway app URL (e.g., https://your-app.railway.app): "
    ).strip()

    if not base_url:
        print("❌ No URL provided")
        sys.exit(1)

    if not base_url.startswith(("http://", "https://")):
        base_url = "https://" + base_url

    print(f"\n🔍 Testing deployment at: {base_url}")
    print("-" * 40)

    # Run tests
    tests_passed = 0
    total_tests = 3

    if test_health_endpoint(base_url):
        tests_passed += 1

    if test_login_page(base_url):
        tests_passed += 1

    if test_static_files(base_url):
        tests_passed += 1

    # Summary
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")

    if tests_passed == total_tests:
        print("🎉 All tests passed! Your deployment is working correctly.")
        print("\n📝 Next steps:")
        print("1. Log in with your admin credentials")
        print("2. Test file upload/download functionality")
        print("3. Verify database operations work correctly")
    else:
        print("⚠️  Some tests failed. Check the Railway logs for more details.")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check Railway deployment logs")
        print("2. Verify environment variables are set correctly")
        print("3. Ensure PostgreSQL database is running")
        print("4. Check that all required files are in your repository")

    print(f"\n🌐 Your application URL: {base_url}")


if __name__ == "__main__":
    main()
