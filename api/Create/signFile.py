import random, os, shutil, logging, xmlsig
from datetime import datetime
from lxml import etree
from xades import XAdESContext, template
from xades.policy import ImpliedPolicy
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from tempfile import NamedTemporaryFile
from fastapi import  HTTPException, File, UploadFile, Form,  APIRouter, Depends, Header
from starlette.responses import JSONResponse
from typing import Optional, List
from jose import jwt
from config import SECRET_KEY, ALGORITHM
from dependencies import get_current_user, TokenData
from database import engine, SessionLocal
from models import Firma, Usuario, ArchivoFirmado, TokenSesion
from cryptography.fernet import Fernet
from services import create_archivo_firmado
import os
import shutil
from tempfile import NamedTemporaryFile
import logging

from fastapi import APIRouter, File, Form, UploadFile, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from lxml import etree
from database import SessionLocal, engine
from models import ArchivoFirmado, Base

Base.metadata.create_all(bind=engine)

def generate_short_id():
    return str(random.randint(100000, 999999))

def parse_xml(file_path):
    return etree.parse(file_path).getroot()

def sign_xml(xml_file, p12_file, p12_password, output_file):
    root = parse_xml(xml_file)

    # IDS
    signatureId = "Signature" + generate_short_id()
    keyInfoId = "Certificate" + generate_short_id()

    # SI
    signedInfoId = "Signature-SignedInfo" + generate_short_id()

    # r2
    idTerceraRef = "Reference-ID-" + generate_short_id()
    signedPropertiesId = signatureId + "-SignedProperties" + generate_short_id()
    objectId = signatureId + "-Object" + generate_short_id()
    signatureValueId = "SignatureValue" + generate_short_id()

    signature = xmlsig.template.create(
        xmlsig.constants.TransformInclC14N,
        xmlsig.constants.TransformRsaSha1,
        signatureId
    )

    # primer reference
    xmlsig.template.add_reference(
        signature, xmlsig.constants.TransformSha1, name="SignedProperties" + generate_short_id(),
        uri_type="http://uri.etsi.org/01903#SignedProperties", uri="#" + signedPropertiesId
    )

    # Segundo reference
    xmlsig.template.add_reference(
        signature, xmlsig.constants.TransformSha1, uri="#" + keyInfoId
    )

    # Tercer reference
    ref = xmlsig.template.add_reference(
        signature, xmlsig.constants.TransformSha1, uri="#comprobante", name=idTerceraRef)
    xmlsig.template.add_transform(ref, xmlsig.constants.TransformEnveloped)

    ki = xmlsig.template.ensure_key_info(signature, name=keyInfoId)
    data = xmlsig.template.add_x509_data(ki)
    xmlsig.template.x509_data_add_certificate(data)
    xmlsig.template.add_key_value(ki)
    qualifying = template.create_qualifying_properties(signature)
    props = template.create_signed_properties(qualifying, name=signedPropertiesId, datetime=datetime.now())
    signed_do = template.ensure_signed_data_object_properties(props)

    template.add_data_object_format(
        signed_do,
        "#" + idTerceraRef,
        description="contenido comprobante",
        mime_type="text/xml",
    )

    # Añade estas líneas para establecer el atributo Id del elemento Object y SignatureValue
    object_element = signature.xpath("ds:Object", namespaces=signature.nsmap)[0]
    object_element.set("Id", objectId)
    signatureValue_element = signature.xpath("ds:SignatureValue", namespaces=signature.nsmap)[0]
    signatureValue_element.set("Id", signatureValueId)
    signedInfo_element = signature.xpath("ds:SignedInfo", namespaces=signature.nsmap)[0]
    signedInfo_element.set("Id", signedInfoId)

    root.append(signature)
    ctx = XAdESContext(ImpliedPolicy(xmlsig.constants.TransformSha1))

    with open(p12_file, "rb") as key_file:
        ctx.load_pkcs12(
            pkcs12.load_key_and_certificates(key_file.read(), p12_password, default_backend())
        )

    ctx.sign(signature)
    ctx.verify(signature)

    et = etree.ElementTree(root)
    et.write(
        output_file,
        pretty_print=True,
        encoding="utf-8",
        xml_declaration=True,
    )

# def generate_signed_file_url(file_basename: str) -> str:
#     #base_url = "https://pulpo.agency"
#     base_url = "http://localhost:8000"
#     signed_file_path = f"/firmados/{file_basename}"  # se agrega la extensión .xml al final del nombre del archivo
#     return f"{base_url}{signed_file_path}"

sign_route = APIRouter()

