{{ fullname }}
{{ underline }}

.. currentmodule:: {{ fullname }}

.. automodule:: {{ fullname }}
    :members:

{% block modules %}
{% if modules %}
.. rubric:: Modules

.. autosummary::
   :toctree:
   :recursive:
{% for item in modules %}
   {{ item }}
{%- endfor %}
{% endif %}
{% endblock %}
