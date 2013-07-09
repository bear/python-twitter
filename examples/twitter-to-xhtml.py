#!/usr/bin/env python

'''Load the latest update for a Twitter user and leave it in an XHTML fragment'''

__author__ = 'dewitt@google.com'

import codecs
import getopt
import sys
import twitter

TEMPLATE = """
<div class="twitter">
  <span class="twitter-user"><a href="http://twitter.com/%s">Twitter</a>: </span>
  <span class="twitter-text">%s</span>
  <span class="twitter-relative-created-at"><a href="http://twitter.com/%s/statuses/%s">Posted %s</a></span>
</div>
"""

def Usage():
  print 'Usage: %s [options] twitterid' % __file__
  print
  print '  This script fetches a users latest twitter update and stores'
  print '  the result in a file as an XHTML fragment'
  print
  print '  Options:'
  print '    --help -h : print this help'
  print '    --output : the output file [default: stdout]'


def FetchTwitter(user, output):
  assert user
  statuses = twitter.Api().GetUserTimeline(id=user, count=1)
  s = statuses[0]
  xhtml = TEMPLATE % (s.user.screen_name, s.text, s.user.screen_name, s.id, s.relative_created_at)
  if output:
    Save(xhtml, output)
  else:
    print xhtml


def Save(xhtml, output):
  out = codecs.open(output, mode='w', encoding='ascii',
                    errors='xmlcharrefreplace')
  out.write(xhtml)
  out.close()

def main():
  try:
    opts, args = getopt.gnu_getopt(sys.argv[1:], 'ho', ['help', 'output='])
  except getopt.GetoptError:
    Usage()
    sys.exit(2)
  try:
    user = args[0]
  except:
    Usage()
    sys.exit(2)
  output = None
  for o, a in opts:
    if o in ("-h", "--help"):
      Usage()
      sys.exit(2)
    if o in ("-o", "--output"):
      output = a
  FetchTwitter(user, output)

if __name__ == "__main__":
  main()
