try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name="kwlist",
    description="A keyword list in Python",
    license="""BSD""",
    version="0.1",
    author="Steven Seguin",
    author_email="steven.seguin+kwlist@gmail.com",
    maintainer="Steven Seguin",
    maintainer_email="steven.seguin+kwlist@gmail.com",
    url="https://github.com/sseg/kwlist",
    packages=['kwlist'],
    classifiers=[
        'Programming Language :: Python',
    ]
)
