"""
Shell environment introspection, e.g. binaries in effective $PATH, etc.
"""


def have_program(c, name):
    return c.run("which {}".format(name), hide=True, warn=True)
