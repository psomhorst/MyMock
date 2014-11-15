from distutils.core import setup

setup(name='MyMock',
      version='0.1',
      description='MySQL mock module',
      author='Peter Somhorst',
      author_email='peter.somhorst@gmail.com',
      url='',
      packages=['mymock'],
      requires=['mirakuru', 'shutil', 'psutil', 'distutils.spawn']
     )
