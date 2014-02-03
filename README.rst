About
-----

SundayTasks is a plugin based solution for a backend using CouchDB to handle
the load that's required of a typical solution like this. While CouchDB it
self can handle a lot of the grunt work of running a service like that,
SundayTasks handles things like verifcation to check if your getting spam
and hooking into various task and social media apis that needed to have
a well rounded back end.

Installation
------------

SundayTasks is consistent of three parts, first the main application
framework which used Tornando for a scalable evented solution. Extensions
which take care of saving the results and providing for example Facebook
tokens. Then plugins which are your code that you want to execute.

Install from source::
  $ python setup.py install

This installs an application called stasks which is used to run a single
solution tree.

Install provided extensions::
  $ pushd sundaytasks/extensions
  $ python setup.py install

Install provided example plugins::
  $ popd
  $ pushd sundaytasks/example
  $ python setup.py install


