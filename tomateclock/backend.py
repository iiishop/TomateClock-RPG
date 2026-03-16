from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot


@dataclass(frozen=True)
class Milestone:
    seconds: int
    title: str


class TitleSystem:
    def __init__(self) -> None:
        self._milestones = [
            Milestone(0, "专注练习生"),
            Milestone(5 * 60, "专注者"),
            Milestone(10 * 60, "节奏掌握者"),
            Milestone(30 * 60, "深度专注者"),
            Milestone(60 * 60, "时间掌控者"),
        ]

    def title_for_seconds(self, total_seconds: int) -> str:
        chosen = self._milestones[0].title
        for milestone in self._milestones:
            if total_seconds >= milestone.seconds:
                chosen = milestone.title
            else:
                break
        return chosen


class TimerBackend(QObject):
    remainingSecondsChanged = Signal()
    isRunningChanged = Signal()
    totalFocusSecondsChanged = Signal()
    currentTitleChanged = Signal()
    titleUnlocked = Signal(str)

    def __init__(self, storage_path: Path | None = None) -> None:
        super().__init__()
        self._title_system = TitleSystem()
        self._remaining_seconds = 0
        self._session_total_seconds = 0
        self._is_running = False

        if storage_path is None:
            base_dir = Path(__file__).resolve().parent.parent
            self._storage_path = base_dir / "data" / "state.json"
        else:
            self._storage_path = storage_path

        self._persist_enabled = (
            storage_path is not None or self._storage_path is not None
        )
        self._total_focus_seconds = self._load_total_focus_seconds()
        self._current_title = self._title_system.title_for_seconds(
            self._total_focus_seconds
        )

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)

    @Property(int, notify=remainingSecondsChanged)
    def remaining_seconds(self) -> int:
        return self._remaining_seconds

    @Property(bool, notify=isRunningChanged)
    def is_running(self) -> bool:
        return self._is_running

    @Property(int, notify=totalFocusSecondsChanged)
    def total_focus_seconds(self) -> int:
        return self._total_focus_seconds

    @Property(str, notify=currentTitleChanged)
    def current_title(self) -> str:
        return self._current_title

    @Property(str, notify=remainingSecondsChanged)
    def remaining_display(self) -> str:
        minutes, seconds = divmod(self._remaining_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    @Property(str, notify=totalFocusSecondsChanged)
    def total_focus_display(self) -> str:
        minutes, seconds = divmod(self._total_focus_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        if hours > 0:
            return f"{hours}h {minutes:02d}m {seconds:02d}s"
        return f"{minutes:02d}m {seconds:02d}s"

    @Slot(int)
    def start_preset_minutes(self, minutes: int) -> None:
        safe_minutes = max(1, int(minutes))
        self._session_total_seconds = safe_minutes * 60
        self._set_remaining_seconds(self._session_total_seconds)
        self._set_is_running(True)
        self._timer.start()

    @Slot()
    def pause(self) -> None:
        if not self._is_running:
            return
        self._timer.stop()
        self._set_is_running(False)

    @Slot()
    def resume(self) -> None:
        if self._is_running or self._remaining_seconds <= 0:
            return
        self._timer.start()
        self._set_is_running(True)

    @Slot()
    def reset(self) -> None:
        self._timer.stop()
        self._set_is_running(False)
        self._session_total_seconds = 0
        self._set_remaining_seconds(0)

    def _on_tick(self) -> None:
        if self._remaining_seconds <= 0:
            self._finish_session()
            return

        self._set_remaining_seconds(self._remaining_seconds - 1)
        if self._remaining_seconds == 0:
            self._finish_session()

    def _finish_session(self) -> None:
        self._timer.stop()
        self._set_is_running(False)
        if self._session_total_seconds > 0:
            self._add_focus_seconds(self._session_total_seconds)
            self._session_total_seconds = 0

    def _set_remaining_seconds(self, value: int) -> None:
        if value == self._remaining_seconds:
            return
        self._remaining_seconds = value
        self.remainingSecondsChanged.emit()

    def _set_is_running(self, value: bool) -> None:
        if value == self._is_running:
            return
        self._is_running = value
        self.isRunningChanged.emit()

    def _add_focus_seconds(self, seconds: int) -> None:
        self._total_focus_seconds += seconds
        self.totalFocusSecondsChanged.emit()
        self._persist_total_focus_seconds()

        new_title = self._title_system.title_for_seconds(self._total_focus_seconds)
        if new_title != self._current_title:
            self._current_title = new_title
            self.currentTitleChanged.emit()
            self.titleUnlocked.emit(new_title)

    def _load_total_focus_seconds(self) -> int:
        try:
            if not self._storage_path.exists():
                return 0
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
            return max(0, int(payload.get("total_focus_seconds", 0)))
        except Exception:
            return 0

    def _persist_total_focus_seconds(self) -> None:
        if not self._persist_enabled:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"total_focus_seconds": self._total_focus_seconds}
        self._storage_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # Test helpers
    def _tick_for_test(self) -> None:
        self._on_tick()

    def add_focus_seconds_for_test(self, seconds: int) -> None:
        self._add_focus_seconds(max(0, int(seconds)))
