rear_fan = 'input_number.receiver_fan_speed_rear'
internal_fan = 'input_number.receiver_fan_speed_internal'

philips_tv = data.get('philips_tv', "home")

cpu_temp = data.get('cpu_temp', 0)
retropie_temp = data.get('retropie_temp', 0)
receiver_temp = data.get('receiver_temp', 0)

current_rear_fan = data.get('current_rear_fan', 0)
current_internal_fan = data.get('current_internal_fan', 0)


def getRearSpeed(cpu, receiver, rearSpeed, tv):
    if cpu >= 72 or receiver > 35:
        return 100

    elif cpu >= 70 or receiver > 34:
        return 90

    elif cpu >= 65 or receiver > 33:
        return 80

    elif cpu >= 60 or receiver > 32:
        return 70

    elif cpu >= 58 or receiver > 31:
        return 60

    elif cpu >= 56 or receiver >= 30:
        return 50

    elif (cpu >= 52 or receiver >= 28) and rearSpeed is not None and rearSpeed >= 40:
        return 40

    elif tv is not None and tv == 'home':
        return 20

    return 0


def getInternalSpeed(cpu, receiver, internalSpeed, tv):
    if cpu >= 72 or receiver > 36:
        return 100

    elif cpu >= 70 or receiver > 35:
        return 90

    elif cpu >= 64 or receiver > 34:
        return 80

    elif cpu >= 60 or receiver > 33:
        return 70

    elif cpu >= 56 or receiver > 32:
        return 60

    elif cpu >= 52 or receiver > 31:
        return 50

    elif (cpu >= 48 or receiver >= 30) and internalSpeed is not None and internalSpeed >= 40:
        return 40

    elif tv is not None and tv == 'home':
        return 20

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

    cpu = 0
    retropie = 0
    receiver = 0

    try:
        if cpu_temp is None or receiver_temp is None:
            raise ValueError('Temperatures cannot be "None"')

        cpu = float(cpu_temp)
        receiver = float(receiver_temp)

        if philips_tv is None or philips_tv == "not_home":
            receiver = receiver - 1
        else:
            philips_tv = "home"

        try:
            retropie = float(retropie_temp)
        except:
            retropie = 0

    except Exception as e:
        logger.error(e)
        logger.error(cpu_temp)
        logger.error(retropie_temp)
        logger.error(receiver_temp)
        logger.error(philips_tv)

    else:
        pi_temp = cpu
        if retropie > cpu:
            pi_temp = retropie

        rear = generateJSON(rear_fan, getRearSpeed(pi_temp, receiver, current_rear_fan, philips_tv))
        if rear is not None:
            hass.services.call('input_number', 'set_value', rear)

        internal = generateJSON(internal_fan, getInternalSpeed(pi_temp, receiver, current_internal_fan, philips_tv))
        if internal is not None:
            hass.services.call('input_number', 'set_value', internal)
