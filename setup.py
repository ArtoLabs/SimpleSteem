from setuptools import setup, find_packages

setup(
    python_requires='>=3.0',
    name='SimpleSteem',
    version='1.1.18',
    packages=['simplesteem'],
    license='MIT',
    keywords='steem steemit steem-python python3',
    url='http://github.com/artolabs/simplesteem',
    author='ArtoLabs',
    author_email='artopium@gmail.com',
    install_requires=[
        'python-dateutil',
        'urllib3==1.26.5',
        'steem==1.0.0',
        'steemconnect==0.0.2',
        'screenlogger==1.3.1',
    ],
    py_modules=['simplesteem'],
    include_package_data=True,
    zip_safe=False
)


