from fastapi import FastAPI
import OS
app = FastAPI()


@app.get("/")
async def root():
    return {'message': "Check it!"}
