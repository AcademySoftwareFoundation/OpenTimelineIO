#
# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project
import re

import sphinx_rtd_theme
import opentimelineio

# -- Project information ---------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'OpenTimelineIO'
copyright = "Copyright Contributors to the OpenTimelineIO project"
author = 'Contributors to the OpenTimelineIO project'

try:
    RELEASE = opentimelineio.__version__
except AttributeError:
    RELEASE = 'unknown'

# The short X.Y version.
version = RELEASE.split('-')[0]
# The full version, including alpha/beta/rc tags.
release = RELEASE

# -- General configuration -------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'myst_parser',  # This plugin is used to format our markdown correctly
]

templates_path = ['_templates']

exclude_patterns = ['_build', '_templates', '.venv']

pygments_style = 'sphinx'


# -- Options for HTML output -----------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

htmlhelp_basename = f'{project.lower()}doc'


# -- Options for LaTeX output ----------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output

latex_documents = [
    ('index', f'{project.lower()}.tex',
     f'{project} Documentation',
     author, 'manual'),
]

# -- Options for manual page output ----------------------------------------------------
# sphinx-doc.org/en/master/usage/configuration.html#options-for-manual-page-output

man_pages = [
    ('index', project.lower(), f'{project} Documentation',
     [author], 1)
]

# -- Options for Texinfo output --------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-texinfo-output

texinfo_documents = [
    ('index', project.lower(), f'{project} Documentation',
     author, project, 'One line description of project.',
     'Miscellaneous'),
]

# -- Options for intersphinx -----------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

# -- Options for Autodoc ---------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

# Both the class’ and the __init__ method’s docstring are concatenated and inserted.
# Pybind11 generates class signatures on the __init__ method.
autoclass_content = "both"

autodoc_default_options = {
    'undoc-members': True
}

# -- Options for linkcheck -------------------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-the-linkcheck-builder

linkcheck_exclude_documents = [
    r'cxx/cxx'
]

# For some reason this URL gives 403 Forbidden when running in github actions
linkcheck_ignore = [r'https://opensource.org/licenses/MIT']

# -- Options for MySt-Parser -----------------------------------------------------------
# https://myst-parser.readthedocs.io/en/latest/sphinx/reference.html

myst_heading_anchors = 5

# -- Custom ----------------------------------------------------------------------------

def process_signature(
    app,
    what: str,
    name: str,
    obj: object,
    options: dict[str, str],
    signature: str,
    return_annotation,
):
    """This does several things:
    * Removes "self" argument from a signature. Pybind11 adds self to
      method arguments, which is useless in a python reference documentation.
    * Handles overloaded methods/functions by using the docstrings generated
      by Pybind11. Pybind11 adds the signature of each overload in the first function's
      signature. So the idea is to generate a new signature for each one instead.
    """
    signatures = []
    isClass = what == "class"

    # This block won't be necessary once https://github.com/pybind/pybind11/pull/2621
    # gets merged in Pybind11.
    if signature or isClass:
        docstrLines = obj.__doc__ and obj.__doc__.split("\n") or []
        if not docstrLines or isClass:
            # A class can have part of its doc in its docstr or in the __init__ docstr.
            docstrLines += (
                obj.__init__.__doc__ and obj.__init__.__doc__.split("\n") or []
            )

        # This could be solidified by using a regex on the reconstructed docstr?
        if len(docstrLines) > 1 and "Overloaded function." in docstrLines:
            # Overloaded function detected. Extract each signature and create a new
            # signature for each of them.
            for line in docstrLines:
                nameToMatch = name.split(".")[-1] if not isClass else "__init__"

                # Maybe get use sphinx.util.inspect.signature_from_str ?
                if match := re.search(fr"^\d+\.\s{nameToMatch}(\(.*)", line):
                    signatures.append(match.group(1))
        elif signature:
            signatures.append(signature)

    signature = ""

    # Remove self from signatures.
    for index, sig in enumerate(signatures):
        newsig = re.sub(r"self\: [a-zA-Z0-9._]+(,\s)?", "", sig)
        signatures[index] = newsig

    signature = "\n".join(signatures)
    return signature, return_annotation


def process_docstring(
    app,
    what: str,
    name: str,
    obj: object,
    options: dict[str, str],
    lines: list[str],
):
    for index, line in enumerate(lines):
        # Remove "self" from docstrings of overloaded functions/methods.
        # For overloaded functions/methods/classes, pybind11
        # creates docstrings that look like:
        #
        #     Overloaded function.
        #     1. func_name(self: <something>, param2: int)
        #     1. func_name(self: <something>, param2: float)
        #
        # "self" is a distraction that can be removed to improve readability.
        # This should be removed once https://github.com/pybind/pybind11/pull/2621 is merged.
        if re.match(fr'\d+\. {name.split("."[0])}', line):
            line = re.sub(r"self\: [a-zA-Z0-9._]+(,\s)?", "", line)
            lines[index] = line


def setup(app):
    app.connect("autodoc-process-signature", process_signature)
    app.connect("autodoc-process-docstring", process_docstring)
