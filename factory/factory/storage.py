"""Manifest + contabilidad de GB + subida opcional a S3/R2."""
import hashlib
import json
import pathlib
from datetime import datetime, timedelta

from ..i18n import translate

MAN = pathlib.Path("out/manifest.json")


def init_manifest():
    """Inicializar manifest.json si no existe."""
    pathlib.Path("out").mkdir(parents=True, exist_ok=True)
    if not MAN.exists():
        MAN.write_text(json.dumps({"assets": [], "bytes": 0, "created": datetime.now().isoformat()}, indent=1), encoding="utf-8")


def record(kind, path: pathlib.Path, **meta):
    """Registrar un archivo generado en el manifest con metadatos completos."""
    init_manifest()
    man = json.loads(MAN.read_text(encoding="utf-8"))
    b = path.stat().st_size
    sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    entry = {
        "kind": kind,
        "path": str(path),
        "bytes": b,
        "sha256": sha256,
        "generated": datetime.now().isoformat(),
        "scale": meta.get("scale", "unknown"),
        "program": meta.get("program", "unknown"),
        "expires": (datetime.now() + timedelta(days=365)).isoformat(),  # 1-year expiry
    }
    # Agregar metadatos adicionales si fueron proveídos
    entry.update(meta)
    man["assets"].append(entry)
    man["bytes"] += b
    # Actualizar fecha de creación si es la primera entrada
    if man.get("created") == "" or man.get("created") is None:
        man["created"] = datetime.now().isoformat()
    MAN.write_text(json.dumps(man, indent=1, ensure_ascii=False), encoding="utf-8")


def stats():
    """Mostrar estadísticas del manifest de activos."""
    man = json.loads(MAN.read_text(encoding="utf-8"))
    gb = man["bytes"] / 1e9
    by: dict = {}
    for a in man["assets"]:
        by[a["kind"]] = by.get(a["kind"], 0) + a["bytes"]
    print(f"TOTAL: {gb:.2f} GB · {len(man['assets'])} activos")
    print(f"Generado: {man.get('created', 'desconocido')[:10]}")
    for k, v in sorted(by.items(), key=lambda x: -x[1]):
        print(f"   {k:12s} {v / 1e9:8.2f} GB")
    # Mostrar expiraciones próximas
    print("\nPróximas expiraciones (día):")
    from datetime import datetime
    now = datetime.now()
    for a in man["assets"]:
        exp = datetime.fromisoformat(a.get("expires", "1970-01-01"))
        days_left = (exp - now).days
        if 0 < days_left <= 30:
            print(f"  ⚠️  {a['kind']:12s} expira en {days_left} días")
