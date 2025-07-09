#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api')

from fastapi.testclient import TestClient
from app.main import app
import json

def test_invitation_api():
    """Test the invitation info API endpoint"""
    client = TestClient(app)
    
    # Test with a made-up token to see the error response
    test_token = "nonexistent-token"
    
    print(f"Testing API endpoint: /api/v1/games/invitations/{test_token}/info")
    
    response = client.get(f"/api/v1/games/invitations/{test_token}/info")
    
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response body: {response.text}")
    
    if response.status_code == 404:
        print("✅ API returns 404 for non-existent token (expected)")
    
    try:
        response_json = response.json()
        print(f"Parsed JSON: {json.dumps(response_json, indent=2)}")
    except Exception as e:
        print(f"Failed to parse JSON: {e}")

if __name__ == '__main__':
    test_invitation_api()