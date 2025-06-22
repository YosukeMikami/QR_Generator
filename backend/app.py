from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
import uvicorn
from pydantic import BaseModel
import qrgenerate
from midcode import LengthError

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
    error_correction_level: str
    format: str
    size: int
    dpi: int


@app.post("/generate/")
def generate(request: Request):
    try:
        buf = qrgenerate.main(
            request.text,
            request.error_correction_level,
            format=request.format,
            pixel_num=request.size,
            dpi=request.dpi,
            blob=True
        )
    except LengthError:
        raise HTTPException(
            status_code=422,
            detail="input text is too long"
        )
    if buf is not None:
        return Response(
            content=buf.read(),
            media_type=f"image/{request.format}"
        )
    else:
        raise HTTPException(
            status_code=500,
            detail="failed to generate"
        )


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000, log_level="debug")
