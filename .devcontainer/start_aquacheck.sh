#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

if pgrep -af "streamlit run .*streamlit_app.py" >/dev/null; then
    exit 0
fi

if [[ -x ".venv/bin/streamlit" ]]; then
    streamlit_command=(".venv/bin/streamlit")
elif command -v uv >/dev/null 2>&1; then
    streamlit_command=(uv run streamlit)
else
    streamlit_command=(streamlit)
fi

nohup "${streamlit_command[@]}" run streamlit_app.py \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    > .streamlit.log 2>&1 < /dev/null &

echo "AquaCheck is starting at http://localhost:8501"