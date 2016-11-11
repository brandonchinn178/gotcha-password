GOTCHA Password
===============

A server implementing the GOTCHA password scheme (details found [here](http://dl.acm.org/citation.cfm?id=2517319)) for the purposes of a final research project for UGIS 188.

Installation
------------
1. `git clone` this repository
1. If you have Conda, run `conda env create -f=environment.yml`. Otherwise, install `requirements.txt` in your favorite virtual environment
1. Run `npm install && grunt build` (Requires Node.js and Sass)
1. Run `python gotcha_password/manage.py migrate`
1. Run `python gotcha_password/manage.py runserver`
1. Go to `http://localhost:8000`

Security
--------

The paper mentions to set the following security parameters:

- Number of bits in the random seeds (n): in this implementation, n = 71
- Number of images/labels: we will be varying this per user
- Accuracy threshold: we will be varying this in the analysis

One aspect of the research project involves analyzing the accuracy and security of the password scheme. Consequently, we will be changing some parts of the scheme in order to collect and analyze data. These changes include:

- The server will not actually authenticate the user. It will merely show a results page with whether they got the initial password right and the number of image/labels they correctly paired.
- This implementation will store the permutation of the labels, whereas in a production server, the permutation will be hashed with the password (so the only way to retrieve the permutation is to try every possibility). This is to test accuracy levels quickly.
