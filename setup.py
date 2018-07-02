from setuptools import setup

setup( name = 'centralnotice_analytics',
    version  = '0.1',
    description = 'Analytics library for data from CentralNotice Mediawiki extension',
    license = 'GPL',
    packages = [ 'centralnotice_analytics' ],
    install_requires = [
        'pyyaml >= 3.12',
        'pydruid >= 0.3.1',
        'pandas >= 0.22.0'
    ],
    extras_require = {
        'plots': [
            'matplotlib >= 2.1.1',
            'numpy >= 1.13.3'
        ]
    }
)