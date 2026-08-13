import sys

from PySide6.QtWidgets import QApplication

from app.core.application import ALCOSApplication


def main():
    """
    Entry point of the ALCOS Operating System.
    """

    app = QApplication(sys.argv)

    application = ALCOSApplication(app)

    application.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
