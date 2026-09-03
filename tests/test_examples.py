import json
from pathlib import Path


EXAMPLES_DIR = Path("examples")


def test_example_notebooks_are_valid_notebook_documents():
    notebooks = sorted(EXAMPLES_DIR.glob("*.ipynb"))

    assert len(notebooks) >= 4

    for notebook_path in notebooks:
        payload = json.loads(notebook_path.read_text(encoding="utf-8"))
        assert payload["nbformat"] == 4
        assert payload["cells"]
        assert any(cell.get("cell_type") == "markdown" for cell in payload["cells"])
        assert any(cell.get("cell_type") == "code" for cell in payload["cells"])
