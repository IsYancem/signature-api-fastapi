from datetime import datetime
import random
from lxml import etree
import xmlsig
from xades import XAdESContext, template
from xades.policy import ImpliedPolicy
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend


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

