from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='flux_sensors',
    version='0.0.1',
    description='Sensor component of Flux-Coordinator',
    long_description=readme,
    author='Patrick Scherler, Esteban Luchsinger',
    author_email='pacs01dev@gmail.com',
    url='https://github.com/Flux-Coordinator/flux-sensors',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=['python-osc==1.6.6', 'pyserial==3.4', 'pypozyx==1.1.7', 'docopt==0.6.2', 'smbus2==0.2.0', 'requests==2.18.4', 'requests-futures==0.9.7',
                      'futures==3.1.1', 'polling==0.3.0'],
    entry_points={
        'console_scripts': [
            'flux=flux_sensors.__main__:main'
        ]
    }
)