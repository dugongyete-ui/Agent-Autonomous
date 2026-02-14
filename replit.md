# AgenticSeek / KodeAgent

## Overview
AgenticSeek is an autonomous AI agent system with web browsing, code execution, and file manipulation capabilities. It uses a FastAPI backend serving a React frontend, powered by Groq's llama-3.3-70b-versatile model. Features include sandboxed code execution, ML-based agent routing (BART + AdaptiveClassifier), multi-agent architecture, and robust error recovery.

## Architecture
- **Backend**: Python FastAPI (api.py) on port 5000
- **Frontend**: React app pre-built at `frontend/agentic-seek-front/build/`, served as static files by FastAPI
- **AI Provider**: Groq API with llama-3.3-70b-versatile model
- **Agent System**: ML-based router (BART zero-shot + AdaptiveClassifier) selects from 5 agents:
  - CasualAgent (Jarvis) - general conversation
  - CoderAgent (Coder) - code execution with sandbox safety
  - FileAgent (File) - file manipulation
  - BrowserAgent (Browser) - web browsing via Selenium/Chromium headless
  - PlannerAgent (Planner) - multi-step task planning with robust JSON parsing
- **Memory**: Conversation memory with compression via LED summarization model (pszemraj/led-base-book-summary)
- **Language**: LanguageUtility with MarianMT translation models (Helsinki-NLP)
- **Browser**: Selenium with headless Chromium for web automation
- **Sandbox**: Safe code execution with pattern blocking, timeout, resource limiting, output truncation

## Key Files
- `api.py` - FastAPI server, serves frontend + API endpoints
- `config.ini` - Configuration (provider, model, browser settings, work_dir)
- `sources/llm_provider.py` - LLM provider abstraction (Groq, OpenAI, Anthropic, etc.)
- `sources/interaction.py` - Main interaction loop
- `sources/router.py` - ML-based agent routing (AdaptiveClassifier + BART zero-shot)
- `sources/browser.py` - Browser automation via Selenium
- `sources/memory.py` - Conversation memory with LED-based compression
- `sources/language.py` - Language detection (langid) + translation (MarianMT)
- `sources/sandbox.py` - Safe code execution sandbox (Python, JS, Go, Bash)
- `sources/schemas.py` - Request/response schemas
- `sources/agents/` - Agent implementations
  - `code_agent.py` - CoderAgent with sandbox integration
  - `planner_agent.py` - PlannerAgent with robust JSON parsing (4 fallback methods)
  - `casual_agent.py` - CasualAgent for general chat
  - `browser_agent.py` - BrowserAgent for web browsing
  - `file_agent.py` - FileAgent for file operations
- `sources/tools/` - Tool implementations
  - `PyInterpreter.py` - Python code execution
  - `BashInterpreter.py` - Bash command execution with safety checks
  - `fileFinder.py` - File search and reading
  - `searxSearch.py` - Web search (DuckDuckGo fallback, SearxNG optional)
  - `webSearch.py` - Web search via SerpApi (deprecated)
  - `flightSearch.py` - Flight info via SerpApi
  - `mcpFinder.py` - MCP server discovery
  - `safety.py` - Command safety validation
- `setup_dependencies.sh` - Auto-install all dependencies
- `llm_router/` - Pre-trained AdaptiveClassifier model for agent routing

## Dependencies (Heavy)
- PyTorch (CPU, ~200MB) - ML backbone
- Transformers (~300MB) - BART, MarianMT, LED models
- AdaptiveClassifier - Agent routing model
- Selenium + chromedriver - Browser automation
- Full list in setup_dependencies.sh

## Configuration
- Provider: groq (set in config.ini)
- Model: llama-3.3-70b-versatile
- GROQ_API_KEY: stored as secret
- Browser: headless mode (required for Replit environment)
- work_dir: /home/runner/workspace/work

## User Preferences
- Language: Indonesian (Bahasa Indonesia)
- Keep all heavy ML dependencies (torch, transformers) - user explicitly approved 2GB+ size
- Full ML-based routing preferred over lightweight keyword-based

## Recent Changes
- 2026-02-13: Restored full ML router (BART + AdaptiveClassifier) with torch/transformers
- 2026-02-13: Restored full memory compression with LED summarization model
- 2026-02-13: Upgraded Sandbox: added JS/Go support, resource limiting, output truncation, logging
- 2026-02-13: Updated setup_dependencies.sh with complete dependency list
- 2026-02-13: Added work_dir to config.ini
- 2026-02-13: Fixed port 5000 conflict (killed stale Node.js/Expo processes)
- 2026-02-13: Fixed Memory.get() to strip unsupported fields before sending to Groq API
- 2026-02-13: Added Sandbox system (SafeExecutor) with dangerous pattern checks
- 2026-02-13: Fixed PlannerAgent JSON parsing with 4 fallback extraction methods
- 2026-02-13: Fixed interaction.py is_active property/attribute conflict
- 2026-02-13: Speech import made optional with try/except fallback
- 2026-02-14: PlannerAgent now displays plan in chat (format_plan_text, current_plan, plan_progress)
- 2026-02-14: Added normalize_agent_name() with alias mapping for robust agent name parsing
- 2026-02-14: Increased make_plan retries to 5 with escalating retry prompts
- 2026-02-14: Plan progress shown real-time in chat: "Langkah X dari Y" with current task
- 2026-02-14: parse_agent_tasks fallback: auto-detect plan key, fallback unknown agents to coder
- 2026-02-14: Updated setup_dependencies.sh with LLM providers, more ML packages, pip upgrade, module verification
- 2026-02-14: Added fallback plan builder (try_build_fallback_plan) - extracts tasks from non-JSON LLM responses
- 2026-02-14: Improved planning prompt with stronger JSON format enforcement in Indonesian
- 2026-02-14: Added [MODELS] section to config.ini with all supported providers and model options
- 2026-02-14: ChromeDriver discovery: added Nix store search fallback for dynamic paths
- 2026-02-14: Cleaned up requirements.txt (removed duplicates, added huggingface-hub, tokenizers, rich, emoji, nltk)

## Running
- Workflow "Start application" runs `python api.py`
- Server binds to 0.0.0.0:5000
- Frontend served from same port
- First startup downloads ML models (~500MB), subsequent starts use cached models
