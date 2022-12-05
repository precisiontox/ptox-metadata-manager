# Precision Toxicology Metadata Manager
[![CI Build](https://github.com/precisiontox/PTMDM/actions/workflows/build.yml/badge.svg)](https://github.com/precisiontox/PTMDM/actions/workflows/build.yml)[![Coverage Status](https://coveralls.io/repos/github/precisiontox/PTMDM/badge.svg?branch=terazus-badges)](https://coveralls.io/github/precisiontox/PTMDM?branch=terazus-badges)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/341709b9be4141158f01b2930e6a8b97)](https://www.codacy.com/gh/ISA-tools/PTMD/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ISA-tools/PTMD&amp;utm_campaign=Badge_Grade)
![Status](https://camo.githubusercontent.com/d101bf45a713753a714d0cd41b86cd92fbcda60c63f32f48c611e63b5df2e656/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f7374617475732d616c7068612d6f72616e6765)
![Documentation Coverage](./docs_badge.svg)
[![Documentation Status](https://readthedocs.org/projects/pretox-metadata-manager/badge/?version=latest)](https://pretox-metadata-manager.readthedocs.io/en/latest/?badge=latest)

## Getting started
```shell
git clone https://github.com/ISA-tools/ptmd.git
cd ptmd
pip install -r requirements.txt # for production
pip install -r requirements-dev.txt # for development
```

## Verify and generate the documentation
```shell
docstr-coverage ptmd/ --fail-under=100
cd docs
make html
```
