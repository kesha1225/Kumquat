# kumquat

Simple asynchronous web framework, based on uvicorn.
  
<img src="https://i.imgur.com/8iU3Ex6l.jpg" title="source: imgur.com" />

### Installation

Stable:
```
pip install kumquat
```

Unstable:
```
pip install https://github.com/kesha1225/Kumquat/archive/master.zip --upgrade
```

### Usage

You can see more examples [here](./examples).

```python3
from kumquat.application import Kumquat
from kumquat.response import TextResponse, JsonResponse, HTMLResponse
from kumquat.request import Request
from kumquat.response import SimpleResponse, TemplateResponse
import logging

logging.basicConfig(level="INFO")

app = Kumquat()


@app.index()
async def index(request: Request, response: SimpleResponse):
    response.status_code = 418
    response.set_headers({"shue": "ppsh"})
    return HTMLResponse("<h1>hello</h1>")


@app.get("/<name>/<age>")
async def some_json_route(request: Request, response: SimpleResponse):
    name = request.path_dict["name"]
    age = request.path_dict["age"]
    return {"user": {"name": name, "age": age}}


app.run() # you can use ngrok - app.ngrok_run()

```
