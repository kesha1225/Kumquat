from setuptools import setup, find_packages
import kumquat

setup(
    name="kumquat",
    version=kumquat.__version__,
    url="https://github.com/kesha1225/Kumquat",
    author="kesha1225",
    packages=find_packages(),
    description="simple web framework with features",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    install_requires=["uvicorn", "vbml", "jinja2", "aiofile"],
)
