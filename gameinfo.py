import obspython as obs

import json
import datetime as dt

from twitchAPI.twitch import Twitch
from igdb.wrapper import IGDBWrapper


class GameInfo(object):
    IGDB_REGION_ENUM = {
        1: 'EU',
        2: 'NA',
        3: 'AU',
        4: 'NZ',
        5: 'JP',
        6: 'CN',
        7: 'Asia',
        8: 'World'        
    }

    def __init__(self, twitch_client_id=None, twitch_client_secret=None, twitch_username=None, source_name=None, game_override=None):
        self.source_name = source_name
        self.twitch_client_id = twitch_client_id
        self.twitch_client_secret = twitch_client_secret
        self.twitch_username = twitch_username
        self.twitch_auth_token = None
        self.broadcast_id = None
        self.game_name = None
        self.game_override = game_override
        self.game_info = None
        
    def twitch_api_connect(self):
        """ authenticate against the Twitch API and set object properties """
        if (self.twitch_client_id is not None) or (self.twitch_client_secret is not None):
            twitch = Twitch(self.twitch_client_id, self.twitch_client_secret)
            try:
                twitch.authenticate_app([])
            except:
                # if something goes wrong, at a minimum we want to unset the auth token
                # so that the script doesn't keep trying to fire unauthorized requests
                # against IGDB.
                self.twitch_auth_token = None
            
            # pull auth token, broadcast id, and game name from Twitch API
            self.twitch_auth_token = twitch.get_app_token()
            self.broadcast_id = twitch.get_users(logins=[self.twitch_username])['data'][0]['id']
            self.game_name = twitch.get_channel_information(self.broadcast_id)['data'][0]['game_name']

        else:
            self.twitch_auth_token = None

    def get_current_game(self):
        """ fetch game info from IGDB """
        byte_array = None

        if self.twitch_auth_token is not None:
            # If we have an auth token, attempt to authenticate to the IGDB API.
            try:
                igdb = IGDBWrapper(client_id=self.twitch_client_id, auth_token=self.twitch_auth_token)
            except:
                # If IGDB shits the bed, set self.game_info to None
                self.game_info = None

            if self.game_override is not None:
                # search for game info based on stub supplied by user
                byte_array = igdb.api_request(
                    'games',
                    'fields id, name, platforms.abbreviation, involved_companies.company.name, involved_companies.developer, involved_companies.publisher, cover.image_id, release_dates.date, release_dates.region, release_dates.platform.abbreviation; where name = "{}";'.format(self.game_override)
                )                
            else:
                # search for game based on user's current Twitch category
                byte_array = igdb.api_request(
                    'games',
                    'fields id, name, platforms.abbreviation, involved_companies.company.name, involved_companies.developer, involved_companies.publisher, cover.image_id, release_dates.date, release_dates.region, release_dates.platform.abbreviation; where name = "{}";'.format(self.game_name)
                )            

            # convert the byte array returned by the IGDB wrapper into something useful
            game_info = json.loads(byte_array)

            # if game_info is an empty list, we don't need to do anything
            if len(game_info) > 0:

                # Set the game name
                game_name = game_info[0]['name']

                # Set the cover image
                game_cover = "https://images.igdb.com/igdb/image/upload/t_cover_small/{}.jpg".format(game_info[0]['cover']['image_id'])


                # Release Dates: we only want the oldest dates from each region
                release_dates_sorted = sorted(game_info[0]['release_dates'], key = lambda i: i['date'])
                release_dates_filtered = []
                for release_date in release_dates_sorted:
                    if not any(i.get('region', False) == release_date['region'] for i in release_dates_filtered):
                        release_dates_filtered.append(release_date)

                release_dates_final = []
                for release_date in release_dates_filtered:
                    tmp = {
                        'date': dt.datetime.utcfromtimestamp(release_date['date']).strftime("%Y-%m"),
                        'region': self.IGDB_REGION_ENUM[release_date['region']]
                    }
                    release_dates_final.append(tmp)

                # Platforms: filter out anything that doesn't have a proper abbreviation
                platforms_filtered = []
                for platform in game_info[0]['platforms']:
                    if 'abbreviation' in platform:
                        platforms_filtered.append(platform['abbreviation'])

                platforms_filtered.sort()

                # Devevelopers & publishers
                developers_filtered = []
                for developer in game_info[0]['involved_companies']:
                    if developer['developer'] == True:
                        developers_filtered.append(developer['company']['name'])

                publishers_filtered = []
                for publisher in game_info[0]['involved_companies']:
                    if publisher['publisher'] == True:
                        publishers_filtered.append(publisher['company']['name'])

                self.game_info = {
                    'game_name':        game_name,
                    'game_cover':       game_cover,
                    'release_dates':    release_dates_final,
                    'platforms':        ", ".join(platforms_filtered),
                    'developers':       developers_filtered,
                    'publishers':       publishers_filtered
                }

            else:
                self.game_info = None

        else:
            self.game_info = None

    def generate_html(self):
        """ parse the template and write it to disk """
        pass


# create local instance of GameInfo
gi = GameInfo()

def script_description():
    return """Populate local browser source with game information from IGDB.
    
Before using this plugin, you will need to obtain a Twitch API client ID and client secret.  Browse to https://dev.twitch.tv/console/apps and click "Register Your Application", then follow the instructions on the page.

NOTE: treat your client ID and secret like you would your Twitch username and password!

To customize the panel, you should become acquainted with the Jinja2 template language.  Visit https://jinja.palletsprojects.com/en/2.11.x/ for more information."""

def script_update(settings):
    """ Do something when the user changes the settings """
    pass

def script_properties():
    """ Script user interface """
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(
        props,
        "twitch_client_id",
        "Twitch Client ID",
        obs.OBS_TEXT_PASSWORD
    )

    obs.obs_properties_add_text(
        props,
        "twitch_client_secret",
        "Twitch Client Secret",
        obs.OBS_TEXT_PASSWORD
    )

    p_browser_source = obs.obs_properties_add_list(
        props,
        "browser_source",
        "Browser Source",
        obs.OBS_COMBO_TYPE_LIST,
        obs.OBS_COMBO_FORMAT_STRING
    )

    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "browser_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p_browser_source, name, name)
        
        obs.source_list_release(sources)

    obs.obs_property_set_long_description(p_browser_source, "Select the browser source that you want to be used as your gameinfo panel")

    obs.obs_properties_add_text(
        props,
        "jinja2_template",
        "Jinja2 Template",
        obs.OBS_TEXT_MULTILINE
    )

    return props

def script_defaults(settings):
    """ Define the default settings for the plugin """
    pass