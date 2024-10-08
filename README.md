# FH Münster iCal Proxy

This project provides a proxy server for modifying iCal (.ics) files from FH Münster. It cleans up event summaries and descriptions, making them more readable and user-friendly.

<img width="824" alt="image" src="https://github.com/user-attachments/assets/23cc95df-3fe5-469f-8e1b-e9e4fd241936">
<img width="824" alt="image" src="https://github.com/user-attachments/assets/4e01faad-5a2e-4040-ac0d-1f8d13ff8afb">

## Features

- Fetches an original iCal file from a specified URL
- Modifies event summaries and descriptions:
  - Removes prefixes from summaries (e.g., "ETI.1.0230.0.V.4")
  - Adds "Tutorium" to the summary for specific events
  - Cleans up HTML tags and formatting in descriptions
- Serves the modified iCal file via HTTP

## Prerequisites

- Docker

## Configuration

Copy and rename the `.env.example` file to `.env`. Modify the `ORIGINAL_ICS_URL` variable to point to the original iCal file URL.

## Usage

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/fh-muenster-ical-proxy.git
   cd fh-muenster-ical-proxy
   ```

2. Build and run the Docker container:
   ```
   docker-compose up -d
   ```

3. Access the modified iCal file at:
   ```
   http://localhost:<PORT>/calendar.ics
   ```

## Local Development

If you want to run the project locally without Docker:

1. Install the required Python packages:
    ```
    python -m venv .venv

    # On Windows
    .venv\Scripts\activate

    # On macOS/Linux
    source .venv/bin/activate

    pip install -r requirements.txt
    ```

2. Run the server:
   ```
   python main.py
   ```


## Contributing

If you have any ideas to futher improve the calendar, feel free to open an issue or submit a pull request.
