try:
    from setuptools import setup
except:
    from distutils.core import setup

readme = open("README.md")
requirements = open("requirements.txt").read().splitlines()


setup(name="inference_interface",
      version="0.1",
      description="functions to read, convert and handle toyMC simulations, fit results and templates used by the XENONnT inference codes",
      author="XENONnT collaboration",
      author_email="knut.dundas.moraa@columbia.edu",
      url="https://github.com/XENONnT/inference_interface",
      install_requires=requirements,
      py_modules=["inference_interface"]
      )
