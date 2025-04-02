obs = obslua

-- These will be set via the OBS Scripts UI:
source_mouth_open = ""
source_mouth_closed = ""
audio_source = ""
threshold = 0.1

function script_description()
    return "Switches between two images based on mic audio level (currently simulated)."
end

function script_properties()
    local props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "source_mouth_open", "Mouth Open Source", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "source_mouth_closed", "Mouth Closed Source", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "audio_source", "Audio Source", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_float_slider(props, "threshold", "Audio Threshold", 0.0, 1.0, 0.01)
    return props
end

function script_update(settings)
    source_mouth_open = obs.obs_data_get_string(settings, "source_mouth_open")
    source_mouth_closed = obs.obs_data_get_string(settings, "source_mouth_closed")
    audio_source = obs.obs_data_get_string(settings, "audio_source")
    threshold = obs.obs_data_get_double(settings, "threshold")
end

-- This function is called periodically (in our case, ~30 times/sec)
function update_avatar()
    -- NOTE: This is simulating an audio level using math.random().
    -- In a real scenario, you'd retrieve the actual mic audio level via a plugin or method.
    local simulated_level = math.random()  -- random value between 0 and 1

    if simulated_level > threshold then
        set_source_visibility(source_mouth_open, true)
        set_source_visibility(source_mouth_closed, false)
    else
        set_source_visibility(source_mouth_open, false)
        set_source_visibility(source_mouth_closed, true)
    end
end



function set_source_visibility(source_name, visibility)
    local source = obs.obs_get_source_by_name(source_name)
    if source then
        local current_scene = obs.obs_frontend_get_current_scene()
        local scene_as_source = obs.obs_scene_from_source(current_scene)

        -- Pass the string (source_name), not the source object:
        local scene_item = obs.obs_scene_find_source(scene_as_source, source_name)
        if scene_item then
            obs.obs_sceneitem_set_visible(scene_item, visibility)
        end

        obs.obs_source_release(source)
    end
end

-- Start/stop the timer when streaming starts/stops
function on_event(event)
    if event == obs.OBS_FRONTEND_EVENT_STREAMING_STARTED then
        obs.timer_add(update_avatar, 33)  -- ~30 times per second
    elseif event == obs.OBS_FRONTEND_EVENT_STREAMING_STOPPED then
        obs.timer_remove(update_avatar)
    end
end

obs.obs_frontend_add_event_callback(on_event)
