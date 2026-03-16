from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from tomateclock.backend import TimerBackend


def main() -> int:
    app = QGuiApplication(sys.argv)
    app.setApplicationName("TomateClock RPG")

    backend = TimerBackend()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("timerBridge", backend)

    qml_path = Path(__file__).resolve().parent / "resources" / "qml" / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))

    if not engine.rootObjects():
        return 1
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
