#!/usr/bin/env python3
"""
Simple test to identify the exact issue with the invitation URL
"""

import requests
import json
import sys

def test_invitation_url():
    """Test the failing invitation URL"""
    token = "Qa636IGpDc_8Tq4m6Md_bSpcxpgkNDXBUTSzCqsUA-I"
    url = f"https://padelgo-backend-production.up.railway.app/api/v1/games/invitations/{token}/info"
    
    print(f"Testing URL: {url}")
    print("=" * 80)
    
    try:
        response = requests.get(url, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        print("\nResponse Body:")
        print(response.text)
        
        # Try to parse as JSON
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                json_data = response.json()
                print("\nParsed JSON:")
                print(json.dumps(json_data, indent=2, default=str))
            except json.JSONDecodeError as e:
                print(f"\nFailed to parse JSON: {e}")
        
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_invitation_url()
    sys.exit(0 if success else 1)