from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
)

from app.core.context import get_context
from app.core.lc_workflow import stage_label


class TransactionHeader(QWidget):
    """
    Header for individual trade transaction.

    Displays the LC currently open in the shared application context.
    Updates live via context signals; shows a neutral placeholder when
    no LC is open.
    """

    def __init__(self):

        super().__init__()

        self.setObjectName(
            "transactionHeader"
        )

        self.context = get_context()

        self.build_ui()

        self.context.currentLCChanged.connect(
            self._on_lc_changed
        )

        self.context.currentLCCleared.connect(
            self._on_lc_cleared
        )

        self.context.lcMetadataChanged.connect(
            self._refresh_from_metadata
        )

        # Synchronize with any LC opened before this header existed.
        if self.context.has_lc:
            self._on_lc_changed(
                self.context.current_lc_id,
                self.context.current_lc_number,
            )

    def build_ui(self):

        self.setFixedHeight(70)

        layout = QHBoxLayout(self)

        layout.setContentsMargins(
            20,
            10,
            20,
            10
        )


        title = QLabel(
            "ALCOS Trade Transaction"
        )

        title.setObjectName(
            "headerTitle"
        )


        self.status = QLabel(
            "No LC open"
        )

        self.status.setObjectName(
            "statusLabel"
        )


        layout.addWidget(title)

        layout.addStretch()

        layout.addWidget(self.status)

    #################################################################
    # Context synchronization
    #################################################################

    def _on_lc_changed(self, lc_id: int, lc_number: str):
        """Reflect the newly opened LC and its workflow position."""
        metadata = self.context.lc_metadata

        parts = [f"LC: {lc_number}"]

        current_stage = metadata.get("current_stage")

        if current_stage is not None:
            try:
                parts.append(
                    f"Stage {int(current_stage)} — "
                    f"{stage_label(current_stage)}"
                )
            except (ValueError, KeyError):
                parts.append(f"Stage {current_stage}")

        stage_status = metadata.get("stage_status")

        if stage_status:
            parts.append(str(stage_status))

        overall_status = metadata.get("overall_status")

        if overall_status:
            parts.append(str(overall_status))

        self.status.setText(" | ".join(parts))

    def _refresh_from_metadata(self):
        """Re-render after metadata refresh (e.g., stage transition)."""
        if self.context.has_lc:
            self._on_lc_changed(
                self.context.current_lc_id,
                self.context.current_lc_number,
            )

    def _on_lc_cleared(self):
        """Return to the neutral no-LC state."""
        self.status.setText("No LC open")
