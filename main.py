
import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def authenticate():
    # Disable OAuthlib's HTTPS verification when running locally.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    
    # Specify the path to your client_secrets.json file
    client_secrets_file = "client_secret_1034812063898-4l93lat3v5jivnhni9kff5554j9ko20m.apps.googleusercontent.com.json"
    
    # Check if token.pickle file exists
    credentials = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, scopes)
            credentials = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
    
    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

def get_playlist_id_by_title(youtube, title):
    page_token = None
    
    while True:
        request = youtube.playlists().list(
            part="snippet",
            mine=True,
            maxResults=50,
            pageToken=page_token
        )
        response = request.execute()
        
        for item in response['items']:
            if item['snippet']['title'] == title:
                return item['id']
        
        page_token = response.get('nextPageToken')
        if not page_token:
            break
    
    return None

def delete_playlist(youtube, playlist_id):
    youtube.playlists().delete(
        id=playlist_id
    ).execute()

def create_playlist(youtube, title, description):

    # Create a new playlist
    playlists_insert_response = youtube.playlists().insert(
        part='snippet,status',
        body=dict(
            snippet=dict(
                title=title,
                description=description
            ),
            status=dict(
                privacyStatus='unlisted'  # Change as needed: 'private', 'public', 'unlisted'
            )
        )
    ).execute()

    return playlists_insert_response['id']

def add_videos_to_playlist(youtube, playlist_id, video_ids):
    # Add videos to the playlist
    for video_id in video_ids:
        youtube.playlistItems().insert(
            part='snippet',
            body=dict(
                snippet=dict(
                    playlistId=playlist_id,
                    resourceId=dict(
                        kind='youtube#video',
                        videoId=video_id
                    )
                )
            )
        ).execute()

if __name__ == '__main__':

    youtube = authenticate()

    # Example usage
    playlist_title = 'Temp Playlist'
    playlist_description = 'A playlist created using the YouTube Data API'
    curr_playlist_id_fpath = 'curr-playlist-id.txt'
    playlist_id: str = None

    # Get current playlist ID if it exists
    if os.path.isfile(curr_playlist_id_fpath):
        with open(curr_playlist_id_fpath) as f:
            playlist_id = f.readline().rstrip('\n')

    if not playlist_id:
        playlist_id = get_playlist_id_by_title(youtube, playlist_title)

    if playlist_title:
        delete_playlist(youtube, playlist_id)

    # Create the playlist
    playlist_id = create_playlist(youtube, playlist_title, playlist_description)
    print(f'Playlist "{playlist_title}" created with ID: {playlist_id}')
    
    # Save playlist ID for managing later
    with open(curr_playlist_id_fpath, 'w') as f:
        f.write(playlist_id)

    # List of video IDs to add to the playlist
    video_ids = ['kRSZ5_eIGNI','uFH8it0VBcs','a1vw1dqvzX4','B-QTmMjNQEw','zaSP6qAiqk0','tz82xbLvK_k','XH4pNIF32L8','JPu_aqoeXxM','8RmlH2X51Ic','a545Gv3jGzg','kcOob03cibA','Rw5biVUNTd8','LmBDru41aws','3YL_j4BBCnY','VdVpXGpuwCw','mLUguXpUIb0','4nrI88fmc-I','fDJf232023M','Yu9ykgGUm1w','cjUPVKEN9tI','bKpsUU6SgSo','abDT1DcskMA','gZDE8UGVQyU','gmyG7pHgN8U','-kQowIsJJR4','rMudHClToL0','RFaMRR0Ys9Q','gECmuiQhbOQ','NrB5bL1wqwk','e1qqjX3sjwE','WM3RRVuwf6k','7tMfTk-rYcI','PXDq27OxTkc','qdUSITnZd_0','UNRJ1KH0uf4','1C7m3EdFfDQ','DT711RYmZtg','IJiHDmyhE1A','NR3C-J1HezM','j8YnSgiGuJs','yPDNA-5Sqqc','wpsu8UO8gKQ','bEVY-3vm-pk','7lEB7V-KIb0','ODPPV_GTpXA','irgZYu3dKIg','7y_W6XHFfFc','_liy8WAWsxw','ThVy861W6uc']

    # Add videos to the playlist
    add_videos_to_playlist(youtube, playlist_id, video_ids)
    print(f'Videos added to the playlist.')

    # Access playlist
    print('URL:')
    print(f'https://www.youtube.com/playlist?list={playlist_id}')