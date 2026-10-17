"""Canonical signed release metadata shared by publisher and HA. No network I/O."""
import re, time, hashlib
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
MAX_IMAGE=0x300000
REPO='Oliver19802/camper-level-updates'
def version(v):
    if not isinstance(v,str) or not re.fullmatch(r'(0|[1-9][0-9]{0,5})\.(0|[1-9][0-9]{0,5})\.(0|[1-9][0-9]{0,5})',v):raise ValueError('Ungültige Version')
    return tuple(map(int,v.split('.')))
def payload(m):
    if m.get('schema')!=1 or type(m['schema']) is not int:raise ValueError('Katalogformat')
    if m.get('target') not in ('atoms3r','xiao-esp32c3') or m.get('edition') not in ('official','private'):raise ValueError('Firmwareziel')
    version(m.get('version'))
    for k in ('size','sequence','expires'):
        if type(m.get(k)) is not int or not 0<m[k]<2**53:raise ValueError(k)
    if not 256<m['size']<=MAX_IMAGE:raise ValueError('Dateigröße')
    if not isinstance(m.get('sha256'),str) or not re.fullmatch('[0-9a-f]{64}',m['sha256']):raise ValueError('Prüfsumme')
    return ('CAMPER_LEVEL_RELEASE_V1\n'+'\n'.join(str(m[k]) for k in ('target','edition','version','size','sha256','sequence','expires'))).encode('ascii')
def verify(m,pem,target,edition,now=None,minimum_sequence=0):
    data=payload(m)
    if (m['target'],m['edition'])!=(target,edition):raise ValueError('Falsche Firmwarevariante')
    if m['expires']<=int(time.time() if now is None else now):raise ValueError('Updatekatalog abgelaufen')
    if m['sequence']<minimum_sequence:raise ValueError('Veralteter Updatekatalog')
    sig=m.get('signature','')
    if not isinstance(sig,str) or not re.fullmatch('[0-9a-f]{128,144}',sig) or len(sig)%2:raise ValueError('Signaturformat')
    key=serialization.load_pem_public_key(pem.encode() if isinstance(pem,str) else pem)
    if not isinstance(key,ec.EllipticCurvePublicKey) or not isinstance(key.curve,ec.SECP256R1):raise ValueError('Prüfschlüssel')
    key.verify(bytes.fromhex(sig),data,ec.ECDSA(hashes.SHA256()))
    return m

def image(m,data):
    if len(data)!=m['size'] or hashlib.sha256(data).hexdigest()!=m['sha256']:raise ValueError('Firmware-Prüfsumme')
    marker=f"CAMPER_LEVEL_IMAGE_V1:{m['target']}:{m['edition']}:{m['version']}".encode()
    if data[0]!=0xe9 or int.from_bytes(data[12:14],'little')!=({'atoms3r':9,'xiao-esp32c3':5}[m['target']]) or marker not in data:raise ValueError('Firmwareinhalt passt nicht')
    return data

def filename(m):return f"camper-level-{m['target']}-{m['edition']}-{m['version']}.bin"
def image_url(m):return f"https://github.com/{REPO}/releases/download/v{m['version']}/{filename(m)}"
