from setuptools import setup, Extension


setup(name='aiotkinter',
      author='Mathias Rav',
      url='https://github.com/Mortal/aiotkinter',
      description='An asyncio API for the Tkinter event loop',
      long_description=open('README.rst').read(),
      version='0.3.1',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6'],
      packages=['aiotkinter'])
