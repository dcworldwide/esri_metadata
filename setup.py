from setuptools import setup


with open('esri_metadata/version.py') as fin: exec(fin.read())
with open('README.rst') as fin: long_decription=fin.read()

setup(
    name='esri_metadata',
    version=__version__,

    packages=['esri_metadata'],

    # PyPI MetaData
    author='Adam Kerz',
    author_email='github@kerz.id.au',
    description='Wrapper around the xml format of ESRI\'s metadata',
    long_description=long_decription,
    license='BSD 3-Clause',
    keywords='esri, metadata',
    url='https://github.com/adamkerz/esri_metadata',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
#         'Programming Language :: Python :: 3',
#         'Programming Language :: Python :: 3.4',
#         'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],

    zip_safe=False,
)
