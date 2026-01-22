"""
Integration test: reading SAV file from HTTP server.
Uses Python's built-in http.server - no external dependencies.

Run with: pytest tests/test_http_integration.py -v
"""
import io
import os
import threading
import urllib.request
from contextlib import contextmanager
from http.server import HTTPServer, SimpleHTTPRequestHandler

import pyreadstat


@contextmanager
def http_server(directory):
    """Context manager that runs an HTTP server serving files from directory."""
    class QuietHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
        def log_message(self, *args):
            pass
    
    server = HTTPServer(("127.0.0.1", 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()


def test_read_sav_from_http():
    """Test reading SAV file from local HTTP server (simulates remote URL)."""
    data_folder = os.path.join(os.path.dirname(__file__), "..", "test_data", "basic")
    
    with http_server(data_folder) as base_url:
        url = f"{base_url}/sample.sav"
        with urllib.request.urlopen(url) as response:
            df, meta = pyreadstat.read_sav(io.BytesIO(response.read()))
        
        assert len(df) == 5, f"Expected 5 rows, got {len(df)}"
        assert len(df.columns) == 7, f"Expected 7 columns, got {len(df.columns)}"
