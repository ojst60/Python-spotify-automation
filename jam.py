
import os
import requests

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
# import youtube_dl
from youtube_dl import YoutubeDL as yt
import store


scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
user_id = store.id

auth_key = store.key


def youtube_liked_videos():

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server(host="localhost")
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    # Get the first 50 liked videos

    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        maxResults=50,
        myRating="like"
    )

    response = request.execute()
    global g
    g = {}

    page_token = response['nextPageToken']
    for item in response["items"]:
        video_name = item["snippet"]["title"]
        video_id = item["id"]
        g[video_name] = video_id

    while page_token:
        fem = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            maxResults=50,
            myRating="like",
            pageToken=page_token

        ).execute()

        for item in fem["items"]:
            video_name1 = item["snippet"]["title"]
            video_id1 = item["id"]
            g[video_name1] = video_id1

        if 'nextPageToken' in fem:
            page_token = fem['nextPageToken']
        else:
            break

    num_of_liked_videos = len(g)
    print("The number of liked video is {}".format(str(num_of_liked_videos)))

    return g


track_artist = {}


def get_song_name_and_artist_name():
    youtube_liked_videos()
    global track_artist
    for id in g.values():
        result = yt().extract_info(url="https://www.youtube.com/watch?v={}".format(id), download=False, ie_key=None)
        track_name = result["track"]
        song_artist = result["artist"]
        track_artist[song_artist] = track_name
        num_songs =len(track_artist)
        print("The number of songs info is " + str(num_songs))
    return track_artist


def create_playlist():
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(auth_key),
    }

    data = '{"name":"Python","description":"New playlist description","public":false}'

    response = requests.post('https://api.spotify.com/v1/users/{}/playlists'.format(user_id), headers=headers,
                             data=data)
    global playlist_id
    playlist_id = response.json()["id"]
    return playlist_id


def search_liked_on_spotify_and_get_uri():
    global uri_list
    uri_list = []
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(auth_key),
    }

    for artist,track in track_artist.items():
        params = (
            ('q', 'track:{} artist:{}'.format(track,artist)),
            ('type', 'track,artist'),
            ('limit', '20'),
        )
        response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
        if response.json()["tracks"]["items"] == []:
            continue
        else:
            track_uri = response.json()["tracks"]["items"][0]["uri"]
            uri_list.append(track_uri)
    num_uri = len(uri_list)
    print("The number of Uris found is " + str(num_uri))
    return uri_list


def add_songs_to_playlist():
    create_playlist()
    search_liked_on_spotify_and_get_uri()
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(auth_key),
    }
    for uri in uri_list:
        params = (
            ('uris', uri),
        )

        response = requests.post('https://api.spotify.com/v1/playlists/{}/tracks'.format(playlist_id), headers=headers,
                                 params=params)


    return response


get_song_name_and_artist_name()
add_songs_to_playlist()





