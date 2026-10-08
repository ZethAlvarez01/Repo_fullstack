import os
from bson import ObjectId
from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import StreamingResponse
from pymongo.errors import PyMongoError
from app.database import db


import resend
from pydantic import BaseModel, EmailStr, Field

from botocore.exceptions import BotoCoreError, ClientError
from app.r2_client import R2_BUCKET_NAME, r2

import uuid
from fastapi import File, UploadFile, HTTPException


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


@app.get("/r2-test")
def probar_r2():
    try:
        archivo = r2.head_object(
            Bucket=R2_BUCKET_NAME,
            Key="digimon_world.jpg"
        )

        return {
            "estado": "ok",
            "mensaje": "Conexión con Cloudflare R2 exitosa",
            "archivo": "digimon_world.jpg",
            "tipo": archivo.get("ContentType"),
            "bytes": archivo.get("ContentLength")
        }

    except (ClientError, BotoCoreError) as error:
        print(f"Error al consultar R2: {type(error).__name__}")
        raise HTTPException(
            status_code=503,
            detail="No fue posible consultar Cloudflare R2"
        )


@app.get("/imagen-prueba")
def obtener_imagen():
    try:
        objeto = r2.get_object(
            Bucket=R2_BUCKET_NAME,
            Key="digimon_world.jpg"
        )

        return StreamingResponse(
            objeto["Body"],
            media_type=objeto.get("ContentType", "image/jpeg"),
            headers={
                "Cache-Control": "public, max-age=300"
            }
        )

    except (ClientError, BotoCoreError) as error:
        print(f"Error R2: {type(error).__name__}")
        raise HTTPException(
            status_code=503,
            detail="No se pudo recuperar la imagen"
        )




collection_name = os.getenv("MONGODB_COLLECTION")
productos_collection = db[collection_name]

class ProductoCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    descripcion: str = ""
    precio: float = Field(ge=0)
    imagen_key: str


@app.post("/productos")
def crear_producto(producto: ProductoCrear):
    resultado = productos_collection.insert_one(
        producto.model_dump()
    )

    return {
        "mensaje": "Producto guardado correctamente",
        "id": str(resultado.inserted_id)
    }

@app.post("/productos/imagen")
async def subir_imagen_producto(imagen: UploadFile = File(...)):
    tipos_permitidos = {
        "image/jpeg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
    }

    if imagen.content_type not in tipos_permitidos:
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten imágenes JPG, PNG o WebP"
        )

    contenido = await imagen.read(5 * 1024 * 1024 + 1)
    await imagen.close()

    if len(contenido) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="La imagen no puede superar los 5 MB"
        )

    extension = tipos_permitidos[imagen.content_type]
    nombre_archivo = f"productos/{uuid.uuid4().hex}.{extension}"

    try:
        r2.put_object(
            Bucket=R2_BUCKET_NAME,
            Key=nombre_archivo,
            Body=contenido,
            ContentType=imagen.content_type
        )
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="No se pudo subir la imagen a R2"
        )

    return {
        "mensaje": "Imagen subida correctamente",
        "imagen_key": nombre_archivo
    }


@app.get("/productos")
def obtener_productos():
    documentos = productos_collection.find()

    return [
        {
            "id": str(producto["_id"]),
            "nombre": producto.get("nombre", ""),
            "descripcion": producto.get("descripcion", ""),
            "precio": producto.get("precio", 0),
            "imagen_key": producto.get("imagen_key")
        }
        for producto in documentos
    ]


@app.get("/productos/{producto_id}/imagen")
def obtener_imagen_producto(producto_id: str):
    if not ObjectId.is_valid(producto_id):
        raise HTTPException(status_code=404, detail="ID inválido")

    producto = productos_collection.find_one({
        "_id": ObjectId(producto_id)
    })

    if not producto or not producto.get("imagen_key"):
        raise HTTPException(
            status_code=404,
            detail="Producto sin imagen en R2"
        )

    try:
        objeto = r2.get_object(
            Bucket=R2_BUCKET_NAME,
            Key=producto["imagen_key"]
        )

        return StreamingResponse(
            objeto["Body"],
            media_type=objeto.get("ContentType", "image/jpeg")
        )

    except (ClientError, BotoCoreError):
        raise HTTPException(
            status_code=503,
            detail="No se pudo recuperar la imagen"
        )