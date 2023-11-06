import setuptools

def open_requirements(path):
    with open(path) as f:
        requires = [
            r.split('/')[-1] if r.startswith('git+') else r
            for r in f.read().splitlines()]
    return requires

requires = open_requirements('requirements.txt')

with open('README.md') as file:
    readme = file.read()

with open('HISTORY.md') as file:
    history = file.read()

setuptools.setup(
    name='inference_interface',
    version='0.0.2',
    description='Functions to read, convert and handle toyMC simulations, fit results and templates used by the XENONnT inference codes',
    author='XENONnT collaboration',
    author_email="knut.dundas.moraa@columbia.edu",
    long_description=readme + '\n\n' + history,
    long_description_content_type='text/markdown',
    setup_requires=['pytest-runner'],
    install_requires=requires,
    python_requires='>=3.8',
    packages=setuptools.find_packages(),
    url="https://github.com/XENONnT/inference_interface",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Scientific/Engineering :: Physics',
    ],
    py_modules=['inference_interface'],
    zip_safe=False,
)
