"""Deletion must be atomic across hierarchy, references, and reaction delivery.

A small SQLite adapter executes ObjectStore's SQL helpers with real transactions;
only PostgreSQL placeholders/JSON operators and the connection factory are adapted.
"""

from copy import deepcopy
from pathlib import Path
from queue import Queue
import sqlite3
import sys
import types
import os
import uuid

import pytest

CHAPTER = Path(__file__).resolve().parents[1] / "chapter5/permission-embedded-data-objects"
sys.path.insert(0, str(CHAPTER))
import psycopg2
from pedo.core.store import ObjectStore, PermissionDeniedError, ReferentialIntegrityError
from pedo.core.models import (
    AccessContext, DataObject, ObjectType, Operation, PermissionRule,
    PrivilegeType, ReactionDeclaration, Relationship, RelationshipAction,
)


class Cursor:
    def __init__(self, connection, dictionaries=False):
        self.connection = connection
        self.cursor = connection.raw.cursor()
        self.dictionaries = dictionaries

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.cursor.close()

    def execute(self, sql, params=()):
        if sql.strip().startswith("DELETE FROM objects WHERE") and params[0] == self.connection.db.fail_delete:
            raise RuntimeError("injected delete failure")
        sql = sql.replace("content->>%s", "json_extract(content, '$.' || ?)")
        sql = sql.replace("refs->>%s", "json_extract(refs, '$.' || ?)").replace("%s", "?")
        self.cursor.execute(sql, params)

    def fetchone(self):
        row = self.cursor.fetchone()
        return dict(row) if self.dictionaries and row is not None else row

    def fetchall(self):
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows] if self.dictionaries else rows


class Connection:
    def __init__(self, db):
        self.db = db
        self.raw = sqlite3.connect(db.path)
        self.raw.row_factory = sqlite3.Row

    def __enter__(self):
        return self

    def __exit__(self, kind, value, traceback):
        try:
            if kind is None:
                self.commit()
            else:
                self.rollback()
        finally:
            self.close()

    def cursor(self, cursor_factory=None):
        return Cursor(self, dictionaries=cursor_factory is not None)

    def commit(self):
        if self.db.fail_commit:
            self.rollback()
            raise RuntimeError("injected commit failure")
        self.raw.commit()
        self.db.events.append("commit")

    def rollback(self):
        self.raw.rollback()
        self.db.events.append("rollback")

    def close(self):
        self.raw.close()


@pytest.fixture
def store(tmp_path, monkeypatch):
    db = types.SimpleNamespace(path=tmp_path / "objects.db", events=[], fail_delete=None, fail_commit=False)
    with sqlite3.connect(db.path) as conn:
        conn.execute("""CREATE TABLE objects (
            id TEXT PRIMARY KEY, type_name TEXT, content TEXT, owner_id TEXT,
            org_id TEXT, parent_id TEXT, permission_rules TEXT,
            created_at REAL, updated_at REAL, refs TEXT)""")
    monkeypatch.setattr(ObjectStore, "_setup_db", lambda self: None)
    monkeypatch.setattr(ObjectStore, "_get_conn", lambda self: Connection(db))
    result = ObjectStore("unused")
    result.test_db = db
    rules = [PermissionRule(Operation.ACCEPT, p) for p in PrivilegeType]
    for name in ("parent", "child"):
        result.register_type(ObjectType(name, {}, permission_rules=deepcopy(rules),
            reactions=[ReactionDeclaration("after_delete", "observe")]))
    result.register_type(ObjectType("nullable", {}, permission_rules=deepcopy(rules), relationships=[
        Relationship("target", "parent", RelationshipAction.NULLIFY)]))
    result.register_type(ObjectType("blocker", {}, permission_rules=deepcopy(rules), relationships=[
        Relationship("target", "parent", RelationshipAction.RESTRICT)]))
    return result


def seed(store, *objects):
    for obj in objects:
        store._store_object(obj)
    store.test_db.events.clear()


