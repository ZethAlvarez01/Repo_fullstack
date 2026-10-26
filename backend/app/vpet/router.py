"""HTTP routes for V-Pet catalogs and battle configuration."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from botocore.exceptions import BotoCoreError, ClientError

from app.vpet import service


router = APIRouter(prefix="/api/vpet", tags=["vpet"])


@router.get("/bootstrap")
def get_bootstrap():
    return service.bootstrap()


@router.get("/reference")
def get_reference(
    query: str = Query(default="", max_length=100),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
):
    return service.search_reference(query=query, offset=offset, limit=limit)


@router.get("/reference/{name}")
def get_reference_variants(name: str):
    variants = service.reference_variants(name)
    if not variants:
        raise HTTPException(status_code=404, detail="Digimon no encontrado")
    return {"name": name, "variants": variants}


@router.get("/catalog")
def get_catalog():
    return service.catalog_family()


@router.get("/catalog/{family}")
def get_catalog_family(family: str, include_reference: bool = False):
    try:
        return service.catalog_family(family, include_reference=include_reference)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Familia V-Pet no encontrada") from error


@router.get("/config/{name}")
def get_config(name: str):
    try:
        return service.public_config(name)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Configuración V-Pet no encontrada") from error


@router.get("/images/{filename}")
def get_image(filename: str):
    object_key = service.image_object_key(filename)
    if object_key is None:
        raise HTTPException(status_code=404, detail="Imagen V-Pet no encontrada")
    try:
        from app.r2_client import R2_BUCKET_NAME, r2

        image = r2.get_object(Bucket=R2_BUCKET_NAME, Key=object_key)
        return StreamingResponse(
            image["Body"],
            media_type=image.get("ContentType", "application/octet-stream"),
            headers={"Cache-Control": "public, max-age=86400"},
        )
    except ClientError as error:
        error_code = error.response.get("Error", {}).get("Code", "")
        if error_code not in {"NoSuchKey", "404", "NotFound"}:
            raise HTTPException(status_code=503, detail="No fue posible consultar R2") from error
    except (BotoCoreError, KeyError) as error:
        local_path = service.image_path(filename)
        if local_path is None:
            raise HTTPException(status_code=503, detail="Almacenamiento de imágenes no disponible") from error
        return FileResponse(local_path, headers={"Cache-Control": "public, max-age=86400"})

    local_path = service.image_path(filename)
    if local_path is not None:
        return FileResponse(local_path, headers={"Cache-Control": "public, max-age=86400"})
    raise HTTPException(status_code=404, detail="Imagen V-Pet no encontrada")
