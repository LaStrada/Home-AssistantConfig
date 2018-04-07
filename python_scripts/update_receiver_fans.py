rear_fan = 'input_number.receiver_fan_speed_rear'
internal_fan = 'input_number.receiver_fan_speed_internal'

philips_tv = data.get('philips_tv', 'home')

cpu_temp = data.get('cpu_temp', 0)
receiver_temp = data.get('receiver_temp')

current_rear_fan = data.get('current_rear_fan', 0)
current_internal_fan = data.get('current_internal_fan', 0)


def getRearSpeed(cpu, receiver, rearSpeed):
    if cpu >= 70 or receiver > 40:
        return 100

    elif cpu >= 68 or receiver > 38:
        return 90

    elif cpu >= 66 or receiver > 36:
        return 80

    elif cpu >= 64 or receiver > 34:
        return 70

    elif cpu >= 62 or receiver > 32:
        return 60

    elif cpu >= 60 or receiver > 31:
        return 50

    elif cpu >= 58 or receiver > 30:
        return 40

    elif (cpu >= 56 or receiver >= 29) and rearSpeed is not None and rearSpeed > 0:
        return 40

    return 0


def getInternalSpeed(cpu, receiver, internalSpeed):
    if cpu >= 80 or receiver > 38:
        return 100

    elif cpu >= 76 or receiver > 36:
        return 90

    elif cpu >= 74 or receiver > 35:
        return 80

    elif cpu >= 72 or receiver > 34:
        return 70

    elif cpu >= 70 or receiver > 33:
        return 60

    elif cpu >= 65 or receiver > 32:
        return 50

    elif cpu >= 62 or receiver > 31:
        return 40

    elif (cpu >= 60 or receiver >= 30) and internalSpeed is not None and internalSpeed > 0:
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
    if current_rear_fan is None or not isinstance(current_rear_fan, int):
        current_rear_fan = 0
    if current_internal_fan is None or not isinstance(current_internal_fan, int):
        current_internal_fan = 0
    try:
        if cpu_temp is None or receiver_temp is None:
            raise ValueError('Temperatures cannot be "None"')

        cpu = 0
        if isinstance(cpu_temp, float):
            cpu = float(cpu_temp)

        receiver = 0
        if isinstance(receiver_temp, float):
            receiver = float(receiver_temp)

            if philips_tv is None or philips_tv == "not_home":
                receiver -= 2

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
        rear = generateJSON(rear_fan, getRearSpeed(cpu, receiver, current_rear_fan))
        if rear is not None:
            hass.services.call('input_number', 'set_value', rear)

        internal = generateJSON(internal_fan, getInternalSpeed(cpu, receiver, current_internal_fan))
        if internal is not None:
            hass.services.call('input_number', 'set_value', internal)
