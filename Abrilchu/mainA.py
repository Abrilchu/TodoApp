from fastapi import FastAPI, Depends, HTTPException
import modelsA
from databaseA import engine, SessionLocal
from sqlalchemy.orm import Session
from schemasA import Todo

app = FastAPI()

modelsA.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""def get_db():
    session = sessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()"""


""" esta funcion se utilizo para crear la base de datos, vacia."""

@app.get("/create/database")
async def create_database():
    return{"Database" : "Created :)"} 

def exceptions():
    return HTTPException(status_code=404, detail="Todo not found")

def successfull_response(statuscode : int):
    return {
        'status' : statuscode,
        'transaction' : 'succesfull'
    }


@app.get("/")
async def get_db(db: Session = Depends(get_db)):
    return db.query(modelsA.Todos).all()

@app.post("/")
async def create_todo(todo: Todo, db: Session = Depends(get_db)):
    todo_model = modelsA.Todos()
    todo_model.title = todo.title
    todo_model.description = todo.description
    todo_model.priority = todo.priority
    todo_model.complete = todo.complete


    db.add(todo_model)

    db.commit()
    return successfull_response(201)


@app.get("/get_todo/{todo_id}")
async def get_todo_id(todo_id: int, db: Session = Depends(get_db)):
    todo_model = db.query(modelsA.Todos).filter(modelsA.Todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise exceptions()


@app.put("/{todo_id}")
async def update_book(todo_id : int, todo: Todo, db : Session = Depends(get_db)):
    todo_model = db.query(modelsA.Todos).filter_by(id=todo_id).first()
    if todo_model is not None:
        # todo_model.title, todo_model.description, todo_model.priority, todo_model.complete = todo.title, todo.description, todo.priority, todo.complete
        todo_model.title = todo.title
        todo_model.description = todo.description
        todo_model.priority = todo.priority
        todo_model.complete = todo.complete
        db.add(todo_model)
        db.commit()
        return successfull_response(200) # the exchange btw client and server was succesfull
    raise exceptions()


@app.delete("/{todo_id}")
async def delete_todo_id(todo_id : int, db : Session = Depends(get_db)):
    todo_model = db.query(modelsA.Todos).filter_by(id=todo_id).first()
    
    if todo_model is not None:
        db.query(modelsA.Todos).filter_by(todo_id=id).delete()
        # db.delete(todo_model)
        db.commit()
        return successfull_response(200)

    raise exceptions()