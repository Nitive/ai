import json
from pathlib import Path
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

daemon = "http://127.0.0.1:7456"
projects_dir = Path("open-design/projects")
if not projects_dir.exists():
    sys.exit(0)

projects = sorted(path.name for path in projects_dir.iterdir() if path.is_dir() and not path.name.startswith("."))


def wait_for_daemon(url=daemon, timeout=30):
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            with urlopen(f"{url}/api/health", timeout=2) as response:
                if response.status == 200:
                    return
        except URLError, HTTPError, TimeoutError:
            pass

        time.sleep(0.5)

    raise TimeoutError(f"Open Design daemon not healthy after {timeout}s")


wait_for_daemon()

for project in projects:
    folder = projects_dir.joinpath(project).resolve()
    payload = json.dumps(
        {
            "baseDir": folder.as_posix(),
            "name": project,
        }
    ).encode()

    request = Request(
        f"{daemon}/api/import/folder",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request) as response:
        imported_project = json.load(response)["project"]

    print(imported_project["id"])