def state(store):
    with sqlite3.connect(store.test_db.path) as conn:
        return conn.execute("SELECT * FROM objects ORDER BY id").fetchall()


USER = AccessContext("owner")


@pytest.mark.parametrize("failure", ["root_restrict", "later_child_restrict", "later_child_permission", "parent_write", "commit"])
def test_failed_delete_preserves_entire_graph_and_queues_nothing(store, failure):
    objects = [DataObject(id="p", type_name="parent"),
               DataObject(id="a", type_name="child", parent_id="p"),
               DataObject(id="b", type_name="child", parent_id="p"),
               DataObject(id="n", type_name="nullable", content={"target_id": "p"}, references={"target": "p"})]
    expected = RuntimeError
    if failure in ("root_restrict", "later_child_restrict"):
        expected = ReferentialIntegrityError
        target = "p" if failure == "root_restrict" else "b"
        if target == "b":
            store.types["blocker"].relationships[0].target_type = "child"
        objects.append(DataObject(id="r", type_name="blocker", content={"target_id": target}))
    elif failure == "later_child_permission":
        expected = PermissionDeniedError
        store.types["parent"].permission_rules = [r for r in store.types["parent"].permission_rules if r.privilege != PrivilegeType.UPDATE]
        objects[2].permission_rules = [PermissionRule(Operation.DENY, PrivilegeType.WRITE)]
    elif failure == "parent_write":
        store.test_db.fail_delete = "p"
    seed(store, *objects)
    before = state(store)
    if failure == "commit":
        store.test_db.fail_commit = True
    with pytest.raises(expected):
        store.delete("p", USER)
    assert state(store) == before
    assert store._reaction_queue.empty()
    assert "rollback" in store.test_db.events
    assert "commit" not in store.test_db.events


class ObservedQueue(Queue):
    def __init__(self, store):
        super().__init__()
        self.store = store
        self.snapshots = []

    def put(self, item, *args, **kwargs):
        assert self.store.test_db.events[-1] == "commit"
        self.snapshots.append(state(self.store))
        super().put(item, *args, **kwargs)


def test_success_commits_once_then_publishes_all_delete_reactions(store):
    store.register_type(ObjectType("cascade", {}, default_policy=Operation.ACCEPT,
        relationships=[Relationship("target", "parent", RelationshipAction.CASCADE)],
        reactions=[ReactionDeclaration("after_delete", "observe")]))
    seed(store, DataObject(id="p", type_name="parent"),
         DataObject(id="a", type_name="child", parent_id="p"),
         DataObject(id="c", type_name="cascade", content={"target_id": "p"}),
         DataObject(id="n", type_name="nullable", content={"target_id": "p"}, references={"target": "p"}))
    queue = ObservedQueue(store)
    store._reaction_queue = queue
    assert store.delete("p", USER, _reaction_depth=1) is True
    after = state(store)
    assert [row[0] for row in after] == ["n"]
    assert store.test_db.events == ["commit"]
    assert queue.qsize() == 3
    assert queue.snapshots == [after, after, after]
    queued = [queue.get_nowait() for _ in range(3)]
    assert {item["object_id"] for item in queued} == {"a", "c", "p"}
    assert all(item["depth"] == 2 for item in queued)
    nullable = store.raw_read("n")
    assert nullable.content["target_id"] is None
    assert "target" not in nullable.references


def test_missing_object_rolls_back_and_next_delete_can_succeed(store):
    seed(store, DataObject(id="p", type_name="parent"))
    with pytest.raises(ValueError, match="not found"):
        store.delete("missing", USER)
    assert store.delete("p", USER)
    assert state(store) == []
    assert store.test_db.events == ["rollback", "commit"]


def test_standalone_create_and_update_still_commit_and_queue_reactions(store):
    store.types["parent"].reactions = [ReactionDeclaration("after_create", "observe"), ReactionDeclaration("after_update", "observe")]
    store.create(DataObject(id="p", type_name="parent", content={"value": 1}), USER)
    store.update("p", {"value": 2}, USER)
    assert store.raw_read("p").content == {"value": 2}
    assert store._reaction_queue.qsize() == 2

