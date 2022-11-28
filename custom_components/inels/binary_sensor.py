"""Inels binary sensor entity."""
from __future__ import annotations
from typing import Any
from dataclasses import dataclass
from collections.abc import Callable


from inelsmqtt.devices import Device
from inelsmqtt.const import GTR3_50

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

    value: Callable[[Device], Any | None]


@dataclass
class InelsBinarySensorEntityDescription(
    BinarySensorEntityDescription, InelsBinarySensorEntityDescriptionMixin
):
    """Class for describing inels binary sensors."""


async def async_setup_platfrom(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    device_list: "list[Device]" = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities: "list[InelsBinarySensor]" = []

    for device in device_list:
        if device.device_type == Platform.SENSOR:
            if device.inels_type == GTR3_50:
                entities.append(
                    InelsBinarySensor(
                        device=device,
                    )
                )

    async_add_entities(entities, True)


class InelsBinarySensor(InelsBaseEntity, BinarySensorEntity):
    """Platform class for Home Assistant."""

    entity_description: InelsBinarySensorEntityDescription

    def __init__(
        self, device: Device, description: InelsBinarySensorEntityDescription = None
    ) -> None:
        """Initialize the sensor."""
        super().__init__(device)

        self.entity_description = description
        self._attr_unique_id = f"{self._attr_unique_id}-{description.key}"

        if description.name:
            self._attr_name = f"{self._attr_name}-{description.name}"

        self._attr_native_value = self.entity_description.value(self._device)

    def _callback(self, new_value: Any) -> None:
        """Refresh data."""
        super()._callback(new_value)
        self._attr_native_value = self.entity_description.value(self._device)
