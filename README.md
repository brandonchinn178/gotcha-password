GOTCHA Password
===============

A server implementing the GOTCHA password scheme (details found [here](http://dl.acm.org/citation.cfm?id=2517319)) for the purposes of a final research project for UGIS 188.

Security
--------

One aspect of the research project involves attempting to crack people's passwords. Due to the limitations of a personal laptop, this server will be reducing the security levels that would typically be implemented on a production server in order to efficiently test passwords. These parameters include:

- Hash iteration: typical Django hashers use 24000 iterations; we will be using 1000 iterations
- Number of bits in random seeds: production servers should use a high value of n; we will be using n = 16
- Password length: Django defaults to a password cap of 128 characters; we will be capping at 16 characters

The following parameters should be set to a fixed value on a production server, but we will be varying them to test the security of the scheme for various values:

- Number of images/labels
- Usability parameter
