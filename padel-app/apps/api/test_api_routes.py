#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app

def list_all_routes():
    """List all registered routes in the FastAPI application"""
    print("ALL REGISTERED API ROUTES")
    print("=" * 80)
    
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            for method in route.methods:
                routes.append((method, route.path))
    
    # Sort routes by path and method
    routes.sort(key=lambda x: (x[1], x[0]))
    
    # Group by path prefix
    games_routes = []
    invitation_routes = []
    other_routes = []
    
    for method, path in routes:
        if "/games/" in path:
            games_routes.append((method, path))
            if "invitation" in path.lower():
                invitation_routes.append((method, path))
        else:
            other_routes.append((method, path))
    
    print("\nGAMES ROUTES:")
    print("-" * 80)
    for method, path in games_routes:
        print(f"{method:8} {path}")
    
    print("\nINVITATION-SPECIFIC ROUTES:")
    print("-" * 80)
    for method, path in invitation_routes:
        print(f"{method:8} {path}")
        # Check if this is the problematic endpoint
        if "invitations/{token}/info" in path:
            print(f"         ^^^^ THIS IS THE ENDPOINT WE'RE LOOKING FOR")
    
    print("\nEXPECTED INVITATION URL PATTERN:")
    print("-" * 80)
    print("Production URL: https://padelgo-backend-production.up.railway.app/api/v1/games/invitations/{token}/info")
    
    # Check if the specific endpoint exists
    target_path = "/api/v1/games/invitations/{token}/info"
    found = False
    for method, path in routes:
        if path == target_path and method == "GET":
            found = True
            print(f"\n✅ Found exact match: {method} {path}")
            break
    
    if not found:
        print(f"\n❌ Endpoint NOT found: GET {target_path}")
        print("\nPossible issues:")
        print("1. The endpoint path might be different")
        print("2. The router might not be properly registered")
        print("3. There might be a prefix issue")
        
        # Look for similar paths
        print("\nSimilar paths found:")
        for method, path in routes:
            if "invitation" in path.lower() and "/games/" in path:
                print(f"  - {method} {path}")

if __name__ == '__main__':
    list_all_routes()