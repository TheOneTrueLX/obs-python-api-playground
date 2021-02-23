import obspython as obs

#######################################################################
# smw_exit_counter.py - turns a text source in OBS into a rudimentary
#                       exit counter for Super Mario World.
########################################################################


class SMWCounter(object):
    def __init__(self, source=None, counter_start=0):
        self.source = source
        self.counter = counter_start
        self.counter_prefix = "Exits: "
        self.counter_suffix = ""
        self.counter_max_enabled = False
        self.counter_max = None
        self.counter_max_delimiter = None

    def update_counter(self):
        source = obs.obs_get_source_by_name(self.source)
        if source is not None:

            if self.counter_max_enabled:
                data = "{}{}{}{}{}".format(self.counter_prefix, self.counter, self.counter_max_delimiter, self.counter_max, self.counter_suffix)
            else:
                data = "{}{}{}".format(self.counter_prefix, self.counter, self.counter_suffix)

            settings = obs.obs_data_create()
            obs.obs_data_set_string(settings, "text", data)
            obs.obs_source_update(source, settings)
            obs.obs_data_release(settings)
            obs.obs_source_release(source)
        
    def increment(self):
        if self.counter < self.counter_max:
            self.counter += 1
            self.update_counter()

    def decrement(self):
        if self.counter > 0:
            self.counter -= 1
            self.update_counter()

    def reset(self):
        self.counter = 0
        self.update_counter()


class Hotkey:
    def __init__(self, callback, obs_settings, _id):
        self.obs_data = obs_settings
        self.hotkey_id = obs.OBS_INVALID_HOTKEY_ID
        self.hotkey_saved_key = None
        self.callback = callback
        self._id = _id

        self.load_hotkey()
        self.register_hotkey()
        self.save_hotkey()

    def register_hotkey(self):
        description = "LX Generic Counter: " + str(self._id)
        self.hotkey_id = obs.obs_hotkey_register_frontend(
            "htk_id" + str(self._id), description, self.callback
        )
        obs.obs_hotkey_load(self.hotkey_id, self.hotkey_saved_key)

    def load_hotkey(self):
        self.hotkey_saved_key = obs.obs_data_get_array(
            self.obs_data, "htk_id" + str(self._id)
        )
        obs.obs_data_array_release(self.hotkey_saved_key)

    def save_hotkey(self):
        self.hotkey_saved_key = obs.obs_hotkey_save(self.hotkey_id)
        obs.obs_data_set_array(
            self.obs_data, "htk_id" + str(self._id), self.hotkey_saved_key
        )
        obs.obs_data_array_release(self.hotkey_saved_key)


class h:
    htk_copy = None

ctr = SMWCounter()
h_increment = h()
h_decrement = h()
h_reset = h()

def increment_callback(pressed):
    if pressed:
        ctr.increment()

def decrement_callback(pressed):
    if pressed:
        ctr.decrement()

def reset_callback(pressed):
    if pressed:
        ctr.reset()

def counter_max_toggle_callback(props, prop, settings):
    _show_counter_max = obs.obs_data_get_bool(settings, "counter_max_value_enable")
    p_counter_max = obs.obs_properties_get(props, "counter_max")
    p_counter_max_delimiter = obs.obs_properties_get(props, "counter_max_delimiter")
    obs.obs_property_set_visible(p_counter_max, _show_counter_max)
    obs.obs_property_set_visible(p_counter_max_delimiter, _show_counter_max)
    return True

def script_update(settings):
    ctr.source = obs.obs_data_get_string(settings, "text_source")
    ctr.counter = obs.obs_data_get_int(settings, "counter_start")
    ctr.counter_prefix = obs.obs_data_get_string(settings, "counter_prefix")
    ctr.counter_suffix = obs.obs_data_get_string(settings, "counter_suffix")
    ctr.counter_max_enabled = obs.obs_data_get_bool(settings, "counter_max_value_enable")
    if ctr.counter_max_enabled:
        ctr.counter_max = obs.obs_data_get_int(settings, "counter_max")
        ctr.counter_max_delimiter = obs.obs_data_get_string(settings, "counter_max_delimiter")
    else:
        ctr.counter_max = None
        ctr.counter_max_delimiter = None
        
    ctr.update_counter()

def script_description():
    return """Turns a text source into a basic exit counter for Super Mario World (controlled by hotkeys)"""

def script_properties():
    props = obs.obs_properties_create()

    # Allows the user to set a default starting value for the counter
    # (default is 0)
    obs.obs_properties_add_int(
        props,
        "counter_start",
        "Counter Start",
        0,
        999,
        0
    )

    # Sets a text prefix for the counter
    # (default: "Exits: ")
    obs.obs_properties_add_text(
        props,
        "counter_prefix",
        "Counter Prefix",
        obs.OBS_TEXT_DEFAULT
    )

    # Sets a text suffix for the counter
    # (default: "")
    obs.obs_properties_add_text(
        props,
        "counter_suffix",
        "Counter Suffix",
        obs.OBS_TEXT_DEFAULT
    )

    # Enable a max value for the counter
    p_toggle_counter_max = obs.obs_properties_add_bool(
        props,
        "counter_max_value_enable",
        "Enable max value for counter?"
    )

    # If enabled, defines a max value for the counter
    # (Default: 999)
    p_counter_max = obs.obs_properties_add_int(
        props,
        "counter_max",
        "Counter Max",
        0,
        999,
        0
    )

    p_counter_max_delimiter = obs.obs_properties_add_text(
        props,
        "counter_max_delimiter",
        "Counter Max Delimiter",
        obs.OBS_TEXT_DEFAULT
    )

    obs.obs_property_set_long_description(p_counter_max_delimiter, "If counter_max is enabled, this string separates the counter and counter max values.")

    # Text source for the counter
    p_text_source = obs.obs_properties_add_list(
        props,
        "text_source",
        "Text Source",
        obs.OBS_COMBO_TYPE_LIST,
        obs.OBS_COMBO_FORMAT_STRING
    )

    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p_text_source, name, name)
        
    obs.source_list_release(sources)

    obs.obs_property_set_visible(p_counter_max, False)
    obs.obs_property_set_visible(p_counter_max_delimiter, False)
    obs.obs_property_set_modified_callback(p_toggle_counter_max, counter_max_toggle_callback)

    return props

def script_load(settings):
    h_increment.htk_copy = Hotkey(increment_callback, settings, "Increment")
    h_decrement.htk_copy = Hotkey(decrement_callback, settings, "Decrement")
    h_reset.htk_copy = Hotkey(reset_callback, settings, "Reset")

def script_save(settings):
    h_increment.htk_copy.save_hotkey()
    h_decrement.htk_copy.save_hotkey()
    h_reset.htk_copy.save_hotkey()

def script_defaults(settings):
    obs.obs_data_set_string(settings, "counter_prefix", "Exits: ")
    obs.obs_data_set_string(settings, "counter_suffix", "")
    obs.obs_data_set_int(settings, "counter_start", 0)
    obs.obs_data_set_int(settings, "counter_max", 999)
    obs.obs_data_set_string(settings, "counter_max_delimiter", "/")
    obs.obs_data_set_bool(settings, "counter_max_value_enable", False)