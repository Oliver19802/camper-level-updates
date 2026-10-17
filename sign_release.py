"""Offline release preparation. Does not upload or publish anything."""
import argparse,json,time,hashlib,getpass
from pathlib import Path
from cryptography.hazmat.primitives import serialization,hashes
from cryptography.hazmat.primitives.asymmetric import ec
from key_store import protect
from release_format import payload,image,filename
p=argparse.ArgumentParser();p.add_argument('--key',type=Path,required=True);p.add_argument('--firmware',type=Path);p.add_argument('--target',choices=['atoms3r','xiao-esp32c3']);p.add_argument('--version');p.add_argument('--edition',choices=['official','private'],default='official');p.add_argument('--allow-private',action='store_true');p.add_argument('--out',type=Path);p.add_argument('--days',type=int,default=90);p.add_argument('--export-encrypted-key',type=Path)
a=p.parse_args();key=serialization.load_der_private_key(protect(a.key.read_bytes(),True),password=None)
if a.export_encrypted_key:
    password=getpass.getpass('Neues Passwort für die verschlüsselte Schlüsselsicherung: ')
    if len(password)<12 or password!=getpass.getpass('Passwort wiederholen: '):raise SystemExit('Passwörter stimmen nicht überein oder zu kurz')
    with a.export_encrypted_key.open('xb') as f:f.write(key.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.BestAvailableEncryption(password.encode())))
    raise SystemExit('Verschlüsselte Schlüsselsicherung erstellt. Passwort getrennt aufbewahren.')
if not all([a.firmware,a.target,a.version,a.out]) or not 1<=a.days<=90:p.error('Firmware, Ziel, Version, Ausgabeordner und 1–90 Tage nötig')
if a.edition=='private' and not a.allow_private:p.error('Private Variante nur mit --allow-private lokal vorbereiten, niemals öffentlich hochladen')
with a.firmware.open('rb') as f:data=f.read(0x300001)
now=int(time.time())
m=dict(schema=1,target=a.target,edition=a.edition,version=a.version,size=len(data),sha256=hashlib.sha256(data).hexdigest(),sequence=now,expires=now+a.days*86400)
image(m,data) # rejects wrong edition, stale version and wrong-target builds
m['file']=filename(m)
m['signature']=key.sign(payload(m),ec.ECDSA(hashes.SHA256())).hex()
a.out.mkdir(parents=True,exist_ok=True)
(a.out/filename(m)).write_bytes(data)
(a.out/f'{a.target}-{a.edition}.json').write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')
print(f'Signierte Variante {a.edition} vorbereitet. Noch nicht veröffentlicht. Katalog spätestens nach 90 Tagen erneuern.')
