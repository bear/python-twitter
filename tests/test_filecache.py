import twitter
import unittest
import time


class FileCacheTest(unittest.TestCase):
    def testInit(self):
        """Test the twitter._FileCache constructor"""
        cache = twitter._FileCache()
        self.assert_(cache is not None, 'cache is None')

    def testSet(self):
        """Test the twitter._FileCache.Set method"""
        cache = twitter._FileCache()
        cache.Set("foo", 'Hello World!')
        cache.Remove("foo")

    def testRemove(self):
        """Test the twitter._FileCache.Remove method"""
        cache = twitter._FileCache()
        cache.Set("foo", 'Hello World!')
        cache.Remove("foo")
        data = cache.Get("foo")
        self.assertEqual(data, None, 'data is not None')

    def testGet(self):
        """Test the twitter._FileCache.Get method"""
        cache = twitter._FileCache()
        cache.Set("foo", 'Hello World!')
        data = cache.Get("foo")
        self.assertEqual('Hello World!', data)
        cache.Remove("foo")

    def testGetCachedTime(self):
        """Test the twitter._FileCache.GetCachedTime method"""
        now = time.time()
        cache = twitter._FileCache()
        cache.Set("foo", 'Hello World!')
        cached_time = cache.GetCachedTime("foo")
        delta = cached_time - now
        self.assert_(delta <= 1,
                     'Cached time differs from clock time by more than 1 second.')
        cache.Remove("foo")
