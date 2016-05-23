.. _searching:

Searching
+++++++++


.. _raw_queries:

Raw Queries
===========

To the ``Api.GetSearch()`` method, you can pass the parameter ``raw_query``, which should be the query string you wish to use for the search **omitting the leading "?"**. This will override every other parameter. Twitter's search parameters are quite complex, so if you have a need for a very particular search, you can find Twitter's documentation at https://dev.twitter.com/rest/public/search.

For example, if you want to search for only tweets containing the word "twitter", then you could do the following: ::

    results = api.GetSearch(
        raw_query="q=twitter%20&result_type=recent&since=2014-07-19&count=100")

If you want to build a search query and you're not quite sure how it should look all put together, you can use Twitter's Advanced Search tool: https://twitter.com/search-advanced, and then use the part of search URL after the "?" to use for the Api, removing the ``&src=typd`` portion.
