from .api_config import get_api
from fastapi.middleware.cors import CORSMiddleware


app = get_api()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)