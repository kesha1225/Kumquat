"""
context var for jinja2 templates path
"""
from contextvars import ContextVar

env_var: ContextVar[str] = ContextVar("var")
