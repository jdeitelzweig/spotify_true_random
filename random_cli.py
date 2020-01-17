import sys
import random

import spotipy
import spotipy.util as util


def get_all_tracks(username, playlist_id):
	track_ids = []
	results = sp.user_playlist(username, playlist_id, fields="tracks,next")
	tracks = results['tracks']
	for item in tracks['items']:
		track_ids.append((item['track']['id']))

	while tracks['next']:
		tracks = sp.next(tracks)
		for item in tracks['items']:
			track_ids.append((item['track']['id']))
	return track_ids


if len(sys.argv) > 2:
	username = sys.argv[1]
	old = sys.argv[2]
	new = sys.argv[3]
else:
	print(
		"Usage: %s username old-playlist-name new-playlist-name" %
		(sys.argv[0],))
	sys.exit()

scope = "playlist-modify-public playlist-read-collaborative"
token = util.prompt_for_user_token(username, scope)

if token:
	sp = spotipy.Spotify(auth=token)
	sp.trace = False

	track_ids = []
	old_id = ""
	new_id = ""
	playlist_names = []

	playlists = sp.user_playlists(username)
	for playlist in playlists['items']:
		playlist_names.append(playlist['name'])
		if playlist['name'] == old:
			old_id = playlist['id']
		if playlist['name'] == new:
			clear = input("Clear playlist (y/n): ")
			if clear.lower() == "y":
				new_id = playlist['id']
				temp = get_all_tracks(username, new_id)
				for i in range(0, len(temp), 100):
					results = sp.user_playlist_remove_all_occurrences_of_tracks(username, new_id, temp[i:i+100])
			else:
				new = input("Enter new name: ")
				while new in playlist_names:
					new = input("Enter new name: ")

	if old not in playlist_names:
		print("Must enter a valid playlist name")
		sys.exit()
	track_ids = get_all_tracks(username, old_id)

	if new not in playlist_names:
		playlists = sp.user_playlist_create(username, new, description="Random version of {}".format(old))
		new_id = playlists['id']

	random.shuffle(track_ids)
	for i in range(0, len(track_ids), 100):
		results = sp.user_playlist_add_tracks(username, new_id, track_ids[i:i+100])
else:
	print("Can't get token for", username)
