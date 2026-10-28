"""Converte as fixtures (formato source do SFDX) para o formato metadata da Metadata API.

Só para testes do modo pasta: o mesmo repositório nos dois formatos tem de gerar os mesmos
documentos. Formato metadata: `<Nome>.<sufixo>` sem `-meta.xml` (exceto tipos com arquivo de
conteúdo, como `.cls`), e campos/record types/regras dentro do `.object`.
"""

import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

META = "-meta.xml"
CONTENT_FOLDERS = {"classes", "triggers", "certs"}
BUNDLE_FOLDERS = {"lwc"}
INLINE = {"fields": "fields", "recordTypes": "recordTypes", "validationRules": "validationRules",
          "webLinks": "webLinks", "businessProcesses": "businessProcesses"}
NS = "http://soap.sforce.com/2006/04/metadata"


def to_metadata_format(src: Path, dest: Path):
    for path in sorted(src.rglob("*")):
        if not path.is_file() or path.name == "manifest.json":
            continue
        rel = path.relative_to(src)
        top = rel.parts[0]
        if top == "objects":
            continue
        out = dest / rel
        if top not in CONTENT_FOLDERS and top not in BUNDLE_FOLDERS and path.name.endswith(META) \
                and not (top == "experiences" and len(rel.parts) > 2):
            out = out.with_name(path.name[:-len(META)])
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, out)
    _objects(src / "objects", dest / "objects")


def _objects(src: Path, dest: Path):
    if not src.is_dir():
        return
    ET.register_namespace("", NS)
    dest.mkdir(parents=True, exist_ok=True)
    for obj_dir in sorted(p for p in src.iterdir() if p.is_dir()):
        name = obj_dir.name
        parent = obj_dir / f"{name}.object{META}"
        root = ET.parse(parent).getroot() if parent.is_file() else ET.Element(f"{{{NS}}}CustomObject")
        for folder, element in INLINE.items():
            for child in sorted((obj_dir / folder).glob(f"*{META}")) if (obj_dir / folder).is_dir() else []:
                croot = ET.parse(child).getroot()
                elem = ET.SubElement(root, f"{{{NS}}}{element}")
                for c in croot:
                    elem.append(c)
                if not any(c.tag.endswith("fullName") for c in croot):
                    full = ET.Element(f"{{{NS}}}fullName")
                    full.text = child.name.split(".")[0]
                    elem.insert(0, full)
        ET.ElementTree(root).write(dest / f"{name}.object", encoding="UTF-8", xml_declaration=True)
