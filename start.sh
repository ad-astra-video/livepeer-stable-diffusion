GPU="cuda:0" GO_LIVEPEER_URL=https://svd.ad-astra.video:9935 uvicorn sd-video-api:app --host 0.0.0.0 --port 9000 --reload --log-level=debug
