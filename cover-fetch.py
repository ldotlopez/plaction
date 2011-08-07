#!/usr/bin/env python

import gst
import os
import sys
import gst
import glib
import gobject
import urllib, urllib2
import re
import imghdr

class MetadataExtractor:
	def __init__(self):
		self._pipeline = gst.element_factory_make("playbin")
		self._pipeline.set_property("audio-sink", gst.element_factory_make("fakesink"))
		self._pipeline.set_property("video-sink", gst.element_factory_make("fakesink"))

	def parse_file(self, path):
		self._state_changed = False
		self._new_clock     = False

		self._tags = {}
		self._pipeline.set_property("uri", 'file://' + urllib.pathname2url(path))

		self._bus = self._pipeline.get_bus()
		self._bus.add_signal_watch()
		self._bus.connect("message", self._bus_message_cb)

		glib.idle_add(self._start)

		self._loop = gobject.MainLoop()
		self._loop.run()
		return self._tags

	def _start(self):
		self._pipeline.set_state(gst.STATE_PLAYING)
		return False

	def _fmt_tag(self, v):
		asis = (int, float, bool, str, unicode)
		if type(v) in asis:
			return v
		else:
			return repr(v)

	def _bus_message_cb (self, bus, message):
		stop = False
		if (message.type == gst.MESSAGE_EOS) or (message.type == gst.MESSAGE_ERROR):
			stop = True

		elif message.type == gst.MESSAGE_STATE_CHANGED:
			(old, new, pending) = message.parse_state_changed()
			if (old == gst.STATE_READY) and (new == gst.STATE_PAUSED):
				self._state_changed = True

		elif (message.type == gst.MESSAGE_NEW_CLOCK):
			self._new_clock = True

		elif message.type == gst.MESSAGE_TAG:
			taglist = message.parse_tag()
			for key in taglist.keys():
				self._tags[key] = self._fmt_tag(taglist[key])

		if self._state_changed and self._new_clock:
			stop = True

		if stop:
			self._pipeline.set_state(gst.STATE_NULL)
			self._loop.quit()
			return False
		else:
			return True

class Inspector:
	def __init__(self, path):
		self._path = path
		self._has_music = None

	def get_music(self, **kwargs):
		if self._has_music is None:
			self.has_music()

		kw = dict(kwargs)
		if kw['absolute']:
			return [os.path.join(self._path, e) for e in self._listing]
		else:
			return self._listing

	def has_music(self):
		if self._has_music is not None:
			return self._has_music

		try:
			self._listing = os.listdir(self._path)
		except:
			self._has_music = False
			return False

		self._has_music = False
		tmp = []
		self._listing.sort()
		for e in self._listing:
			for i in ('mp3','ogg','flac','aac','m4a'):
				if e.lower().endswith('.' + i):
					self._has_music = True
					tmp.append(e)

		self._listing = tmp

		return self._has_music

def fetch_url_simple(url, referer = 'http://www.last.fm'):
	try:
		handler = urllib2.HTTPHandler()
		opener = urllib2.build_opener(handler)
		req = urllib2.Request(url, None, {
			'Referer': referer,
			'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.1 (KHTML, like Gecko) Ubuntu/11.04 Chromium/15.0.841.0 Chrome/15.0.841.0 Safari/535.1"})
		resp = opener.open(req)
	except:
		raise Exception("Unable to open URL '%s'" % (url))
	if resp.getcode() != 200:
		raise Exception("Invalid return code: %s" % (resp.getcode()))

	buff = ''.join(resp.readlines())
	resp.close()
	return buff

def fetch_cover(tagdict):
	if not all(tagdict[i] != None for i in ('artist','album')):
		raise Exception("Missing tags")

	url = 'http://www.last.fm/music/%s/%s' % (urllib.quote(tagdict['artist'].encode('utf-8')), urllib.quote(tagdict['album'].encode('utf-8')))
	buff = fetch_url_simple(url)

	cover_url = None
	try:
		#m1 = re.search('<meta .*property="og:image".*>', buff)
		#m2 = re.search('content="(.+)"', m1.group(0))
		m1 = re.search('<span id="albumCover".*?>(.+?)</span>', buff)
		m2 = re.search('src="(.+?)"', m1.group(1))
		cover_url = m2.group(1)
	except:
		raise Exception("Unable to find cover URL")

	if (cover_url.find('default') != -1) or (cover_url.find('noimage') != -1):
		raise Exception("Default cover detected")

	return fetch_url_simple(cover_url, url)

if __name__ == '__main__':
	parser = MetadataExtractor()
	for path in sys.argv[1:]:

		i = Inspector(path)
		musicfiles = i.get_music(absolute = True)
		print "'%s': Found %d music files" % (path, len(musicfiles))

		for mf in musicfiles:
			tags = parser.parse_file(mf)

			if not all(tags.has_key(k) for k in ('artist','album')):
				print "Missing tags"
				continue

			coverfound = False
			coverf = os.path.join(path, "%s - %s" % (tags['artist'].encode('utf-8'), tags['album'].encode('utf-8')))
			if any([os.access(coverf + '.' + ext, os.R_OK) for ext in ('png', 'jpg', 'jpeg', 'gif')]):
				continue

			print "Downloading cover %s" % (coverf)
			try:
				data = fetch_cover(tags)
			except Exception as e:
				print e
				continue

			fh = open(coverf, 'w')
			fh.write(data)
			fh.close()

			t = imghdr.what(coverf)
			os.rename(coverf, coverf + "." + t)

