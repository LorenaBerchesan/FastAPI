#from typing import Annotated
from fastapi import FastAPI, Query, Path, Body, Cookie, Header, Response, status, Form, File, UploadFile
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import List, Union, Set, Dict, Any
from datetime import datetime, time, timedelta
from uuid import UUID

from starlette.responses import RedirectResponse, JSONResponse, HTMLResponse

app = FastAPI()

#http://127.0.0.1:8000
@app.get("/")
async def root():
    return {"message": "Hello World"}

#Path parametres/variables
# http://127.0.0.1:8000/items/foo
@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}

#Path parametres with types
# http://127.0.0.1:8000/items/3
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id" : item_id}

#order matters (fixed path)
@app.get("/users/me")
async def read_user_me():
    return {"user_id" : "the current user"}

@app.get("/users/{user_id}")
async def read_user(user_id : str):
    return { "user_id" : user_id}

@app.get("/users")
async def read_users():
    return ["Rick", "Morty"]

#create an Enum class
#http://127.0.0.1:8000/models/alexnet
class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

@app.get("/models/{model_name}")
async def get_model(model_name : ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name" : model_name , "message" : "Deep Learning FTW!"}
    if model_name.value == "lenet":
        return {"model_name" : model_name , "message" : "LeCNN all the images"}
    return {"model_name" : model_name , "message" : "Have some residuals"}

#path convertor /files/{file_path:path} (se pune ca sa se potriveasca cu orice cale folosind o adresa URL)
# http://127.0.0.1:8000/files/hey
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path" : file_path}

#query parameters
#http://127.0.0.1:8000/items/?skip=0&limit=10
fake_items_db = [{"item_name" : "Foo"}, {"item_name": "Bar"}, {"item_name" : "Baz"}]

@app.get("/items/")
async def read_items(skip: int=0, limit : int =10):
    return fake_items_db[skip : skip + limit]

#optional parametres
@app.get("/items/{item_id}")
async def read_item(item_id: str, q : str or None = None):
    if q:
        return {"item_id": item_id, "q":q}
    return {"item_id":item_id}

#query parameter type conversion
#http://127.0.0.1:8000/items/foo?short=1 sau True sau on sau yes
@app.get("/items/{item_id}")
async def read_item(item_id: str, q: str or None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q":q})
    if not short:
        item.update({"description": "This is an amazing item that has a long description"})
    return item

#multiple path and query parameters
@app.get("/users/{id_user}/items/{id_item}")
async def reda_user_item(user_id : int, item_id : str, q : str or None = None, short: bool =False):
    item = {"item_id": item_id , "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

#required query parameters
#http://127.0.0.1:8000/items/foo-item?needy=sooooneedy
@app.get("/items/{item_id}")
async def read_user_item(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item

#Request Body

class Item(BaseModel):
    name: str
    #description: str or None = None
    description: Union[str, None] = None
    price: float
    #tax: float or None = None
    tax: Union[float, None] = None

app = FastAPI()

@app.post("/items/")
async def create_item(item: Item):
    #convert to dictionary
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax":price_with_tax})

    return item_dict

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}

@app.put("/items/{item_id}")
async def update_item2(item_id: int, item: Item, q: str or None = None):
    #**item.dict() - all key and value are add to result
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result

#query validation and string validations
# @app.get("/items/")
# async def read_items(q: Annotated[str | None, Query(max_length=50)] = None):
#     results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q": q})
#     return results

#instead of annotated(3.9) i will use query(3.8)
@app.get("/items/")
# async def read_items( q: str or None = Query(default=None, max_length = 50)):
#     results = {"items" : [{"items_id":"Foo"}, {"item_id": "Bar"}]}
#     if q:
#         results.update({"q":q})
#     return results

async def read_items2(q:Union[List[str],None] = Query(default=["foo","bar"])):
    query_items = {"q" : q}
    return query_items

@app.get("/items/")
async def read_items(q : Union[str, None] = Query(
    default=None,
    title="Query string",
    description="allalala",
    min_length=3,)
        ,):
    results = {"items": [{"item_id":"foo"},{"item_id":"boo"}]}
    if q:#if q is null return foo,boo else q
        results.update({"q":q})
    return results

#path-It's used to define parameters that are extracted from the request URL's path
@app.get("/items/{item_id}")
async def read_items(
    item_id: int = Path(title="The ID of the item to get"),
    q: Union[str, None] = Query(default=None, alias="item-query"),
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

#* -all parameters must be explicitly specified by their name when calling the function.
#ge:greater than, le:less then or equal, gt,lt-float
@app.get("/items/{item_id}")
async def read_items2(*, item_id: int = Path(title="The ID of the item to get",ge=1,le=1000), q: str):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results

#union- allows defining a type that can be one of several types.

#body multiple parameters
class User(BaseModel):
    username: str
    full_name: Union[str, None] = None


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User):
    results = {"item_id": item_id, "item": item, "user": user}
    return results

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User, importance: int = Body()):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item, user: User, importance: int = Body(embed = True)):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results

#body fields
class Image(BaseModel):
    #url: str
    url: HttpUrl
    name: str

class Item2(BaseModel):
    name: str
    description: Union[str, None] = Field(default=None, title="The description of the item", max_length = 300)
    price: float = Field(gt=0, description= "The price must be than zero")
    tax: Union[float,None] = None
    #tags: list = []
    tags: List[str] = []
    #set-shouldn't repeat/unique strings
    tags2: Set[str] = set()
    #image: Union[Image, None] = None
    image: Union[List[Image], None] = None

@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item2 = Body(embed=True)):
    results = {"item_id": item_id, "item": item}
    return results

