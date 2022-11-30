"""Inels binary sensor entity."""
from __future__ import annotations
from typing import Any
from dataclasses import dataclass
from collections.abc import Callable


from inelsmqtt.devices import Device
from inelsmqtt.const import GTR3_50, GSB3_90SX

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, TEMP_CELSIUS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .base_class import InelsBaseEntity
from .base_class import InelsBaseEntity
from .const import (
    DEVICES,
    DOMAIN,
    LOGGER,
)


@dataclass
class InelsBinarySensorEntityDescriptionMixin:
    """Mixin keys."""

    value: Callable[[Device, int], Any | None]


@dataclass
class InelsBinarySensorEntityDescription(
    BinarySensorEntityDescription, InelsBinarySensorEntityDescriptionMixin
):
    """Class for describing inels binary sensors."""


def __get_button_state(device: Device, id: int) -> str | None:
    return "hello"


BINARY_SENSOR_DESCRIPTION: "tuple[InelsBinarySensorEntityDescription, ...]" = (
    InelsBinarySensorEntityDescription(
        key="dn1",
        name="Digital input 1",
        # icon =
        value=__get_button_state,
    ),
    InelsBinarySensorEntityDescription(
        key="dn2",
        name="Digital input 2",
        # icon =
        value=__get_button_state,
    ),
    InelsBinarySensorEntityDescription(
        key="sw1",
        name="Switch 1",
        # icon =
        value=__get_button_state,
    ),
    InelsBinarySensorEntityDescription(
        key="sw2",
        name="Switch 2",
        # icon =
        value=__get_button_state,
    ),
    InelsBinarySensorEntityDescription(
        key="sw3",
        name="Switch 3",
        # icon =
        value=__get_button_state,
    ),
    InelsBinarySensorEntityDescription(
        key="sw4",
        name="Switch 4",
        # icon =
        value=__get_button_state,
    ),
    InelsBinarySensorEntityDescription(
        key="sw5",
        name="Switch 5",
        # icon =
        value=__get_button_state,
    ),
    InelsBinarySensorEntityDescription(
        key="plus",
        name="Plus button",
        # icon =
        value=__get_button_state,
    ),
    InelsBinarySensorEntityDescription(
        key="minus",
        name="Minus button",
        # icon =
        value=__get_button_state,
    ),
)


async def async_setup_platfrom(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load Inels binary sensors."""

    device_list: "list[Device]" = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities: "list[InelsBinarySensor]" = []

    for device in device_list:
        if device.device_type == Platform.SENSOR:
            if device.inels_type == GSB3_90SX:  # GTR3_50:
                descriptions = BINARY_SENSOR_DESCRIPTION
                for description in descriptions:
                    entities.append(
                        InelsBinarySensor(
                            device=device,
                            description=description,
                        )
                    )

    async_add_entities(entities, True)


class InelsBinarySensor(InelsBaseEntity, BinarySensorEntity):
    """Platform class for Home Assistant."""

    entity_description: InelsBinarySensorEntityDescription

    def __init__(
        self, device: Device, *, description: InelsBinarySensorEntityDescription = None
    ) -> None:
        """Initialize the sensor."""
        super().__init__(device)

        self.entity_description = description
        self._attr_unique_id = f"{self._attr_unique_id}-{description.key}"

        if description.name:
            self._attr_name = f"{self._attr_name}-{description.name}"

        self._attr_native_value = self.entity_description.value(
            self._device,
        )

    def _callback(self, new_value: Any) -> None:
        """Refresh data."""
        super()._callback(new_value)
        self._attr_native_value = self.entity_description.value(self._device)
