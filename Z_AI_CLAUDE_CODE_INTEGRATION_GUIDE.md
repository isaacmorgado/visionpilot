# Z.AI Integration with Claude Code - Complete Guide

**Date**: 2026-01-12
**Research Sources**:
- https://github.com/xqsit94/glm
- https://docs.z.ai/devpack/tool/claude

---

## Overview

This guide documents two approaches for integrating alternative AI providers (like Z.AI/GLM) with Claude Code:

1. **Session-Based Approach** (GLM CLI model) - Temporary, non-persistent
2. **Persistent Configuration** (Z.AI model) - Modifies settings file

---

## Approach 1: Session-Based Environment Variables (GLM CLI Model)

### Architecture

**Key Principle**: Launch Claude Code with temporary environment variables that override default API endpoints without modifying configuration files.

### Implementation Pattern

```bash
#!/bin/bash
# Launch Claude Code with Z.AI/GLM configuration

export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="your_zai_api_key_here"
export ANTHROPIC_MODEL="glm-4.7"  # or glm-4-air, glm-4-flash, etc.

# Launch Claude Code with these environment variables
claude "$@"
```

### Advantages
- ✅ **Non-invasive**: No modification to `~/.claude/settings.json`
- ✅ **Session-scoped**: Each terminal session can use different providers
- ✅ **Clean separation**: Users can run `claude` (default) or `zai-claude` (custom)
- ✅ **No file conflicts**: Multiple configurations don't interfere

### Disadvantages
- ⚠️ Requires setting environment variables each session
- ⚠️ Not persistent across terminal sessions
- ⚠️ Needs wrapper script for convenience

---

## Approach 2: Persistent Settings Configuration (Z.AI Model)

### Architecture

**Key Principle**: Modify `~/.claude/settings.json` to permanently configure Claude Code with custom API endpoints.

### Configuration File Location

```bash
~/.claude/settings.json
```

### Configuration Format

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "your_zai_api_key_here",
    "API_TIMEOUT_MS": "3000000"
  },
  "modelMappings": {
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.7",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.7",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4-air"
  }
}
```

### Setup Methods

#### Method 1: Automated Setup (Recommended)
```bash
npx @z_ai/coding-helper
```
Provides guided CLI setup that:
- Prompts for API key
- Automatically configures environment variables
- Sets up model mappings
- Configures MCP servers

#### Method 2: Script-Based Setup (macOS/Linux)
```bash
curl -fsSL https://cdn.bigmodel.cn/install/claude_code_zai_env.sh | bash
```
Automatically modifies `~/.claude/settings.json`

#### Method 3: Manual Configuration
1. Open `~/.claude/settings.json` in text editor
2. Add `env` section with credentials
3. Add `modelMappings` section (optional)
4. Save and restart Claude Code

### Advantages
- ✅ **Persistent**: Configuration survives terminal restarts
- ✅ **Convenient**: No need to set environment variables
- ✅ **Automatic**: Works for all Claude Code sessions
- ✅ **Model mappings**: Can customize which models map to Opus/Sonnet/Haiku

### Disadvantages
- ⚠️ Modifies system configuration file
- ⚠️ Requires manual editing to switch providers
- ⚠️ Can prevent automatic updates if custom mappings used
- ⚠️ All sessions use same provider (no per-session control)

---

## Model Mappings

### Z.AI/GLM Model Options

| Claude Model | Z.AI Mapping | Use Case |
|--------------|--------------|----------|
| Opus 4.5 | GLM-4.7 | Complex tasks, architecture |
| Sonnet 4.5 | GLM-4.7 | Balanced performance |
| Haiku 3.5 | GLM-4-Air | Fast, simple tasks |

### Custom Model Selection

You can configure specific models per Claude tier:

```json
{
  "modelMappings": {
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "glm-4.7",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "glm-4.6",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "glm-4-air"
  }
}
```

---

## MCP Integration

Once configured, Claude Code supports these Z.AI MCP servers:

1. **Vision MCP Server** - Image analysis capabilities
2. **Web Search MCP Server** - Real-time web search
3. **Web Reader MCP Server** - Web page reading and extraction

These are automatically enabled with Z.AI configuration.

---

## Environment Variables Reference

### Required Variables

| Variable | Purpose | Z.AI Value |
|----------|---------|------------|
| `ANTHROPIC_BASE_URL` | API endpoint | `https://api.z.ai/api/anthropic` |
| `ANTHROPIC_AUTH_TOKEN` | Authentication | Your Z.AI API key |
| `API_TIMEOUT_MS` | Request timeout | `3000000` (50 minutes) |

### Optional Variables (for session-based approach)

| Variable | Purpose | Example |
|----------|---------|---------|
| `ANTHROPIC_MODEL` | Override model | `glm-4.7` |

---

## Getting Z.AI API Key