class Offer(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    items: List[Item2]


@app.post("/offers/")
async def create_offer(offer: Offer):
    return offer

@app.post("/images/multiple/")
async def create_multiple_images(*,images: List[Image]):
    for image in images:
        return image+List[image]
    # return images

#Dict[int,float] , key-value , dictionary
@app.post("/index-weights/")
async def create_index_weights(weights: Dict[int, float]):
    return weights

class Item3(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: Union[float, None] = None

    class Config:
        schema_extra = {
            "examples": [
                {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                }
            ]
        }


@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item3):
    results = {"item_id": item_id, "item": item}
    return results

#path()/query()/header()/cookie()/body()/form()/file() - can declare group of examples
#we can have multiple examples
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,
    item: Item = Body(
        examples=[
            {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            },
            {
                "name": "Bar",
                "price": "35.4",
            },
            {
                "name": "Baz",
                "price": "thirty five point four",
            },
        ],
    ),
):
    results = {"item_id": item_id, "item": item}
    return results

# Each specific example dict in the examples can contain:(dict)
# summary: Short description for the example.
# description: A long description that can contain Markdown text.
# value: This is the actual example shown, e.g. a dict.
# externalValue: alternative to value, a URL pointing to the example. Although this might not be supported by as many tools as value.

@app.put("/items/{item_id}")
async def update_item(
    *,
    item_id: int,
    item: Item = Body(
        openapi_examples={
            "normal": {
                "summary": "A normal example",
                "description": "A **normal** item works correctly.",
                "value": {
                    "name": "Foo",
                    "description": "A very nice Item",
                    "price": 35.4,
                    "tax": 3.2,
                },
            },
            "converted": {
                "summary": "An example with converted data",
                "description": "FastAPI can convert price `strings` to actual `numbers` automatically",
                "value": {
                    "name": "Bar",
                    "price": "35.4",
                },
            },
            "invalid": {
                "summary": "Invalid data is rejected with an error",
                "value": {
                    "name": "Baz",
                    "price": "thirty five point four",
                },
            },
        },
    ),
):
    results = {"item_id": item_id, "item": item}
    return results

# other data type
# UUID = Universally Unique Identifier ~ str
# datetime.datetime = 2008-09-15T15:53:00+05:00 ~ str
# datetime.date = 2008-09-15 ~ str
# datetime.time = 14:23:55.003 ~ str
# datetime.timedelta = float of total seconds
# frozenset = the same as a set, In responses, the set will be converted to a list
# bytes = In requests and responses will be treated as str, it's a str with binary "format"
# Decimal = In requests and responses, handled the same as a float

