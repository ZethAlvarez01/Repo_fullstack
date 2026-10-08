import os
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from pymongo.errors import PyMongoError
from app.database import db

import resend
from pydantic import BaseModel, EmailStr, Field




from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mi API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    # Permite todas las fuentes, incluyendo el protocolo file:// del navegador
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def root():
    return {"message": "Backend funcionando"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/datos")
def obtener_datos():
    collection_name = os.getenv("MONGODB_COLLECTION")
    if not collection_name:
        raise HTTPException(
            status_code=500,
            detail="Falta MONGODB_COLLECTION en el archivo .env",
        )

    try:
        documentos = db[collection_name].find()
        return [
            jsonable_encoder(documento, custom_encoder={ObjectId: str})
            for documento in documentos
        ]
    except PyMongoError as error:
        raise HTTPException(
            status_code=503,
            detail="No fue posible conectar con MongoDB Atlas.",
        ) from error

class Contacto(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    correo: EmailStr
    mensaje: str = Field(min_length=1, max_length=3000)


@app.post("/contacto")
def enviar_contacto(datos: Contacto):
    api_key = os.getenv("RESEND_API_KEY")
    destino = os.getenv("CONTACT_EMAIL")

    if not api_key or not destino:
        raise HTTPException(
            status_code=503,
            detail="Servicio de correo no configurado"
        )

    resend.api_key = api_key

    try:
        resend.Emails.send({
            "from": "Contacto Web <contacto@zethalvarezh.com>",
            "to": [destino],
            "subject": f"Nuevo contacto de {datos.nombre}",
            "text": (
                f"Nombre: {datos.nombre}\n"
                f"Correo: {datos.correo}\n\n"
                f"Mensaje:\n{datos.mensaje}"
            ),
            "reply_to": str(datos.correo),
        })
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="No se pudo enviar el correo"
        )

    return {"mensaje": "Correo enviado correctamente"}