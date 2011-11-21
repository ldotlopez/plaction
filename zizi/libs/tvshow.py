import os
import re
import shutil

TEAMS = "proper fqm kiss 2hd tpb webrip dimension tastetv eztv barge momentum asap lol vtv river".split(" ")
FORMATS = "xvid hdtv 720p x264".split(" ")

class ParseError(Exception): pass
class RenameError(Exception): pass

"""
Normalizes show name
"""
def normalize_show_name(show_name, replacements = {}):
	# Ensure basename
	show_name = os.path.basename(show_name).lower()

	# Try to guess show name
	show_name = re.split('(S\d+E\d+)', show_name)[0]
	show_name = re.split('(\d+x\d+)', show_name)[0]

	# Do basic normalization
	key = re.sub('[^a-zA-Z0-9]', '', show_name.lower())

	# Use user-supplied map
	if replacements.has_key(key):
		return replacements[key]

	# Try to do our best
	ret = show_name.lower()
	ret = re.sub(r'\s?-\s?$', ''  , ret)
	ret = re.sub(r'[\._]'   , ' ' , ret)
	ret = re.sub(r'\s+$'    , ''  , ret)
	ret = re.sub(r'^\s+'    , ''  , ret)
	ret = ret[0].upper() + ret[1:]

	return ret

"""
Normalizes episode string 
"""
def normalize_title(title, teams = TEAMS, formats = FORMATS):
	parts = re.split(r'[\.\-_\[\]\(\)]', title.lower())
	parts = [x for x in parts if x != "" ]
	parts = [x for x in parts if x not in teams]
	parts = [x for x in parts if x not in formats]
	return " ".join(parts)
	return title if ret == "" else ret

"""
Splits filename into 4 parts:
Show name, season number (as int), episode number (as int) and episode title
"""
def split_info(filename, replacements = {}, teams = TEAMS, formats = FORMATS):
	basename = os.path.basename(filename)
	name = os.path.splitext(basename)[0].lower()

	m = re.match(r'^(.+)(s0?(\d)+e0?(\d)+|0?(\d)+x0?(\d)+)(.+)$', name)
	if m is None:
		raise ParseError('Unable to parse string')

	return ( \
		normalize_show_name(m.group(1), replacements),
		int(m.group(3) or m.group(5)), \
		int(m.group(4) or m.group(6)), \
		normalize_title(m.group(7)))

"""
Renames file
"""
def rename_file(filepath, replacements = {}, output_fmt = "%(name)s - %(season)dx%(episode)02d %(title)s",  teams = TEAMS, formats = FORMATS):
	(show, season, episode, title) = split_info(filepath)
	data = {'name':show , 'season':season, 'episode':episode, 'title':title}

	tmp = output_fmt % (data)
	tmp = re.sub(r'^\s+', '', tmp)
	tmp = re.sub(r'\s+$', '', tmp)

	newbasename = tmp + os.path.splitext(os.path.basename(filepath))[1]
	newfilepath = os.path.join(os.path.dirname(filepath), newbasename)

	#print repr(data)
	#print "In:  %s" % filepath
	#print "Out: %s" % newfilepath

	if filepath == newfilepath:
		raise RenameError('Source and destination files are the same')
	if os.path.exists(newfilepath):
		raise RenameError('Destination file already exists')

	shutil.move(filepath, newfilepath)

