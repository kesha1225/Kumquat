from kumquat.application import Kumquat
from kumquat.response import TextResponse, JSONResponse, HTMLResponse
from kumquat.request import Request
from kumquat.response import SimpleResponse
import logging

logging.basicConfig(level="INFO")

app = Kumquat()
app.app_name = "SUPER_APP_3000_MEGA_COOL"


@app.index()
async def index(request: Request, response: SimpleResponse):
    response.status_code = 418
    response.set_headers({"shue": "ppsh"})
    return HTMLResponse("<h1>hello</h1>")


@app.get("/<param>")
async def some_param_route(request: Request, response: SimpleResponse):
    param = request.path_dict["param"]
    return f"your path now - /{param}", 200


@app.get("/<name>/<age>")
async def some_json_route(request: Request, response: SimpleResponse):
    name = request.path_dict["name"]
    age = request.path_dict["age"]
    return {"user": {"name": name, "age": age}}


app.run()
