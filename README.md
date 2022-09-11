# language_study
## Learning languages the wrong way

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Currently this project is designed to build a simple probability model from sample inputs.
The model can then be queried to provide options for the continuation of a sentence.

### Goals:
 - Provide a language adaptable interface to build models for multiple languages.
 - Visualize the model to some degree.
 - Provide some methods for integraing external API tools.
 - Expose the model to users such that they can learn correlations in unfamiliar languages.
 ### Notes:
 - The current probability model is built on the unproven assumption that sentences are defined linearly through progression. This may be more suited to a Markov network that functions off of thought expression instead of representation. 

### Quickstart
 1. Clone the repository
 2. Install python dependacies
 3. Set environment variable(s) ``DB_URI=sqlite:///localpath_to_your_db`` (export/set depending on your os)
 4. Instantiate the database ``$ ./dbsuite.py erase_db``
 5. Find a sample book to use and clean it. ``$ ./db_suite.py clean_book "title of novel in your books directory"``
 6. Start loading in some sample data ``$ ./db_suite.py push_book "title of novel in your books directory"``
 7. Follow directions to load information in and mess around with queries. 
