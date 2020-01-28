from setuptools import setup, find_packages
import kumquat

setup(
    name="kumquat",
    version=kumquat.__version__,
    url="https://github.com/kesha1225/Kumquat",
    author="kesha1225",
    packages=find_packages(),
    description="simple wev framework with features",
    install_requires=["uvicorn", "vbml", "jinja2", "aiofile"],
    long_description="Docs: https://kesha1225.github.io/kumquat"
)