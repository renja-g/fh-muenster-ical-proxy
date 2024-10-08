import http.server
import socketserver
import urllib.request
import re
from icalendar import Calendar, Event
from dotenv import load_dotenv
import os
import logging
from typing import Callable

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

load_dotenv()

# Constants
ORIGINAL_ICS_URL = os.getenv("ORIGINAL_ICS_URL")
if not ORIGINAL_ICS_URL:
    raise ValueError("ORIGINAL_ICS_URL environment variable is not set")

PORT = int(os.getenv("PORT", "8000"))


def clean_description(description: str) -> str:
    """Remove HTML tags and replace specific characters in the description."""
    description = re.sub(r"<[^>]*>", "", description)
    description = description.replace("&nbsp;", "")
    description = description.replace("l", "I")
    return description


def patch_clean_summary(component: Event) -> None:
    """Clean up the SUMMARY (get rid of the prefix)."""
    summary = component.get("summary", "")
    pattern = r"^(?:ETI\.\d+\.\d+\.\d+\.V\.\d+\s+)?(.+)$"
    match = re.match(pattern, summary)
    if match:
        component["summary"] = match.group(1)


def patch_informatik_tutorium(component: Event) -> None:
    """Patch for 'Einführung in die Informatik' tutorial."""
    summary = component.get("summary", "")
    description = component.get("description", "")

    if "Einführung in die Informatik" in summary and "Freies Tutorium" in description:
        component["description"] = clean_description(description)
        component["summary"] = f"{summary} Tutorium"


# List of patch functions to apply
PATCHES: list[Callable[[Event], None]] = [
    patch_clean_summary,
    patch_informatik_tutorium,
]


def modify_ics(ics_content: bytes) -> bytes:
    """Modify the entire iCal content."""
    calendar = Calendar.from_ical(ics_content)

    for component in calendar.walk():
        if isinstance(component, Event):
            for patch in PATCHES:
                patch(component)

    return calendar.to_ical()


class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/calendar.ics":
            try:
                with urllib.request.urlopen(ORIGINAL_ICS_URL) as response:
                    ics_content = response.read()

                modified_ics = modify_ics(ics_content)

                self.send_response(200)
                self.send_header("Content-Type", "text/calendar")
                self.end_headers()
                self.wfile.write(modified_ics)
                logging.info("Successfully served modified iCal")
            except urllib.error.URLError as e:
                logging.error(f"Error fetching original iCal: {e}")
                self.send_error(502, f"Error fetching original iCal: {e}")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                self.send_error(500, f"Internal server error: {e}")
        else:
            self.send_error(404, "File not found")


def run_server():
    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        logging.info(f"Serving iCal under http://localhost:{PORT}/calendar.ics")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logging.info("Server stopped by user")
        finally:
            httpd.server_close()


if __name__ == "__main__":
    run_server()
