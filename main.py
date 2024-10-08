import http.server
import socketserver
import urllib.request
import re
from icalendar import Calendar
from dotenv import load_dotenv
import os


load_dotenv()
# URL of the original .ics file
ORIGINAL_ICS_URL = os.getenv("ORIGINAL_ICS_URL")
PORT = int(os.getenv("PORT"))


def modify_ics(ics_content):
    calendar = Calendar.from_ical(ics_content)

    for component in calendar.walk():
        if component.name == "VEVENT":
            summary = component.get("summary")
            description = component.get("description", "")

            # Clean up the SUMMARY (get rid of the prefix)
            # ETI.1.0230.0.V.4 Einführung in die Informatik > Einführung in die Informatik
            pattern = r"^(?:ETI\.\d+\.\d+\.\d+\.V\.\d+\s+)?(.+)$"
            match = re.match(pattern, component.get("summary"))
            if match:
                summary = match.group(1)

            if (
                "Einführung in die Informatik" in summary
                and "Freies Tutorium" in description
            ):
                # Clean up description
                # remove html tags from description
                description = re.sub(r"<[^>]*>", "", description)
                description = description.replace("&nbsp;", "")
                description = description.replace("l", "I")
                component["description"] = description

                # Add 'Tutorium' to SUMMARY
                summary = f"{summary} Tutorium"
            component["summary"] = summary
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
            except Exception as e:
                self.send_error(500, str(e))
        else:
            self.send_error(404, "File not found")


def run_server():
    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        print(f"Serving iCal under http://localhost:{PORT}/calendar.ics")
        httpd.serve_forever()


if __name__ == "__main__":
    run_server()
