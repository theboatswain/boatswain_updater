#  This file is part of Boatswain.
#
#      Boatswain is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      Boatswain is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with Boatswain.  If not, see <https://www.gnu.org/licenses/>.
#
#

from distutils.core import setup
from setuptools import find_packages

setup(name='boatswain_updater',
      version='1.0.1',
      packages=find_packages(exclude=("venv*",)),
      author='Manh Tu VU',
      author_email='glmanhtu@gmail.com',
      install_requires=[
          'PyQt5==5.13.0',
          'semantic_version==2.6.0',
          'requests'
      ],
      classifiers=[
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.7",
      ],
      package_data={
          '': ['*.sh', '*.bat']
      }
      )
