# Home-AssistantConfig
My Home-Assistant config

## Sensors
### [MQTT sensors](https://github.com/LaStrada/MQTT-sensors)
My MQTT sensors.

### [Combining multiple temperature/humidity sensors](https://github.com/LaStrada/Home-AssistantConfig/blob/master/input/sensors/average_temperatures.yaml)
I'm using 'min_max' to get an average temperature/humidity. I was using a custom template before to generate this before, but it wasn't always working. If a battery sensor stops working, this will change the readings a bit, but a [battery warning automation](https://github.com/LaStrada/Home-AssistantConfig/blob/master/automation/battery.yaml) is running each evening to give me a warning.

### Plant monitoring
I'm using the [Mi Flora plan sensor component](https://www.home-assistant.io/components/sensor.miflora/). It works well, but does not have signal throug concrete walls... [This automation](https://github.com/LaStrada/Home-AssistantConfig/blob/master/automation/plant_moisture_warning.yaml) warns me every evening to remind me to give the plants some water. I also have [one input_boolean for each sensor to enable/disable notifications](https://github.com/LaStrada/Home-AssistantConfig/blob/master/input/input_booleans/plant_notifications.yaml). Very useful if a sensor is not in use, the plant has died when I'm on vacation...

## Custom components
- ~~Workday tomorrow (changed 'workday' sensor to a 'workday tomorrow' sensor).~~ [Merged into Home Assistant.](https://github.com/home-assistant/home-assistant/pull/8824)

## Climate
Scheduling thermostat with dynamic temperatures.

Scheduling:
- [Bedroom weekday](https://github.com/LaStrada/Home-AssistantConfig/blob/master/automation/heat_bedroom_weekday.yaml)
- [Bedroom weekend](https://github.com/LaStrada/Home-AssistantConfig/blob/master/automation/heat_bedroom_weekend.yaml)
- [Living room](https://github.com/LaStrada/Home-AssistantConfig/blob/master/automation/heat_living_room.yaml)
- [Office](https://github.com/LaStrada/Home-AssistantConfig/blob/master/automation/heat_office.yaml)

[Input sliders for dynamic temperatures (thermostat_*)](https://github.com/LaStrada/Home-AssistantConfig/tree/master/input/input_numbers)
