"""Inelse sensor entity."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from operator import itemgetter
from typing import Any

from inelsmqtt.const import (
    # Data types
    BATTERY,
    TEMP_IN,
    TEMP_OUT,
    LIGHT_IN,
    AIN,
    HUMIDITY,
    DEW_POINT,
    # Inels types
    RFTI_10B,
    SA3_01B,
    DA3_22M,
    GTR3_50,
    GSB3_90SX,
    # Device data types
    TEMP_SENSOR_DATA,
    RELAY_DATA,
    TWOCHANNELDIMMER_DATA,
    THERMOSTAT_DATA,
    BUTTONARRAY_DATA,
)
from inelsmqtt.devices import Device

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, TEMP_CELSIUS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import (
    DEVICES,
    DOMAIN,
    ICON_BATTERY,
    ICON_TEMPERATURE,
    ICON_HUMIDITY,
    ICON_DEW_POINT,
    ICON_LIGHT_IN,
)

# TODO
# ask how to better add the data structure for reference


@dataclass
class InelsSensorEntityDescriptionMixin:
    """Mixin keys."""

    value: Callable[[Device], Any | None]


@dataclass
class InelsSensorEntityDescription(
    SensorEntityDescription, InelsSensorEntityDescriptionMixin
):
    """Class for describing inels entities."""


def _process_data(data: str, indexes: list) -> str:
    """Process data for specific type of measurements."""
    array = data.split("\n")[:-1]
    data_range = itemgetter(*indexes)(array)
    range_joined = "".join(data_range)

    return f"0x{range_joined}"


def __get_battery_level(
    device: Device, data_struct: dict[str, list[int]]
) -> int | None:
    """Get battery level of the device."""
    if device.is_available is False:
        return None

    # then get calculate the battery. In our case is 100 or 0
    return 100 if int(_process_data(device.state, data_struct[BATTERY]), 16) == 0 else 0


def __get_temperature_in(
    device: Device, data_struct: dict[str, list[int]]
) -> float | None:
    """Get temperature inside."""
    if device.is_available is False:
        return None

    return int(_process_data(device.state, data_struct[TEMP_IN]), 16) / 100


def __get_temperature_out(
    device: Device, data_struct: dict[str, list[int]]
) -> float | None:
    """Get temperature outside."""
    if device.is_available is False:
        return None

    return int(_process_data(device.state, data_struct[TEMP_OUT]), 16) / 100


def __get_light_intensity(
    device: Device,
    data_struct: dict[str, list[int]],
) -> float | None:
    """Get light intensity."""
    if device.is_available is False:
        return None

    return int(_process_data(device.state, data_struct[LIGHT_IN]), 16) / 100


def __get_analog_temperature(
    device: Device, data_struct: dict[str, list[int]]
) -> float | None:
    """Get analog temperature."""
    if device.is_available is False:
        return None

    return int(_process_data(device.state, data_struct[AIN]), 16) / 100


def __get_humidity(device: Device, data_struct: dict[str, list[int]]) -> float | None:
    """Get humidity."""
    if device.is_available is False:
        return None

    return int(_process_data(device.state, data_struct[HUMIDITY]), 16) / 100


def __get_dew_point(device: Device, data_struct: dict[str, list[int]]) -> float | None:
    """Get dew point."""
    if device.is_available is False:
        return None

    return int(_process_data(device.state, data_struct[DEW_POINT]), 16) / 100


# RFTI_10B

SENSOR_DESCRIPTION_TEMPERATURE: "tuple[InelsSensorEntityDescription, ...]" = (
    InelsSensorEntityDescription(
        key="battery_level",
        name="Battery",
        device_class=SensorDeviceClass.BATTERY,
        icon=ICON_BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        value=__get_battery_level,
    ),
    InelsSensorEntityDescription(
        key="temp_in",
        name="Temperature In",
        device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_temperature_in,
    ),
    InelsSensorEntityDescription(
        key="temp_out",
        name="Temperature Out",
        device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_temperature_out,
    ),
)

# SA3_01B
# DA3_22M
SENSOR_DESCRIPTION_TEMPERATURE_GENERIC: "tuple[InelsSensorEntityDescription, ...]" = (
    InelsSensorEntityDescription(
        key="temp_in",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_temperature_in,
    ),
)

# GTR3_50
# GSB3_90SX
SENSOR_DESCRIPTION_MULTISENSOR: "tuple[InelsSensorEntityDescription, ...]" = (
    InelsSensorEntityDescription(
        key="temp_in",
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_temperature_in,
    ),
    InelsSensorEntityDescription(
        key="light_in",
        name="Light intensity",
        device_class=SensorDeviceClass.ILLUMINANCE,
        icon=ICON_LIGHT_IN,
        native_unit_of_measurement="lux",
        value=__get_light_intensity,
    ),
    InelsSensorEntityDescription(
        key="ain",
        name="Analog temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_TEMPERATURE,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_analog_temperature,
    ),
    InelsSensorEntityDescription(
        key="humidity",
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        icon=ICON_HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        value=__get_humidity,
    ),
    InelsSensorEntityDescription(
        key="dew_point",
        name="Dew point",
        device_class=SensorDeviceClass.TEMPERATURE,
        icon=ICON_DEW_POINT,
        native_unit_of_measurement=TEMP_CELSIUS,
        value=__get_dew_point,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load Inels switch.."""
    device_list: "list[Device]" = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities: "list[InelsSensor]" = []

    # TODO find solution to avoid including data_struct to the callbacks
    for device in device_list:
        if device.device_type == Platform.SENSOR:
            if device.inels_type == RFTI_10B:
                descriptions = SENSOR_DESCRIPTION_TEMPERATURE
                data_struct = TEMP_SENSOR_DATA
            elif device.inels_type == SA3_01B:
                descriptions = SENSOR_DESCRIPTION_TEMPERATURE_GENERIC
                data_struct = RELAY_DATA
            elif device.inels_type == DA3_22M:
                descriptions = SENSOR_DESCRIPTION_TEMPERATURE_GENERIC
                data_struct = TWOCHANNELDIMMER_DATA
            elif device.inels_type == GTR3_50:
                descriptions = SENSOR_DESCRIPTION_MULTISENSOR
                data_struct = THERMOSTAT_DATA
            elif device.inels_type == GSB3_90SX:
                descriptions = SENSOR_DESCRIPTION_MULTISENSOR
                data_struct = BUTTONARRAY_DATA
            else:
                continue

            for description in descriptions:
                entities.append(
                    InelsSensor(
                        device, description=description, data_struct=data_struct
                    )
                )

    async_add_entities(entities, True)


class InelsSensor(InelsBaseEntity, SensorEntity):
    """The platform class required by Home Assistant."""

    entity_description: InelsSensorEntityDescription
    data_struct: dict[str, list[int]]

    def __init__(
        self,
        device: Device,
        description: InelsSensorEntityDescription,
        data_struct: dict[str, list[int]],
    ) -> None:
        """Initialize a sensor."""
        super().__init__(device=device)

        self.entity_description = description
        self._attr_unique_id = f"{self._attr_unique_id}-{description.key}"

        if description.name:
            self._attr_name = f"{self._attr_name}-{description.name}"

        self._attr_native_value = self.entity_description.value(
            self._device, data_struct
        )

        self.data_struct = data_struct

    def _callback(self, new_value: Any) -> None:
        """Refresh data."""
        super()._callback(new_value)
        self._attr_native_value = self.entity_description.value(
            self._device, self.data_struct
        )
