import logging
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)

MODULE_TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
INSTANCE_TEMPLATE_DIR = Path("templates")

def load_template(template_name):
    """
    Retrieve the content of a template file.
    First, it checks the instance template directory, then the module template directory.
    """
    instance_template_path = INSTANCE_TEMPLATE_DIR / template_name
    if not instance_template_path.exists():
        logger.warning(f"Template {template_name} not found in instance directory, copying from module directory to {instance_template_path}")
        module_template_path = MODULE_TEMPLATE_DIR / template_name
        try:
            INSTANCE_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy(module_template_path, instance_template_path)
            return load_template(template_name)
        except Exception as e:
            logger.error(f"Failed to copy template {template_name} from module to instance directory: {e}")
    return instance_template_path.read_text()

SVG_STYLE_FN = "svg_styles.css"
def load_svg_style():
    return load_template(SVG_STYLE_FN)