# Multi-Provider LLM Support - Setup Guide

## 🎉 Implementation Complete

Multi-provider LLM support has been successfully added to VisionPilot. You can now use **Google Gemini (FREE tier)**, Anthropic Claude, OpenAI GPT, or Featherless.ai for cost-effective operation.

---

## 📁 What Was Implemented

### New Provider Architecture

**Created Files:**
- `src/providers/base.py` - Abstract base class defining provider interface
- `src/providers/anthropic_provider.py` - Anthropic Claude integration (native Computer Use API)
- `src/providers/gemini_provider.py` - Google Gemini integration (FREE tier supported)
- `src/providers/openai_provider.py` - OpenAI GPT-4o/GPT-4o-mini integration
- `src/providers/featherless_provider.py` - Featherless.ai integration
- `src/providers/factory.py` - Provider selection and auto-fallback logic
- `src/providers/__init__.py` - Provider module exports
- `tests/test_providers.py` - Comprehensive test suite for provider functionality

**Updated Files:**
- `src/agent.py` - Modified to use provider abstraction instead of direct Anthropic client
- `src/cli.py` - Enhanced `info` command to show provider status, added `--provider` flag to commands
- `.env` - Added environment variables for all providers
- `requirements.txt` - Added new dependencies (google-generativeai, openai, requests)
- `README.md` - Comprehensive provider documentation with comparison tables and setup guides

### Key Features

✅ **Multi-Provider Support**: Google Gemini, Anthropic Claude, OpenAI GPT, Featherless.ai  
✅ **Auto-Selection**: Automatically chooses best available provider (prioritizes free tier)  
✅ **Manual Override**: Force specific provider via environment variable or CLI flag  
✅ **Fallback Chain**: Gemini (free) → Claude → OpenAI → Featherless  
✅ **Cost Optimization**: Free tier prioritized, with graceful fallback to paid options  
✅ **Provider Info Display**: Enhanced CLI to show provider status and recommendations  
✅ **Unified Interface**: All providers use same standardized API  

---

## 🚀 Quick Start: Free Tier Setup (Recommended)

### Step 1: Get Google API Key (100% Free)

