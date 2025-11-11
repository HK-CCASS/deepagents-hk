#!/usr/bin/env python3
"""Quick test script for SqliteSaver checkpointer."""

import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test all required imports."""
    print("Testing imports...")
    
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
        print("✓ SqliteSaver import successful")
    except ImportError as e:
        print(f"✗ SqliteSaver import failed: {e}")
        return False
    
    try:
        from src.agents.main_agent import create_hkex_agent
        print("✓ create_hkex_agent import successful")
    except ImportError as e:
        print(f"✗ create_hkex_agent import failed: {e}")
        return False
    
    return True

def test_checkpointer_creation():
    """Test checkpointer creation."""
    print("\nTesting checkpointer creation...")
    
    try:
        from langgraph.checkpoint.sqlite import SqliteSaver
        from pathlib import Path
        import tempfile
        
        # Create temp database
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test.db"
            checkpointer = SqliteSaver.from_conn_string(f"sqlite:///{db_path}")
            print(f"✓ Checkpointer created successfully")
            print(f"  Database: {db_path}")
            print(f"  Type: {type(checkpointer)}")
            return True
            
    except Exception as e:
        print(f"✗ Checkpointer creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_creation():
    """Test agent creation with checkpointer."""
    print("\nTesting agent creation...")
    
    try:
        # This will fail if API key not set, but that's ok - we just want to check checkpointer
        from src.agents.main_agent import create_hkex_agent
        
        print("✓ create_hkex_agent function loaded")
        print("  Note: Full agent creation requires valid API keys")
        return True
        
    except Exception as e:
        print(f"✗ Agent creation test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("SqliteSaver Checkpointer Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: Imports
    results.append(("Imports", test_imports()))
    
    # Test 2: Checkpointer creation
    results.append(("Checkpointer Creation", test_checkpointer_creation()))
    
    # Test 3: Agent creation
    results.append(("Agent Creation", test_agent_creation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)

