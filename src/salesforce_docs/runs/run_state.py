"""Estado de execução em runs/run-<AAAAMMDD-HHMMSS>.json (salvar e retomar)."""

from __future__ import annotations

from pathlib import Path

from salesforce_docs import status as st
from salesforce_docs.utils import iso_now, now_local, read_json, write_json


class RunState:
    def __init__(self, path: Path, data: dict):
        self.path = Path(path)
        self.data = data
        # Máscara aplicada a TODO texto do estado antes de gravar (token, segredos do XML).
        self.masker = None

    # Criação / carga ---------------------------------------------------
    @classmethod
    def create(cls, runs_dir, org_alias, api_version=None, resumed_from=None):
        stamp = now_local().strftime("%Y%m%d-%H%M%S")
        run_id = f"run-{stamp}"
        path = Path(runs_dir) / f"{run_id}.json"
        n = 1
        while path.exists():
            n += 1
            run_id = f"run-{stamp}-{n}"
            path = Path(runs_dir) / f"{run_id}.json"
        data = {
            "runId": run_id,
            "orgAlias": org_alias,
            "apiVersion": api_version,
            "startedAt": iso_now(),
            "finishedAt": None,
            "status": st.IN_PROGRESS,
            "resumedFrom": resumed_from,
            "cli": {},
            "session": {},
            "failure": None,
            "steps": [],
            "metadataTypes": [],
            "components": [],
            "events": [],
        }
        state = cls(path, data)
        state.save()
        return state

    @classmethod
    def load(cls, path):
        return cls(Path(path), read_json(path))

    @staticmethod
    def find(runs_dir, run_id):
        runs_dir = Path(runs_dir)
        if run_id == "latest":
            files = sorted(runs_dir.glob("run-*.json"))
            return files[-1] if files else None
        p = runs_dir / (run_id if run_id.endswith(".json") else f"{run_id}.json")
        return p if p.is_file() else None

    # Persistência -------------------------------------------------------
    def save(self):
        data = _mask_tree(self.data, self.masker) if self.masker else self.data
        write_json(self.path, data, private=True)

    @property
    def run_id(self):
        return self.data["runId"]

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def step(self, name, status, detail=None):
        self.data["steps"].append({"step": name, "status": status, "at": iso_now(),
                                   "detail": detail})
        self.save()

    def event(self, level, message):
        self.data["events"].append({"at": iso_now(), "level": level, "message": message})

    def type_status(self, metadata_type, status, group=None, detail=None, **extra):
        entry = {"metadataType": metadata_type, "group": group, "status": status, "detail": detail}
        entry.update(extra)
        self.data["metadataTypes"] = [
            t for t in self.data["metadataTypes"]
            if not (t["metadataType"] == metadata_type and t.get("group") == group
                    and t.get("stage") == extra.get("stage")
                    and t.get("component") == extra.get("component"))
        ]
        self.data["metadataTypes"].append(entry)
        self.save()

    def upsert_component(self, entry: dict):
        key = (entry.get("unitId"), entry.get("metadataType"), entry.get("component"))
        comps = self.data["components"]
        for i, c in enumerate(comps):
            if (c.get("unitId"), c.get("metadataType"), c.get("component")) == key:
                comps[i] = dict(c, **entry)
                self.save()
                return comps[i]
        comps.append(entry)
        self.save()
        return entry

    def unit_status(self, unit_id):
        for c in self.data["components"]:
            if c.get("unitId") == unit_id and c.get("role") == "primary":
                return c.get("status")
        return None

    def successful_units(self):
        return {c["unitId"]: c for c in self.data["components"]
                if c.get("role") == "primary" and c.get("status") == st.SUCCESS}

    def carry_successes_from(self, previous: "RunState", only=None):
        """Retomada: herda unidades SUCCESS (não serão reprocessadas).

        `only` restringe às unidades verificadas como compatíveis com esta execução.
        """
        done = previous.successful_units()
        if only is not None:
            done = {k: v for k, v in done.items() if k in only}
        for c in previous.data["components"]:
            if c.get("unitId") in done:
                self.data["components"].append(dict(c, carriedFrom=previous.run_id))
        self.save()
        return set(done)

    def finish(self, status, failure=None):
        self.data["status"] = status
        self.data["failure"] = failure
        self.data["finishedAt"] = iso_now()
        self.save()

    def summary(self):
        counts = {}
        for c in self.data["components"]:
            if c.get("role") != "primary":
                continue
            counts[c.get("status")] = counts.get(c.get("status"), 0) + 1
        return counts


def _mask_tree(value, masker):
    if isinstance(value, str):
        return masker(value)
    if isinstance(value, dict):
        return {k: _mask_tree(v, masker) for k, v in value.items()}
    if isinstance(value, list):
        return [_mask_tree(v, masker) for v in value]
    return value
