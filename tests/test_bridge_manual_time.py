from pathlib import Path

import main


def test_set_custom_time_updates_timer_values(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(main.Path, "home", lambda: tmp_path)
    bridge = main.PomodoroBridge()

    bridge.setCustomTime(1, 2, 3)

    assert bridge.totalSeconds == 3723
    assert bridge.remainingSeconds == 3723
    assert bridge.manualHours == 1
    assert bridge.manualMinutes == 2
    assert bridge.manualSeconds == 3
    assert bridge.formattedRemaining == "1:02:03"
    assert bridge.selectedPreset == 0


def test_set_custom_time_clamps_to_at_least_one_second(
    monkeypatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(main.Path, "home", lambda: tmp_path)
    bridge = main.PomodoroBridge()

    bridge.setCustomTime(0, 0, 0)

    assert bridge.totalSeconds == 1
    assert bridge.remainingSeconds == 1
    assert bridge.formattedRemaining == "00:01"


def test_set_custom_time_ignored_while_running(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(main.Path, "home", lambda: tmp_path)
    bridge = main.PomodoroBridge()

    bridge.choosePreset(10)
    bridge.toggleRun()

    bridge.setCustomTime(0, 2, 0)

    assert bridge.isRunning is True
    assert bridge.totalSeconds == 600
    assert bridge.remainingSeconds == 600
