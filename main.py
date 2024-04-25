from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
import databases
import sqlalchemy
from sqlalchemy import Column, Integer, String

DATABASE_URL = "sqlite:///./test.db"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

students = sqlalchemy.Table(
    "students",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("full_name", String),
    Column("birth_year", Integer),
    Column("birth_place", String),
    Column("age", Integer),
    Column("gender", String),
    Column("course", Integer),
    Column("department", String),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

metadata.create_all(engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/")
async def index(request: Request):
    query = students.select()
    result = await database.fetch_all(query)
    return templates.TemplateResponse("index.html", {"request": request, "students": result})


@app.post("/")
async def add_student(
    request: Request,
    full_name: str = Form(...),
    birth_year: int = Form(...),
    birth_place: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    course: int = Form(...),
    department: str = Form(...),
):
    query = students.insert().values(
        full_name=full_name,
        birth_year=birth_year,
        birth_place=birth_place,
        age=age,
        gender=gender,
        course=course,
        department=department,
    )
    await database.execute(query)
    return await index(request)


@app.get("/delete/{student_id}")
async def delete_student(request: Request, student_id: int):
    query = students.delete().where(students.c.id == student_id)
    await database.execute(query)
    return await index(request)


@app.get("/edit/{student_id}")
async def edit_student(request: Request, student_id: int):
    query = students.select().where(students.c.id == student_id)
    result = await database.fetch_one(query)
    return templates.TemplateResponse("edit.html", {"request": request, "student": result})


@app.post("/edit/{student_id}")
async def update_student(
    request: Request,
    student_id: int,
    full_name: str = Form(...),
    birth_year: int = Form(...),
    birth_place: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    course: int = Form(...),
    department: str = Form(...),
):
    query = (
        students.update()
        .where(students.c.id == student_id)
        .values(
            full_name=full_name,
            birth_year=birth_year,
            birth_place=birth_place,
            age=age,
            gender=gender,
            course=course,
            department=department,
        )
    )
    await database.execute(query)
    return await index(request)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
