#
# song.py
# Contains the Song class
#


class Song():
    """
    Song Class: Used to hold individual song information once fetched from the database
    The constructor for this particular class object is quite... Massive...
    This implementation was basically a database fetch and dump into a constructor...
    """

    def __init__(self, id=-1, song_id=-1, title='', title_translated='', title_pronunciation='',
                 artist='', nov_level=0, nov_link='', adv_level=0, adv_link='', exh_level=0, exh_link='',
                 max_level=0, max_link='', video_play='', video_nofx='', video_og='', jacket=''):
        """
        :param id: Database ID of the song
        :param song_id: The ID of the song from the sdvx.in site, not the same as regular music ids
        :param title: Name of the song
        :param title_translated: The machine translated title of the song
        :param title_pronunciation: The romanized version of the song name
        :param artist: The artist of the song
        :param nov_level: The numerical level of the novice chart
        :param nov_link: The link to the novice difficulty chart
        :param adv_level: The numerical level of the advanced chart
        :param adv_link: The link to the advanced difficulty chart
        :param exh_level: The numerical level of the exhaust chart
        :param exh_link: The link to the exhaust difficulty chart
        :param max_level: The numerical level of the maximum difficulty chart
        :param max_link: The link to the maximum difficulty chart (INF/GRV/HVN/MXM/IDOLS)
        :param video_play: The link to a video of someone playing the chart
        :param video_nofx: The link to a video of the song without any effect sounds
        :param video_og: The link to the original version of the song (fairly rare now)
        :param jacket: The link to the jacket cover
        """
        self.id = id
        self.song_id = song_id
        self.title = title
        self.title_translated = title_translated
        self.title_pronunciation = title_pronunciation
        self.artist = artist
        self.nov_level = nov_level
        self.nov_link = nov_link
        self.adv_level = adv_level
        self.adv_link = adv_link
        self.exh_level = exh_level
        self.exh_link = exh_link
        self.max_level = max_level
        self.max_link = max_link
        self.video_play = video_play
        self.video_nofx = video_nofx
        self.video_og = video_og
        self.jacket = jacket
