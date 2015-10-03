import ast
import os
from collections import deque
import sys
from stdlib_list import stdlib_list

conf = {
    'ignore_relative_imports': True,
    'ignore_builtin_modules': True,
    'pyver': None,
}


def get_imported_libs(code):
    tree = ast.parse(code)
    imports = deque()
    for t in tree.body:
        # ast.Import represents lines like 'import foo' and 'import foo, bar'
        # the extra for name in t.names is needed, because names is a list that
        # would be ['foo'] for the first and ['foo', 'bar'] for the second
        if type(t) == ast.Import:
            imports.extend([name.name.split('.')[0] for name in t.names])
        # ast.ImportFrom represents lines like 'from foo import bar'
        # t.level == 0 is to get rid of 'from .foo import bar' and higher levels
        # of relative importing
        if type(t) == ast.ImportFrom:
            if t.level > 0:
                if conf['ignore_relative_imports'] or not t.module:
                    continue
                else:
                    imports.append(t.module.split('.')[0])

    return list(imports)


def iterate_over_library(path_to_source_code):
    libs = set()
    for parent, folders, files in os.walk(path_to_source_code):
        for file in files:
            if file.endswith('.py'):
                print('.', end='')
                full_file_path = os.path.join(parent, file)
                with open(full_file_path, 'r') as f:
                    code = f.read()
                libs.update(set(get_imported_libs(code)))

    if conf['ignore_builtin_modules']:
        if not conf['pyver']:
            pyver = '%s.%s' % (sys.version_info.major, sys.version_info.minor)
        std_libs = stdlib_list("3.4")
        # print(std_libs)
        libs = [lib for lib in libs if lib not in std_libs]

    return libs