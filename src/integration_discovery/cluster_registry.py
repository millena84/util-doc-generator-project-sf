"""Números estáveis dos clusters e histórico das revisões humanas.

Arquivo: `discovery/org-<alias>/api-v<N>/state/cluster-registry.json` (um registro por org e versão).

- Cada composição de cluster (assinatura = membros) recebe um número uma única vez
  (`cluster-NNN`). Em execuções seguintes, a mesma composição reaproveita o número, mesmo que a
  ordem por evidências mude. Composição nova recebe o próximo número livre.
- Número de cluster que deixou de existir é APOSENTADO e nunca é reutilizado por outra
  composição; o registro guarda para onde foram os componentes dele (`successors`). Se a mesma
  composição voltar, o número volta a valer.
- As revisões ficam num histórico que só cresce (nunca é apagado com os arquivos de cluster);
  a decisão vigente de uma composição é a última revisão dela.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

VERSION = 1
ACTIVE = "ACTIVE"
RETIRED = "RETIRED"


class RegistryError(ValueError):
    """Registro existe mas não pode ser usado: nada é gravado (evita renumerar em silêncio)."""


def write_atomic(path, text):
    """Grava num temporário da mesma pasta e troca de uma vez: interrupção não deixa arquivo pela metade."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


class ClusterRegistry:
    def __init__(self, path):
        self.path = Path(path)
        self.existed = self.path.is_file()
        if not self.existed:
            self.data = {"version": VERSION, "nextNumber": 1, "clusters": {}, "reviews": []}
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise RegistryError(self._unusable(f"não é um JSON válido ({type(exc).__name__})")) from None
        if not isinstance(data, dict) or data.get("version") != VERSION \
                or not isinstance(data.get("clusters"), dict) or not isinstance(data.get("reviews"), list) \
                or not isinstance(data.get("nextNumber"), int):
            raise RegistryError(self._unusable(f"estrutura inesperada (versão esperada {VERSION})"))
        self.data = data

    def _unusable(self, why):
        return (f"registro de clusters ilegível: {self.path} {why}. Nada foi gravado. Recomeçar a numeração "
                "faria um número antigo apontar para outra composição. Restaure o arquivo (backup) ou, se aceitar "
                "perder os números e as decisões registradas, apague-o conscientemente e rode de novo.")

    # Números --------------------------------------------------------------
    def _new_id(self):
        n = self.data["nextNumber"]
        self.data["nextNumber"] = n + 1
        return f"cluster-{n:03d}"

    def seed(self, signature, cluster_id, members):
        """Migração: arquivos de cluster gerados antes do registro mantêm o número."""
        if signature in self.data["clusters"]:
            return
        self.data["clusters"][signature] = {"clusterId": cluster_id, "members": sorted(members),
                                            "status": RETIRED, "successors": []}
        try:
            n = int(cluster_id.rsplit("-", 1)[1])
        except (IndexError, ValueError):
            return
        self.data["nextNumber"] = max(self.data["nextNumber"], n + 1)

    def assign(self, clusters, now):
        """Atribui números estáveis aos clusters desta execução e aposenta os que sumiram."""
        current = {c["signature"] for c in clusters}
        for c in clusters:
            entry = self.data["clusters"].get(c["signature"])
            members = [x["id"] for x in c["components"]]
            if entry is None:
                entry = {"clusterId": self._new_id(), "members": sorted(members), "firstSeen": now}
                self.data["clusters"][c["signature"]] = entry
            entry.update(status=ACTIVE, lastSeen=now, successors=[])
            entry.pop("retiredAt", None)
            c["clusterId"] = entry["clusterId"]
        by_member = {}
        for c in clusters:
            for x in c["components"]:
                by_member.setdefault(x["id"], set()).add(c["clusterId"])
        for sig, entry in self.data["clusters"].items():
            if sig in current:
                continue
            if entry.get("status") != RETIRED:
                entry.update(status=RETIRED, retiredAt=now)
            entry["successors"] = sorted(set().union(*(by_member.get(m, set()) for m in entry["members"])))

    def find(self, cluster_id):
        for sig, entry in self.data["clusters"].items():
            if entry["clusterId"] == cluster_id:
                return sig, entry
        return None, None

    # Revisões -------------------------------------------------------------
    def add_review(self, signature, cluster_id, review, approved_name=None):
        self.data["reviews"].append(dict(review, signature=signature, clusterId=cluster_id,
                                         approvedName=approved_name))

    def latest_review(self, signature):
        for r in reversed(self.data["reviews"]):
            if r["signature"] == signature:
                return r
        return None

    def stale_reviews(self, decided_ids):
        """Clusters aposentados com decisão vigente (não PENDING) cujos componentes estão hoje em
        clusters ainda sem decisão: a revisão precisa ser refeita."""
        out = []
        for sig, entry in sorted(self.data["clusters"].items(), key=lambda kv: kv[1]["clusterId"]):
            if entry.get("status") != RETIRED:
                continue
            review = self.latest_review(sig)
            if not review or review.get("decision") in (None, "PENDING"):
                continue
            pending = [s for s in entry.get("successors") or [] if s not in decided_ids]
            if pending or not entry.get("successors"):
                out.append({"clusterId": entry["clusterId"], "signature": sig, "decision": review["decision"],
                            "reviewedBy": review.get("reviewedBy"), "notes": review.get("notes"),
                            "successors": entry.get("successors") or []})
        return out

    def save(self):
        write_atomic(self.path, json.dumps(self.data, indent=2, ensure_ascii=False) + "\n")
