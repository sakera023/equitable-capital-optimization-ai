import json


NOTEBOOKS = [
    "examples/01_capital_readiness.ipynb",
    "examples/02_fairness_audit.ipynb",
    "examples/03_equitable_allocation.ipynb",
    "examples/04_public_us_data_context.ipynb",
]


def test_example_notebooks_are_valid_notebook_documents():
    assert len(NOTEBOOKS) >= 4

    for notebook_path in NOTEBOOKS:
        with open(notebook_path, encoding="utf-8") as notebook_file:
            payload = json.load(notebook_file)

        assert payload["nbformat"] == 4
        assert payload["cells"]
        assert any(cell.get("cell_type") == "markdown" for cell in payload["cells"])
        assert any(cell.get("cell_type") == "code" for cell in payload["cells"])
