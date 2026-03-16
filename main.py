from __future__ import annotations

# /// script
# dependencies = [
#   "PySide6>=6.7",
# ]
# ///

import json
import sys
from pathlib import Path

from PySide6.QtCore import Property, QTimer, QObject, Signal, Slot, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


class PomodoroBridge(QObject):
    remainingSecondsChanged = Signal()
    formattedRemainingChanged = Signal()
    totalSecondsChanged = Signal()
    progressChanged = Signal()
    isRunningChanged = Signal()
    selectedPresetChanged = Signal()
    presetsChanged = Signal()
    totalFocusSecondsChanged = Signal()
    totalFocusTextChanged = Signal()
    currentTitleChanged = Signal()
    nextMilestoneTextChanged = Signal()
    titleUpgraded = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self._state_path = Path.home() / ".tomateclock_rpg_state.json"
        self._presets = [10, 15, 25]
        self._selected_preset = 25
        self._total_seconds = self._selected_preset * 60
        self._remaining_seconds = self._total_seconds
        self._is_running = False
        self._total_focus_seconds = 0
        self._last_title = "新手冒险者"
        self._title_tiers = [
            (300, "初阶专注者"),
            (600, "稳定专注者"),
            (1800, "深度专注者"),
            (3600, "专注大师"),
        ]

        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._on_tick)

        self._load_state()
        self._last_title = self._calculate_title()

    @Property(int, notify=remainingSecondsChanged)
    def remainingSeconds(self) -> int:
        return self._remaining_seconds

    @Property(str, notify=formattedRemainingChanged)
    def formattedRemaining(self) -> str:
        minutes = self._remaining_seconds // 60
        seconds = self._remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    @Property(int, notify=totalSecondsChanged)
    def totalSeconds(self) -> int:
        return self._total_seconds

    @Property(float, notify=progressChanged)
    def progress(self) -> float:
        if self._total_seconds <= 0:
            return 0.0
        return max(
            0.0,
            min(
                1.0,
                (self._total_seconds - self._remaining_seconds) / self._total_seconds,
            ),
        )

    @Property(bool, notify=isRunningChanged)
    def isRunning(self) -> bool:
        return self._is_running

    @Property(int, notify=selectedPresetChanged)
    def selectedPreset(self) -> int:
        return self._selected_preset

    @Property("QVariantList", notify=presetsChanged)
    def presets(self) -> list[int]:
        return self._presets

    @Property(int, notify=totalFocusSecondsChanged)
    def totalFocusSeconds(self) -> int:
        return self._total_focus_seconds

    @Property(str, notify=totalFocusTextChanged)
    def totalFocusText(self) -> str:
        return self._format_duration(self._total_focus_seconds)

    @Property(str, notify=currentTitleChanged)
    def currentTitle(self) -> str:
        return self._calculate_title()

    @Property(str, notify=nextMilestoneTextChanged)
    def nextMilestoneText(self) -> str:
        for threshold, title in self._title_tiers:
            if self._total_focus_seconds < threshold:
                remain = threshold - self._total_focus_seconds
                return f"距离 {title} 还差 {self._format_duration(remain)}"
        return "已达到最高称号，继续保持！"

    @Slot(int)
    def choosePreset(self, minutes: int) -> None:
        if self._is_running:
            return
        if minutes not in self._presets:
            return
        self._selected_preset = minutes
        self._total_seconds = minutes * 60
        self._remaining_seconds = self._total_seconds
        self.selectedPresetChanged.emit()
        self.totalSecondsChanged.emit()
        self._emit_timer_changes()

    @Slot()
    def toggleRun(self) -> None:
        if self._is_running:
            self._is_running = False
            self._timer.stop()
            self.isRunningChanged.emit()
            self._save_state()
            return

        if self._remaining_seconds <= 0:
            self._remaining_seconds = self._total_seconds
            self._emit_timer_changes()

        self._is_running = True
        self._timer.start()
        self.isRunningChanged.emit()

    @Slot()
    def resetSession(self) -> None:
        if self._timer.isActive():
            self._timer.stop()
        self._is_running = False
        self._remaining_seconds = self._total_seconds
        self.isRunningChanged.emit()
        self._emit_timer_changes()
        self._save_state()

    def _on_tick(self) -> None:
        if not self._is_running:
            return

        if self._remaining_seconds > 0:
            self._remaining_seconds -= 1
            self._total_focus_seconds += 1
            self._emit_timer_changes()
            self._emit_focus_changes()

            if self._remaining_seconds % 10 == 0:
                self._save_state()

            if self._remaining_seconds == 0:
                self._is_running = False
                self._timer.stop()
                self.isRunningChanged.emit()
                self._save_state()

    def _emit_timer_changes(self) -> None:
        self.remainingSecondsChanged.emit()
        self.formattedRemainingChanged.emit()
        self.progressChanged.emit()

    def _emit_focus_changes(self) -> None:
        self.totalFocusSecondsChanged.emit()
        self.totalFocusTextChanged.emit()
        new_title = self._calculate_title()
        if new_title != self._last_title:
            self._last_title = new_title
            self.currentTitleChanged.emit()
            self.titleUpgraded.emit(new_title)
        self.nextMilestoneTextChanged.emit()

    def _calculate_title(self) -> str:
        result = "新手冒险者"
        for threshold, title in self._title_tiers:
            if self._total_focus_seconds >= threshold:
                result = title
            else:
                break
        return result

    def _format_duration(self, seconds: int) -> str:
        seconds = max(0, seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours} 小时 {minutes} 分钟"
        if minutes > 0:
            return f"{minutes} 分钟 {secs} 秒"
        return f"{secs} 秒"

    def _load_state(self) -> None:
        if not self._state_path.exists():
            return
        try:
            raw = json.loads(self._state_path.read_text(encoding="utf-8"))
        except (OSError, ValueError, TypeError):
            return

        seconds = raw.get("total_focus_seconds")
        if isinstance(seconds, int) and seconds >= 0:
            self._total_focus_seconds = seconds
            self.totalFocusSecondsChanged.emit()
            self.totalFocusTextChanged.emit()
            self.currentTitleChanged.emit()
            self.nextMilestoneTextChanged.emit()

    def _save_state(self) -> None:
        payload = {"total_focus_seconds": self._total_focus_seconds}
        try:
            self._state_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError:
            pass


def main() -> int:
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    bridge = PomodoroBridge()
    engine.rootContext().setContextProperty("bridge", bridge)

    qml_path = Path(__file__).resolve().parent / "resources" / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))

    if not engine.rootObjects():
        return 1

    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
