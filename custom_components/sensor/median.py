"""
Support for displaying the median value.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.min_max/
"""
import asyncio
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, STATE_UNKNOWN, CONF_UNIT_OF_MEASUREMENT)
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_state_change

_LOGGER = logging.getLogger(__name__)

CONF_ENTITY_IDS = 'entity_ids'
CONF_ROUND_DIGITS = 'round_digits'

ICON = 'mdi:calculator'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME): cv.string,
    vol.Required(CONF_ENTITY_IDS): cv.entity_ids,
    vol.Optional(CONF_UNIT_OF_MEASUREMENT, default=None): cv.string,
    vol.Optional(CONF_ROUND_DIGITS, default=2): vol.Coerce(int),
})


@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the median sensor."""
    entity_ids = config.get(CONF_ENTITY_IDS)
    name = config.get(CONF_NAME)
    unit_of_measurement = config.get(CONF_UNIT_OF_MEASUREMENT)
    round_digits = config.get(CONF_ROUND_DIGITS)

    async_add_devices(
        [MedianSensor(hass, entity_ids, name, unit_of_measurement, round_digits)],
        True)
    return True


def calc_median(sensor_values, round_digits):
    """Calculate median value, honoring unknown states."""
    count = 0
    tempList = []
    for sval in sensor_values:
        if sval != STATE_UNKNOWN:
            count += 1
            tempList.append(sval)
    if count == 0:
        return STATE_UNKNOWN
    elif count % 2 == 1:
        val1 = tempList[int((count-1)/2)]
        val2 = tempList[int((count-1)/2) + 1]
        median = (val1 + val2) / 2
        return round(median, round_digits)
    median = tempList[(count-1) / 2]
    return round(median, round_digits)


def calc_median(sensor_values, round_digits):
    """Calculate median value, honoring unknown states."""
    count = 0
    tempList = []
    for sval in sensor_values:
        if sval != STATE_UNKNOWN:
            count += 1
            tempList.append(sval)
    if count == 0:
        return STATE_UNKNOWN
    elif count % 2 == 1:
        return round(tempList[int((count)/2)], round_digits)
    val1 = tempList[int((count)/2) - 1]
    val2 = tempList[int((count)/2)]
    median = (val1 + val2) / 2
    return round(median, round_digits)


class MedianSensor(Entity):
    """Representation of a median sensor."""

    def __init__(self, hass, entity_ids, name, unit_of_measurement, round_digits):
        """Initialize the median sensor."""
        self._hass = hass
        self._entity_ids = entity_ids
        self._round_digits = round_digits

        if name:
            self._name = name
        else:
            self._name = 'Median Sensor'
        self._unit_of_measurement = None
        self.count_sensors = len(self._entity_ids)
        self._state = STATE_UNKNOWN
        self.states = {}

        @callback
        def async_median_sensor_state_listener(entity, old_state, new_state):
            """Handle the sensor state changes."""
            if new_state.state is None or new_state.state in STATE_UNKNOWN:
                self.states[entity] = STATE_UNKNOWN
                hass.async_add_job(self.async_update_ha_state, True)
                return

            try:
                self.states[entity] = float(new_state.state)
                self.last = float(new_state.state)
            except ValueError:
                _LOGGER.warning("Unable to store state. "
                                "Only numerical states are supported")

            hass.async_add_job(self.async_update_ha_state, True)

        async_track_state_change(
            hass, entity_ids, async_median_sensor_state_listener)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return ICON

    @asyncio.coroutine
    def async_update(self):
        """Get the latest data and updates the states."""
        sensor_values = [self.states[k] for k in self._entity_ids
                         if k in self.states]
        self._state = calc_median(sensor_values, self._round_digits)
