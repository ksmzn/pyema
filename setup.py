from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pyema',
        version='0.1',
        description='ema(Extract -> Mogrify -> Archive) images',
        long_description=readme(),
        url='http://github.com/ksmzn/pyema',
        author='ksmzn',
        author_email='',
        license='MIT',
        packages=['pyema'],
        install_requires=[
            'patool',
            'pyunpack'
            ],
        entry_points = {
            'console_scripts': ['pyema=pyema.command_line:main'],
        },
        zip_safe=False)
# setup({
#     install_requires: open('requirements.txt').read().splitlines(),
#     })
