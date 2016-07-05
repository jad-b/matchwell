from setuptools import setup, find_packages
# import subprocess


with open('README.md') as f:
    readme = f.read()

install_requires = [
    'beautifulsoup4>=4.4.1',
    'google-api-python-client>=1.5.1',
    'numpy>=1.10',
    'pandas>=0.17',
    'scipy>=0.16',
    'scikit-learn>=0.16'
]
tests_require = [
    'ipython>=4.0',
    'pdbpp==0.8.1',
    'pytest>=2.9.1',
    'pytest-cov>=2.2.1'
] + install_requires

setup(
    name='matchwell',
    description="Hierarchical gmail classification",
    long_description=readme,
    version='0.0.1',
    url='https://github.com/jad-b/matchwell',
    author='Jeremy Dobbins-Bucklad',
    author_email='j.american.db@gmail.com',
    packages=find_packages(),
    install_requires=install_requires,
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
    },
    zip_safe=False,
    include_package_data=True
)
