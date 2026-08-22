from fastapi import FastAPI
app = FastAPI()
@app.get("/health")
def health_check():
    return{"stutus": "ok"}