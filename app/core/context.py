"""
ALCOS Application Context
=========================

Frontend-only application state shared across the UI layer:

- the authenticated operator (username / role)
- the current Letter of Credit under work (lc_id / lc_number)

The context is intentionally NOT a business-logic object. Services never
import this module; widgets read the context and pass explicit
``lc_id`` / ``performed_by`` values into services. This keeps the service
layer reusable unchanged behind a future server/API boundary.

Thread note: the context is GUI-thread state. Qt signals emitted here are
delivered to connected slots in the GUI thread.
"""

from __future__ import annotations

from typing import Any, Optional

from PySide6.QtCore import QObject, Signal


class ApplicationContext(QObject):
    """
    Shared application/frontend state for ALCOS.

    Signals:
        userChanged: Emitted with (username, role) after authentication.
        userCleared: Emitted when the authenticated session is dropped.
        currentLCChanged: Emitted with (lc_id, lc_number) when an LC is opened.
        currentLCCleared: Emitted when the current LC context is released.
        lcMetadataChanged: Emitted when display metadata of the open LC
            was refreshed (e.g., after a workflow transition).
    """

    userChanged = Signal(str, str)
    userCleared = Signal()
    currentLCChanged = Signal(int, str)
    currentLCCleared = Signal()
    lcMetadataChanged = Signal()

    def __init__(self) -> None:
        super().__init__()

        self._username: Optional[str] = None
        self._role: Optional[str] = None

        self._lc_id: Optional[int] = None
        self._lc_number: Optional[str] = None
        self._lc_metadata: dict[str, Any] = {}

    #################################################################
    # Authenticated operator
    #################################################################

    @property
    def current_user(self) -> Optional[str]:
        """Authenticated username, or ``None`` when unauthenticated."""
        return self._username

    @property
    def current_role(self) -> Optional[str]:
        """Authenticated role, or ``None`` when unauthenticated."""
        return self._role

    @property
    def has_user(self) -> bool:
        """Whether an authenticated operator is present."""
        return self._username is not None

    def set_user(self, username: str, role: str) -> None:
        """
        Record the authenticated operator.

        Args:
            username: Authenticated username (never a password).
            role: Authenticated role string.
        """
        clean_name = str(username or "").strip()
        clean_role = str(role or "").strip()

        if not clean_name:
            raise ValueError("Username must not be empty.")

        self._username = clean_name
        self._role = clean_role or "USER"

        self.userChanged.emit(self._username, self._role)

    def clear_user(self) -> None:
        """Drop the authenticated session (e.g., on logout)."""
        if self._username is None and self._role is None:
            return

        self._username = None
        self._role = None

        self.userCleared.emit()

    #################################################################
    # Current Letter of Credit
    #################################################################

    @property
    def current_lc_id(self) -> Optional[int]:
        """Canonical LC identity (letters_of_credit.id), or ``None``."""
        return self._lc_id

    @property
    def current_lc_number(self) -> Optional[str]:
        """Business reference of the current LC, or ``None``."""
        return self._lc_number

    @property
    def lc_metadata(self) -> dict[str, Any]:
        """Read-only view of cached LC metadata (applicant, stage, ...)."""
        return dict(self._lc_metadata)

    @property
    def has_lc(self) -> bool:
        """Whether an LC is currently open in the context."""
        return self._lc_id is not None

    def set_current_lc(
        self,
        lc_id: int,
        lc_number: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Open an LC in the application context.

        Args:
            lc_id: Canonical database identity (letters_of_credit.id).
            lc_number: Business reference shown in the UI.
            metadata: Optional display snapshot (applicant, stage, ...).

        Raises:
            ValueError: If lc_id is not a positive integer or the
                LC number is empty.
        """
        try:
            clean_id = int(lc_id)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid lc_id: {lc_id!r}") from exc

        if clean_id <= 0:
            raise ValueError(f"Invalid lc_id: {lc_id!r}")

        clean_number = str(lc_number or "").strip()

        if not clean_number:
            raise ValueError("LC number must not be empty.")

        changed = (
            self._lc_id != clean_id
            or self._lc_number != clean_number
        )

        self._lc_id = clean_id
        self._lc_number = clean_number
        self._lc_metadata = dict(metadata or {})

        if changed:
            self.currentLCChanged.emit(clean_id, clean_number)

    def update_lc_metadata(self, metadata: dict[str, Any]) -> None:
        """Merge display metadata for the current LC and notify observers."""
        if not self.has_lc:
            return
        self._lc_metadata.update(metadata or {})
        self.lcMetadataChanged.emit()

    def clear_current_lc(self) -> None:
        """Release the current LC context (no LC open)."""
        if not self.has_lc and not self._lc_metadata:
            return

        self._lc_id = None
        self._lc_number = None
        self._lc_metadata = {}

        self.currentLCCleared.emit()


_context: Optional[ApplicationContext] = None


def get_context() -> ApplicationContext:
    """
    Return the shared ApplicationContext instance.

    A module-level singleton is intentional here: it represents the one
    interactive desktop session. Services must never call this; only the
    UI layer may depend on it.
    """
    global _context
    if _context is None:
        _context = ApplicationContext()
    return _context
