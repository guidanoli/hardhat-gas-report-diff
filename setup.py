from setuptools import setup


def read_version():
    env = {}

    with open('hhgrdiff/version.py') as fp:
        exec(fp.read(), env)

    return env['__version__']


setup(
    name='hardhat-gas-reporter-diff',
    version=read_version(),
    description='Hardhat Gas Reporter Diff',
    url='https://github.com/guidanoli/hardhat-gas-reporter-diff',
    author='Guilherme Dantas',
    author_email='guidanoli@hotmail.com',
    license='GNU General Public License v3.0',
    packages=['hhgrdiff'],
    install_requires=['setuptools'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.8',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
)
