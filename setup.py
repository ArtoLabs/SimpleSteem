from setuptools import setup, find_packages

setup(
    python_requires='>=3.0',
    name='SimpleSteem',
    version='0.4.9',
    packages=['simplesteem'],
    license='MIT',
    keywords='steem steemit steem-python python3',
    url='http://github.com/artolabs/simplesteem',
    author='ArtoLabs',
    author_email='artopium@gmail.com',
    install_requires=[
        'python-dateutil',
        'steem',
        'steemconnect',
        'screenlogger',
    ],
    py_modules=['simplesteem'],
    include_package_data=True,
    zip_safe=False
)


