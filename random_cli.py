import sys
import random

import spotipy
import spotipy.util as util


def get_all_tracks(pl_username, playlist_id):
	'''Return a list of all the songs in a given playlist'''
	track_ids = []
	results = sp.user_playlist(pl_username, playlist_id, fields="tracks,next")
	tracks = results['tracks']
	for item in tracks['items']:
		track_ids.append((item['track']['id']))

	while tracks['next']:
		tracks = sp.next(tracks)
		for item in tracks['items']:
			track_ids.append((item['track']['id']))
	return track_ids


def main():
	'''Randomizes the order of all songs in the specified Spotify playlist'''
	global new
	track_ids = []
	old_id = ""
	new_id = ""
	playlist_names = []

	# Get user's playlist names
	playlists = sp.user_playlists(username)
	for playlist in playlists['items']:
		playlist_names.append(playlist['name'])

		# Get id of old and new playlists
		if playlist['name'] == old:
			old_id = playlist['id']
		# If playlist already exists, prompt if they want to overwrite
		if playlist['name'] == new:
			clear = input("Clear playlist (y/n): ")
			if clear.lower() == "y":
				new_id = playlist['id']
				temp = get_all_tracks(username, new_id)
				for i in range(0, len(temp), 100):
					results = sp.user_playlist_remove_all_occurrences_of_tracks(username, new_id, temp[i:i+100])
			# Change name if playlist should not be overwritten
			else:
				new = input("Enter new name: ")
				while new in playlist_names:
					new = input("Enter new name: ")

	# If old playlist doesn't exist, stop execution
	if old not in playlist_names:
		print("Must enter a valid playlist name")
		sys.exit()

	# Get all songs in the old playlist
	track_ids = get_all_tracks(username, old_id)

	# Create playlist if it doesn't exist
	if new not in playlist_names:
		playlists = sp.user_playlist_create(username, new, description="Random version of {}".format(old))
		new_id = playlists['id']

	# Randomize songs
	random.shuffle(track_ids)

	# Add songs to playlist in batches of 100
	for i in range(0, len(track_ids), 100):
		results = sp.user_playlist_add_tracks(username, new_id, track_ids[i:i+100])


if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Usage: {} username old-playlist-name new-playlist-name".format(sys.argv[0]))
		sys.exit()

	username = sys.argv[1]
	old = sys.argv[2]
	new = sys.argv[3]

	scope = "playlist-modify-public playlist-read-collaborative"
	token = util.prompt_for_user_token(username, scope)

	if token:
		sp = spotipy.Spotify(auth=token)
		sp.trace = False
	else:
		print("Can't get token for", username)

	main()
