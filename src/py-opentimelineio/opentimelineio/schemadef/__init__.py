
def _add_schemadef_module(name, mod):
    """Insert a new module name and module object into schemadef namespace."""
    ns = globals()  # the namespace dict of the schemadef package
    ns[name] = mod
