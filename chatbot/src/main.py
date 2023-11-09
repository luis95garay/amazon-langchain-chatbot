from fastapi.middleware.cors import CORSMiddleware

from .api_config import get_api


app = get_api()

# Enable requests from localhost port 3000
origins = ["http://localhost:3000", "http://localhost:9003"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
