import logging

from kumquat.application import Kumquat
from kumquat.response import HTMLResponse
from kumquat.request import Request
from kumquat.response import SimpleResponse, TemplateResponse
from kumquat.utils import BackgroundTask

logging.basicConfig(level="INFO")

app = Kumquat(templates_path="custom_templates/")


@app.index()
async def index(request: Request, response: SimpleResponse):
    response.status_code = 418
    response.set_headers({"shue": "ppsh"})
    return HTMLResponse("<h1>hello</h1>")


@app.post("/")
async def post(request: Request, response: SimpleResponse):
    # getting post data
    print(await request.body())
    return {"123": "456"}


@app.middleware()
async def middleware(request: Request, response: SimpleResponse):
    response.set_headers({"extra_data": "from middleware!"})


@app.get("/render")
async def some_render_route(request: Request, response: SimpleResponse):
    return TemplateResponse("template_example.html", param="hello world")


@app.get("/<name>/<age>")
async def some_json_route(request: Request, response: SimpleResponse):
    name = request.path_dict["name"]
    age = request.path_dict["age"]
    return {"user": {"name": name, "age": age}}


def blocking_io(some_arg):
    print(some_arg)
    return sum(i * i for i in range(10 ** 7))


@app.get("/task")
async def background_task(request: Request, response: SimpleResponse):
    async with BackgroundTask(blocking_io, some_arg="hello") as task:
        result = await task()
    return {"result_of_blocking_io": str(result)}


app.run()  # or app.ngrok_run() for ngrok use
