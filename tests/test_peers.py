import pytest

from opendevmate.service import DomainError, Store


def _ready(store, task_id):
    store.transition(task_id, "ready")
    store.transition(task_id, "running")


def test_contract_blocks_out_of_scope_and_failed_tests():
    store = Store(":memory:")
    project = store.create_project("demo", "管理一个示例仓库")
    task = store.create_task(project["id"], "改扫描", "只改 src")
    with pytest.raises(DomainError):
        store.set_contract(task["id"], [], ["src"])
    with pytest.raises(DomainError):
        store.set_contract(task["id"], ["pytest 通过"], ["../secret"])
    store.set_contract(task["id"], ["pytest 通过"], ["src"])
    _ready(store, task["id"])
    store.add_diff(task["id"], "越界", ["README.md"])
    store.add_test_run(task["id"], 1, 0, "通过")
    store.transition(task["id"], "review")
    with pytest.raises(DomainError):
        store.add_review(task["id"], "范围看起来没问题", "low", True)

    other = store.create_task(project["id"], "补测试", "只改 src")
    store.set_contract(other["id"], ["pytest 通过"], ["src"])
    _ready(store, other["id"])
    store.add_diff(other["id"], "范围内", ["src/app.py"])
    store.add_test_run(other["id"], 1, 1, "还有失败")
    store.transition(other["id"], "review")
    with pytest.raises(DomainError):
        store.add_review(other["id"], "测试还没绿", "low", True)

    third = store.create_task(project["id"], "收尾", "只改 src")
    store.set_contract(third["id"], ["pytest 通过"], ["src"])
    _ready(store, third["id"])
    recorded = store.add_execution(third["id"], "recorded", "完成")
    assert "pytest 通过" in recorded["instruction"]
    assert "src" in recorded["instruction"]
    store.add_diff(third["id"], "范围内", ["src/app.py"])
    store.add_test_run(third["id"], 2, 0, "通过")
    store.transition(third["id"], "review")
    store.add_review(third["id"], "范围和测试都符合约定", "low", True)
    assert store.get_task(third["id"])["status"] == "accepted"
