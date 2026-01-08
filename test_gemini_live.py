#!/usr/bin/env python3
"""
Live integration test for Gemini provider.
Tests actual API connectivity and vision capabilities.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv()

from src.providers.factory import create_provider
from src.screen import ScreenCapture


def test_gemini_api_key():
    """Test 1: Verify Gemini API key is set."""
    print("\n🔑 Test 1: Checking Gemini API key...")
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ FAILED: GOOGLE_API_KEY not found in environment")
        return False
    print(f"✅ PASSED: API key found (length: {len(api_key)})")
    return True


def test_create_gemini_provider():
    """Test 2: Create Gemini provider instance."""
    print("\n🏗️  Test 2: Creating Gemini provider...")
    try:
        provider = create_provider("gemini")
        info = provider.get_info()
        print(f"✅ PASSED: Provider created - {info.name}")
        print(f"   Model: {provider.model}")
        print(f"   Free tier: {info.free_tier}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_gemini_simple_completion():
    """Test 3: Make a simple API call to Gemini."""
    print("\n💬 Test 3: Testing simple text completion...")
    try:
        provider = create_provider("gemini")
        
        # Simple test prompt
        messages = [
            {"role": "user", "content": "Say 'Hello from Gemini!' and nothing else."}
        ]
        
        response = provider.create_message(
            messages=messages,
            system="You are a helpful assistant.",
            max_tokens=50,
            tools=[]
        )
        
        print(f"✅ PASSED: Gemini API responded")
        text = response.content[0].text if response.content else "N/A"
        print(f"   Response: {text[:100]}")
        print(f"   Stop reason: {response.stop_reason}")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gemini_vision():
    """Test 4: Test Gemini's vision capability with a screenshot."""
    print("\n👁️  Test 4: Testing vision capability (screenshot analysis)...")
    try:
        provider = create_provider("gemini")
        screen_capture = ScreenCapture()
        
        # Take a screenshot and get base64
        print("   Taking screenshot...")
        image = screen_capture.capture(save=False)
        screenshot_data = screen_capture.to_base64(image)
        
        # Create message with image
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe what you see in this screenshot in one sentence."
                    },
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": screenshot_data
                        }
                    }
                ]
            }
        ]
        
        response = provider.create_message(
            messages=messages,
            system="You are a helpful assistant that describes images.",
            max_tokens=200,
            tools=[]
        )
        
        description = response.content[0].text if response.content else "N/A"
        print(f"✅ PASSED: Gemini analyzed the screenshot")
        print(f"   Description: {description[:150]}...")
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all live integration tests."""
    print("=" * 70)
    print("🚀 GEMINI LIVE INTEGRATION TESTS")
    print("=" * 70)
    
    results = []
    
    # Run all tests
    results.append(("API Key Check", test_gemini_api_key()))
    results.append(("Provider Creation", test_create_gemini_provider()))
    results.append(("Simple Completion", test_gemini_simple_completion()))
    results.append(("Vision Capability", test_gemini_vision()))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Gemini provider is fully functional.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
