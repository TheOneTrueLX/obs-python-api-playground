import obspython as obs

#######################################################################
# smw_exit_counter.py - turns a text source in OBS into a rudimentary
#                       exit counter for Super Mario World.
########################################################################
# How to use:
# 
# 1. Install python 3.6.x onto the same system as your OBS installation
# 2. Copy this script somewhere onto your computer
# 3. Create a "Text (GDI+)" source and name it something like
#    "SMW Counter"
# 4. In OBS, go to "Tools" -> "Scripts"
# 5. Under the "Python Settings" tab, make sure the Python path is set
#    to wherever python is installed on your computer
# 6. Under the "Scripts" tab, click on the "+" button and browse to
#    this script
# 7. If everything worked, you should see configuration settings on the
#    right side of the scripts window.  Select the "Text Source" that
#    corresponds with the source you want to use for your counter.
# 8. Now, go to "File" -> "Settings", and under "Hotkeys", set some
#    sensible hotkeys for:
#      "SMW Counter: Increment"
#      "SMW Counter: Decrement"
#      "SMW Counter: Reset"
#
# Now, when you hit the hotkeys you set in step #8, the counter will
# increment or decrement, or reset to zero.
#
# The default settings are stock for vanilla SMW, but you can adjust
# them for things like romhacks that have different exit counts.
#
# Also, the settings should persist across 
#
########################################################################

class SMWCounter(object):
    def __init__(self, source=None, counter_start=0, counter_max=96):
        self.source = source
        self.counter = counter_start
        self.counter_max = counter_max

    def update_counter(self):
        source = obs.obs_get_source_by_name(self.source)
        if source is not None:
            data = "Exits: {}/{}".format(self.counter, self.counter_max)
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
        description = "SMW Exit Counter: " + str(self._id)
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


def script_update(settings):
    ctr.source = obs.obs_data_get_string(settings, "text_source")
    ctr.counter = obs.obs_data_get_int(settings, "counter_start")
    ctr.counter_max = obs.obs_data_get_int(settings, "counter_max")
    ctr.update_counter()

def script_description():
    return """Turns a text source into a basic exit counter for Super Mario World (controlled by hotkeys)"""

def script_properties():
    props = obs.obs_properties_create()

    obs.obs_properties_add_int(
        props,
        "counter_start",
        "Counter Start",
        0,
        999,
        0
    )

    obs.obs_properties_add_int(
        props,
        "counter_max",
        "Counter Max",
        0,
        999,
        0
    )

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
    obs.obs_data_set_int(settings, "counter_start", 0)
    obs.obs_data_set_int(settings, "counter_max", 96)