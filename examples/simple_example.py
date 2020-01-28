import logging

from kumquat.application import Kumquat
from kumquat.response import HTMLResponse
from kumquat.request import Request
from kumquat.response import SimpleResponse, TemplateResponse

logging.basicConfig(level="INFO")

app = Kumquat(templates_path="custom_templates/")
app.app_name = "KumquatApp"


@app.index()
async def index(request: Request, response: SimpleResponse):
    response.status_code = 418
    response.set_headers({"shue": "ppsh"})
    return HTMLResponse("<h1>hello</h1>")


@app.get("/render")
async def some_render_route(request: Request, response: SimpleResponse):
    return TemplateResponse("template_example.html", param="hello world")


@app.get("/<name>/<age>")
async def some_json_route(request: Request, response: SimpleResponse):
    name = request.path_dict["name"]
    age = request.path_dict["age"]
    return {"user": {"name": name, "age": age}}


app.run()
