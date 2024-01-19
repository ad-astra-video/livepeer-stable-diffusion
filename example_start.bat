@ECHO OFF
cd %~dp0
py -3 -m ensurepip

echo python3 version installed:
python3 --version
set /p "choice=tested with python 3.10.12, may need that version installed for all to work (y: continue, n: stop): "
IF %choice% == "n" (
  exit
)
pip uninstall virtualenv -y
pip uninstall pipenv -y
pip install pipenv
set /p "update=if received warning of update to path needed, add path in warning to environment variables and then close and re-run setup.bat (press enter if no warning received)"

pipenv install
REM install packages in virtualenv with pipenv (auto creates virtualenv)
REM pipenv uninstall torch torchaudio torchvision -y
REM pipenv install torch torchvision torchaudio
REM pipenv install diffusers transformers accelerate python-multipart opencv-python
REM pipenv install httpx
REM pipenv install fastapi uvicorn[standard]

echo "installation complete!"
pause




