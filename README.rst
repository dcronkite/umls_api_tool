|Contributors| |Forks| |Stargazers| |Issues| |MIT License|

.. raw:: html

      <p>

      </p>

      <h3 align="center">UMLS API Tool</h3>

      <p>
       Tools to simplify retrieving from the UMLS API. 
      </p>


Table of Contents
=================

-  `About the Project <#about-the-project>`__
-  `Getting Started <#getting-started>`__

   -  `Prerequisites <#prerequisites>`__
   -  `Installation <#installation>`__

-  `Usage <#usage>`__
-  `Roadmap <#roadmap>`__
-  `Contributing <#contributing>`__
-  `License <#license>`__
-  `Contact <#contact>`__
-  `Acknowledgements <#acknowledgements>`__

About the Project
=================

Tools to simplify retrieving from the UMLS API. 

In particular, this library is designed to handle:
* Repeated authentication calls (once you have your [api key](https://documentation.uts.nlm.nih.gov/rest/authentication.html), the `Authenticator` will handle everything else)


Getting Started
===============

Prerequisites
-------------

-  Python 3.8+ (probably works in earlier versions)
- Create UMLS account (see https://uts.nlm.nih.gov/uts/umls/home)
- Obtain UMLS API KEY (once signed in, see https://uts.nlm.nih.gov/uts/profile)
- pip install git+https://github.com/dcronkite/umls_api_tool.git
  * Or, `git pull`; `cd umls_api_tool`; `pip install .`

Usage
=====

See the examples in the `examples` folder to see how to use the code.

Use the [UMLS REST API Home Page](https://documentation.uts.nlm.nih.gov/rest/home.html) for complete API documentation.


Versions
========

Uses `SEMVER <https://semver.org/>`__.

See https://github.com/dcronkite/umls_api_tool/releases.


Roadmap
=======

See the `open issues <https://github.com/dcronkite/umls_api_tool/issues>`__
for a list of proposed features (and known issues).


Contributing
============

Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch
   (``git checkout -b feature/AmazingFeature``)
3. Commit your Changes (``git commit -m 'Add some AmazingFeature'``)
4. Push to the Branch (``git push origin feature/AmazingFeature``)
5. Open a Pull Request


License
=======

Distributed under the MIT License.

See ``LICENSE`` or https://dcronkite.mit-license.org for more
information.


Contact
=======

Please use the `issue
tracker <https://github.com/dcronkite/umls_api_tool/issues>`__.


Acknowledgements
================

.. |Contributors| image:: https://img.shields.io/github/contributors/dcronkite/umls_api_tool.svg?style=flat-square
   :target: https://github.com/dcronkite/umls_api_tool/graphs/contributors
.. |Forks| image:: https://img.shields.io/github/forks/dcronkite/umls_api_tool.svg?style=flat-square
   :target: https://github.com/dcronkite/umls_api_tool/network/members
.. |Stargazers| image:: https://img.shields.io/github/stars/dcronkite/umls_api_tool.svg?style=flat-square
   :target: https://github.com/dcronkite/umls_api_tool/stargazers
.. |Issues| image:: https://img.shields.io/github/issues/dcronkite/umls_api_tool.svg?style=flat-square
   :target: https://github.com/dcronkite/umls_api_tool/issues
.. |MIT License| image:: https://img.shields.io/github/license/dcronkite/umls_api_tool.svg?style=flat-square
   :target: https://kpwhri.mit-license.org/