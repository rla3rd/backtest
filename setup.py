from setuptools import setup
from backtest import __version__
 
setup( name='backtest',
    description='backtest abstract class taken from www.quantstart.com',
    author='Michael Halls-Moore',
    version=__version__,
    requires=['abc'],
    py_modules=['backtest', 'event'],
    license='MIT License' )
