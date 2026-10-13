"""Builders da seção "Acesso e configuração" (onde o componente está configurado).

Fonte: XML (Profile, PermissionSet, PermissionSetGroup, Queue, SharingRules e o XML do
próprio componente), via índice do passo 6b. Sem índice (retrieve de acesso falhou ou não
executado) a tabela fica "Não informado" — nunca "sem acesso".
"""

from __future__ import annotations

from salesforce_docs.parsing.xml_parser import as_list
from salesforce_docs.rendering.context import resolve

ACCESS_PLACEHOLDERS = ("origin_type", "origin_name", "access_granted", "access_via")
SHARING_PLACEHOLDERS = ("sharing_kind", "sharing_name", "shared_to", "sharing_access_level")
DASH = "—"


def _row(origin_type, origin, access, via):
    return {"origin_type": origin_type, "origin_name": origin, "access_granted": access or DASH,
            "access_via": via or DASH}


def _lookup(index, key, name, prefix=False):
    grants = ((index or {}).get("grants") or {}).get(key) or {}
    if not prefix:
        return [(name, r) for r in grants.get(name, [])]
    out = []
    for gname, rows in sorted(grants.items()):
        if gname.startswith(f"{name}-"):
            out.extend((gname, r) for r in rows)
    return out


def _split(value):
    out = []
    for v in as_list(value):
        out.extend(x.strip() for x in str(v or "").split(",") if x.strip())
    return out


def access_rows(ctx, args):
    """Perfis, permission sets e permission set groups que concedem acesso ao componente.

    args:
      accessKey / prefixMatch — chave no índice (ex.: ApexClass); prefixMatch casa `Nome-*`
        (principals de External Credential);
      ownFields — {campo do XML do próprio componente: tipo de origem} (ex.: ConnectedApp);
      relatedFields — {metadataType, fields} em componente relacionado (ex.: políticas da ECA);
      relatedAccess — {metadataType, accessKey, prefixMatch}: acesso via relacionado (ex.: NC → EC);
      byPath — [{path, itemField?, accessKey, via}]: acesso a componentes que o próprio
        componente referencia (ex.: trigger -> objeto e classes chamadas);
      notApplicable — motivo quando o tipo não tem atribuição por perfil/permission set.
    """
    if args.get("notApplicable"):
        return [_row("Não aplicável", args["notApplicable"], None, None)]
    root = ctx.root()
    rows, needs_index = [], False
    if args.get("accessKey"):
        needs_index = True
        for gname, r in _lookup(root.access_index, args["accessKey"], root.full_name, args.get("prefixMatch")):
            via = r.get("via")
            if args.get("prefixMatch"):
                via = "; ".join(x for x in (f"Principal {gname.split('-', 1)[1]}", via) if x)
            rows.append(_row(r["originType"], r["origin"], r["access"], via))
    for field, label in (args.get("ownFields") or {}).items():
        for name in _split((root.data or {}).get(field)):
            rows.append(_row(label, name, "Autorizado no componente", None))
    rf = args.get("relatedFields") or {}
    related_sources = root.related_of(rf.get("metadataType")) if rf else []
    if rf and not related_sources and not args.get("accessKey") and not args.get("ownFields"):
        return []  # a fonte (componente relacionado) não foi recuperada: "Não informado"
    for rel in related_sources:
        for field, label in (rf.get("fields") or {}).items():
            for name in _split((rel.get("data") or {}).get(field)):
                rows.append(_row(label, name, "Autorizado no componente",
                                 f"{rf['metadataType']} {rel['fullName']}"))
    ra = args.get("relatedAccess") or {}
    if ra:
        needs_index = True
        for rel in root.related_of(ra.get("metadataType")):
            for gname, r in _lookup(root.access_index, ra["accessKey"], rel["fullName"], ra.get("prefixMatch")):
                via = f"{ra['metadataType']} {rel['fullName']}"
                if ra.get("prefixMatch"):
                    via += f" (principal {gname.split('-', 1)[1]})"
                if r.get("via"):
                    via += f"; {r['via']}"
                rows.append(_row(r["originType"], r["origin"], r["access"], via))
    for bp in args.get("byPath") or []:
        # Acesso a componentes que o próprio componente referencia (ex.: trigger -> objeto e
        # classes chamadas). bp: {path, itemField?, accessKey, via ("Objeto {name}")}.
        needs_index = True
        value, _ = resolve(root, bp["path"])
        names = [v.get(bp["itemField"]) if isinstance(v, dict) else v
                 for v in as_list(value)] if bp.get("itemField") else _split(value)
        for name in [n for n in names if n]:
            for _gname, r in _lookup(root.access_index, bp["accessKey"], name):
                via = bp.get("via", "{name}").format(name=name)
                if r.get("via"):
                    via += f"; {r['via']}"
                rows.append(_row(r["originType"], r["origin"], r["access"], via))
    if rows:
        return rows
    if needs_index and root.access_index is None:
        return []  # índice indisponível: "Não informado"
    return [_row("Nenhuma concessão encontrada", DASH, None, None)]


def object_sharing_rows(ctx, args):
    """Filas que aceitam o objeto e regras de compartilhamento (role, grupo, fila...)."""
    root = ctx.root()
    if root.access_index is None:
        return []
    name = root.full_name
    items = list((root.access_index.get("queues") or {}).get(name, [])) + \
        list((root.access_index.get("sharingRules") or {}).get(name, []))
    if not items:
        return [{"sharing_kind": "Nenhuma fila ou regra de compartilhamento encontrada",
                 "sharing_name": DASH, "shared_to": DASH, "sharing_access_level": DASH}]
    return [{"sharing_kind": i["kind"], "sharing_name": i.get("name") or DASH,
             "shared_to": i.get("sharedTo") or DASH, "sharing_access_level": i.get("accessLevel") or DASH}
            for i in items]


TABLE_BUILDERS = {"access_rows": access_rows, "object_sharing_rows": object_sharing_rows}
BLOCK_BUILDERS = {}