1. Visit **[Google AI Studio](https://aistudio.google.com/apikey)**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy your API key

**No credit card required!** Free tier includes:
- 15 requests per minute
- 1 million tokens per minute
- 1,500 requests per day

### Step 2: Configure Environment

```bash
cd ~/Desktop/autonomous-computer-control

# Create/edit .env file
nano .env
```

Add these lines:
```bash
# Google Gemini (FREE tier - recommended)
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# Provider selection (auto = use free tier when available)
LLM_PROVIDER=auto
```

Save and exit (Ctrl+X, Y, Enter).

### Step 3: Install Dependencies

```bash
# Create virtual environment (if not already done)
python3 -m venv venv
source venv/bin/activate

# Install updated dependencies
pip install -r requirements.txt
```

Expected new packages:
- `google-generativeai>=0.8.0` (Gemini)
- `openai>=1.0.0` (OpenAI)
- `requests>=2.31.0` (Featherless)
- `anthropic>=0.40.0` (already installed)

### Step 4: Verify Setup

```bash
# Check provider status
python -m src.cli info
```

Expected output:
```
Provider Configuration:
┌────────────┬──────────────────────┬─────────┬────────┬──────────────┬──────┬───────────┐
│ Provider   │ Model                │ API Key │ Vision │ Computer Use │ Cost │ Free Tier │
├────────────┼──────────────────────┼─────────┼────────┼──────────────┼──────┼───────────┤
│ gemini     │ gemini-2.0-flash-exp │ ✓       │ ✓      │ ✓            │ FREE │ ✓         │
│ anthropic  │ claude-sonnet-4      │ ✗       │ ✓      │ ✓✓✓          │ $$$  │ ✗         │
│ openai     │ gpt-4o-mini          │ ✗       │ ✓      │ ✓            │ $$   │ ✗         │
│ featherless│ llama-3.1-70b        │ ✗       │ ~      │ ✓            │ $    │ ~         │
└────────────┴──────────────────────┴─────────┴────────┴──────────────┴──────┴───────────┘

Selected Provider: gemini (gemini-2.0-flash-exp)
Recommendation: ✓ Using free tier - excellent choice for cost-effective operation!
```

### Step 5: Test It

```bash
# Simple test (ensure screen recording permission is granted first)
python -m src.cli run "Take a screenshot" --provider gemini

# Check verbose output
python -m src.cli -v info
```

---

## 🔧 Alternative Provider Setup

### Option B: Anthropic Claude (Best Accuracy)

**When to use**: Need highest accuracy for computer control tasks

```bash
# Get API key from https://console.anthropic.com/
# Add to .env:
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-sonnet-4-20250514
LLM_PROVIDER=anthropic  # or 'auto' for fallback
```

**Cost**: ~$3/1M input tokens, ~$15/1M output tokens  
**Best for**: Critical automation tasks where accuracy matters most

### Option C: OpenAI (ChatGPT Users)

**When to use**: Have OpenAI API access (separate from ChatGPT Plus subscription)

```bash
# Get API key from https://platform.openai.com/api-keys
# Add to .env:
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini  # or gpt-4o for higher capability
LLM_PROVIDER=openai  # or 'auto' for fallback
```

**Cost**: ~$0.15/1M input tokens (gpt-4o-mini), ~$2.50/1M (gpt-4o)  
**Note**: ChatGPT Plus subscription ≠ API access (need separate API key)

### Option D: Featherless.ai (Open Source Models)

**When to use**: Want to use open-source models

```bash
# Get API key from https://featherless.ai/
# Add to .env:
FEATHERLESS_API_KEY=your_api_key_here
FEATHERLESS_MODEL=meta-llama/llama-3.1-70b-instruct
LLM_PROVIDER=featherless  # or 'auto' for fallback
```

**Note**: Vision support varies by model. Check model capabilities.

---

## 🎯 Usage Examples

### Auto-Select Provider (Recommended)

```bash
# System automatically chooses best available provider
python -m src.cli run "Open Safari and navigate to google.com"

# Priority: Gemini (free) → Claude → OpenAI → Featherless
```

### Force Specific Provider

```bash
# Force Gemini (free tier)
python -m src.cli run "task" --provider gemini

# Force Claude (best accuracy)
python -m src.cli run "task" --provider anthropic

# Force OpenAI
python -m src.cli run "task" --provider openai --model gpt-4o

# Force Featherless
python -m src.cli run "task" --provider featherless
```

### Check Provider Status

```bash
# View all providers and current selection
python -m src.cli info

# Verbose mode shows more details
python -m src.cli -v info
```

### Python API Usage

```python
from src.providers import ProviderFactory, ProviderType
from src.agent import ComputerUseAgent, AgentConfig

# Auto-select provider
provider = ProviderFactory.create_provider()

# Or manually specify
provider = ProviderFactory.create_provider(ProviderType.GEMINI)

# Use in agent
config = AgentConfig(provider=provider)
agent = ComputerUseAgent(config=config)
result = agent.run("Your task here")
```

---

## 💰 Cost Comparison

| Provider | Input | Output | Image | Est. Cost/Task |
|----------|-------|--------|-------|----------------|
| **Gemini Free** | FREE | FREE | FREE | **$0.00** |
| Gemini Paid | $0.075/1M | $0.30/1M | Included | $0.01-0.05 |
| GPT-4o-mini | $0.15/1M | $0.60/1M | Included | $0.02-0.10 |
| GPT-4o | $2.50/1M | $10.00/1M | Included | $0.25-1.00 |
| Claude Sonnet 4 | $3.00/1M | $15.00/1M | Included | $0.30-1.50 |

**Recommendation**: Start with Gemini free tier for development/testing, upgrade to paid tier or Claude for production if needed.

---

## 🧪 Testing

### Run Test Suite

```bash
cd ~/Desktop/autonomous-computer-control
source venv/bin/activate

# Run provider tests
python3 tests/test_providers.py
```

Tests verify:
- ✅ Provider information display
- ✅ Auto-selection based on available API keys
- ✅ Manual provider selection
- ✅ Error handling for missing keys
- ✅ Provider priority order (Gemini → Claude → OpenAI → Featherless)

### Manual Testing

```bash
# Test each provider individually (requires API keys)
python -m src.cli run "Take a screenshot" --provider gemini
python -m src.cli run "Take a screenshot" --provider anthropic
python -m src.cli run "Take a screenshot" --provider openai

# Test fallback (remove all keys except one)
# Should automatically select the available provider
```

---

## 📊 Provider Comparison Table

| Feature | Gemini | Claude | OpenAI | Featherless |
|---------|--------|--------|--------|-------------|
| **Free Tier** | ✅ Yes | ❌ No | ❌ No | Varies |
| **Vision** | ✅ Full | ✅ Full | ✅ Full | ⚠️ Limited |
| **Computer Use API** | Via functions | ✅ Native | Via functions | Via functions |
| **Cost** | FREE/$ | $$$ | $$ | $ |
| **Best For** | Development, cost-saving | Production accuracy | General use | Open source |
| **Rate Limits (Free)** | 15 RPM, 1500 RPD | N/A | N/A | Varies |
| **Setup Difficulty** | ⭐ Easy | ⭐⭐ Medium | ⭐⭐ Medium | ⭐⭐⭐ Advanced |

---

## 🔍 Troubleshooting

### "No LLM provider available" Error

**Cause**: No API keys configured  
**Solution**: Add at least one provider's API key to `.env`

```bash
# Quickest fix: Use free Gemini
GOOGLE_API_KEY=your_api_key_here
```

### "ModuleNotFoundError: No module named 'google.generativeai'"

**Cause**: Dependencies not installed  
**Solution**: Install requirements

```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Wrong Provider Selected

**Cause**: Priority order or manual override  
**Solution**: Check environment variables

```bash
# See current selection
python -m src.cli info

# Force specific provider
export LLM_PROVIDER=gemini  # or anthropic, openai, featherless
```

### Gemini Free Tier Rate Limit

**Symptom**: 429 errors after many requests  
**Solution**: 
- Wait for rate limit reset (1 minute for RPM, 1 day for RPD)
- Upgrade to paid tier (same API key, billing auto-activated)
- Add fallback provider (Claude, OpenAI)

---

## 📚 Additional Resources

- **Google Gemini**: https://ai.google.dev/
- **Anthropic Claude**: https://docs.anthropic.com/
- **OpenAI GPT**: https://platform.openai.com/docs
- **Featherless.ai**: https://featherless.ai/

---

## ✅ Implementation Checklist

- [x] Provider abstraction layer created
- [x] Google Gemini provider implemented (free tier support)
- [x] Anthropic Claude provider migrated
- [x] OpenAI GPT provider implemented
- [x] Featherless.ai provider implemented
- [x] Provider factory with auto-selection
- [x] CLI updated with provider info and selection
- [x] Environment configuration updated
- [x] Dependencies added to requirements.txt
- [x] README documentation updated
- [x] Test suite created
- [x] Setup guide created (this file)

---

## 🎁 Benefits

1. **Zero Cost Development**: Use Gemini free tier for unlimited development
2. **Flexible Scaling**: Start free, upgrade when needed
3. **Provider Redundancy**: Automatic fallback if primary provider fails
4. **Cost Optimization**: System prefers free tier when available
5. **Future-Proof**: Easy to add new providers
6. **User Choice**: Manual override for specific use cases

---

**Next Steps**: Follow the Quick Start guide above to configure your free Gemini API key and start using the system at zero cost!
