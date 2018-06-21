from setuptools import setup, find_packages
from os import path


cur_dir = path.abspath(path.dirname(__file__))

with open(path.join(cur_dir, 'README.md'), encoding='utf-8') as rfile:
    long_descript = rfile.read()

setup(
    name='pycalc',
    version='1.0.1a1',
    description='Pure-python command line calculator.',
    long_description=long_descript,
    url='https://git.epam.com/Raman_Siamionau/python-test-task',
    author='Raman Siamionau',
    author_email='raman_siamionau@epam.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Topic :: Utilities',
        'Operating System :: POSIX :: Linux',
        'License :: Other/Proprietary License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='math calculator cli',
    packages=find_packages(),
    project_urls={'Source': 'https://git.epam.com/'
                            'Raman_Siamionau/python-test-task'},
    entry_points={'console_scripts':
                      ['pycalc = pycalc.main:main']},
)
