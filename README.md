# Home-AssistantConfig
My Home-Assistant config

## Sensors
### [MQTT sensors](https://github.com/LaStrada/MQTT-sensors)
My MQTT sensors.

### [Template temperature/humidity sensors with fallback sensor](https://github.com/LaStrada/Home-AssistantConfig/blob/master/sensors/template.yaml#L116)
I needed a temperature sensor with a fallback sensor. Many of my temperature sensors is battery powered. I'm changing a lot of them to MQTT now (USB powered), but I wanted a fallback sensor if wifi is down.

## Custom components
- [Workday tomorrow (changed 'workday' sensor to a 'workday tomorrow' sensor)](https://github.com/LaStrada/Home-AssistantConfig/blob/master/custom_components/binary_sensor/workday_tomorrow.py)

## Climate
Scheduling thermostat with dynamic temperatures.

Scheduling:
- [Bedroom weekday](https://github.com/LaStrada/Home-AssistantConfig/blob/master/automation/heat_bedroom_weekday.yaml)
- [Bedroom weekend](https://github.com/LaStrada/Home-AssistantConfig/blob/master/automation/heat_bedroom_weekend.yaml)
- [Living room](https://github.com/LaStrada/Home-AssistantConfig/blob/master/automation/heat_living_room.yaml)
- [Office](https://github.com/LaStrada/Home-AssistantConfig/blob/master/automation/heat_office.yaml)

[Input sliders for dynamic temperatures](https://github.com/LaStrada/Home-AssistantConfig/blob/master/input_slider.yaml)
