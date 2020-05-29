import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name = 'saphyra',
  version = '1.0.1',
  license='GPL-3.0',
  description = '',
  long_description = long_description,
  long_description_content_type="text/markdown",
  packages=setuptools.find_packages(),
  author = 'João Victor da Fonseca Pinto',
  author_email = 'jodafons@lps.ufrj.br',
  url = 'https://github.com/jodafons/Gaugi',
  keywords = ['framework', 'flexibility', 'python', 'online', 'machine learning', 'deep learning'],
  install_requires=[
          'numpy',
          'six',
          'scipy',
          'tensorflow',
          'future'
      ],
  classifiers=[
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)
