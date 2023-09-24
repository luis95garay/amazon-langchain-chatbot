#!/bin/sh
python3 -m uvicorn assistant_api.main:app --host 0.0.0.0 --port 9000 &
python3 -m uvicorn data_processing_api.main:app --host 0.0.0.0 --port 9002