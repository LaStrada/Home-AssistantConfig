# -*- coding: utf-8 -*-

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (ATTR_ATTRIBUTION, CONF_CURRENCY, CONF_OFFSET,
                                 CONF_REGION, CONF_NAME)
import datetime
from random import randrange
import homeassistant.helpers.config_validation as cv
import logging
import requests
import voluptuous

_LOGGER = logging.getLogger(__name__)

_CURRENCY_LIST = ['DKK', 'EUR', 'NOK', 'SEK']

_CURRENCY_FRACTION = {
    'DKK': 'Ã˜re',
    'EUR': 'Cent',
    'NOK': 'Ã˜re',
    'SEK': 'Ã–re'
}

_REGION_NAME = ['DK1', 'DK2', 'EE', 'FI', 'LT', 'LV', 'Oslo', 'Kr.sand',
                'Bergen', 'Molde', 'Tr.heim', 'TromsÃ¸', 'SE1', 'SE2', 'SE3',
                'SE4', 'SYS']

DEFAULT_CURRENCY = 'EUR'
DEFAULT_REGION = 'SYS'
DEFAULT_NAME = 'Elspot kWh'

_TODAY = 0
_TOMORROW = 1

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    voluptuous.Optional(CONF_CURRENCY, default=DEFAULT_CURRENCY):
        voluptuous.In(_CURRENCY_LIST),
    voluptuous.Optional(CONF_REGION, default=DEFAULT_REGION):
        voluptuous.In(_REGION_NAME),
    voluptuous.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    voluptuous.Optional(CONF_OFFSET, default=0): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    currency = config.get(CONF_CURRENCY)
    region = config.get(CONF_REGION)
    name = config.get(CONF_NAME)
    offset = config.get(CONF_OFFSET)
    add_devices([Nordpool(name, currency, region, offset)])


