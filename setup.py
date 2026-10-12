import setuptools

setuptools.setup(
    name='batoolset-gui',
    version='0.1.11',
    author='Benoit Aigouy',
    author_email='benoit.aigouy@gmail.com',
    description='Qt/GUI layer for batoolset (drawings, figure, luts, widgets)',
    url='https://github.com/baigouy/batoolset',
    package_data={'': ['*.md', '*.json']},
    license='BSD',
    include_package_data=True,
    packages=setuptools.find_namespace_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'batoolset',
        'PyQt6',
        'QtPy>=2.1.0',
        'qtawesome',
        'pyqt6-plugins',
        'matplotlib>=3.5.2',
    ],
    python_requires='>=3.7, <3.12',
)
