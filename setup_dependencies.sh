#!/bin/bash

echo "============================================"
echo "  Agent Dzeck AI - Auto Install Dependencies"
echo "============================================"
echo ""

TIMEOUT_PIP=120

check_command() {
  command -v "$1" >/dev/null 2>&1
}

echo "[1/6] Checking Python..."
if check_command python3; then
  PYTHON=python3
elif check_command python; then
  PYTHON=python
else
  echo "  ERROR: Python not found."
  exit 1
fi
echo "  -> $($PYTHON --version)"

echo ""
echo "[2/6] Upgrading pip..."
$PYTHON -m pip install --upgrade pip 2>/dev/null
echo "  -> pip upgraded"

echo ""
echo "[3/6] Installing Python dependencies..."

install_pkg() {
  echo "  Installing $1..."
  timeout $TIMEOUT_PIP $PYTHON -m pip install --no-cache-dir -q "$1" 2>/dev/null
  if [ $? -eq 0 ]; then
    echo "    -> OK"
  else
    echo "    -> WARN: $1 failed"
    return 1
  fi
}

CORE_PACKAGES=(
  "fastapi"
  "uvicorn[standard]"
  "aiofiles"
  "pydantic"
  "pydantic-core"
  "python-dotenv"
  "requests"
  "httpx"
  "numpy"
  "colorama"
  "termcolor"
  "tqdm"
  "sniffio"
  "distro"
  "certifi"
  "openai"
  "configparser"
  "langid"
  "pypinyin"
  "pypdf"
  "ipython"
  "anyio"
  "jiter"
  "setuptools"
  "wheel"
  "protobuf"
)

BROWSER_PACKAGES=(
  "selenium"
  "selenium-stealth"
  "undetected-chromedriver"
  "chromedriver-autoinstaller"
  "beautifulsoup4"
  "markdownify"
  "fake-useragent"
)

ML_PACKAGES=(
  "torch --index-url https://download.pytorch.org/whl/cpu"
  "transformers"
  "adaptive-classifier"
  "sentencepiece"
  "sacremoses"
  "scipy"
  "scikit-learn"
  "safetensors"
  "faiss-cpu"
  "huggingface-hub"
  "tokenizers"
)

LLM_PROVIDER_PACKAGES=(
  "together"
  "ollama"
  "huggingface-hub"
)

OPTIONAL_PACKAGES=(
  "text2emotion"
  "soundfile"
  "protobuf"
  "ordered-set"
  "celery"
  "emoji"
  "nltk"
  "regex"
  "pillow"
  "rich"
  "markdown-it-py"
  "ollama"
)

echo ""
echo "  [Core packages]"
for pkg in "${CORE_PACKAGES[@]}"; do
  install_pkg "$pkg" || true
done
echo "  -> Core done."

echo ""
echo "  [Browser packages]"
for pkg in "${BROWSER_PACKAGES[@]}"; do
  install_pkg "$pkg" || true
done
echo "  -> Browser done."

echo ""
echo "  [ML packages - may take a while]"
for pkg in "${ML_PACKAGES[@]}"; do
  echo "  Installing $pkg..."
  timeout 600 $PYTHON -m pip install --no-cache-dir -q $pkg 2>/dev/null
  if [ $? -eq 0 ]; then
    echo "    -> OK"
  else
    echo "    -> SKIP: $pkg (non-critical)"
  fi
done
echo "  -> ML done."

echo ""
echo "  [LLM Provider packages]"
for pkg in "${LLM_PROVIDER_PACKAGES[@]}"; do
  install_pkg "$pkg" || true
done
echo "  -> LLM Provider done."

echo ""
echo "  [Optional packages]"
for pkg in "${OPTIONAL_PACKAGES[@]}"; do
  install_pkg "$pkg" || true
done
echo "  -> Optional done."

echo ""
echo "[4/6] Checking configuration..."
if [ -f "config.ini" ]; then
  echo "  -> config.ini OK"
  if ! grep -q "work_dir" config.ini; then
    echo "  WARN: work_dir not set in config.ini"
  fi
else
  echo "  WARN: config.ini missing - creating default..."
  cat > config.ini << 'EOF'
[MAIN]
is_local = False
provider_name = groq
provider_model = llama-3.3-70b-versatile
provider_server_address = https://api.groq.com/openai/v1
agent_name = Dzeck
recover_last_session = False
save_session = False
speak = False
listen = False
jarvis_personality = False
languages = id
work_dir = ./work
[BROWSER]
headless_browser = True
stealth_mode = False
EOF
  echo "  -> config.ini created"
fi

echo ""
echo "[5/6] Creating work directory..."
WORK_DIR=$(grep "work_dir" config.ini 2>/dev/null | cut -d'=' -f2 | tr -d ' ')
if [ -n "$WORK_DIR" ]; then
  mkdir -p "$WORK_DIR"
  echo "  -> $WORK_DIR created"
else
  mkdir -p "./work"
  echo "  -> ./work created (default)"
fi

echo ""
echo "[6/6] Verifying critical modules..."
$PYTHON -c "
import sys
modules = {
    'fastapi': 'FastAPI',
    'uvicorn': 'Uvicorn',
    'requests': 'Requests',
    'httpx': 'HTTPX',
    'bs4': 'BeautifulSoup4',
    'numpy': 'NumPy',
    'openai': 'OpenAI',
    'torch': 'PyTorch',
    'transformers': 'Transformers',
    'adaptive_classifier': 'AdaptiveClassifier',
    'selenium': 'Selenium',
    'langid': 'LangID',
    'scipy': 'SciPy',
    'sentencepiece': 'SentencePiece',
    'safetensors': 'SafeTensors',
    'PIL': 'Pillow',
    'together': 'Together',
    'pydantic': 'Pydantic',
    'dotenv': 'python-dotenv',
    'aiofiles': 'AioFiles',
    'markdownify': 'Markdownify',
    'colorama': 'Colorama',
    'termcolor': 'Termcolor',
    'tqdm': 'TQDM',
    'protobuf': 'Protobuf',
    'faiss': 'FAISS',
    'huggingface_hub': 'HuggingFace Hub',
    'sklearn': 'Scikit-Learn',
    'tokenizers': 'Tokenizers',
    'rich': 'Rich',
    'emoji': 'Emoji',
}
ok = 0
fail = 0
for mod, name in modules.items():
    try:
        __import__(mod)
        ok += 1
        print(f'  [OK] {name}')
    except ImportError:
        fail += 1
        print(f'  [MISSING] {name}')
print(f'\n  -> {ok}/{ok+fail} modules OK')
if fail > 0:
    print(f'  -> {fail} modules missing (may need manual install)')
" 2>/dev/null || echo "  -> Module check skipped"

echo ""
echo "============================================"
echo "  Selesai! Jalankan: python api.py"
echo "============================================"
