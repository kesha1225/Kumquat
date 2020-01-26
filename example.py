from kumquat.application import Kumquat
from kumquat.response import TextResponse, JSONResponse, HTMLResponse
from kumquat.request import Request
import logging

logging.basicConfig(level="INFO")

app = Kumquat()
app.app_name = "SUPER_APP_3000_MEGA_COOL"


@app.index()
async def index(request: Request):
    return HTMLResponse("hello")


@app.get("/<param>")
async def index(request: Request):
    print(request.path_dict)
    return TextResponse("hi")


app.run()
