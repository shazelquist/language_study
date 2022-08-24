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
