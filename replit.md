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
- 2026-02-14: FEATURE - Frontend: WebSocket real-time connection (status, progress, file updates)
- 2026-02-14: FEATURE - Frontend: Live Preview tab dengan iframe untuk preview website yang dibuat AI
- 2026-02-14: FEATURE - Frontend: Files tab dengan file browser dan code viewer
- 2026-02-14: FEATURE - Frontend: Quick action buttons (Website Portfolio, Kalkulator Web, To-Do App)
- 2026-02-14: FEATURE - Frontend: Progress bar real-time saat AI memproses permintaan
- 2026-02-14: FEATURE - Frontend: WebSocket "Live" indicator di sidebar
- 2026-02-14: FEATURE - Backend: WebSocket endpoint /ws untuk broadcast status updates
- 2026-02-14: FEATURE - Backend: /api/preview-files, /api/project-files, /api/file-content endpoints
- 2026-02-14: FEATURE - Backend: /api/preview/{filename} untuk serve file preview via iframe
- 2026-02-14: FEATURE - Workspace Manager: Dynamic multi-project, session isolation, project type detection
- 2026-02-14: FEATURE - Sandbox: Whitelist mode, workspace isolation per session, path restriction
- 2026-02-14: UPGRADE - CoderAgent: Full-Stack Autonomous Developer mode
- 2026-02-14: MAJOR FIX - Coder prompt ditingkatkan: larang pip install, Tkinter, server run via bash
- 2026-02-14: MAJOR FIX - BashInterpreter skip pip/npm install commands otomatis
- 2026-02-14: MAJOR FIX - Sandbox skip package install commands (return success)
- 2026-02-14: CRITICAL FIX - work_dir directory auto-creation
- 2026-02-14: CRITICAL FIX - Chat history: session disimpan sebelum new_chat/clear_history
- 2026-02-14: CRITICAL FIX - Agent stop flag & blocks_result di-reset saat new_chat/clear_history
- 2026-02-14: CRITICAL FIX - is_generating flag di-reset di finally block
- 2026-02-14: FEATURE - Download ZIP: /api/download-zip endpoint, tombol "Unduh .ZIP"
- 2026-02-14: MAJOR FIX - Router keyword override: tugas koding langsung ke code agent
- 2026-02-14: CLEANUP - Hapus semua provider kecuali Groq dan HuggingFace

## Running
- Workflow "Start application" runs `python api.py`
- Server binds to 0.0.0.0:5000
- Frontend served from same port
- First startup downloads ML models (~500MB)
