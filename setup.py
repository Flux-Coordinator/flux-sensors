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
    install_requires=['python-osc', 'pyserial', 'pypozyx', 'docopt', 'smbus2', 'requests', 'polling'],
    entry_points={
        'console_scripts': [
            'flux=flux_sensors.__main__:main'
        ]
    }
)