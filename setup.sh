sudo apt-get install pip
pv=$(python3 --version)
echo "python3 version installed: $pv"
echo "tested with python 3.10.12, may need that version installed for all to work (y: continue, n: stop)"
read choice
if [ choice == "n" ]; then
  exit
fi

python3 -m venv venv
source venv/bin/activate
pip install diffusers transformers accelerate python-multipart
pip install httpx
pip install fastapi uvicorn[standard]




