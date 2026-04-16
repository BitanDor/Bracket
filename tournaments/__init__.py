import pkgutil
import importlib

def load_all_configs():
    """סורק את התיקייה וטוען את כל הקונפיגורציות באופן דינמי"""
    configs = {}
    # עובר על כל המודולים בתיקייה הנוכחית
    for loader, module_name, is_pkg in pkgutil.iter_modules(__path__):
        if module_name == "__init__":
            continue
        # ייבוא המודול
        module = importlib.import_module(f".{module_name}", package=__name__)
        # אם יש לו ID, נוסיף אותו למילון
        if hasattr(module, "ID"):
            configs[module.ID] = module
    return configs