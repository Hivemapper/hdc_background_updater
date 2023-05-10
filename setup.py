from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='onboard-updater',
    version='0.1.0',
    description='Client facing over-the-air update app',
    long_description=readme,
    author='Chris Shaw',
    author_email='cshaw9@gmail.com',
    url='https://hellbender.com/',
    license=license,
    python_requires='>=3.7',
    install_requires=[
        'transitions'
    ],
    packages=find_packages(exclude=['tests']),
    entry_points={
        'console_scripts': [
            'onboardupdater = onboardupdater.onboardupdater:main'
        ],
    },
)
