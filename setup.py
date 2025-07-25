# setup.py
from setuptools import setup, find_packages

setup(
    name='django_tokens',
    version='0.3.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
    ],
    python_requires='>=3.8',
    
    # Metadata
    author='witwar',
    author_email='witwar@gmail.com',
    description='A Django app for handling tokens in text',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/witwar/django_tokens',
    
    # Classifiers help users find your project
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Text Processing :: Markup',
    ],
    
    # Package will be available as tokens
    package_data={
        'tokens': [
            'templates/tokens/*.html',
        ],
    },
    
    # Optional but recommended
    project_urls={
        'Source': 'https://github.com/witwar/django_tokens',
        'Tracker': 'https://github.com/witwar/django_tokens/issues',
    },
)