@pytest.mark.skipif(not os.environ.get("PEDO_TEST_DSN"), reason="set PEDO_TEST_DSN to exercise PostgreSQL")
@pytest.mark.parametrize("failure", ["root_restrict", "later_child_restrict", "parent_sql_error"])
def test_postgres_cascade_rolls_back_then_success_publishes_committed_state(failure):
    """Exercise PostgreSQL JSONB, aborted transactions, and post-commit visibility."""
    schema = "pedo_atomic_" + uuid.uuid4().hex
    admin = psycopg2.connect(os.environ["PEDO_TEST_DSN"])
    admin.autocommit = True
    with admin.cursor() as cursor:
        cursor.execute(f'CREATE SCHEMA "{schema}"')
    try:
        params = psycopg2.extensions.parse_dsn(os.environ["PEDO_TEST_DSN"])
        params["options"] = "-csearch_path=" + schema
        store = ObjectStore(psycopg2.extensions.make_dsn(**params))
        rules = [PermissionRule(Operation.ACCEPT, p) for p in PrivilegeType]
        for name in ("parent", "child"):
            store.register_type(ObjectType(name, {}, permission_rules=deepcopy(rules),
                reactions=[ReactionDeclaration("after_delete", "observe")]))
        store.register_type(ObjectType("nullable", {}, permission_rules=deepcopy(rules),
            relationships=[Relationship("target", "parent", RelationshipAction.NULLIFY)]))
        target = "child" if failure == "later_child_restrict" else "parent"
        store.register_type(ObjectType("blocker", {}, permission_rules=deepcopy(rules),
            relationships=[Relationship("target", target, RelationshipAction.RESTRICT)]))
        for obj in [DataObject(id="p", type_name="parent"),
                    DataObject(id="a", type_name="child", parent_id="p"),
                    DataObject(id="b", type_name="child", parent_id="p"),
                    DataObject(id="n", type_name="nullable", content={"target_id": "p"}, references={"target": "p"})]:
            store._store_object(obj)
        if failure == "parent_sql_error":
            with store._get_conn() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""CREATE FUNCTION reject_parent() RETURNS trigger LANGUAGE plpgsql AS $$
                        BEGIN IF OLD.id = 'p' THEN RAISE EXCEPTION 'injected parent delete failure'; END IF;
                        RETURN OLD; END $$;
                        CREATE TRIGGER reject_parent BEFORE DELETE ON objects
                        FOR EACH ROW EXECUTE FUNCTION reject_parent();""")
            expected = psycopg2.Error
        else:
            store._store_object(DataObject(id="r", type_name="blocker", content={"target_id": "b" if target == "child" else "p"}))
            expected = ReferentialIntegrityError
        before = {obj.id: obj for name in store.types for obj in store.raw_query(name)}
        with pytest.raises(expected):
            store.delete("p", USER)
        assert {obj.id: obj for name in store.types for obj in store.raw_query(name)} == before
        assert store._reaction_queue.empty()
        if failure == "parent_sql_error":
            with store._get_conn() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("DROP TRIGGER reject_parent ON objects")
        else:
            store.delete("r", USER)

        class CommittedQueue(Queue):
            def put(self, item, *args, **kwargs):
                # raw_read opens an independent PostgreSQL connection here.
                assert store.raw_read("p") is None
                assert store.raw_read("a") is None
                assert store.raw_read("b") is None
                assert store.raw_read("n").content["target_id"] is None
                super().put(item, *args, **kwargs)

        store._reaction_queue = CommittedQueue()
        assert store.delete("p", USER)
        assert store._reaction_queue.qsize() == 3
    finally:
        with admin.cursor() as cursor:
            cursor.execute(f'DROP SCHEMA "{schema}" CASCADE')
        admin.close()
