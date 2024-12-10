import base64
from fastapi import HTTPException
from io import BytesIO
from PIL import Image
import cloudinary.uploader

from utils import config

# Configurar Cloudinary
cloudinary.config(
    cloud_name=config.Settings().cloudinary_cloud_name,
    api_key=config.Settings().cloudinary_api_key,
    api_secret=config.Settings().cloudinary_secret_key
)

def upload_image(file_base64: str):
    try:
        # Decodificar el archivo base64
        file_data = base64.b64decode(file_base64)
        image = Image.open(BytesIO(file_data))

        # Validar tipo de archivo
        if image.format not in ["JPEG", "PNG"]:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Usar public_id proporcionado o generar uno único
        public_id = "ecommerce/" + file_base64[:10]

        # Subir imagen a Cloudinary
        result = cloudinary.uploader.upload(
            file_data,  # Datos del archivo decodificado
            public_id=public_id,
            overwrite=False  # Evita sobrescribir archivos existentes
        )

        # Obtener URL público de la imagen
        src_url = result.get("secure_url")
        return src_url

    except Exception as e:
        # Manejo de errores y retorno de una excepción HTTP
        raise HTTPException(status_code=500, detail=f"Error uploading image: {str(e)}")
