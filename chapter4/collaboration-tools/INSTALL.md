# Installation Guide

## Quick Installation

### 1. Install Core Dependencies

```bash
cd projects/week4/collaboration-tools

# Upgrade pip first
pip install --upgrade pip

# Install with correct versions
pip install --upgrade pydantic>=2.8.0 pydantic-settings>=2.4.0 anyio>=4.5.0
pip install -r requirements.txt
```

### 2. Install Browser Dependencies

```bash
# Install Playwright browsers
playwright install chromium
```

### 3. Configure Environment

```bash
# Copy example configuration
cp env.example .env

# Edit .env with your credentials
# At minimum, set OPENAI_API_KEY for browser AI tasks
nano .env  # or use your preferred editor
```

### 4. Verify Installation

```bash
# Run basic tests
python test_basic.py

# Or run the quickstart demo
python quickstart.py
```

## Troubleshooting

### Issue: Pydantic Import Errors

**Error:** `ModuleNotFoundError: No module named 'pydantic._internal._signature'`

**Solution:**
```bash
pip install --upgrade pydantic>=2.8.0 pydantic-settings>=2.4.0
```

### Issue: anyio Type Errors

**Error:** `TypeError: 'function' object is not subscriptable`

**Solution:**
```bash
pip install --upgrade anyio>=4.5.0
```

### Issue: Browser Errors

**Error:** Browser fails to start or Playwright not found

**Solution:**
```bash
playwright install chromium --force
```

### Issue: MCP Server Won't Start

**Solution:**
```bash
# Clean install
pip uninstall mcp fastmcp pydantic pydantic-settings anyio -y
pip install -r requirements.txt
```
