"""Small local REST API used by the project when internet is unavailable."""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

STUDENTS = [
    {"student_id": 1001, "gpa": 3.45, "attendance": 92, "status": "Active"},
    {"student_id": 1002, "gpa": 3.80, "attendance": 88, "status": "Active"},
    {"student_id": 1003, "gpa": 2.90, "attendance": 78, "status": "Active"},
    {"student_id": 1004, "gpa": 3.20, "attendance": 70, "status": "Active"},
    {"student_id": 1005, "gpa": None, "attendance": 91, "status": "Active"},
    {"student_id": 1006, "gpa": 3.60, "attendance": None, "status": "Active"},
    {"student_id": 1007, "gpa": 4.20, "attendance": 96, "status": "Active"},
    {"student_id": 1008, "gpa": 2.50, "attendance": 80, "status": "Active"},
    {"student_id": 1009, "gpa": 1.80, "attendance": 60, "status": "Probation"},
    {"student_id": 1010, "gpa": 3.10, "attendance": 85, "status": "Active"},
    {"student_id": 1011, "gpa": 2.70, "attendance": 76, "status": "Active"},
]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/students":
            body = json.dumps(STUDENTS).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return


if __name__ == "__main__":
    print("Mock API running at http://127.0.0.1:8000/students")
    HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
