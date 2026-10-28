"""Modo pasta (`run --source-dir`): metadados lidos de um projeto Salesforce já clonado.

Substitui, sem login e sem Salesforce CLI, os passos que buscam metadados na org:
inventário (6), retrieve das fontes de acesso (6b) e retrieve por componente (7).
Normalização (8) e Markdown (10) são os mesmos do modo com login.

Regras:
- o repositório é o raw: nunca é alterado; cada arquivo usado é copiado byte a byte para
  inventory/.../components/ e o manifesto da execução registra caminho e sha256 de origem;
- formato source do SFDX (`<Nome>.<sufixo>-meta.xml`, objeto em subpastas) e formato metadata
  da Metadata API (`<Nome>.<sufixo>`, campos dentro do `.object`). Na cópia, o nome segue o
  formato source (o conteúdo não muda), que é o que o restante do utilitário lê;
- formato metadata: o `.object` é separado em objeto + filhos (campos, record types...) como
  arquivos DERIVADOS (o original fica copiado intacto ao lado) — regeneráveis a partir dele;
- pasta e sufixo de cada tipo vêm de `sourceDirectory` em config/metadata-types-mvp.json;
- links simbólicos e pastas ocultas (ex.: .git) são ignorados; nada fora do repositório é lido.
"""

from __future__ import annotations

import copy
import json
import os
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath
from urllib.parse import unquote

from salesforce_docs import status as st
from salesforce_docs.errors import ConfigError
from salesforce_docs.extraction.xml_retriever import find_main_file
from salesforce_docs.parsing.xml_parser import local_name
from salesforce_docs.utils import (copy_private, iso_now, rel, sha256_file, sha256_text, slugify, write_json,
                                   write_text_raw)

META = "-meta.xml"
FORMAT_SOURCE, FORMAT_METADATA = "SOURCE", "METADATA"


def find_repository_entry(app, source_dir):
    """De-para da pasta informada em `--source-dir` (nome da pasta) em config.json sourceRepositories."""
    path = Path(source_dir).expanduser()
    if not path.is_dir():
        raise ConfigError(f"--source-dir: pasta não encontrada: {source_dir}")
    folder = path.resolve().name
    for entry in app.source_repositories:
        if entry["folder"] == folder:
            return path.resolve(), entry
    known = ", ".join(e["folder"] for e in app.source_repositories) or "nenhuma"
    raise ConfigError(
        f"--source-dir: a pasta {folder!r} não está em sourceRepositories do config.json "
        f"(cadastradas: {known}). Inclua {{\"folder\": \"{folder}\", \"orgName\": \"<nome da org>\"}} "
        "para registrar de qual org é o repositório.")


class SourceFile(dict):
    """Arquivo do repositório que representa (parte de) um componente.

    kind: meta (XML do componente), content (.cls/.trigger/.crt), bundle (arquivo do bundle),
    inline (`.object` do formato metadata, com filhos dentro), inline-child (filho dentro do .object).
    """


