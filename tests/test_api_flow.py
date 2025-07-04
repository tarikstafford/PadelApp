#!/usr/bin/env python3
"""
Quick test script to verify API endpoints work correctly
Tests the flow: create user -> create team -> register for tournament
"""

import requests
import json

API_BASE_URL = "https://padelgo-backend-production.up.railway.app/api/v1"
TOURNAMENT_ID = 1

def test_api_flow():
    print("Testing API flow...")
    
    # Step 1: Create a test user
    print("\n1. Creating test user...")
    user_data = {
        "full_name": "Test Player 1",
        "email": "testplayer1@example.com",
        "password": "test123"
    }
    
    response = requests.post(f"{API_BASE_URL}/auth/register", json=user_data)
    print(f"Register response: {response.status_code}")
    
    if response.status_code == 201:
        auth_data = response.json()
        token = auth_data.get("access_token")
        user_id = auth_data.get("user", {}).get("id")
        print(f"✓ User created with ID: {user_id}")
    elif response.status_code == 400 and "already registered" in response.text:
        print("User already exists, trying to login...")
        response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get("access_token")
            user_id = auth_data.get("user", {}).get("id")
            print(f"✓ User logged in with ID: {user_id}")
        else:
            print(f"✗ Login failed: {response.status_code} - {response.text}")
            return
    else:
        print(f"✗ User creation failed: {response.status_code} - {response.text}")
        return
    
    # Step 2: Create a team
    print("\n2. Creating team...")
    headers = {"Authorization": f"Bearer {token}"}
    team_data = {"name": "Test Team 1"}
    
    response = requests.post(f"{API_BASE_URL}/users/me/teams", json=team_data, headers=headers)
    print(f"Team creation response: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code in [200, 201]:
        team_info = response.json()
        team_id = team_info.get("id")
        print(f"✓ Team created with ID: {team_id}")
    else:
        print(f"✗ Team creation failed: {response.status_code} - {response.text}")
        return
    
    # Step 3: Check tournament exists
    print(f"\n3. Checking tournament {TOURNAMENT_ID}...")
    response = requests.get(f"{API_BASE_URL}/tournaments/{TOURNAMENT_ID}")
    print(f"Tournament check response: {response.status_code}")
    
    if response.status_code == 200:
        tournament = response.json()
        print(f"✓ Tournament found: {tournament.get('name')}")
        print(f"  Status: {tournament.get('status')}")
    else:
        print(f"✗ Tournament not found: {response.status_code} - {response.text}")
        return
    
    # Step 4: Check team eligibility (with authentication)
    print(f"\n4. Checking team eligibility...")
    response = requests.get(f"{API_BASE_URL}/tournaments/{TOURNAMENT_ID}/eligibility/{team_id}", headers=headers)
    print(f"Eligibility check response: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        eligibility = response.json()
        print(f"✓ Eligibility checked: {eligibility}")
        eligible_categories = eligibility.get("eligible_categories", [])
        if eligible_categories:
            category = eligible_categories[0]
            print(f"  Using category: {category}")
        else:
            print("  No eligible categories found")
            category = "BRONZE"  # Fallback
    else:
        print(f"⚠ Eligibility check failed: {response.status_code} - {response.text}")
        print("Using default category...")
        category = "BRONZE"
    
    # Step 5: Register team for tournament
    print(f"\n5. Registering team for tournament...")
    registration_data = {
        "team_id": team_id,
        "category": category
    }
    
    response = requests.post(
        f"{API_BASE_URL}/tournaments/{TOURNAMENT_ID}/register", 
        json=registration_data, 
        headers=headers
    )
    print(f"Registration response: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code in [200, 201]:
        print("✓ Team successfully registered for tournament!")
    else:
        print(f"✗ Team registration failed: {response.status_code} - {response.text}")
    
    print("\n" + "="*50)
    print("API Flow Test Complete")
    print("="*50)

if __name__ == "__main__":
    test_api_flow()