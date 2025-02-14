import types
import sys



def var_dump(var, do_print=True, depth=0, max_depth=5):
    def dump(var, depth):
        indent = '  ' * depth
        var_type = type(var)
        result = ""

        # Basic types
        if isinstance(var, (int, float, str, bool, type(None))):
            result += f"{indent}{var_type.__name__}({repr(var)})\n"
        
        # Lists, Tuples, Sets
        elif isinstance(var, (list, tuple, set)):
            result += f"{indent}{var_type.__name__} (size={len(var)}) [\n"
            if depth < max_depth:
                for item in var:
                    result += dump(item, depth + 1)
            else:
                result += f"{indent}  ...\n"
            result += f"{indent}]\n"
        
        # Dictionaries
        elif isinstance(var, dict):
            result += f"{indent}{var_type.__name__} (size={len(var)}) {{\n"
            if depth < max_depth:
                for key, value in var.items():
                    result += f"{indent}  Key: {repr(key)} =>\n"
                    result += dump(value, depth + 1)
            else:
                result += f"{indent}  ...\n"
            result += f"{indent}}}\n"

        # Functions, Modules, Classes
        elif isinstance(var, (types.FunctionType, types.ModuleType, type)):
            name = getattr(var, '__name__', repr(var))
            result += f"{indent}{var_type.__name__}: {name}\n"

        # Objects
        elif hasattr(var, '__dict__'):
            result += f"{indent}{var_type.__name__} Object {{\n"
            if depth < max_depth:
                for attr, value in vars(var).items():
                    result += f"{indent}  {attr} =>\n"
                    result += dump(value, depth + 1)
            else:
                result += f"{indent}  ...\n"
            result += f"{indent}}}\n"

        # Fallback for unknown types
        else:
            result += f"{indent}{var_type.__name__}({repr(var)})\n"

        return result

    if (do_print):
        print(dump(var, depth))
    return dump(var, depth)



def dd(var):
    var_dump(var)
    sys.exit()

