# coding: utf-8
import urllib
import json


def download_song(song_name):
    address = "https://api.vk.com/method/audio.search?owner_id=330310575&" \
          "access_token=73847e48ad6169fb68087e0e78f740a4fcf32909520c39c" \
          "43b15193bc98890ac1dc5a2c258edd1559de97&q=" + song_name
    data = urllib.urlopen(address)
    decoded_response = data.read()
    final_data = json.loads(decoded_response)
    songs = final_data['response'][1:]
    song_artist = songs[0]['artist']
    song_title = songs[0]['title']
    song_url = songs[0]['url']
    cached_song = urllib.urlopen(song_url).read()
    file = open('{0}.mp3'.format(song_name), 'wb')
    file.write(cached_song)
    file.close()
    return "Song downloaded"


if __name__ == '__main__':
    download_song(raw_input('Введите имя песни'))