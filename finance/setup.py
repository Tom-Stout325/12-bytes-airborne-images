from setuptools import setup, find_packages

setup(
    name='django-finance-12bucks',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    description='A Django finance app to track income, expenses, mileage, and generate reports.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/12bucks',
    author='Tom Stout',
    author_email='tom@airborne-images.net',
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'Django>=4.0',
        'psycopg2-binary',
        'pillow',
        'django-crispy-forms',
        'django-bootstrap-v5',
        'django-environ',
        'weasyprint',
    ],
)
