from optparse import Option
import bcrypt
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional 
import modelsA
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from databaseA import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm

class Create_user(BaseModel):
    username : str
    email : Optional[str]
    first_name : str
    last_name : str 
    password : str 

bcrypt_context = CryptContext(schemes= ["bcrypt"], deprecated = "auto" )

# La siguiente linea creara la base de datos y la tabla con todo lo necesario en caso
# de por alguna razon se ejecute auth.py antes que main.py

modelsA.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_password_hash(password):
    return bcrypt_context.hash(password)
# Crea el encrypted hash password

def verify_function(plain_password, hash_password):
    return bcrypt_context.verify(plain_password, hash_password)

# .verify compara si la contraseña ingresada por el usuario al intentar el sign in 
# coincido con la hash password guardad en la db

def authenticate_user(username : str, password : str, db):
    user = db.query(modelsA.Users).filter(modelsA.Users.username == username).first()
    if not user:
        return False
    # En la siguiente instruccion le decimos que si no esta verificada la 
    # contraseña, que devuelva Falso para indicar que el usuario no es autentificado
    if not verify_function(password, user.hashed_password):
        return False
    return user


@app.post("/create/user")
async def create_new_user(createuser : Create_user, db: Session = Depends(get_db)):
    create_user_Model = modelsA.Users()
    create_user_Model.email = createuser.email
    create_user_Model.username = createuser.username
    create_user_Model.first_name = createuser.first_name
    create_user_Model.last_name = createuser.last_name
    hash_password = get_password_hash(createuser.password)
    create_user_Model.hashed_password = hash_password
    create_user_Model.is_active = True

    db.add(create_user_Model)
    db.commit()

@app.post("/token")
async def login_for_acces_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session= Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return "User is validated"

    #la funcion authenticate me devuelve el usuario ya validado, por lo que en esta funcion 
    # utilizo ese mismo usuario y creo el token de acceso con el form_data(la forma que va a tener la informacion del usuarrio, 
    # # que es la que nos otorga el OAuthForm)
    # OAuth2PasswordRequestFormtiene atributos de uso común como 'nombre de usuario', 'contraseña' y 'alcance'.
    # Después de verificar en la base de datos que el usuario existe, se crea un token de acceso para el usuario. 
    # El token de acceso consta de datos que describen al usuario, sus límites de tiempo de acceso y los permisos 
    # de alcance que se le asignan y que se codifica en un objeto compacto de tipo cadena, que es el token.