class SourceRepository:
    def __init__(self, path: Path, entry: dict, cfg: dict, project_root: Path):
        self.root = Path(path).resolve()
        self.entry = entry
        self.folder = entry["folder"]
        self.org_name = entry["orgName"]
        self.alias = entry.get("alias") or slugify(self.folder)
        self.project_root = Path(project_root).resolve()
        self.cfg = cfg or {}
        self.types = self.cfg.get("types") or {}
        if not self.types:
            raise ConfigError("metadata-types-mvp.json sem sourceDirectory.types: o modo pasta não sabe "
                              "onde cada metadata type fica no repositório")
        self.metadata_dir = self._metadata_dir(entry.get("metadataPath"))
        self.files = []           # SourceFile
        self.ignored = {}         # pasta -> quantidade de arquivos não reconhecidos
        self.unmapped_folders = []
        self.problems = []
        self._copied = {}         # destino -> entrada de arquivo já copiada nesta execução
        self._decomposed = {}     # (.object, destino) -> arquivos derivados
        self.manifest = None
        self._hashes = {}         # sha256 por arquivo do repositório (calculado uma vez)
        self._scan()

    # Localização ------------------------------------------------------------
    def _mapped_folders(self):
        return {t["folder"] for t in self.types.values()}

    def _metadata_dir(self, metadata_path):
        if metadata_path:
            candidate = (self.root / metadata_path).resolve()
            if candidate != self.root and self.root not in candidate.parents:
                raise ConfigError(f"sourceRepositories: metadataPath {metadata_path!r} sai do repositório")
            if not candidate.is_dir():
                raise ConfigError(f"sourceRepositories: metadataPath {metadata_path!r} não existe em {self.root}")
            return candidate
        folders = self._mapped_folders()
        found = []
        for cand in self.cfg.get("metadataPathCandidates") or ["."]:
            d = (self.root / cand).resolve()
            if d.is_dir() and not d.is_symlink() and any((d / f).is_dir() for f in folders):
                found.append(d)
        if len(found) == 1:
            return found[0]
        tried = ", ".join(self.cfg.get("metadataPathCandidates") or ["."])
        if not found:
            raise ConfigError(
                f"Repositório {self.folder}: nenhuma pasta de metadata reconhecida (ex.: profiles, roles, "
                f"objects) em {tried}. Informe metadataPath em sourceRepositories.")
        raise ConfigError(
            f"Repositório {self.folder}: pastas de metadata em mais de um lugar "
            f"({', '.join(rel(d, self.root) or '.' for d in found)}). Informe metadataPath em sourceRepositories.")

    # Varredura ----------------------------------------------------------------
    def _walk(self, top: Path):
        """Arquivos sob `top` (caminhos relativos a metadata_dir), sem seguir links simbólicos."""
        for dirpath, dirnames, filenames in os.walk(top, followlinks=False):
            base = Path(dirpath)
            dirnames[:] = sorted(d for d in dirnames
                                 if not d.startswith(".") and not (base / d).is_symlink())
            for name in sorted(filenames):
                full = base / name
                if name.startswith(".") or full.is_symlink() or not full.is_file():
                    continue
                yield PurePosixPath(full.relative_to(self.metadata_dir).as_posix())

    def _scan(self):
        by_folder = {}
        for mtype, tcfg in self.types.items():
            by_folder.setdefault(tcfg["folder"], []).append((mtype, tcfg))
        for entry in sorted(os.listdir(self.metadata_dir)):
            d = self.metadata_dir / entry
            if entry.startswith(".") or d.is_symlink() or not d.is_dir():
                continue
            if entry not in by_folder:
                self.unmapped_folders.append(entry)
                continue
            for relpath in self._walk(d):
                hit = None
                for mtype, tcfg in by_folder[entry]:
                    hit = self._classify(mtype, tcfg, relpath)
                    if hit:
                        break
                if hit:
                    self.files.extend(hit)
                else:
                    self.ignored[entry] = self.ignored.get(entry, 0) + 1
        self._check_duplicates()
        self._index()

    def _index(self):
        """Índices por componente, por tipo e por pai (repositórios com milhares de arquivos)."""
        self._by_key, self._by_type, self._by_parent, self._lower = {}, {}, {}, {}
        for f in self.files:
            key = (f["type"], f["fullName"])
            self._by_key.setdefault(key, []).append(f)
            self._by_type.setdefault(f["type"], []).append(f)
            self._lower.setdefault((f["type"], f["fullName"].lower()), f["fullName"])
            if f.get("parent"):
                self._by_parent.setdefault(tuple(f["parent"]), []).append(f)

    def _classify(self, mtype, tcfg, relpath: PurePosixPath):
        parts = relpath.parts
        name = parts[-1]
        suffix = tcfg.get("suffix")
        if tcfg.get("bundle"):
            if len(parts) >= 3:
                return [self._file(mtype, parts[1], relpath, "bundle")]
            if len(parts) == 2 and suffix:
                comp = _strip(name, suffix)
                if comp:
                    return [self._file(mtype, comp, relpath, "meta")]
            return None
        if tcfg.get("nested"):
            if len(parts) == 2:  # formato metadata: objects/Conta.object (filhos dentro)
                comp = _strip(name, suffix, meta_only=False)
                if comp and not name.endswith(META):
                    return self._inline(mtype, tcfg, comp, relpath)
                return None
            if len(parts) == 3:
                comp = _strip(name, suffix)
                if comp and comp == parts[1]:
                    return [self._file(mtype, comp, relpath, "meta")]
                return None
            if len(parts) == 4:
                child = (tcfg.get("children") or {}).get(parts[2])
                cname = _strip(name, child["suffix"]) if child else None
                if cname:
                    return [self._file(child["type"], f"{parts[1]}.{cname}", relpath, "meta",
                                       parent=(mtype, _decode(parts[1])))]
            return None
        if len(parts) != 2:
            return None
        if tcfg.get("content"):
            if name.endswith(f".{suffix}{META}"):
                return [self._file(mtype, name[:-len(f".{suffix}{META}")], relpath, "meta")]
            if name.endswith(f".{suffix}"):
                return [self._file(mtype, name[:-len(f".{suffix}")], relpath, "content")]
            return None
        comp = _strip(name, suffix)
        return [self._file(mtype, comp, relpath, "meta")] if comp else None

    def _file(self, mtype, name, relpath, kind, parent=None, element=None):
        f = SourceFile(type=mtype, fullName=_decode(name), relpath=relpath.as_posix(), kind=kind)
        if parent:
            f["parent"] = parent
        if element is not None:
            f["element"] = element
        return f

    def _inline(self, mtype, tcfg, comp, relpath):
        """`.object` do formato metadata: o próprio objeto e os filhos declarados em `children`."""
        out = [self._file(mtype, comp, relpath, "inline")]
        inline = {c["inlineElement"]: c for c in (tcfg.get("children") or {}).values() if c.get("inlineElement")}
        if not inline:
            return out
        try:
            root = ET.parse(str(self.metadata_dir / relpath)).getroot()
        except ET.ParseError as exc:
            self.problems.append(f"{relpath}: XML inválido ({exc})")
            return out
        for elem in root:
            child = inline.get(local_name(elem.tag))
            if not child:
                continue
            full = next((c.text for c in elem if local_name(c.tag) == "fullName"), None)
            if not full or not full.strip():
                self.problems.append(f"{relpath}: <{local_name(elem.tag)}> sem fullName (ignorado)")
                continue
            out.append(self._file(child["type"], f"{comp}.{full.strip()}", relpath, "inline-child",
                                  parent=(mtype, _decode(comp)), element=local_name(elem.tag)))
        return out

    def _check_duplicates(self):
        """O mesmo componente nos dois formatos (ex.: X.profile e X.profile-meta.xml) é ambíguo."""
        seen = {}
        for f in self.files:
            if f["kind"] not in ("meta", "inline"):
                continue
            key = (f["type"], f["fullName"])
            if key in seen:
                self.problems.append(f"{f['type']}:{f['fullName']} aparece em {seen[key]} e {f['relpath']}; "
                                     f"usado {seen[key]}")
                f["duplicate"] = True
            else:
                seen[key] = f["relpath"]
        self.files = [f for f in self.files if not f.get("duplicate")]

    # Consultas ----------------------------------------------------------------
    @property
    def format(self):
        """SOURCE, METADATA, MISTO ou VAZIO. Tipos com arquivo de conteúdo (.cls) e bundles
        têm a mesma forma nos dois formatos e não contam."""
        kinds = set()
        for f in self.files:
            tcfg = self.types.get(f["type"]) or {}
            if f["kind"] in ("inline", "inline-child"):
                kinds.add(FORMAT_METADATA)
            elif f["kind"] == "meta" and not tcfg.get("content") and not tcfg.get("bundle"):
                kinds.add(FORMAT_SOURCE if f["relpath"].endswith(META) else FORMAT_METADATA)
        if len(kinds) == 1:
            return kinds.pop()
        return "MISTO" if kinds else "VAZIO"

    def readable_types(self):
        out = set(self.types)
        for tcfg in self.types.values():
            out.update(c["type"] for c in (tcfg.get("children") or {}).values())
        return out

    def found_types(self):
        return {f["type"] for f in self.files}

    def inventory(self, metadata_type):
        """Componentes do tipo no repositório (o que `sf org list metadata` listaria)."""
        items = {}
        for f in self._by_type.get(metadata_type, []):
            if f["kind"] == "content":
                continue
            if f["kind"] == "bundle" and f["fullName"] in items:
                continue
            items.setdefault(f["fullName"], {"fullName": f["fullName"], "type": metadata_type,
                                             "fileName": f["relpath"]})
        return sorted(items.values(), key=lambda i: i["fullName"])

    def describe(self):
        return {"folder": self.folder, "orgName": self.org_name, "alias": self.alias,
                "path": str(self.root), "metadataPath": rel(self.metadata_dir, self.root) or ".",
                "format": self.format, "files": len(self.files),
                "unmappedFolders": self.unmapped_folders, "ignoredFiles": self.ignored,
                "problems": self.problems}

    def write_manifest(self, path: Path):
        """Registro do raw: cada arquivo reconhecido com caminho no repositório e sha256."""
        seen, files = set(), []
        for f in self.files:
            if f["relpath"] in seen:
                continue
            seen.add(f["relpath"])
            full = self.metadata_dir / f["relpath"]
            files.append({"path": self._repo_path(f["relpath"]), "sha256": self._sha(f["relpath"]),
                          "size": full.stat().st_size})
        write_json(path, {"rawFormat": "source-directory-manifest/v1",
                          "note": "Metadados lidos de repositório clonado (modo pasta). O repositório é o "
                                  "raw e não é alterado; este arquivo registra o que foi lido.",
                          "generatedAt": iso_now(), **self.describe(), "fileList": files}, private=True)
        self.manifest = path
        return path

    def content_fingerprint(self):
        """Pasta + sha256 dos arquivos lidos: a retomada só reaproveita se o repositório não mudou."""
        listing = sorted((f["relpath"], self._sha(f["relpath"])) for f in self.files)
        return f"{self.folder} ({self.org_name}), conteúdo sha256 {sha256_text(json.dumps(listing))[:16]}"

    def _sha(self, relpath):
        if relpath not in self._hashes:
            self._hashes[relpath] = sha256_file(self.metadata_dir / relpath)
        return self._hashes[relpath]

    def _repo_path(self, relpath):
        """Caminho de origem como aparece nos documentos e no run state: <pasta do repositório>/..."""
        return (PurePosixPath(self.folder) / rel(self.metadata_dir / relpath, self.root)).as_posix()

    # "Retrieve" ---------------------------------------------------------------
    def _select(self, metadata_type, full_name=None):
        tcfg = self.types.get(metadata_type) or {}
        if full_name is None:
            exact = list(self._by_type.get(metadata_type, []))
        else:
            exact = list(self._by_key.get((metadata_type, full_name), []))
            if not exact:  # mesma regra do retrieve: nome sem diferenciar maiúsculas como 2ª opção
                other = self._lower.get((metadata_type, full_name.lower()))
                exact = list(self._by_key.get((metadata_type, other), [])) if other else []
        if tcfg.get("retrieveIncludesChildren"):
            for parent in sorted({f["fullName"] for f in exact}):
                exact += self._by_parent.get((metadata_type, parent), [])
        return exact

    def collect(self, specs, components_dir: Path):
        """Equivalente a `sf project retrieve start --metadata <spec>...` sobre o repositório.

        specs: `Tipo` (todos do tipo) ou `Tipo:Nome`. Mesmo formato de retorno de
        xml_retriever.retrieve_specs (arquivos copiados para components_dir)."""
        out = {"ok": True, "error": None, "retrieveRaw": rel(self.manifest, self.project_root),
               "files": [], "problems": []}
        chosen = []
        for spec in specs:
            mtype, _, name = spec.partition(":")
            if mtype not in self.readable_types():
                out["problems"].append(f"{mtype}: tipo sem pasta configurada em sourceDirectory")
                continue
            picked = self._select(mtype, name or None)
            if name and not picked:
                out["problems"].append(f"{mtype}:{name} não encontrado no repositório {self.folder}")
            chosen += picked
        seen = set()
        for f in chosen:
            try:
                items = self._materialize(f, components_dir)
            except (ET.ParseError, OSError) as exc:  # um arquivo ruim não derruba os demais
                out["problems"].append(f"{f['type']}:{f['fullName']}: {self._repo_path(f['relpath'])} "
                                       f"não pôde ser lido ({type(exc).__name__}: {exc})")
                continue
            for item in items:
                if item["path"] not in seen:
                    seen.add(item["path"])
                    out["files"].append(item)
        return out

    def collect_component(self, metadata_type, full_name, components_dir: Path):
        """Equivalente a xml_retriever.retrieve_component."""
        res = self.collect([f"{metadata_type}:{full_name}"], components_dir)
        outcome = {"metadataType": metadata_type, "fullName": full_name, "retrieveRaw": res["retrieveRaw"],
                   "files": res["files"], "status": None, "error": None}
        main = find_main_file(res["files"], metadata_type, full_name)
        if not res["files"]:
            outcome.update(status=st.RETRIEVE_FAILED, error="; ".join(res["problems"])
                           or f"{metadata_type}:{full_name} não encontrado no repositório {self.folder}")
        elif main is None:
            outcome.update(status=st.MISMATCH, error=f"Nenhum arquivo do repositório corresponde a "
                                                     f"{metadata_type}:{full_name}")
        else:
            outcome.update(status=st.SUCCESS, xml=main["path"], error="; ".join(res["problems"]) or None)
        return outcome

    def _materialize(self, f, components_dir: Path):
        src = self.metadata_dir / f["relpath"]
        if f["kind"] in ("inline", "inline-child"):
            item = self._decompose(f["relpath"], components_dir).get((f["type"], f["fullName"]))
            return [item] if item else []
        dest_rel = PurePosixPath(f["relpath"])
        if f["kind"] == "meta" and not dest_rel.name.endswith(META):
            # Formato metadata: mesmo conteúdo, nome no formato source (o que o utilitário lê).
            dest_rel = dest_rel.with_name(dest_rel.name + META)
        return [self._copy(src, components_dir / dest_rel, f)]

    def _copy(self, src: Path, dest: Path, f, derived=False):
        key = str(dest)
        if key not in self._copied:
            if not derived:
                dest.parent.mkdir(parents=True, exist_ok=True)
                copy_private(src, dest)  # byte a byte: o conteúdo do repositório não muda
            item = {"type": f["type"], "fullName": f["fullName"], "path": rel(dest, self.project_root),
                    "sha256": sha256_file(dest), "source": self._repo_path(f["relpath"]),
                    "sourceSha256": self._sha(f["relpath"])}
            if derived:
                item["derived"] = True
            self._copied[key] = item
        return dict(self._copied[key])

    def _decompose(self, relpath, components_dir: Path):
        """`.object` (formato metadata) -> objeto + filhos no formato source, como o retrieve devolveria.

        Feito uma vez por arquivo e pasta de destino. O original é copiado intacto (raw) em
        components/_repositorio/; objeto e filhos são DERIVADOS dele (`derived: true`)."""
        key = (relpath, str(components_dir))
        if key in self._decomposed:
            return self._decomposed[key]
        inline_file = next(f for f in self._by_type.get(self._inline_type(relpath), [])
                           if f["relpath"] == relpath and f["kind"] == "inline")
        mtype, parent = inline_file["type"], inline_file["fullName"]
        tcfg = self.types[mtype]
        src = self.metadata_dir / relpath
        rel_src = PurePosixPath(relpath)
        raw_dest = components_dir / "_repositorio" / rel_src
        raw_dest.parent.mkdir(parents=True, exist_ok=True)
        copy_private(src, raw_dest)
        root = ET.parse(str(src)).getroot()
        ns = root.tag[1:].split("}", 1)[0] if root.tag.startswith("{") else ""
        inline = {c["inlineElement"]: (folder, c) for folder, c in (tcfg.get("children") or {}).items()
                  if c.get("inlineElement")}
        stem = rel_src.name[:-len("." + tcfg["suffix"])]
        folder = components_dir / rel_src.parent / stem
        parent_root = ET.Element(root.tag, root.attrib)
        parent_root.text = root.text
        out = {}
        for elem in root:
            spec = inline.get(local_name(elem.tag))
            if spec is None:
                parent_root.append(copy.deepcopy(elem))
                continue
            child_folder, ccfg = spec
            full = next((c.text for c in elem if local_name(c.tag) == "fullName"), None)
            if not full or not full.strip():
                continue
            croot = ET.Element(_qname(ns, ccfg["type"]))
            for c in elem:
                croot.append(copy.deepcopy(c))
            cname = f"{parent}.{full.strip()}"
            dest = folder / child_folder / f"{full.strip()}.{ccfg['suffix']}{META}"
            out[(ccfg["type"], cname)] = self._write_derived(
                croot, ns, dest, SourceFile(type=ccfg["type"], fullName=cname, relpath=relpath))
        dest = folder / f"{stem}.{tcfg['suffix']}{META}"
        out[(mtype, parent)] = self._write_derived(parent_root, ns, dest, inline_file)
        self._decomposed[key] = out
        return out

    def _inline_type(self, relpath):
        folder = PurePosixPath(relpath).parts[0]
        return next(t for t, c in self.types.items() if c.get("nested") and c["folder"] == folder)

    def _write_derived(self, root, ns, dest: Path, f):
        if str(dest) not in self._copied:
            _indent(root)
            if ns:
                ET.register_namespace("", ns)
            text = ET.tostring(root, encoding="unicode")
            write_text_raw(dest, '<?xml version="1.0" encoding="UTF-8"?>\n' + text + "\n")
        return self._copy(self.metadata_dir / f["relpath"], dest, f, derived=True)


def _strip(name, suffix, meta_only=False):
    """Nome do componente sem `.sufixo-meta.xml` (formato source) ou `.sufixo` (formato metadata)."""
    if not suffix:
        return None
    for end in (f".{suffix}{META}",) + (() if meta_only else (f".{suffix}",)):
        if name.endswith(end) and len(name) > len(end):
            return name[:-len(end)]
    return None


def _decode(name):
    """Nomes de arquivo de metadata codificam caracteres especiais (ex.: `%3A` = `:`)."""
    return unquote(name)


def _qname(ns, tag):
    return f"{{{ns}}}{tag}" if ns else tag


def _indent(elem, level=0):
    """Indentação de 4 espaços (como o retrieve), só para leitura humana do derivado."""
    pad = "\n" + "    " * level
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = pad + "    "
        for child in elem:
            _indent(child, level + 1)
        last = elem[-1]
        last.tail = pad
        for child in list(elem)[:-1]:
            if not child.tail or not child.tail.strip():
                child.tail = pad + "    "
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = pad
