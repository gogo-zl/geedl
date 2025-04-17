from setuptools import setup, find_packages
from pathlib import Path


def get_version():
    version_path = Path(__file__).parent / "geepy" / "__version__.py"
    exec(version_path.read_text(), version := {})
    return version["__version__"]


setup(
    name='geepy',
    version=get_version(),
    description='A Python package for Google Earth Engine tools',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Zhang Lei',
    author_email='zhanglei1136@163.com',
    url='https://github.com/gg-zl/GEE_py',
    packages=find_packages(), 
    install_requires=[
        'numpy',              
        'earthengine-api',     
        'geemap',             
        'pandas',              
        'matplotlib',           
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)


# cd geepy
# change version in setup.py and readme.md
# git add -A
# git commit -m "Bump version to 0.1.2 and add new function xxx"
# git push origin master
# git tag v0.1.2
# git push origin v0.1.2