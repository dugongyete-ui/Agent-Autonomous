# Agent Dzeck AI

## Overview
Agent Dzeck AI adalah sistem AI agent otonom dengan kemampuan browsing web, eksekusi kode, dan manipulasi file. Menggunakan backend FastAPI yang melayani frontend React, didukung oleh model Groq dan HuggingFace. Fitur meliputi eksekusi kode sandbox, routing agent berbasis ML (AdaptiveClassifier), arsitektur multi-agent, dan pemulihan error yang robust.

## Architecture
- **Backend**: Python FastAPI (api.py) on port 5000
- **Frontend**: React app pre-built at `frontend/agentic-seek-front/build/`, served as static files by FastAPI
- **AI Providers**: Hanya 2 provider yang didukung:
  - **Groq** - llama-3.3-70b-versatile (utama)
  - **HuggingFace** - Qwen/Qwen2.5-72B-Instruct (gratis)
- **Agent System**: ML-based router (AdaptiveClassifier + keyword override) selects from 5 agents:
  - CasualAgent (Dzeck) - general conversation
  - CoderAgent (Coder) - Full-Stack Autonomous Developer with sandbox safety
  - FileAgent (File) - file manipulation
  - BrowserAgent (Browser) - web browsing via Selenium/Chromium headless
  - PlannerAgent (Planner) - multi-step task planning
- **Router**: Keyword-based override untuk tugas koding (mendeteksi "buatkan website", "buat program", dll) + ML classifier sebagai fallback
- **Memory**: Conversation memory with compression
- **Language**: LanguageUtility with MarianMT translation models
- **Browser**: Selenium with headless Chromium
- **Sandbox**: Safe code execution with whitelist mode, workspace isolation per session, path restriction
- **Workspace Manager**: Dynamic multi-project workspace with session isolation, project type detection
- **Real-time**: WebSocket for live status updates, execution progress, file notifications
- **Live Preview**: Iframe-based preview for generated websites, file selector, project file viewer

## Key Files
- `api.py` - FastAPI server, serves frontend + API endpoints
- `config.ini` - Configuration (provider, model, browser settings, work_dir)
- `sources/llm_provider.py` - LLM provider (hanya Groq dan HuggingFace)
- `sources/interaction.py` - Main interaction loop
- `sources/router.py` - Agent routing (keyword override + AdaptiveClassifier)
- `sources/browser.py` - Browser automation via Selenium
- `sources/memory.py` - Conversation memory
- `sources/language.py` - Language detection + translation
- `sources/sandbox.py` - Safe code execution sandbox
- `sources/agents/` - Agent implementations
  - `code_agent.py` - CoderAgent with sandbox (max 7 attempts, auto-fix)
  - `planner_agent.py` - PlannerAgent
  - `casual_agent.py` - CasualAgent
  - `browser_agent.py` - BrowserAgent
  - `file_agent.py` - FileAgent
- `setup_dependencies.sh` - Auto-install all dependencies (dengan --break-system-packages)

## Configuration
- Provider: huggingface atau groq (set in config.ini)
- HUGGINGFACE_API_KEY: stored as secret
- GROQ_API_KEY: stored as secret
- agent_name: Dzeck
- Browser: headless mode
- work_dir: /home/runner/workspace/work
- languages: id (Indonesian)

## User Preferences
- Language: Indonesian (Bahasa Indonesia)
- Hanya gunakan 2 provider: Groq dan HuggingFace
- Provider lain (OpenAI, DeepSeek, Together, Google, OpenRouter, Ollama, Anthropic, LM-Studio) sudah dihapus
- Project name: Agent Dzeck AI

## Recent Changes
- 2026-02-14: MAJOR FEATURE - Autonomous Orchestrator: Plan→Execute→Observe→Reflect loop di PlannerAgent
- 2026-02-14: FEATURE - sources/orchestrator.py: AutonomousOrchestrator dengan WebSocket status updates, auto-retry, recovery plan
- 2026-02-14: UPGRADE - Planner prompt: autonomous principles, detailed task instructions, no-confirmation policy
- 2026-02-14: CRITICAL FIX - Sandbox: auto-strip server start code (app.run(), uvicorn.run(), if __name__) sebelum eksekusi
- 2026-02-14: CRITICAL FIX - Port 5000 conflict resolved: sandbox mencegah kode bind ke port 5000
- 2026-02-14: FEATURE - Auto-install dependencies script (install_deps.py) terintegrasi di startup
- 2026-02-14: UPGRADE - Coder prompt diperkuat: larangan eksplisit app.run(), port 5000, dan socket server
- 2026-02-14: UPGRADE - Jarvis coder prompt juga diupdate dengan aturan yang sama
- 2026-02-14: FIX - Renamed all AgenticSeek references to Agent-DzeckAi
- 2026-02-14: FIX - Model selector now visible in chat header (clickable badge)
- 2026-02-14: FIX - Default model changed to Qwen/Qwen2.5-72B-Instruct
- 2026-02-14: FEATURE - Frontend: WebSocket real-time, Live Preview, Files tab, Quick actions
- 2026-02-14: FEATURE - Backend: WebSocket, preview, project files, download ZIP endpoints
- 2026-02-14: FEATURE - Workspace Manager: Dynamic multi-project, session isolation
- 2026-02-14: FEATURE - Sandbox: Whitelist mode, workspace isolation, path restriction
- 2026-02-14: UPGRADE - CoderAgent: Full-Stack Autonomous Developer mode (max 7 attempts, auto-fix)
- 2026-02-14: MAJOR FIX - BashInterpreter & Sandbox skip pip/npm install commands
- 2026-02-14: MAJOR FIX - Router keyword override: tugas koding langsung ke code agent
- 2026-02-14: CLEANUP - Hapus semua provider kecuali Groq dan HuggingFace

## Running
- Workflow "Start application" runs `python api.py`
- Server binds to 0.0.0.0:5000
- Frontend served from same port
- First startup downloads ML models (~500MB)
