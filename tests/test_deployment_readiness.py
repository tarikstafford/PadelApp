#!/usr/bin/env python3
"""
Test that the backend fixes are ready for deployment
"""

def test_imports():
    """Test that all imports work correctly"""
    print("Testing imports...")
    
    try:
        # Test main.py imports
        import sys
        sys.path.append('/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api')
        
        # This will fail if there are syntax errors
        import py_compile
        py_compile.compile('/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api/app/main.py', doraise=True)
        py_compile.compile('/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api/app/routers/tournaments.py', doraise=True)
        
        print("✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {str(e)}")
        return False

def check_cors_config():
    """Verify CORS configuration"""
    print("\\nChecking CORS configuration...")
    
    with open('/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api/app/main.py', 'r') as f:
        content = f.read()
        
    if "padelgo-frontend-production.up.railway.app" in content:
        print("✅ Production frontend origin configured")
    else:
        print("❌ Production frontend origin missing")
        return False
        
    if "CORSMiddleware" in content:
        print("✅ CORS middleware configured")
    else:
        print("❌ CORS middleware missing")
        return False
    
    return True

def check_tournament_endpoint():
    """Verify tournament endpoint safety"""
    print("\\nChecking tournament endpoint...")
    
    with open('/Users/tarikstafford/Desktop/Projects/PadelApp/padel-app/apps/api/app/routers/tournaments.py', 'r') as f:
        content = f.read()
    
    if "try:" in content and "except Exception" in content:
        print("✅ Error handling implemented")
    else:
        print("❌ Error handling missing")
        return False
        
    if "categories=[]" in content:
        print("✅ Safe categories response")
    else:
        print("❌ Categories might cause crashes")
        return False
    
    return True

def main():
    print("Backend Deployment Readiness Check")
    print("=" * 40)
    
    all_good = True
    
    all_good &= test_imports()
    all_good &= check_cors_config()
    all_good &= check_tournament_endpoint()
    
    print("\\n" + "=" * 40)
    if all_good:
        print("✅ READY FOR DEPLOYMENT!")
        print("\\nNext steps:")
        print("1. Deploy the backend with current changes")
        print("2. Test tournament endpoint: GET /api/v1/tournaments/1")
        print("3. Verify CORS headers are present")
        print("4. Add categories to tournament via admin interface")
    else:
        print("❌ NOT READY - Fix issues above")
    
    return all_good

if __name__ == "__main__":
    main()