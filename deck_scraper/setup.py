from setuptools import setup

setup(
   name='deck_scraper',
   version='1.0',
   description='Scrape decklists from Moxfield and more.',
   author='Colton Rowe',
   author_email='coltonjack.rowe@gmail.com',
   packages=['deck_scraper'],  #same as name
   install_requires=['selenium'], #external packages as dependencies
)