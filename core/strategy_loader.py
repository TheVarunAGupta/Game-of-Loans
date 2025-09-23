import sys
import importlib
import inspect
from pathlib import Path
import ast
import re
from strats.base_strategy import BaseStrategy

STRATEGY_DIR = Path(__file__).resolve().parent.parent / 'strats'
_strategy_cache = None

def discover_strategies(refresh=False):
    global _strategy_cache
    if _strategy_cache is not None and not refresh:
        return _strategy_cache
    
    strategies = {}
    if not STRATEGY_DIR.exists():
        print(f'[StrategyLoader] Strategy folder not found: {STRATEGY_DIR}')
        return strategies
    
    for file in STRATEGY_DIR.glob('*.py'):
        if file.name.startswith('__') or file.name == 'base_strategy.py':
            continue

        module_name = f'strats.{file.stem}'
        try:
            if module_name in sys.modules:
                module = importlib.reload(sys.modules[module_name])
            else:
                module = importlib.import_module(module_name)

            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseStrategy) and obj is not BaseStrategy:
                    try:
                        instance = obj()
                        strategies[instance.name] = obj
                    except:
                        strategies[obj.__name__] = obj

        except Exception as e:
                if 'No module named' not in str(e):
                    print(f'[StrategyLoader] Failed to load {file.name}: {e}')
    _strategy_cache = strategies
    return strategies

def get_strategy_file_path(name):
    cls = discover_strategies().get(name)
    if not cls:
        return None
    module = cls.__module__
    filename = f'{module.split(".")[-1]}.py'
    return STRATEGY_DIR / filename

def read_strategy_code(name):
    path = get_strategy_file_path(name)
    if path and path.exists():
        return path.read_text()
    return ''

def save_strategy_code(name, code):
    path = get_strategy_file_path(name)
    if not path:
        return False
    path.write_text(code)
    discover_strategies(refresh=True)
    return True

def delete_strategy_file(name):
    path = get_strategy_file_path(name)
    if path and path.exists():
        path.unlink()
        discover_strategies(refresh=True)
        return True
    return False

def add_strategy_file(name, code):
    if not name.endswith('.py'):
        name += '.py'
    path = STRATEGY_DIR / name
    if path.exists():
        return False
    path.write_text(code)
    discover_strategies(refresh=True)
    return True

def generate_strategy_filename(name):
    return f'{name.lower()}_code.py'

def get_strategy_name(code):
    # match = re.search(r'class\s+(\w+)\(BaseStrategy\):', code)
    # if match:
    #     return match.group(1)
    # return None
    match = re.search(r"super\(\)\.__init__\(\s*['\"]([^'\"]+)['\"]", code)
    if match:
        return match.group(1)
    return None

def validate_strategy_code(code, mode, original_name):
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f'Syntax error in code: {e}', None
    
    strategy_classes = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == 'BaseStrategy':
                    strategy_classes.append(node.name)
                elif isinstance(base, ast.Attribute) and base.attr == 'BaseStrategy':
                    strategy_classes.append(node.name)

    if not strategy_classes:
        return False, 'No subclass of BaseStrategy found.', None
    class_name = strategy_classes[0]
    existing = list(discover_strategies().keys())

    if mode == 'add':
        if class_name in existing:
            return False, f'Class name "{class_name}" already exists.', class_name

    elif mode == 'edit':
        # Only allow duplicates if it’s the same strategy being edited
        if class_name != original_name and class_name in existing:
            return False, f'Class name "{class_name}" already exists.', class_name

    else:
        return False, f'Invalid mode "{mode}". Must be "add" or "edit".', class_name

    return True, 'Valid strategy code.', class_name