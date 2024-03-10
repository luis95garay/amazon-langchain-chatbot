from fastapi.middleware.cors import CORSMiddleware

from .api_config import get_api


app = get_api()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
