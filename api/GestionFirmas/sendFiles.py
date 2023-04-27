from typing import List
from fastapi import APIRouter, Depends, Header, HTTPException
from dependencies import get_current_user
from database import SessionLocal
from models import TokenSesion
from models import ArchivoFirmado
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Importar bibliotecas adicionales
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Leer las variables de entorno
email_address = os.environ.get("EMAIL_ADDRESS")
email_password = os.environ.get("EMAIL_PASSWORD")

send_files_route = APIRouter()

class SendFile(BaseModel):
    id_archivos: List[int]
    destinatario: str

@send_files_route.post("/sendFiles")
async def send_files(send_file: SendFile, current_user: dict = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    user_id = current_user["id"]
    db = SessionLocal()
    
    try:
        archivos_firmados = db.query(ArchivoFirmado).filter(ArchivoFirmado.id.in_(send_file.id_archivos), ArchivoFirmado.usuario_id == user_id).all()
        if not archivos_firmados:
            raise HTTPException(status_code=404, detail="Archivo no encontrado o no pertenece al usuario")

        # Creamos el mensaje y lo configuramos
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = send_file.destinatario
        msg['Subject'] = "Archivos firmados"
        body = "Se adjuntan los siguientes archivos firmados"
        msg.attach(MIMEText(body, 'plain'))

        # Agregamos los archivos al mensaje
        for archivo_firmado in archivos_firmados:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(archivo_firmado.archivo_firmado)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=archivo_firmado.nombre_archivo)
            msg.attach(part)

        # Enviamos el correo electrónico
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email_address, email_password)
        text = msg.as_string()
        server.sendmail(email_address, send_file.destinatario, text)
        server.quit()

        return {"message": "Archivos enviados exitosamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al enviar archivos: {str(e)}")
