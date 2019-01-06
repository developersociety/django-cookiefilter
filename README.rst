Django Cookie Filter
====================

Django_ middleware which removes all unwanted cookies - useful for improving cache hit ratios when
analytics cookies interfere with caching.

.. _Django: https://www.djangoproject.com/

Installation
------------

Using pip_:

.. _pip: https://pip.pypa.io/

.. code-block:: console

    $ pip install django-cookiefilter

Edit your Django project's settings module, and add the middleware to the start of  ``MIDDLEWARE``
(or ``MIDDLEWARE_CLASSES`` for Django 1.8):

.. code-block:: python

    MIDDLEWARE = [
        'cookiefilter.middleware.CookieFilterMiddleware',
        # ...
    ]

.. note::

    The middleware should be added before ``UpdateCacheMiddleware``, as it uses the value of
    HTTP_COOKIES which needs to be modified.

Configuration
-------------

Out of the box the standard Django cookie names will work without any other configuration. However
if your project uses different or additional cookie names, edit ``COOKIEFILTER_ALLOWED`` in your
project's settings module:

.. code-block:: python

    COOKIEFILTER_ALLOWED = [
        'analytics',
        'csrftoken',
        'sessionid',
    ]
