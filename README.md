# Camper Level Updates

Öffentlicher Updatekanal für Camper Level. **Noch keine neue Firmware freigegeben.**

Firmwaredateien werden als GitHub Release bereitgestellt; die Apps prüfen den
signierten Katalog unter `https://oliver19802.github.io/camper-level-updates/`.
HTTPS, eingebetteter ECDSA-P256-Prüfschlüssel und SHA-256 schützen die Übertragung.
Der Sensor verlangt zusätzlich seinen individuellen lokalen Update-Schlüssel.

## Status

Der Kanal ist vorbereitet. Eine Version wird erst nach Kompilierung und Test am
echten Sensor veröffentlicht. Ohne Katalog oder bei abgelaufener Signatur darf
kein Update angeboten werden. Kein automatisches Installieren.

## Veröffentlichung

1. Offizielle Firmware kompilieren und am Ersatzgerät testen (Neustart, Messung,
   Verbindungsabbruch, falsche Datei, Rückfall).
2. `sign_release.py` lokal mit dem außerhalb dieses Repositories gespeicherten
   DPAPI-Schlüssel ausführen. Benötigt Python und `cryptography`.
3. Release mit Tag `vVERSION` erstellen und ausschließlich die erzeugte offizielle
   BIN-Datei anhängen. Keine Gesamtspeicherabbilder, NVS oder privaten Varianten.
4. Den erzeugten signierten Katalog als `docs/channels/atoms3r-official.json`
   bzw. `docs/channels/xiao-esp32c3-official.json` veröffentlichen.
5. Katalog spätestens nach 90 Tagen neu signieren (auch ohne Versionswechsel).

Die Signatur umfasst Ziel, Edition, Version, Dateigröße, SHA-256, Katalogsequenz
und Ablaufdatum. Clients speichern die zuletzt akzeptierte Sequenz lokal,
weisen ältere oder abgelaufene Kataloge ab und prüfen das Firmwareziel.
Der Sensor prüft die Herausgebersignatur vor Schreibbeginn und die übertragene
Firmware vor Aktivierung. Signaturprüfung ist kein Hardware-Secure-Boot.

## Schlüssel

`release-public-key.pem` ist öffentlich und im Client fest verankert. Ein aus dem
Internet nachgeladener Ersatzschlüssel wird nicht einfach übernommen.
Der geheime Freigabeschlüssel bleibt offline außerhalb des Repositories.
Seine verschlüsselte Sicherung und das Passwort getrennt aufbewahren.
Geräte-Update-Schlüssel werden niemals an GitHub gesendet.

Dieser kleine Updatekanal ist eine eigene signierte Implementierung, keine
vollständige TUF-Implementierung. Schlüsselrotation braucht eine bewusst
geprüfte neue Vertrauenskonfiguration.
