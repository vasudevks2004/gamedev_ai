# Personal AI Game Development Assistant (Ashwin)

An intelligent, local-first, screen-aware, and voice-enabled companion tailored specifically for **Ashwin's** game development journey across **Unreal Engine 5**, **Modern C++**, and **Blender 4.x**.

---

## 🎮 Core Capabilities

1. **Multi-Disciplinary Mentor**:
   - Senior Unreal Engine 5 Software Architect
   - Modern C++ Game Programming Instructor (Concept $\to$ Engine Application $\to$ Example $\to$ Pitfalls $\to$ Practice Quiz)
   - Blender-to-Unreal 3D Technical Artist
   - Methodical Debugging Assistant (ERROR $\to$ UNDERSTAND $\to$ LOCATE $\to$ ROOT CAUSE $\to$ FIX $\to$ VERIFY $\to$ PREVENT)
   - Milestone & Study Roadmap Planner
2. **Context-Aware Workspace**:
   - Tracks Active Project (e.g. `ShooterGame`), Engine Version (`UE 5.4`), Current File (`WeaponComponent.cpp`), Active Task, and compiler errors.
3. **Hardware Acceleration**:
   - Designed to run locally with your **NVIDIA GeForce RTX 4060 GPU** via **Ollama** (`qwen2.5-coder:7b`, `llama3.1:8b`), with zero-latency fallback to the local offline mentor engine.
4. **Multimodal HUD**:
   - Real-time screen sharing and inspection for Unreal Engine Editor / Blender viewports.
   - Push-to-Talk voice recognition and speech synthesis.

---

## 🚀 Quick Start (For You or a Friend)

### Option 1: Double-Click (Zero Setup)
Simply double-click **`start.bat`** (or `run.bat`)!
It will:
1. Auto-detect Python 3.10+
2. Auto-install any missing dependencies (`pip install -r backend/requirements.txt`)
3. Automatically launch your default browser to **`http://localhost:8000`**

### Option 2: PowerShell
Run from PowerShell:
```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

### Option 3: Manual Terminal
```powershell
pip install -r backend/requirements.txt
$env:PYTHONPATH = "backend"
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

---

## 🧪 Verification & Testing
Execute the comprehensive test suite anytime:
```powershell
$env:PYTHONPATH = "V:\personal-gamedev-ai\backend"
python -m pytest V:\personal-gamedev-ai\backend\tests\test_core.py -v
```

---

## 📁 Architecture Overview
```
personal-gamedev-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py           # REST & WebSocket endpoints
│   │   ├── core/
│   │   │   ├── config.py           # Engine & hardware settings
│   │   │   ├── llm_adapter.py      # Ollama, Mock, and Cloud LLM adapters
│   │   │   └── prompt_engine.py    # Game Dev Master Prompts & Mode Routing
│   │   ├── memory/
│   │   │   ├── context_store.py    # Project, file, task, and error state
│   │   │   └── user_profile.py     # Ashwin's profile & skill tracking
│   │   └── main.py                 # FastAPI application & static mount
│   ├── tests/
│   │   └── test_core.py            # Automated tests
│   └── requirements.txt
├── frontend/
│   └── public/
│       ├── index.html              # Modern dark-mode Unreal Slate HUD
│       ├── app.js                  # Chat, speech, screen capture logic
│       └── style.css               # Unreal Slate dark theme styling
├── data/
│   └── profiles/                   # Persistent user & memory JSON stores
└── run.ps1                         # Easy launcher script
```
