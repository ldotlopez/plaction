#!/usr/bin/env ruby 

# == Synopsis
#
# mbox2sqlite: Convert one (or more) mboxes to a sqlite3 database
#
# == Usage
#
# mbox2sqlite [OPTION] ... MBOX ...
#
# -h, --help:
#    show help
#
# --output file, -o file:
#    Use file as sqlite3 db file output
#
# MBOX: The mbox(es) to convert. You can specify one or more mboxes at once

require 'rubygems'
require 'rmail'
require 'sqlite3'
require 'getoptlong'
require 'rdoc/usage'

outdb = "db.sqlite"

GetoptLong.new(
	[ '--help',   '-h', GetoptLong::NO_ARGUMENT ],
	[ '--output', '-o', GetoptLong::OPTIONAL_ARGUMENT ]
).each do |opt, arg|
	case opt
	when '--help'
		RDoc::usage
	when '--output'
		outdb = arg
	end
end

if ARGV.length < 1
	puts "Missing mbox argument (try --help)"
	exit 1
end


begin
	db = SQLite3::Database.new(outdb)
	db.execute("
		CREATE TABLE messages (
			file varchar[128],
			m_id integer not null,
			h_id integer not null,
			key   varchar[128],
			value varchar[10240],
			primary key(file,m_id, h_id)
		);")
	stmt = db.prepare("INSERT INTO messages (file,m_id,h_id,key,value) VALUES(:file,:m_id,:h_id,:key,:value)")
rescue Exception => ex
	puts "Error creating DB. Please delete #{outdb} if exists and try again"
	puts "Details: [#{ex.class}] #{ex}"
	exit 1
end

ARGV.each do |file|

	puts "DBizing #{file}..."
	File.open(file) do |f|
		m_id = 0
		RMail::Mailbox::MBoxReader.new(f).each_message do |input|
			message = RMail::Parser.read(input)
			if m_id % 10 == 0 and m_id != 0
				STDOUT.printf "\r  %d", m_id
				STDOUT.fsync
			end

			h_id = 1 
			message.header.each do |key,val|
				stmt.execute(
					:file => file,
					:m_id => m_id,
					:h_id => h_id,
					:key   => key,
					:value => val) 
				h_id = h_id + 1 
			end
			stmt.execute(
				:file => file,
				:m_id => m_id,
				:h_id => 0,
				:key  => nil,
				:value => message.body)
			m_id = m_id + 1

			end # Mail processed
			STDOUT.printf "\r  %d\n", m_id

		end # File processed
end

