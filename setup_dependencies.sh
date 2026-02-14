#!/bin/bash

echo "============================================"
echo "  Agent Dzeck AI - Auto Install Dependencies"
echo "============================================"
echo ""

TIMEOUT_PIP=180
FAILED_PACKAGES=()
SUCCESS_COUNT=0
FAIL_COUNT=0

check_command() {
  command -v "$1" >/dev/null 2>&1
}

install_pkg() {
  local pkg="$1"
  local extra_args="$2"
  echo "  Installing $pkg..."
  if [ -n "$extra_args" ]; then
    timeout $TIMEOUT_PIP python3 -m pip install --no-cache-dir -q $extra_args "$pkg" 2>/dev/null
  else
    timeout $TIMEOUT_PIP python3 -m pip install --no-cache-dir -q "$pkg" 2>/dev/null
  fi
  if [ $? -eq 0 ]; then
    echo "    -> OK"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    return 0
  else
    echo "    -> FAILED: $pkg"
    FAILED_PACKAGES+=("$pkg")
    FAIL_COUNT=$((FAIL_COUNT + 1))
    return 1
  fi
}

install_pkg_silent() {
  local pkg="$1"
  local extra_args="$2"
  if [ -n "$extra_args" ]; then
    timeout $TIMEOUT_PIP python3 -m pip install --no-cache-dir -q $extra_args "$pkg" 2>/dev/null
  else
    timeout $TIMEOUT_PIP python3 -m pip install --no-cache-dir -q "$pkg" 2>/dev/null
  fi
}

echo "[1/7] Checking Python..."
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
echo "[2/7] Upgrading pip & setuptools..."
$PYTHON -m pip install --upgrade pip setuptools wheel 2>/dev/null
echo "  -> Done"

echo ""
echo "[3/7] Installing Core packages..."

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
  "ordered-set"
  "rich"
  "emoji"
  "nltk"
  "regex"
  "pillow"
  "markdown-it-py"
)

for pkg in "${CORE_PACKAGES[@]}"; do
  install_pkg "$pkg"
done
echo "  -> Core done."

echo ""
echo "[4/7] Installing Browser packages..."

BROWSER_PACKAGES=(
  "selenium"
  "selenium-stealth"
  "undetected-chromedriver"
  "chromedriver-autoinstaller"
  "beautifulsoup4"
  "markdownify"
  "fake-useragent"
)

for pkg in "${BROWSER_PACKAGES[@]}"; do
  install_pkg "$pkg"
done
echo "  -> Browser done."

echo ""
echo "[5/7] Installing ML packages (this may take several minutes)..."

echo "  Installing PyTorch (CPU)..."
timeout 600 $PYTHON -m pip install --no-cache-dir -q torch --index-url https://download.pytorch.org/whl/cpu 2>/dev/null
if [ $? -eq 0 ]; then
  echo "    -> PyTorch OK"
  SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
else
  echo "    -> PyTorch FAILED (will retry with default index)"
  timeout 600 $PYTHON -m pip install --no-cache-dir -q torch 2>/dev/null
  if [ $? -eq 0 ]; then
    echo "    -> PyTorch OK (fallback)"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
  else
    echo "    -> PyTorch FAILED"
    FAILED_PACKAGES+=("torch")
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
fi

ML_PACKAGES=(
  "transformers"
  "adaptive-classifier"
  "sentencepiece"
  "sacremoses"
  "scipy"
  "scikit-learn"
  "safetensors"
  "huggingface-hub"
  "tokenizers"
)

for pkg in "${ML_PACKAGES[@]}"; do
  install_pkg "$pkg"
done
echo "  -> ML done."

echo ""
echo "[6/7] Installing LLM Provider packages..."

LLM_PROVIDER_PACKAGES=(
  "together"
  "ollama"
  "huggingface-hub"
  "celery"
)

for pkg in "${LLM_PROVIDER_PACKAGES[@]}"; do
  install_pkg "$pkg"
done

OPTIONAL_PACKAGES=(
  "text2emotion"
  "soundfile"
)

for pkg in "${OPTIONAL_PACKAGES[@]}"; do
  echo "  Installing $pkg (optional)..."
  install_pkg_silent "$pkg"
  if [ $? -eq 0 ]; then
    echo "    -> OK"
    SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
  else
    echo "    -> SKIP (optional)"
  fi
done
echo "  -> Provider & optional done."

echo ""
echo "[7/7] Verifying critical modules..."
$PYTHON << 'PYEOF'
import importlib
modules = {
    'fastapi': 'FastAPI', 'uvicorn': 'Uvicorn', 'requests': 'Requests',
    'httpx': 'HTTPX', 'bs4': 'BeautifulSoup4', 'numpy': 'NumPy',
    'openai': 'OpenAI', 'torch': 'PyTorch', 'transformers': 'Transformers',
    'adaptive_classifier': 'AdaptiveClassifier', 'selenium': 'Selenium',
    'langid': 'LangID', 'scipy': 'SciPy', 'sentencepiece': 'SentencePiece',
    'safetensors': 'SafeTensors', 'PIL': 'Pillow', 'together': 'Together',
    'pydantic': 'Pydantic', 'dotenv': 'python-dotenv', 'aiofiles': 'AioFiles',
    'markdownify': 'Markdownify', 'colorama': 'Colorama', 'termcolor': 'Termcolor',
    'tqdm': 'TQDM', 'huggingface_hub': 'HuggingFace Hub',
    'sklearn': 'Scikit-Learn', 'tokenizers': 'Tokenizers', 'rich': 'Rich',
    'emoji': 'Emoji', 'nltk': 'NLTK', 'regex': 'Regex',
    'celery': 'Celery', 'sacremoses': 'Sacremoses', 'ollama': 'Ollama',
    'pypdf': 'PyPDF', 'IPython': 'IPython', 'ordered_set': 'OrderedSet',
}
ok = 0
fail = 0
for mod, name in modules.items():
    try:
        importlib.import_module(mod)
        ok += 1
        print(f'  [OK] {name}')
    except ImportError:
        fail += 1
        print(f'  [MISSING] {name}')
print(f'\n  -> {ok}/{ok+fail} modules verified')
if fail > 0:
    print(f'  -> {fail} modules missing (may need manual install)')
else:
    print('  -> All critical modules installed!')
PYEOF

echo ""
echo "============================================"
if [ ${#FAILED_PACKAGES[@]} -gt 0 ]; then
  echo "  WARNING: ${FAIL_COUNT} packages failed to install:"
  for pkg in "${FAILED_PACKAGES[@]}"; do
    echo "    - $pkg"
  done
  echo ""
fi
echo "  ${SUCCESS_COUNT} packages installed successfully"
echo ""

if [ -f "config.ini" ]; then
  echo "  config.ini: OK"
else
  echo "  WARNING: config.ini missing!"
fi

WORK_DIR=$(grep "work_dir" config.ini 2>/dev/null | cut -d'=' -f2 | tr -d ' ')
if [ -n "$WORK_DIR" ]; then
  mkdir -p "$WORK_DIR" 2>/dev/null
fi

echo ""
echo "  Selesai! Jalankan: python api.py"
echo "============================================"
