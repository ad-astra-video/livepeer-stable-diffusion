sudo apt-get install pip
sudo pip install pipenv
pv=$(python3 --version)
echo "python3 version installed: $pv"
echo "tested with python 3.10.12, may need that version installed for all to work (y: continue, n: stop)"
read choice
if [ choice == "n" ]; then
  exit
fi

pipenv install
#pip install diffusers transformers accelerate python-multipart opencv-python
#pip install httpx
#pip install fastapi uvicorn[standard]




