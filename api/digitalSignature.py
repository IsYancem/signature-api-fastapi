import random, os, shutil, logging, xmlsig
from datetime import datetime
from lxml import etree
from xades import XAdESContext, template
from xades.policy import ImpliedPolicy
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from tempfile import NamedTemporaryFile
from fastapi import  HTTPException, File, UploadFile, Form,  APIRouter
from starlette.responses import JSONResponse
from typing import Optional


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


sign_route = APIRouter()

@sign_route.post("/sign-xml")
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
    #base_url = "https://pulpo.agency"
    base_url = "http://localhost:8000"
    signed_file_path = f"/firmados/Firmado_{file_basename}"
    return f"{base_url}{signed_file_path}"