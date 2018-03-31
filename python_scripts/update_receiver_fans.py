rear_fan = 'input_number.receiver_fan_speed_rear'
internal_fan = 'input_number.receiver_fan_speed_internal'

philips_tv = data.get('philips_tv')
cpu_temp = data.get('cpu_temp')
receiver_temp = data.get('receiver_temp')


def getRearSpeed(cpu, receiver):
    if philips_tv is not None or philips_tv == "not_home":
        receiver = 0
    if c > 75 or receiver > 40:
        return 100
    elif c > 76 or receiver > 38:
        return 90
    elif c > 74 or receiver > 36:
        return 80
    elif c > 72 or receiver > 35:
        return 70
    elif c > 70 or receiver > 34:
        return 60
    elif c > 65 or receiver > 33:
        return 50
    elif c > 60 or receiver > 32:
        return 40
    return 0


def getInternalSpeed(cpu, receiver):
    if philips_tv is not None or philips_tv == "not_home":
        receiver = 0
    if c > 80 or receiver > 40:
        return 100
    elif c > 78 or receiver > 38:
        return 90
    elif c > 76 or receiver > 36:
        return 80
    elif c > 74 or receiver > 35:
        return 70
    elif c > 72 or receiver > 34:
        return 60
    elif c > 70 or receiver > 33:
        return 50
    elif c > 65 or receiver > 32:
        return 40
    return 0


def generateJSON(fan, speed):
    if speed < 0 or speed > 100:
        return None
    service_data = {'entity_id': fan, 'value': speed }
    return service_data


if hass is None:
    logger.info("Hass not loaded, try again later")
else:
    try:
        if cpu_temp is None or receiver_temp is None:
            raise ValueError('Temperatures cannot be "None"')
        cpu = int(cpu_temp)
        receiver = int(receiver_temp)
    except Exception as e:
        logger.error(e)
        logger.error(cpu_temp)
        logger.error(receiver_temp)
        rear = generateJSON(rear_fan, 20)
        if rear is not None:
            hass.services.call('input_number', 'set_value', rear)

        internal = generateJSON(internal_fan, 20)
        if internal is not None:
            hass.services.call('input_number', 'set_value', internal)
    else:
        rear = generateJSON(rear_fan, getRearSpeed(cpu, receiver))
        if rear is not None:
            hass.services.call('input_number', 'set_value', rear)

        internal = generateJSON(internal_fan, getInternalSpeed(cpu, receiver))
        if internal is not None:
            hass.services.call('input_number', 'set_value', internal)
