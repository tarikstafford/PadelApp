#!/usr/bin/env python3

import requests
import json
from datetime import datetime

def test_invitation_endpoint():
    """Test the invitation endpoint to see what's happening"""
    
    # The failing token
    token = "Qa636IGpDc_8Tq4m6Md_bSpcxpgkNDXBUTSzCqsUA-I"
    
    # Test URL
    url = f"https://padelgo-backend-production.up.railway.app/api/v1/games/invitations/{token}/info"
    
    print(f"Testing URL: {url}")
    print("=" * 80)
    
    try:
        # Make the request
        response = requests.get(url, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("=" * 80)
        
        # Try to parse response as JSON
        try:
            response_data = response.json()
            print("Response JSON:")
            print(json.dumps(response_data, indent=2, default=str))
        except json.JSONDecodeError:
            print("Response is not valid JSON:")
            print(response.text)
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_invitation_endpoint()