1. Visit Z.AI Open Platform
2. Register or login
3. Navigate to API Key Management
4. Create new API key
5. Copy key for configuration

---

## Implementation Example: Wrapper Script

Create a wrapper script for session-based approach:

```bash
#!/bin/bash
# File: ~/bin/zai-claude

export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="${ZAI_API_KEY:-$(cat ~/.zai/api_key 2>/dev/null)}"
export ANTHROPIC_MODEL="${ZAI_MODEL:-glm-4.7}"
export API_TIMEOUT_MS="3000000"

if [ -z "$ANTHROPIC_AUTH_TOKEN" ]; then
    echo "Error: ZAI_API_KEY not set and ~/.zai/api_key not found"
    echo "Set ZAI_API_KEY environment variable or create ~/.zai/api_key file"
    exit 1
fi

# Launch Claude Code with Z.AI configuration
exec claude "$@"
```

### Usage
```bash
chmod +x ~/bin/zai-claude

# Use Z.AI
zai-claude

# Use default Claude
claude
```

---

## Troubleshooting

### Configuration Not Taking Effect

**Solution 1: Restart Claude Code**
1. Close all Claude Code instances
2. Open new terminal window
3. Restart Claude Code

**Solution 2: Regenerate Settings**
```bash
rm ~/.claude/settings.json
# Settings will regenerate on next launch
```

### Authentication Errors

Check that:
- API key is valid and not expired
- Base URL is exactly `https://api.z.ai/api/anthropic`
- No trailing slashes in URL
- Environment variables are exported correctly

### Timeout Issues

Increase timeout if experiencing connection issues:
```bash
export API_TIMEOUT_MS="6000000"  # 100 minutes
```

---

## Hybrid Approach: Best of Both Worlds

For maximum flexibility, use both approaches:

1. **Default**: Configure `~/.claude/settings.json` for Z.AI (persistent)
2. **Override**: Use wrapper script with environment variables for testing other providers

Environment variables take precedence over settings file, allowing temporary overrides.

---

## Comparison: GLM CLI vs Z.AI Configuration

| Aspect | GLM CLI | Z.AI Config |
|--------|---------|-------------|
| **Persistence** | Session-only | Permanent |
| **File Modification** | None | Modifies settings.json |
| **Ease of Use** | Requires script | Automatic after setup |
| **Flexibility** | High (per-session) | Low (system-wide) |
| **Setup Complexity** | Low | Medium |
| **Maintenance** | Manual updates | Auto-updates supported |

---

## Recommendations

### For Development/Testing
Use **Session-Based Approach** (GLM CLI model):
- Test multiple providers easily
- No risk to production configuration
- Clean separation of concerns

### For Production Use
Use **Persistent Configuration** (Z.AI model):
- Consistent behavior across sessions
- No manual environment variable management
- Automated setup available

### For Maximum Flexibility
Use **Hybrid Approach**:
- Persistent config for primary provider
- Environment variables for testing/overrides

---

## Security Considerations

### API Key Storage

**Best Practices**:
1. Never commit API keys to git
2. Use restricted file permissions: `chmod 600 ~/.claude/settings.json`
3. Consider using environment variables instead of config file for CI/CD
4. Rotate keys regularly

### Configuration File Protection

```bash
# Restrict settings file to user-only access
chmod 600 ~/.claude/settings.json

# Verify permissions
ls -la ~/.claude/settings.json
# Should show: -rw------- (600)
```

---

## Integration with VisionPilot

For VisionPilot integration, the session-based approach is recommended:

```python
import os
import subprocess

def launch_claude_with_zai(api_key: str, model: str = "glm-4.7"):
    """Launch Claude Code with Z.AI configuration."""
    env = os.environ.copy()
    env.update({
        "ANTHROPIC_BASE_URL": "https://api.z.ai/api/anthropic",
        "ANTHROPIC_AUTH_TOKEN": api_key,
        "ANTHROPIC_MODEL": model,
        "API_TIMEOUT_MS": "3000000"
    })

    subprocess.run(["claude"], env=env)
```

---

## Future Enhancements

Potential improvements for integration:

1. **Multi-Provider Support**: Switch between OpenAI, Anthropic, Z.AI at runtime
2. **Cost Tracking**: Monitor API usage across providers
3. **Performance Metrics**: Compare response times and quality
4. **Automatic Failover**: Fall back to alternative provider on errors
5. **Provider-Specific Features**: Leverage unique capabilities per provider

---

## Resources

- **Z.AI Documentation**: https://docs.z.ai/devpack/tool/claude
- **GLM CLI GitHub**: https://github.com/xqsit94/glm
- **Claude Code CLI**: https://github.com/anthropics/claude-code
- **BigModel Platform**: https://open.bigmodel.cn

---

**Status**: Documentation Complete
**Next Steps**: Implement wrapper script or automated configuration for VisionPilot project