class Nordpool(Entity):

    def __init__(self, name, currency, region, offset):
        self._prices = [None, None, None, None, None, None, None, None,
                        None, None, None, None, None, None, None, None,
                        None, None, None, None, None, None, None, None,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._tomorrow = [None, None, None, None, None, None, None, None,
                          None, None, None, None, None, None, None, None,
                          None, None, None, None, None, None, None, None,
                          0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._day = [99, 99]
        self._next = [0, 0]
        self._state = None
        self._name = name
        self._failedFetch = [0, 0]
        self._min = 0
        self._max = 0
        self._average = 0
        self._peak = 0
        self._offPeak1 = 0
        self._offPeak2 = 0
        t = datetime.datetime.strptime(offset, '%H:%M:%S')
        self._offset = t.hour

        # Setup the currency fraction as unit
        self._currency = currency
        self._currency_fraction = _CURRENCY_FRACTION[currency]

        # Setup region name for correct prices
        self._region = region

        # fetch today's prices
        self.fetchNewData(_TODAY)
        # Initiate first value
        now = datetime.datetime.now() + datetime.timedelta(hours=self._offset)
        self._state = self._prices[now.hour]

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._currency_fraction

    @property
    def device_state_attributes(self):
        return {
            'Min': self._min,
            'Max': self._max,
            'Average': self._average,
            'Peak': self._peak,
            'Off-peak1': self._offPeak1,
            'Off-peak2': self._offPeak2,
            '1 next update': self._next[0],
            '2 next update': self._next[1],
            'tomorrow': self._day[1],
            ATTR_ATTRIBUTION: "For details, see https://www.nordpoolgroup.com/"
        }

    def update(self):
        now = datetime.datetime.now() + datetime.timedelta(hours=self._offset)
        # Check for new data once each day
        if self._day[_TODAY] != int(now.day) and \
                self._day[_TOMORROW] == int(now.day):
            # New day, update the data
            self._prices = list(self._tomorrow)
            self._day[_TODAY] = self._day[_TOMORROW]
            self._day[_TOMORROW] = 99

        if self._day[_TODAY] != int(now.day):
            # Fetching of prices failed. Try again
            self.fetchNewData(_TODAY)

        # Fetch new data if it is time to do so
        tomorrow = now + datetime.timedelta(days=1)
        if ((now.hour > self._next[0] or (now.hour >= self._next[0] and
                                          now.minute >= self._next[1])) and
                self._day[_TOMORROW] != tomorrow.day):
            self.fetchNewData(_TOMORROW)

        # Return the current price
        self._state = self._prices[now.hour]
        self._min = self._prices[24]
        self._max = self._prices[25]
        self._average = self._prices[26]
        self._peak = self._prices[27]
        self._offPeak1 = self._prices[28]
        self._offPeak2 = self._prices[29]

    def fetchNewData(self, selectedDay):
        now = datetime.datetime.now() + datetime.timedelta(hours=self._offset)
        if selectedDay == _TOMORROW:
            now += datetime.timedelta(days=1)
        dateToFetch = now.strftime("%d-%m-%Y")

        _LOGGER.error("Fetching Nordpool prices.")

        newData = [None, None, None, None, None, None, None, None, None, None,
                   None, None, None, None, None, None, None, None, None, None,
                   None, None, None, None,
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        self._failedFetch[selectedDay] += 1

        # Set all values to None, and set the date to the requested date
        if self._failedFetch[selectedDay] > 2:
            self._day[selectedDay] = int(dateToFetch[:2])
            if selectedDay == _TODAY:
                self._prices = list(newData)
            else:
                self._tomorrow = list(newData)

        url = "http://www.nordpoolspot.com/api/marketdata/page/10"

        params = dict(currency=self._currency,
                      endDate=dateToFetch)
        date = "Failed"

        resp = requests.get(url=url, params=params)

        data = resp.json()

        row = 0

        data = data['data']
        for rows in data['Rows']:
            for col in rows['Columns']:
                if col['Name'] == self._region:
                    price = col['Value']
                    price = price.replace(',', '.')
                    if "." not in price:
                        newData[row] = 0.0
                    else:
                        newData[row] = round(float(price) / 10, 3)
            row = row + 1
        date = data['DataStartdate']

        # Check for success
        if date[8:10] == dateToFetch[:2]:
            self._day[selectedDay] = int(date[8:10])
            self._failedFetch[selectedDay] = 0
            if selectedDay == _TODAY:
                self._prices = list(newData)
            else:
                self._tomorrow = list(newData)
            _LOGGER.error("Nordpool prices updated.")
        else:
            _LOGGER.error("Nordpool price fetch failed for " +
                          str(dateToFetch) + ". Attempt number:" +
                          str(self._failedFetch))

        self._next[0] = 16 + randrange(4)
        self._next[1] = randrange(60)
# -*- coding: utf-8 -*-

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (ATTR_ATTRIBUTION, CONF_CURRENCY, CONF_OFFSET,
                                 CONF_REGION, CONF_NAME)
import datetime
from random import randrange
import homeassistant.helpers.config_validation as cv
import logging
import requests
import voluptuous

_LOGGER = logging.getLogger(__name__)

_CURRENCY_LIST = ['DKK', 'EUR', 'NOK', 'SEK']

_CURRENCY_FRACTION = {
    'DKK': 'Ã˜re',
    'EUR': 'Cent',
    'NOK': 'Ã˜re',
    'SEK': 'Ã–re'
}

_REGION_NAME = ['DK1', 'DK2', 'EE', 'FI', 'LT', 'LV', 'Oslo', 'Kr.sand',
                'Bergen', 'Molde', 'Tr.heim', 'TromsÃ¸', 'SE1', 'SE2', 'SE3',
                'SE4', 'SYS']

DEFAULT_CURRENCY = 'EUR'
DEFAULT_REGION = 'SYS'
DEFAULT_NAME = 'Elspot kWh'

_TODAY = 0
_TOMORROW = 1

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    voluptuous.Optional(CONF_CURRENCY, default=DEFAULT_CURRENCY):
        voluptuous.In(_CURRENCY_LIST),
    voluptuous.Optional(CONF_REGION, default=DEFAULT_REGION):
        voluptuous.In(_REGION_NAME),
    voluptuous.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    # voluptuous.Optional(CONF_OFFSET, default=0): vol.Range(min=0, max=5),
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    currency = config.get(CONF_CURRENCY)
    region = config.get(CONF_REGION)
    name = config.get(CONF_NAME)
    add_devices([Nordpool(name, currency, region)])


class Nordpool(Entity):

    def __init__(self, name, currency, region):
        self._prices = [None, None, None, None, None, None, None, None,
                        None, None, None, None, None, None, None, None,
                        None, None, None, None, None, None, None, None,
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._tomorrow = [None, None, None, None, None, None, None, None,
                          None, None, None, None, None, None, None, None,
                          None, None, None, None, None, None, None, None,
                          0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self._day = [99, 99]
        self._next = [0, 0]
        self._state = None
        self._name = name
        self._failedFetch = [0, 0]
        self._min = 0
        self._max = 0
        self._average = 0
        self._peak = 0
        self._offPeak1 = 0
        self._offPeak2 = 0

        # Setup the currency fraction as unit
        self._currency = currency
        self._currency_fraction = _CURRENCY_FRACTION[currency]

        # Setup region name for correct prices
        self._region = region

        # fetch today's prices
        self.fetchNewData(_TODAY)
        # Initiate first value
        now = datetime.datetime.now()
        self._state = self._prices[now.hour]

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._currency_fraction

    @property
    def device_state_attributes(self):
        return {
            'Min': self._min,
            'Max': self._max,
            'Average': self._average,
            'Peak': self._peak,
            'Off-peak1': self._offPeak1,
            'Off-peak2': self._offPeak2,
            ATTR_ATTRIBUTION: "For details, see https://www.nordpoolgroup.com/"
        }

    def update(self):
        now = datetime.datetime.now()
        # Check for new data once each day
        if self._day[_TODAY] != int(now.day) and \
                self._day[_TOMORROW] == int(now.day):
            # New day, update the data
            self._prices = list(self._tomorrow)
            self._day[_TODAY] = self._day[_TOMORROW]
            self._day[_TOMORROW] = 99

        if self._day[_TODAY] != int(now.day):
            # Fetching of prices failed. Try again
            self.fetchNewData(_TODAY)

        # Fetch new data if it is time to do so
        tomorrow = now + datetime.timedelta(days=1)
        if ((now.hour > self._next[0] or (now.hour >= self._next[0] and
                                          now.minute >= self._next[1])) and
                self._day[_TOMORROW] != tomorrow.day):
            self.fetchNewData(_TOMORROW)

        # Return the current price
        self._state = self._prices[now.hour]
        self._min = self._prices[24]
        self._max = self._prices[25]
        self._average = self._prices[26]
        self._peak = self._prices[27]
        self._offPeak1 = self._prices[28]
        self._offPeak2 = self._prices[29]

    def fetchNewData(self, selectedDay):
        now = datetime.datetime.now()
        if selectedDay == _TOMORROW:
            now += datetime.timedelta(days=1)
        dateToFetch = now.strftime("%d-%m-%Y")

        newData = [None, None, None, None, None, None, None, None, None, None,
                   None, None, None, None, None, None, None, None, None, None,
                   None, None, None, None,
                   0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        self._failedFetch[selectedDay] += 1

        # Set all values to None, and set the date to the requested date
        if self._failedFetch[selectedDay] > 2:
            self._day[selectedDay] = int(dateToFetch[:2])
            if selectedDay == _TODAY:
                self._prices = list(newData)
            else:
                self._tomorrow = list(newData)

        url = "http://www.nordpoolspot.com/api/marketdata/page/10"

        params = dict(currency=self._currency,
                      endDate=dateToFetch)
        date = "Failed"

        resp = requests.get(url=url, params=params)

        data = resp.json()

        row = 0
        data = data['data']
        for rows in data['Rows']:
            for col in rows['Columns']:
                if col['Name'] == self._region:
                    price = col['Value']
                    price = price.replace(',', '.')
                    if "-" not in price:
                        newData[row] = round(float(price) / 10, 3)
                    else:
                        newData[row] = 0.0
            row = row + 1
        date = data['DataStartdate']

        # Check for success
        if date[8:10] == dateToFetch[:2]:
            self._day[selectedDay] = int(date[8:10])
            self._failedFetch[selectedDay] = 0
            if selectedDay == _TODAY:
                self._prices = list(newData)
            else:
                self._tomorrow = list(newData)
            _LOGGER.debug("Nordpool prices updated.")
        else:
            _LOGGER.error("Nordpool price fetch failed for " +
                          str(dateToFetch) + ". Attempt number:" +
                          str(self._failedFetch))

        self._next[0] = 16 + randrange(4)
        self._next[1] = randrange(60)