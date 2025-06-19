from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
import qrgenerate

app = FastAPI()


class Request(BaseModel):
    text: str


@app.post("/generate/")
def generate(request: Request):
    return {"message": request.text}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, log_level="debug")
