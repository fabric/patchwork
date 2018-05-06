"""
Shell environment introspection, e.g. binaries in effective $PATH, etc.
"""


def have_program(c, name):
    """
    Returns whether connected user has program ``name`` in their ``$PATH``.
    """
    return c.run("which {}".format(name), hide=True, warn=True)
