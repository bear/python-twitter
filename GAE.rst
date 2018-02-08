================================================
How to use python-twitter with Google App Engine
================================================

**********
Background
**********

Google App Engine uses virtual machines to do work and serve your application's content. In order to make a 'regular' external web request, the instance must use the built-in urlfetch library provided by Google in addition to the traditional python requests library. As a result, a few extra steps must be followed to use python-twitter on App Engine.


*************
Prerequisites
*************

Follow the `third party vendor library install instructions <https://cloud.google.com/appengine/docs/python/tools/using-libraries-python-27#vendoring>`_ to include the dependency libraries listed in ``requirements.txt``: ``requests``, ``requests_oauthlib`` and ``requests_toolbelt``, as well as ``python-twitter`` library. Typically you can just place the  module folders into the same place as your app.yaml file; it might look something like this:

| myapp/
| ├── twitter/
| ├── requests_oauthlib/
| ├── requests_toolbelt/
| ├── main.py 
| └── app.yaml


********
app.yaml
********

In order to use HTTPS, you'll have to make sure the built-in SSL library is properly imported in your ``app.yaml`` file. Here's what that section of your ``app.yaml`` file might look like:

| libraries:
| - name: jinja2
|  version: latest
| - name: webapp2
|  version: latest
| - name: ssl
|  version: latest


****************************
Limitations & Considerations
****************************

Caching
^^^^^^^
When using twitter-python on App Engine, caching is disabled. You'll have to add and manage App Engine's memcache logic on your own if you require any caching beyond what is probably already setup on App Engine by default.

Datastore
^^^^^^^^^
If you plan to store tweets or other information returned by the API in Datastore, you'll probably want to make your own NDP models to store the desired components of the response rather than shoving the whole response into an entity.

Sockets
^^^^^^^^^
When urllib3 is imported on App Engine it will throw a warning about sockets: ``AppEnginePlatformWarning: urllib3 is using URLFetch on Google App Engine sandbox...`` This is just a warning that you'd have to use the Sockets API if you intend to use the sockets feature of the library, which we don't use in python-twitter so it can be ignored.
