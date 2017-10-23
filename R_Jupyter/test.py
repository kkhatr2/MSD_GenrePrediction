import csv
import sqlite3 as db
import pandas as pd

def create_db():
	connection = db.connect("./../my_msd.db")
	connection.text_factory = lambda x: unicode(x, "utf-8", "ignore")
	# create a cursor object for queries
	cursor = connection.cursor()

	# Create tables
	sql_user = '''
				CREATE TABLE
				user(
				user_id VARCHAR(40) PRIMARY KEY NOT NULL			
				);
				'''

	sql_song = '''
				 CREATE TABLE
				 song(
				 song_id VARCHAR(20) PRIMARY KEY NOT NULL,				 
				 release VARCHAR(200),
				 title VARCHAR(256),
				 song_hotness REAL			 
				 );
			   '''
	sql_user_song = '''
					CREATE TABLE 
					user_song(
					id INT PRIMARY KEY DESC,
					user_id VARCHAR(50),
					song_id VARCHAR(20),
					count INT DEFAULT 0,
					FOREIGN KEY(user_id) REFERENCES user(user_id),
					FOREIGN KEY(song_id) REFERENCES song(song_id)
					);
					'''

	sql_track = '''
				CREATE TABLE
				track( 
				track_id VARCHAR(20) PRIMARY KEY NOT NULL,
				song_id VARCHAR(20) NOT NULL,
				artist_id VARCHAR(20) NOT NULL,
				key INT,
				duration REAL,
				mode INT,
				tempo REAL,
				loudness REAL,
				genre VARCHAR(50),
				listen_count INT DEFAULT 0,
				year INT,
				FOREIGN KEY(song_id) REFERENCES song(song_id)
				FOREIGN KEY(artist_id) REFERENCES artist(artist_id)
				);
				'''
				
	sql_artist = '''
				CREATE TABLE
				artist(
				artist_id VARCHAR(20) PRIMARY KEY NOT NULL,				
				artist_familiarity REAL,
				artist_hotness REAL,
				artist_name VARCHAR(400)				
				);
				 '''
	
	cursor.execute(sql_user)	
	cursor.execute(sql_song)	
	cursor.execute(sql_track)	
	cursor.execute(sql_artist)	
	cursor.execute(sql_user_song)
	# commit transactions to create tables
	connection.commit()
	# close connections
	cursor.close()
	return connection
	
def populate_user_song(connection):
	cursor = connection.cursor()
	
	sql_user = "INSERT INTO user(user_id) VALUES(?)"
	sql_user_song = "INSERT INTO user_song(user_id, song_id, count) VALUES(?,?,?)"
	sql_song = "INSERT INTO song(song_id) VALUES(?)"
	
	reader = csv.reader(open("./../../train_triplets.txt", mode="r"), delimiter="\t")
	user_set = set()
	song_set = set()
	triplets = []
	print " Looping through triplets file"
	for i in reader:
		user_set.add(i[0]) # add unique users to the set
		song_set.add(i[1])
		triplets.append(tuple(i))
	print " Finished looping through triplets file"
	user_list = [(i,) for i in user_set]
	song_list = [(i,) for i in song_set]
	print "Finished converting sets to lists"
	del user_set
	del song_set
	del reader
	print "Users = ", len(user_list)
	print "Users = ", len(song_list)
	print "Users = ", len(triplets)
	
	cursor.executemany(sql_user, user_list)
	connection.commit()
	print "committed users to database" 
	cursor.executemany(sql_user_song, triplets)
	connection.commit()
	print "committed user_song (triplets) to database" 
	cursor.executemany(sql_song, song_list)
	connection.commit()
	print "committed songs to database" 
	cursor.close()
	return connection
	
