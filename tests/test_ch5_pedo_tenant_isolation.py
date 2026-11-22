"""Tenant regressions through the real PEDO pipeline, without a database."""

import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1] / "chapter5/permission-embedded-data-objects"),
)
from pedo.core.models import AccessContext, DataObject
from pedo.core.store import ObjectStore, PermissionDeniedError
from pedo.scenarios.hiring import register_hiring_types


class MemoryStore(ObjectStore):
    """Replace persistence only; keep permissions, validators and references."""

    def _setup_db(self):
        self.objects = {}

    def _store_object(self, obj):
        self.objects[obj.id] = copy.deepcopy(obj)

    def _load_object(self, object_id):
        return copy.deepcopy(self.objects.get(object_id))


@pytest.fixture
def store():
    store = MemoryStore("unused")
    register_hiring_types(store)
    system = AccessContext("system", role="system")
    for org in ("acme", "other", ""):
        store.create(
            DataObject(
                id=org or "global",
                type_name="position",
                org_id=org,
                content={"status": "open", "salary_min": 0, "salary_max": 200_000},
            ),
            system,
        )
    return store


def candidate(org="", position="acme", parent=None, references=None):
    return DataObject(
        type_name="candidate",
        org_id=org,
        parent_id=parent,
        references=references or {},
        content={"status": "applied", "position_id": position},
    )


@pytest.mark.parametrize("org", [None, "", "other"])
def test_tenant_read_requires_matching_org(store, org):
    with pytest.raises(PermissionDeniedError, match="Tenant isolation"):
        store.get("acme", AccessContext("r", role="recruiter", org_id=org))


@pytest.mark.parametrize("org", [None, "", "other"])
def test_create_cannot_choose_foreign_tenant(store, org):
    before = copy.deepcopy(store.objects)
    with pytest.raises(PermissionDeniedError, match="Tenant isolation"):
        store.create(candidate(org="acme"), AccessContext("r", role="recruiter", org_id=org))
    assert store.objects == before


@pytest.mark.parametrize("reference_source", ["content", "references"])
def test_create_cannot_reference_foreign_tenant(store, reference_source):
    obj = candidate(position="other") if reference_source == "content" else candidate(
        position=None, references={"position": "other"}
    )
    before = copy.deepcopy(store.objects)
    with pytest.raises(PermissionDeniedError, match="Tenant isolation"):
        store.create(obj, AccessContext("r", role="recruiter", org_id="acme"))
    assert store.objects == before


def test_create_cannot_use_foreign_parent(store):
    with pytest.raises(PermissionDeniedError, match="Tenant isolation"):
        store.create(
            candidate(parent="other"), AccessContext("a", role="admin", org_id="acme")
        )


def test_global_object_cannot_link_into_tenant(store):
    with pytest.raises(PermissionDeniedError, match="Tenant isolation"):
        store.create(candidate(position="acme"), AccessContext("r", role="recruiter"))


def test_reference_override_cannot_hide_foreign_content_reference(store):
    with pytest.raises(PermissionDeniedError, match="Tenant isolation"):
        store.create(
            candidate(position="other", references={"position": "acme"}),
            AccessContext("r", role="recruiter", org_id="acme"),
        )


def test_same_tenant_read_and_create_with_inferred_org(store):
    accessor = AccessContext("r", role="recruiter", org_id="acme")
    assert store.get("acme", accessor).org_id == "acme"
    created = store.create(candidate(), accessor)
    assert created.org_id == "acme"
    assert store.get(created.id, accessor).owner_id == "r"


@pytest.mark.parametrize("org", [None, "", "acme"])
def test_global_objects_remain_readable(store, org):
    assert store.get("global", AccessContext("r", role="recruiter", org_id=org)).org_id == ""


def test_global_parent_and_reference_allow_tenant_child(store):
    created = store.create(
        candidate(position="global", parent="global"),
        AccessContext("a", role="admin", org_id="acme"),
    )
    assert created.org_id == "acme"


def test_system_retains_cross_tenant_access_and_create(store):
    system = AccessContext("system", role="system", org_id="other")
    assert store.get("acme", system).org_id == "acme"
    created = store.create(candidate(org="acme", position="other", parent="other"), system)
    assert created.org_id == "acme"