@app.put("/items/{item_id}")
async def read_items(
        item_id: UUID,
        start_datetime : Union[datetime, None] = Body(default=None),
        end_datetime: Union[datetime, None] = Body(default=None),
        repeat_at: Union[time, None] = Body(default=None),
        process_after: Union[timedelta, None] = Body(default=None),
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_datetime
    return {
        "item_id" : item_id,
        "start_datetime" : start_datetime,
        "end_datetime" : end_datetime,
        "repeat_at" : repeat_at,
        "process_after" : process_after,
        "start_process" : start_process,
        "duration" : duration,
    }

#Cookie parameters the same as path, query
@app.get("/items/")
async def read_items(ads_id: Union[str, None] = Cookie(default=None)):
    return {"ads_id": ads_id}

#header same strucrure as path, query, cookie
@app.get("/items/")
async def read_items(user_agent: Union[str, None] = Header(default=None)):
    return {"User-Agent": user_agent}

@app.get("/items/")
async def read_items(
    strange_header: Union[str, None] = Header(default=None, convert_underscores=False),
):
    return {"strange_header": strange_header}

# Response Model - Return Type
#return object type Item2
@app.post("/items/")
async def create_item(item: Item2) -> Item2:
    return item


@app.get("/items/")
#-> return object type List[Item2]
async def read_items() -> List[Item2]:
    return [
        Item(name="Portal Gun", price=42.0),
        Item(name="Plumbus", price=32.0),
    ]
#i can use respone_model instead otf the return type
@app.post("/items/", response_model=Item)
async def create_item(item: Item) -> Any:
    return item


@app.get("/items/", response_model=List[Item])
async def read_items() -> Any:
    return [
        {"name": "Portal Gun", "price": 42.0},
        {"name": "Plumbus", "price": 32.0},
    ]

#return the same input data
class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: Union[str, None] = None

class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: Union [ str, None ] = None

@app.post("/user/", response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    return user
#or
class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: Union[str, None] = None


class UserIn2(BaseUser):
    password: str


@app.post("/user/")
async def create_user(user: UserIn2) -> BaseUser:
    return user

#return a respone directly
#http://localhost:8000/portal?teleport=true
@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal."})

class Item4(BaseModel):
    name: str
    description: Union[str, None] = None
    price: float
    tax: float = 10.5
    tags: List[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}

#response_model_exclude_unset=True - won't be included in the response, only the values actually set
@app.get("/items/{item_id}", response_model=Item4, response_model_exclude_unset=True)
async def read_item(item_id: str):
    return items[item_id]

@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include={"name", "description"},
)
async def read_item_name(item_id: str):
    return items[item_id]


@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude={"tax"})
async def read_item_public_data(item_id: str):
    return items[item_id]

@app.get(
    "/items/{item_id}/name",
    response_model=Item,
    response_model_include=["name", "description"],
)
async def read_item_name(item_id: str):
    return items[item_id]


@app.get("/items/{item_id}/public", response_model=Item, response_model_exclude=["tax"])
async def read_item_public_data(item_id: str):
    return items[item_id]

class UserInDB(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    full_name: Union [ str, None ] = None

def fake_password_hasher(raw_password: str):
    return "supersecret"+ raw_password

def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    #** open the dictionary in a list
    # UserInDB(
    #     username=user_dict [ "username" ],
    #     password=user_dict [ "password" ],
    #     email=user_dict [ "email" ],
    #     full_name=user_dict [ "full_name" ],
    #     hashed_password=hashed_password,
    # )
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User save! ..not really")
    return user_in_db

@app.get("/user/", response_model=UserOut)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    return user_saved

class BaseItem1(BaseModel):
    description: str
    type: str


class CarItem(BaseItem1):
    type: str = "car"


class PlaneItem(BaseItem1):
    type: str = "plane"
    size: int


items = {
    "item1": {"description": "All my friends drive a low rider", "type": "car"},
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}


@app.get("/items/{item_id}", response_model=Union[PlaneItem, CarItem])
async def read_item(item_id: str):
    return items[item_id]

class Item5(BaseModel):
    name: str
    description: str


items = [
    {"name": "Foo", "description": "There comes my hero"},
    {"name": "Red", "description": "It's my aeroplane"},
]


@app.get("/items/", response_model=List[Item5])
async def read_items1():
    return items

#respone status code
@app.post("/items/", status_code=201)
async def create_item(name: str):
    return {"name": name}
#or
@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    return {"name": name}

@app.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}

#import file
@app.post("/files/")
async def create_file(file: bytes = File()):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}

@app.post("/files/")
async def create_file(file: Union[bytes, None] = File(default=None)):
    if not file:
        return {"message": "No file sent"}
    else:
        return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: Union[UploadFile, None] = None):
    if not file:
        return {"message": "No upload file sent"}
    else:
        return {"filename": file.filename}

@app.post("/files/")
async def create_file(file: bytes = File(description="A file read as bytes")):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(
    file: UploadFile = File(description="A file read as UploadFile"),
):
    return {"filename": file.filename}

#pultiple file uploads
@app.post("/files/")
async def create_files(files: List[bytes] = File()):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(files: List[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)

#??
@app.post("/files/")
async def create_file(
    file: bytes = File(), fileb: UploadFile = File(), token: str = Form()
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }
