import os
from flask import Blueprint

file_bp = Blueprint("file", __name__)


def create_api():
    @file_bp.route("/api/files", methods=["GET"])
    def list_files():
        path = os.path.join(os.path.expanduser("~"), "Documents")
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        return {"files": files[:10]}