@sign_route.post("/sign-file")
async def sign_xml_api(
    current_user: dict = Depends(get_current_user),
    api_key: str = Form(...),
    nombre_archivo: str = Form(...),
    xml_files: List[UploadFile] = File(...),
):
    # 1. Autenticar si el usuario está autorizado
    if not current_user:
        raise HTTPException(status_code=401, detail="No autorizado, no existe el usuario activo")

    try:
        user_id = current_user["id"]
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content=e.detail)

    # 2. Autenticar que el API key enviado en el body es válido y corresponde a un registro en firmas
    db = SessionLocal()

    firma = (
        db.query(Firma)
        .filter(Firma.token_p12 == api_key)
        .filter(Firma.usuario_id == current_user["id"])
        .first()
    )

    if not firma:
        return JSONResponse(
            status_code=400,
            content={"detalle": "API key inválido o no corresponde al usuario"},
        )

    # Obtener la clave_cifrado del registro de Firma
    clave_cifrado = firma.clave_cifrado

    # Recorrer los archivos cargados
    archivos_firmados = []
    for xml_file in xml_files:
        try:
            # Descifrar archivo_p12 y contrasena_p12 de la tabla firmas
            cipher_suite = Fernet(clave_cifrado.encode("utf-8"))
            archivo_p12_descifrado = cipher_suite.decrypt(firma.archivo_p12)
            contrasena_p12_descifrado = cipher_suite.decrypt(firma.contrasena_p12)

            # Guardar el archivo descifrado temporalmente
            with NamedTemporaryFile(delete=False) as p12_tempfile:
                p12_tempfile.write(archivo_p12_descifrado)
                p12_tempfile_path = p12_tempfile.name

            with NamedTemporaryFile(delete=False) as xml_tempfile:
                shutil.copyfileobj(xml_file.file, xml_tempfile)
                xml_tempfile_path = xml_tempfile.name

            nombre_archivo_final = f"{nombre_archivo}_{xml_file.filename}"
            # output_file = "firmados/" + nombre_archivo_final
            output_file = nombre_archivo_final

            sign_xml(xml_tempfile_path, p12_tempfile_path, contrasena_p12_descifrado, output_file)

        except FileNotFoundError:
            logging.error("Archivo no encontrado")
            raise HTTPException(
                status_code=400, detail="Archivos enviados como parámetros no encontrados"
            )
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
            raise HTTPException(
                status_code=500,
                detail=f"Error durante la firma del archivo XML: {str(e)}",
            )
        finally:
            # Eliminar archivo descifrado
            if os.path.exists(p12_tempfile_path):
                os.unlink(p12_tempfile_path)

        # 4. Guardar el archivo firmado en la tabla ArchivosFirmados
        try:
            with open(output_file, "rb") as signed_file:
                signed_file_content = signed_file.read()

            archivo_firmado = ArchivoFirmado(
                nombre_archivo=nombre_archivo_final,
                fecha_hora_firma=datetime.now(),
                archivo_firmado=signed_file_content,
                firma_id=firma.id,
                usuario_id=current_user["id"],
            )

            create_archivo_firmado(archivo_firmado)

        except Exception as e:
            logging.error(f"Error al guardar el archivo firmado en la base de datos: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error al guardar el archivo firmado en la base de datos: {str(e)}",
            )

        finally:
            # Eliminar archivos temporales
            if os.path.exists(output_file):
                os.unlink(output_file)
            if os.path.exists(xml_tempfile_path):
                os.unlink(xml_tempfile_path)
            if os.path.exists(p12_tempfile_path):
                os.unlink(p12_tempfile_path)

    return JSONResponse(
        content={
            "status": "ok",
            "mensaje": "La factura se firmó de manera exitosa!",
        }
    )

@sign_route.post("/sign-xml")
async def sign_xml_api2(xml_files: List[UploadFile] = File(...), p12_file: UploadFile = File(...), p12_password: str = Form(...), current_user: dict = Depends(get_current_user)):

    if current_user["role_id"] != 1:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No autorizado")

    try:
        with NamedTemporaryFile(delete=False) as p12_tempfile:
            shutil.copyfileobj(p12_file.file, p12_tempfile)
            p12_tempfile_path = p12_tempfile.name

        output_files = []
        for xml_file in xml_files:
            with NamedTemporaryFile(delete=False) as xml_tempfile:
                shutil.copyfileobj(xml_file.file, xml_tempfile)
                xml_tempfile_path = xml_tempfile.name

            file_basename = os.path.basename(xml_file.filename)
            output_file = "Firmado_" + file_basename

            sign_xml(xml_tempfile_path, p12_tempfile_path, p12_password.encode(), output_file)

            with open(output_file, "rb") as signed_file:
                signed_file_data = signed_file.read()

            db_file = ArchivoFirmado(
                nombre_archivo="Firmado_" + current_user["username"] + "_" + file_basename,
                fecha_hora_firma=datetime.now(),
                firma_id=None,
                usuario_id=current_user["id"],
                archivo_firmado=signed_file_data,
            )

            db = SessionLocal()
            db.add(db_file)
            db.commit()
            db.refresh(db_file)

            os.unlink(xml_tempfile_path)
            os.unlink(output_file)

        return JSONResponse(content={
            "status": "ok",
            "mensaje": "Los archivos se firmaron de manera exitosa!",
        })

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