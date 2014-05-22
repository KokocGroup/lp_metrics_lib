from setuptools import setup, find_packages

setup(
    name='django-metrics',
    version='0.1',
    description='django metrics',
    keywords="django metrics",
    long_description=open('README.rst').read(),
    author="GoTLiuM InSPiRiT",
    author_email='gotlium@gmail.com',
    url='https://github.com/LPgenerator/lpg-metrics',
    packages=find_packages(exclude=['demo']),
    include_package_data=True,
    install_requires=[
        'redis==2.8.0',
        'hiredis==0.1.1',
        'pytz==2014.3',
    ],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
