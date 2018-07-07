from distutils.core import setup

setup(
    name='fysql',
    version=__import__('fysql').__version__,
    url='https://github.com/Fy-Network/fysql',
    license='MIT',
    author='Gasquez Florian',
    author_email='m@fy.to',
    description='fysql is a small ORM.',
    packages=['fysql'],
    platforms='any',
    install_requires=[]
)