def populate_songs(connection):
	main_cursor = connection.cursor()
	print "connect to 'track_metadata.db' query song_id, track_id and make a dataframe"
	tm = db.connect("track_metadata.db")
	tm_c = tm.cursor()
	s_t = tm_c.execute("SELECT song_id, track_id FROM songs").fetchall()
	s_t_df = pd.DataFrame(data=s_t, columns=["song_id","track_id"])
	print "Finished making the dataframe with song_id and track_id"
	
	print "Opening the .h5 file"
	store = pd.HDFStore("msd_summary_file.h5", "r")
	# Metadata_songs for song_hotttnesss, release and title
	# use song_id as the search key, identification is song_id
	
	print "Bringing metadata/songs in memory"
	metadata_song = store['metadata/songs']
	store.close()
	print "closing the .h5 file"	
	print "metadata/songs in memory !"
	# Subset data for release, title and song_hotness from the metadata_song data frame
	subset = metadata_song[["song_id","release","title","song_hotttnesss"]]
	# Finished subsetting the original data frame
	# Now combine the two data frames, the one with track and song id 
	# and the subsetted dataframe on song_id	
	combined = pd.concat([subset,s_t_df], axis=1, join="inner")
	print "Finished Merging data frames and now\nLooping through the data frame contents for update"
	for row in combined.itertuples():
		if	row.song_hotttnesss == 'nan':
			update_sql = "UPDATE song SET release =?, title =? WHERE song_id =?"
			main_cursor.execute(update_sql, (row.release, row.title, row.song_id))
		else:
			update_sql = "UPDATE song SET release =?, title =?, song_hotness=? WHERE song_id =?"
			main_cursor.execute(update_sql, (row.release, row.title, row.song_hotttnesss, row.song_id))
		connection.commit()
	print "Finished committing release, title and song_hotness data to song table !!"
	
	tm_c.close()
	tm.close()
	main_cursor.close()
	return connection
		
	
def populate_artist(connection):
	con = db.connect("./../../track_metadata.db")
	cursor = con.cursor()
	print "Querying artist data"	
	aid = cursor.execute("select distinct artist_id from songs").fetchall()
	print "Artists = ", len(aid)
	insert_data = []
	for id in aid:
		d = cursor.execute('''SELECT artist_id, artist_familiarity, artist_hotttnesss, artist_name FROM songs 
						WHERE artist_id = ?''', id).fetchone()
		insert_data.append(d)
	
	connection.executemany("INSERT INTO artist VALUES(?,?,?,?)", insert_data)
	connection.commit()
	print "Finished committing data to the database"
	cursor.close()
	con.close()

def get_song_hotness(df, song_id):
	return df[df.song_id == song_id]["song_hotttnesss"].values[0]

def get_from_analysis_data(df, track_id):
	ret = df[df.track_id == track_id]
	return {'loudness' : ret["loudness"].values[0],
			'mode' : ret["mode"].values[0],
			'tempo' : ret["tempo"].values[0],
			'duration' : ret["duration"].values[0],
			'key' : ret["key"].values[0]
			}
	
def check_exist(cursor, id, table):
	if table == 'user':
		sql = "Select user_id from user where user_id = ?"	
	elif table == 'song':
		sql = "SELECT song_id FROM song WHERE song_id = ?"
	elif table == 'track':		
		sql = "SELECT track_id FROM track WHERE track_id = ?"
	exists = cursor.execute(sql, (id,)).fetchone()		
	if exists == None:
		return False	
	return True

def add_song(connection, data):
	cursor = connection.cursor()
	cursor.execute("INSERT INTO song(song_id, release, title, song_hotness) VALUES(?,?,?,?)", data)
	connection.commit()
	cursor.close()

def update_user_song(connection, data):
	cursor = connection.cursor()
	cursor.execute("INSERT INTO user_song(user_id, song_id, count) VALUES(?,?,?)", data)
	connection.commit()
	cursor.close()

def add_user(connection, data):
	cursor = connection.cursor()
	cursor.execute("INSERT INTO  user(user_id) VALUES (?)", data)
	connection.commit()
	cursor.close()

def update_listen_count(connection, track_id, listen_count):
	cursor = connection.cursor()
	existing_count = cursor.execute("SELECT listen_count FROM track WHERE track_id = ?", (track_id,)).fetchone()
	new_count = int(existing_count[0]) + int(listen_count)
	cursor.execute("UPDATE track SET listen_count = ? WHERE track_id = ?", (new_count, track_id,))
	connection.commit()
	cursor.close()
	
def add_track(MainConnection, genre_cursor, data):
	cursor = MainConnection.cursor()
	tid, sid, key, dur, mode, tempo, loud, listen_count, aid = data
	ret = genre_cursor.execute("SELECT genre, year FROM track_genre_year WHERE track_id = ?", (tid,)).fetchone()
	genre, year = ('null', 'null')
	if ret is not None:
		genre, year = ret	
	#print data
	new_data = (tid, sid, aid, dur, mode, tempo, loud, listen_count, year, genre.lower(),)	
	sql = '''
			INSERT INTO track(track_id, song_id, artist_id, duration, mode, tempo, loudness, listen_count, year, genre)
			VALUES (?,?,?,?,?,?,?,?,?,?)
		  '''
	cursor.execute(sql, new_data)
	MainConnection.commit()
	cursor.close()
	

