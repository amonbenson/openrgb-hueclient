# remove existing virtual environment
if (Test-Path .venv) { Remove-Item -Recurse -Force .venv }

# setup python virtual environment
python3 -m venv .venv
./.venv/Scripts/Activate.ps1

# install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
