from PySide6.QtCore import QTimer

class ClockSource:
    """Implements a global clock source for timing."""
    _clocks: dict[QTimer] = None

    @classmethod
    def get_clock(cls, name: str, period_ms: int | None) -> QTimer:
        """Get the clock with the specified name."""
        if cls._clocks is None:
            cls._clocks = {}

        if name not in cls._clocks:
            timer = QTimer()
            timer.start(period_ms)
            cls._clocks[name] = timer

        return cls._clocks[name]