def make_structure(connection):
	## main db
	cursor = connection.cursor()
	print "Collecting data in memory"
	#track_id, title(song/track title), song_id, release (album),artist_id
	#artist_mbid, artist_name, artist_familiarity,artist_hotttnesss,year,track_7digitalid
	#shs_perf,shs_work
	connect_tm = db.connect("./../../track_metadata.db")
	cursor_tm = connect_tm.cursor()
	
	# for track year and track genre
	genre_year = db.connect("./../../track_genre_year.db")
	genre_year_cursor = genre_year.cursor()
	
	# File for the supplementary data
	# user_id, song_id, count
	#file = open('./../../train_triplets.txt', mode='r')	#main file
	file = open("./../../train_triplets.txt", mode="r")	# sample file
	reader = csv.reader(file, delimiter='\t')	
	
	
	# File with most of the metadata
	store = pd.HDFStore("./../../msd_summary_file.h5", "r")
	# Analysis_Songs for the supplementary data
	# loudness, mode, tempo, duration
	# Use track_id as the search key
	analysis_song = store['analysis/songs']
	# Metadata_songs for song_hotttnesss
	# use song_id as the search key
	metadata_song = store['metadata/songs']
	# data is loaded so close the store
	store.close()
	print "Finished collecting data in memory"
	
	while True:	
		user_row = []
		try:
			user_row = next(reader)
		except StopIteration:			
			break
			
		user_row = [i.strip() for i in user_row]
		tup = cursor_tm.execute('''SELECT release, title, track_id, artist_id, artist_name,artist_familiarity, 
												     artist_hotttnesss 
											  FROM songs WHERE song_id = ?''',
											  (user_row[1],)).fetchone()
		release = tup[0]
		title = tup[1]
		track_id = tup[2]
		artist_id = tup[3]
		artist_name = tup[4]
		artist_fam = tup[5]
		artist_hot = tup[6]
		song_hot = get_song_hotness(metadata_song, user_row[1])		
		pd_dict = get_from_analysis_data(analysis_song, track_id)
		
		
		# Check if User already exists
		if check_exist(cursor, user_row[0], 'user') == False:
			print "Adding New User"
			add_user(connection, (user_row[0],))
		# check if the song exists
		if check_exist(cursor, user_row[1], 'song') == False:
			print '\tAdding New Song.'
			# if the song does not exist then add the song
			add_song(connection,(user_row[1].strip(),release, title, song_hot))
			print '\tAdding New Track.'			
			# because the song does not exist so does not the track
			# add new track.
			track_data = (track_id, user_row[1], pd_dict['key'], pd_dict['duration'],pd_dict['mode'], pd_dict['tempo'],
									   pd_dict['loudness'], user_row[2], artist_id)
			add_track(connection, genre_year_cursor, track_data)
		else: 
			#if the song exist then check if the track exists
			exist = check_exist(cursor, track_id, 'track')
			#if a track for the song does not exist then add the track
			# else, the song and track exist. So, update the listen count
			if exist:
				print "\tUpdating listen Count"
				update_listen_count(connection, track_id, user_row[2])
			else:
				data = (track_id, user_row[1], pd_dict['key'], pd_dict['duration'],pd_dict['mode'], pd_dict['tempo'],
									   pd_dict['loudness'], user_row[2])
				add_track(connection, genre_year_cursor, data)				
			
			
		# update the user_song regardless because there are unique combinations of user and song
		print "Updating user_song"
		update_user_song(connection, (user_row))			
		
	# End of While Loop			
	
	print '\n\n'
	print 'User_song',cursor.execute("select count(*) from user_song").fetchone()
	print 'User', cursor.execute("select count(*) from user").fetchone()
	print 'Song',cursor.execute("select count(*) from song").fetchone()
	print 'Tracks',cursor.execute("select count(*) from track").fetchone()
	print 'Artists',cursor.execute("select count(*) from artist").fetchone()
	store.close()
	cursor.close()
	
	
if __name__ == '__main__':	
	connection = create_db()
	connection1 = populate_user_song(connection)
	populate_artist(connection1)
	#make_structure(connection)
	connection.close()
	