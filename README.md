# kumquat

Fast asynchronous web framework, based on uvicorn.
  
<img src="https://i.imgur.com/goXLUNU.png" title="source: imgur.com" />


### Installation

stable:
```
pip install kumquat
```

unstable:
```
pip install https://github.com/kesha1225/Kumquat/archive/master.zip --upgrade
```

### Documention

Work in progress...


### Usage

You can see more examples [here](https://github.com/kesha1225/Kumquat/examples).

```python3
from kumquat.application import Kumquat
from kumquat.response import HTMLResponse
from kumquat.request import Request
from kumquat.response import SimpleResponse
import logging

logging.basicConfig(level="INFO")

app = Kumquat()
app.app_name = "MyNewApp"


@app.index()
async def index(request: Request, response: SimpleResponse):
    response.status_code = 418
    response.set_headers({"shue": "ppsh"})
    return HTMLResponse("<h1>hello</h1>")


@app.get("/<param>")
async def some_param_route(request: Request, response: SimpleResponse):
    param = request.path_dict["param"]
    
    # analogue to TextResponse(f"your path now - /{param}", status_code=200)
    return f"your path now - /{param}", 200


@app.get("/<name>/<age>")
async def some_json_route(request: Request, response: SimpleResponse):
    name = request.path_dict["name"]
    age = request.path_dict["age"]
    
    # analogue to JsonResponse({"user": {"name": name, "age": age}})
    return {"user": {"name": name, "age": age}}


app.run()
```
