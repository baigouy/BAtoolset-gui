import setuptools

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='batoolset-gui',
    version='0.2.3',
    author='Benoit Aigouy',
    author_email='benoit.aigouy@gmail.com',
    description='Qt/GUI layer for batoolset (drawings, figure, luts, widgets)',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/baigouy/BAtoolset-gui',
    package_data={'': ['*.md', '*.json']},
    license='BSD',
    include_package_data=True,
    packages=setuptools.find_namespace_packages(include=['batoolset', 'batoolset.*']),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'batoolset>=0.2.1',
        'PyQt6',            # its Qt6 wheel ships the image plugins (qtiff, qwebp...)
        'QtPy>=2.1.0',
        'qtawesome',
        'matplotlib>=3.5.2',
    ],
    python_requires='>=3.10',
)
