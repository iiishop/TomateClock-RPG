import json
from pathlib import Path

from tomateclock.backend import TitleSystem, TimerBackend


def test_title_milestones_are_mapped_correctly() -> None:
    title_system = TitleSystem()

    assert title_system.title_for_seconds(0) == "专注练习生"
    assert title_system.title_for_seconds(300) == "专注者"
    assert title_system.title_for_seconds(600) == "节奏掌握者"
    assert title_system.title_for_seconds(1800) == "深度专注者"
    assert title_system.title_for_seconds(3600) == "时间掌控者"


def test_persistence_survives_restart(tmp_path: Path) -> None:
    storage_file = tmp_path / "state.json"
    first = TimerBackend(storage_path=storage_file)

    first.add_focus_seconds_for_test(900)

    second = TimerBackend(storage_path=storage_file)
    assert second.total_focus_seconds == 900
    assert second.current_title == "节奏掌握者"

    data = json.loads(storage_file.read_text(encoding="utf-8"))
    assert data["total_focus_seconds"] == 900


def test_countdown_and_complete_updates_total(tmp_path: Path) -> None:
    backend = TimerBackend(storage_path=tmp_path / "state.json")
    backend.start_preset_minutes(10)

    assert backend.remaining_seconds == 600
    assert backend.is_running is True

    for _ in range(600):
        backend._tick_for_test()

    assert backend.remaining_seconds == 0
    assert backend.is_running is False
    assert backend.total_focus_seconds == 600
