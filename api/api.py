import os
import shutil
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from starlette.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from lxml import etree
from digitalSignature import sign_xml
import logging
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar la carpeta 'firmados' como ruta estática para servir los archivos XML firmados
app.mount("/firmados", StaticFiles(directory="firmados"), name="firmados")

# Configuración del logger
logging.basicConfig(filename="api.log", level=logging.ERROR)

@app.post("/sign-xml")
async def sign_xml_api(xml_file: Optional[UploadFile] = File(None), p12_file: Optional[UploadFile] = File(None), p12_password: Optional[str] = Form(None)):
    
    if not xml_file:
        return JSONResponse(status_code=400, content={"detalles": [{"Status": "ERROR", "info": "El archivo XML es requerido"}]})
    if not p12_file:
        return JSONResponse(status_code=400, content={"detalles": [{"Status": "ERROR", "info": "El archivo p12 es requerido"}]})
    if not p12_password:
        return JSONResponse(status_code=400, content={"detalles": [{"Status": "ERROR", "info": "La contraseña del archivo p12 es requerida"}]})
    
    try:
        with NamedTemporaryFile(delete=False) as xml_tempfile, NamedTemporaryFile(delete=False) as p12_tempfile:
            shutil.copyfileobj(xml_file.file, xml_tempfile)
            shutil.copyfileobj(p12_file.file, p12_tempfile)
            xml_tempfile_path = xml_tempfile.name
            p12_tempfile_path = p12_tempfile.name

        file_basename = os.path.basename(xml_file.filename)
        output_file = "firmados/Firmado_" + file_basename

        sign_xml(xml_tempfile_path, p12_tempfile_path, p12_password.encode(), output_file)

    except FileNotFoundError:
        logging.error("Archivo no encontrado")
        raise HTTPException(status_code=400, detail="Archivos enviados como parámetros no encontrados")
    except ValueError:
        logging.error("Contraseña inválida")
        raise HTTPException(status_code=400, detail="Contraseña del archivo p12 inválida")
    except etree.XMLSyntaxError:
        logging.error("Archivo XML mal formado")
        raise HTTPException(status_code=400, detail="Archivo XML mal formado")
    except etree.DocumentInvalid:
        logging.error("Archivo XML no válido")
        raise HTTPException(status_code=400, detail="Archivo XML no válido")
    except Exception as e:
        logging.error(f"Error durante la firma del archivo XML: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error durante la firma del archivo XML: {str(e)}")

    finally:
        os.unlink(xml_tempfile_path)
        os.unlink(p12_tempfile_path)

    signed_file_url = generate_signed_file_url(file_basename)

    return JSONResponse(content={
        "status": "ok",
        "mensaje": "La factura se firmó de manera exitosa!",
        "comprobante": signed_file_url,
    })



def generate_signed_file_url(file_basename: str) -> str:
    base_url = "https://pulpo.agency"
    signed_file_path = f"/firmados/Firmado_{file_basename}"
    return f"{base_url}{signed_file_path}"
