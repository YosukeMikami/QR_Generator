from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
import qrgenerate

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class Request(BaseModel):
    text: str


@app.post("/generate/")
def generate(request: Request):
    return {"message": request.text}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, log_level="debug")
