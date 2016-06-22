from setuptools import setup, find_packages

setup(
  name='fysql',
  version=__import__('fysql').__version__,
  url='https://github.com/Fy-Network/fysql',
  license='MIT',
  author='Gasquez Florian',
  author_email='m@fy.to',
  description='fysql is a small ORM.',
  packages=['fysql'],
  include_package_data=True,
  platforms='any',
  install_requires=[
    'MySQL-python>=1.2.5'
  ],
  classifiers=[
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved ::  MIT License',
      'Operating System :: OS Independent',
      'Programming Language :: Python'
  ],
)