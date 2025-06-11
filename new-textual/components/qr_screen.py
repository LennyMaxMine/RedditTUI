from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, Button
from textual.screen import ModalScreen
from utils.logger import Logger
import qrcode
from rich.text import Text
from rich.panel import Panel
from rich import box

class QRScreen(ModalScreen):
    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.logger = Logger()

    def compose(self) -> ComposeResult:
        self.logger.info("Composing QRScreen UI")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=1,
            border=2,
        )
        qr.add_data(self.url)
        qr.make(fit=True)
        matrix = qr.get_matrix()
        # Render QR as Unicode blocks
        qr_lines = []
        for row in matrix:
            line = ''.join('█' if cell else ' ' for cell in row)
            qr_lines.append(line)
        qr_ascii = '\n'.join(qr_lines)
        yield Container(
            Vertical(
                Static(Panel(
                    Text(qr_ascii),
                    title="Scan QR Code",
                    border_style="blue",
                    box=box.ROUNDED
                )),
                Static(f"URL: {self.url}", classes="url"),
                Button("Close", id="close_button"),
                id="qr_form"
            ),
            id="qr_container"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.logger.info(f"Button pressed: {event.button.id}")
        if event.button.id == "close_button":
            self.dismiss() 