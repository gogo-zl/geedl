from setuptools import setup, find_packages

setup(
    name='geepy',
    version='0.1.0',
    description='A Python package for Google Earth Engine tools',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Zhang Lei',
    author_email='zhanglei1136@163.com',
    url='https://github.com/gg-zl/GEE_py',
    packages=find_packages(),  # 自动查找 geepy 包
    install_requires=[
        'earthengine-api',
        'geemap',
        'numpy',
        'matplotlib'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.7',
)
