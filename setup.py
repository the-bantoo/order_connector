from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in order_connector/__init__.py
from order_connector import __version__ as version

setup(
	name="order_connector",
	version=version,
	description="Simplifies order placement from third-parties",
	author="Bantoo",
	author_email="devs@thebantoo.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
