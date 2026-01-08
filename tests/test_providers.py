#!/usr/bin/env python3
"""
Test script for multi-provider LLM support.

This script tests:
1. Provider auto-selection based on available API keys
2. Manual provider selection
3. Provider information display
4. Error handling for missing API keys
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.providers.factory import ProviderFactory
from src.providers.base import ProviderType


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_provider_info():
    """Test provider information display."""
    print_section("Test 1: Provider Information")
    
    try:
        # Get all provider info
        all_info = ProviderFactory.get_all_provider_info()
        
        print(f"Total providers available: {len(all_info)}\n")
        
        for info in all_info:
            print(f"Provider: {info.name}")
            print(f"  Type: {info.provider_type}")
            print(f"  Model: {info.default_model}")
            print(f"  Vision: {info.supports_vision}")
            print(f"  Computer Use: {info.supports_computer_use}")
            print(f"  Cost Tier: {info.cost_tier}")
            print(f"  Free Tier: {info.has_free_tier}")
            print()
        
        print("✅ Provider info test PASSED")
        return True
    except Exception as e:
        print(f"❌ Provider info test FAILED: {e}")
        return False


def test_auto_selection():
    """Test automatic provider selection based on available API keys."""
    print_section("Test 2: Auto Provider Selection")
    
    # Save original env vars
    original_env = {
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'FEATHERLESS_API_KEY': os.getenv('FEATHERLESS_API_KEY'),
        'LLM_PROVIDER': os.getenv('LLM_PROVIDER'),
    }
    
    try:
        # Test 1: All keys available - should prefer Gemini
        print("Test 2a: All API keys available (should prefer Gemini)")
        os.environ['GOOGLE_API_KEY'] = 'test_key_gemini'
        os.environ['ANTHROPIC_API_KEY'] = 'test_key_anthropic'
        os.environ['OPENAI_API_KEY'] = 'test_key_openai'
        os.environ['FEATHERLESS_API_KEY'] = 'test_key_featherless'
        os.environ['LLM_PROVIDER'] = 'auto'
        
        provider = ProviderFactory.create_provider()
        print(f"  Selected: {provider.get_info().name}")
        assert provider.get_info().provider_type == ProviderType.GEMINI, "Should select Gemini when all available"
        print("  ✅ Correctly selected Gemini (free tier priority)\n")
        
        # Test 2: Only Anthropic available
        print("Test 2b: Only Anthropic API key available")
        os.environ.pop('GOOGLE_API_KEY', None)
        os.environ.pop('OPENAI_API_KEY', None)
        os.environ.pop('FEATHERLESS_API_KEY', None)
        os.environ['ANTHROPIC_API_KEY'] = 'test_key_anthropic'
        
        provider = ProviderFactory.create_provider()
        print(f"  Selected: {provider.get_info().name}")
        assert provider.get_info().provider_type == ProviderType.ANTHROPIC, "Should select Anthropic when only one available"
        print("  ✅ Correctly selected Anthropic\n")
        
        # Test 3: Only OpenAI available
        print("Test 2c: Only OpenAI API key available")
        os.environ.pop('ANTHROPIC_API_KEY', None)
        os.environ['OPENAI_API_KEY'] = 'test_key_openai'
        
        provider = ProviderFactory.create_provider()
        print(f"  Selected: {provider.get_info().name}")
        assert provider.get_info().provider_type == ProviderType.OPENAI, "Should select OpenAI when only one available"
        print("  ✅ Correctly selected OpenAI\n")
        
        print("✅ Auto selection test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Auto selection test FAILED: {e}")
        return False
    finally:
        # Restore original env vars
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_manual_selection():
    """Test manual provider selection via LLM_PROVIDER env var."""
    print_section("Test 3: Manual Provider Selection")
    
    original_provider = os.getenv('LLM_PROVIDER')
    original_gemini_key = os.getenv('GOOGLE_API_KEY')
    original_anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    
    try:
        # Set up test keys
        os.environ['GOOGLE_API_KEY'] = 'test_key_gemini'
        os.environ['ANTHROPIC_API_KEY'] = 'test_key_anthropic'
        
        # Test forcing Gemini
        print("Test 3a: Force Gemini provider")
        os.environ['LLM_PROVIDER'] = 'gemini'
        provider = ProviderFactory.create_provider()
        print(f"  Selected: {provider.get_info().name}")
        assert provider.get_info().provider_type == ProviderType.GEMINI
        print("  ✅ Successfully forced Gemini\n")
        
        # Test forcing Anthropic
        print("Test 3b: Force Anthropic provider")
        os.environ['LLM_PROVIDER'] = 'anthropic'
        provider = ProviderFactory.create_provider()
        print(f"  Selected: {provider.get_info().name}")
        assert provider.get_info().provider_type == ProviderType.ANTHROPIC
        print("  ✅ Successfully forced Anthropic\n")
        
        print("✅ Manual selection test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Manual selection test FAILED: {e}")
        return False
    finally:
        # Restore original env vars
        if original_provider is None:
            os.environ.pop('LLM_PROVIDER', None)
        else:
            os.environ['LLM_PROVIDER'] = original_provider
            
        if original_gemini_key is None:
            os.environ.pop('GOOGLE_API_KEY', None)
        else:
            os.environ['GOOGLE_API_KEY'] = original_gemini_key
            
        if original_anthropic_key is None:
            os.environ.pop('ANTHROPIC_API_KEY', None)
        else:
            os.environ['ANTHROPIC_API_KEY'] = original_anthropic_key


def test_error_handling():
    """Test error handling when no API keys are available."""
    print_section("Test 4: Error Handling")
    
    # Save original env vars
    original_env = {
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'FEATHERLESS_API_KEY': os.getenv('FEATHERLESS_API_KEY'),
    }
    
    try:
        # Remove all API keys
        print("Test 4a: No API keys available (should raise error)")
        for key in original_env.keys():
            os.environ.pop(key, None)
        
        try:
            provider = ProviderFactory.create_provider()
            print("  ❌ Should have raised an error but didn't")
            return False
        except ValueError as e:
            print(f"  ✅ Correctly raised error: {e}\n")
        
        # Test invalid provider type
        print("Test 4b: Invalid provider type specified")
        os.environ['LLM_PROVIDER'] = 'invalid_provider'
        os.environ['GOOGLE_API_KEY'] = 'test_key'
        
        try:
            provider = ProviderFactory.create_provider()
            # Should fall back to auto selection (Gemini)
            print(f"  ✅ Fell back to auto selection: {provider.get_info().name}\n")
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
            return False
        
        print("✅ Error handling test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test FAILED: {e}")
        return False
    finally:
        # Restore original env vars
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def test_provider_priority():
    """Test that provider selection follows correct priority order."""
    print_section("Test 5: Provider Priority Order")
    
    original_env = {
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'FEATHERLESS_API_KEY': os.getenv('FEATHERLESS_API_KEY'),
        'LLM_PROVIDER': os.getenv('LLM_PROVIDER'),
    }
    
    try:
        os.environ['LLM_PROVIDER'] = 'auto'
        
        # Priority order should be: Gemini → Anthropic → OpenAI → Featherless
        
        print("Test 5a: Gemini + Anthropic available (should prefer Gemini - free tier)")
        os.environ['GOOGLE_API_KEY'] = 'test_key_gemini'
        os.environ['ANTHROPIC_API_KEY'] = 'test_key_anthropic'
        os.environ.pop('OPENAI_API_KEY', None)
        os.environ.pop('FEATHERLESS_API_KEY', None)
        
        provider = ProviderFactory.create_provider()
        assert provider.get_info().provider_type == ProviderType.GEMINI
        print(f"  ✅ Correctly preferred Gemini over Anthropic\n")
        
        print("Test 5b: Anthropic + OpenAI available (should prefer Anthropic)")
        os.environ.pop('GOOGLE_API_KEY', None)
        os.environ['ANTHROPIC_API_KEY'] = 'test_key_anthropic'
        os.environ['OPENAI_API_KEY'] = 'test_key_openai'
        
        provider = ProviderFactory.create_provider()
        assert provider.get_info().provider_type == ProviderType.ANTHROPIC
        print(f"  ✅ Correctly preferred Anthropic over OpenAI\n")
        
        print("Test 5c: OpenAI + Featherless available (should prefer OpenAI)")
        os.environ.pop('ANTHROPIC_API_KEY', None)
        os.environ['OPENAI_API_KEY'] = 'test_key_openai'
        os.environ['FEATHERLESS_API_KEY'] = 'test_key_featherless'
        
        provider = ProviderFactory.create_provider()
        assert provider.get_info().provider_type == ProviderType.OPENAI
        print(f"  ✅ Correctly preferred OpenAI over Featherless\n")
        
        print("✅ Provider priority test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Provider priority test FAILED: {e}")
        return False
    finally:
        # Restore original env vars
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def main():
    """Run all provider tests."""
    print("\n" + "="*70)
    print("  MULTI-PROVIDER LLM SUPPORT TEST SUITE")
    print("="*70)
    
    results = []
    
    # Run all tests
    results.append(("Provider Information", test_provider_info()))
    results.append(("Auto Selection", test_auto_selection()))
    results.append(("Manual Selection", test_manual_selection()))
    results.append(("Error Handling", test_error_handling()))
    results.append(("Provider Priority", test_provider_priority()))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests PASSED! Multi-provider support is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) FAILED. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
