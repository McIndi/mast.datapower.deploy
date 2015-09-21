#!/usr/bin/env python

from setuptools import setup

setup(name='mast.datapower.deploy',
      version='0.6.0',
      description='An updated deployment process automation',
      author='Clifford Bressette IV',
      author_email='cliffordbressette@mcindi.com',
      maintainer="Clifford Bressette",
      url='https://github.com/mcindi/mast.datapower.deploy',
      namespace_packages=["mast", "mast.datapower"],
      packages=['mast', 'mast.datapower', 'mast.datapower.deploy'],
      data_files=[
          ("mast/datapower/deploy/data", [
              "./mast/datapower/deploy/data/deploy.conf"
          ])
      ],
      license="GPL v2",
      install_requires=[]
     )
