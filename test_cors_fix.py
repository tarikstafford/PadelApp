#!/usr/bin/env python3
"""
Test CORS and tournament endpoint after fixes
"""

import requests
import time

API_BASE_URL = "https://padelgo-backend-production.up.railway.app/api/v1"

def test_cors_and_endpoint():
    """Test if CORS and tournament endpoint work"""
    
    print("Testing CORS and Tournament Endpoint...")
    print("=" * 50)
    
    # Test 1: OPTIONS request (CORS preflight)
    print("1. Testing CORS preflight (OPTIONS):")
    try:
        response = requests.options(
            f"{API_BASE_URL}/tournaments/1",
            headers={
                "Origin": "https://padelgo-frontend-production.up.railway.app",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,content-type"
            }
        )
        print(f"   Status: {response.status_code}")
        print(f"   CORS headers: {dict(response.headers)}")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test 2: GET request
    print("\\n2. Testing GET request:")
    try:
        response = requests.get(
            f"{API_BASE_URL}/tournaments/1",
            headers={
                "Origin": "https://padelgo-frontend-production.up.railway.app"
            }
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Tournament: {data.get('name')}")
            print(f"   ✓ Categories: {len(data.get('categories', []))}")
            print(f"   ✓ Status: {data.get('status')}")
        else:
            print(f"   ✗ Error: {response.text}")
            
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test 3: Check all tournaments
    print("\\n3. Testing tournaments list:")
    try:
        response = requests.get(f"{API_BASE_URL}/tournaments/")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            tournaments = response.json()
            print(f"   ✓ Found {len(tournaments)} tournaments")
        else:
            print(f"   ✗ Error: {response.text}")
            
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test 4: Health check
    print("\\n4. Testing health check:")
    try:
        response = requests.get(f"https://padelgo-backend-production.up.railway.app/health")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✓ Backend is healthy")
        else:
            print(f"   ✗ Backend health check failed")
            
    except Exception as e:
        print(f"   Error: {str(e)}")

def wait_for_deployment():
    """Wait for backend deployment to complete"""
    
    print("\\nWaiting for backend deployment...")
    
    for attempt in range(10):
        try:
            response = requests.get(f"{API_BASE_URL}/tournaments/1", timeout=5)
            
            if response.status_code == 200:
                print(f"✓ Backend deployed successfully!")
                return True
            elif response.status_code == 500:
                print(f"Attempt {attempt + 1}: Still getting 500 error, waiting...")
                time.sleep(10)
            else:
                print(f"Attempt {attempt + 1}: Status {response.status_code}")
                time.sleep(5)
                
        except Exception as e:
            print(f"Attempt {attempt + 1}: Connection error - {str(e)}")
            time.sleep(5)
    
    print("✗ Deployment check timed out")
    return False

if __name__ == "__main__":
    # First wait for deployment
    if wait_for_deployment():
        test_cors_and_endpoint()
    else:
        print("\\nSkipping tests due to deployment issues")
        print("\\nActions needed:")
        print("1. Deploy the backend with CORS and tournament fixes")
        print("2. Run this test again to verify the fixes")