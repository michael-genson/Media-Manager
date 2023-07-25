import logging
from pathlib import Path

import black
import isort
from jinja2 import Template

PROJECT_DIR = Path(__file__).parent.parent.parent
logger = logging.getLogger("rich")


def render_python_template(template_file: Path | str, dest: Path, data: dict):
    """Render and Format a Jinja2 Template for Python Code"""
    if isinstance(template_file, Path):
        tplt = Template(template_file.read_text())
    else:
        tplt = Template(template_file)

    text = tplt.render(data=data)

    text = black.format_str(text, mode=black.FileMode())

    dest.write_text(text)
    isort.file(dest)
