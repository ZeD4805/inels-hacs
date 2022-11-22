"""iNels light."""
from __future__ import annotations

from typing import Any, cast

from inelsmqtt.const import RFDAC_71B, DA3_22M
from inelsmqtt.devices import Device

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_TRANSITION,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .base_class import InelsBaseEntity
from .const import DEVICES, DOMAIN, ICON_LIGHT


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Load Inels lights from config entry."""
    device_list: "list[Device]" = hass.data[DOMAIN][config_entry.entry_id][DEVICES]

    entities = []

    for device in device_list:
        if device.device_type == Platform.LIGHT:
            entities.append(InelsLight(device))
        elif device.device_type == Platform.TWOCHANNELDIMMER:
            # for each light channel
            entities.append(
                InelsLightChannel(device, InelsLightChannelDescription(2, 0))
            )
            entities.append(
                InelsLightChannel(device, InelsLightChannelDescription(2, 1))
            )

    async_add_entities(entities)


class InelsLight(InelsBaseEntity, LightEntity):
    """Light class for HA."""

    def __init__(self, device: Device) -> None:
        """Initialize a light."""
        super().__init__(device=device)

        self._attr_supported_color_modes: set[ColorMode] = set()
        if self._device.inels_type is RFDAC_71B:
            self._attr_supported_color_modes.add(ColorMode.BRIGHTNESS)

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._device.state > 0

    @property
    def icon(self) -> str | None:
        """Light icon."""
        return ICON_LIGHT

    @property
    def brightness(self) -> int | None:
        """Light brightness."""
        if self._device.inels_type is not RFDAC_71B:
            return None
        return cast(int, self._device.state * 2.55)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Light to turn off."""
        if not self._device:
            return

        transition = None

        if ATTR_TRANSITION in kwargs:
            transition = int(kwargs[ATTR_TRANSITION]) / 0.065
            print(transition)
        else:
            await self.hass.async_add_executor_job(self._device.set_ha_value, 0)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Light to turn on."""
        if not self._device:
            return

        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS] / 2.55)
            brightness = min(brightness, 100)

            await self.hass.async_add_executor_job(
                self._device.set_ha_value, brightness
            )
        else:
            await self.hass.async_add_executor_job(self._device.set_ha_value, 100)


class InelsLightChannelDescription:
    """Inels light channel description."""

    def __init__(self, channel_number: int, channel_index: int):
        self.channel_number = channel_number
        self.channel_index = channel_index


class InelsLightChannel(InelsBaseEntity, LightEntity):
    """Light Channel class for HA."""

    entity_description: InelsLightChannelDescription

    def __init__(
        self, device: Device, description: InelsLightChannelDescription
    ) -> None:
        """Initialize a light."""
        super().__init__(device=device)
        self.description = description

        self._attr_unique_id = f"{self._attr_unique_id}-{description.channel_index}"
        self._attr_name = f"{self._attr_name}-{description.channel_index}"

        self._attr_supported_color_modes: set[ColorMode] = set()
        if self._device.inels_type is DA3_22M:
            self._attr_supported_color_modes.add(ColorMode.BRIGHTNESS)

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        return self._device.state.channels[self.entity_description.channel_index] > 0

    @property
    def icon(self) -> str | None:
        """Light icon."""
        return ICON_LIGHT

    @property
    def brightness(self) -> int | None:
        """Light brightness."""
        if self._device.inels_type is not DA3_22M:
            return None
        return cast(int, self._device.state.out[self.entity_description.channel_index])

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Light to turn off."""
        if not self._device:
            return

        transition = None
        if ATTR_TRANSITION in kwargs:
            transition = int(kwargs[ATTR_TRANSITION]) / 0.065
            print(transition)
        else:
            # mount device ha value
            ha_val = self._device.get_ha_value()
            ha_val.out[self.entity_description.channel_index] = 0
            await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Light to turn on"""
        if not self._device:
            return

        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS] / 2.55)
            brightness = min(brightness, 100)

            ha_val = self._device.get_ha_value()
            ha_val.out[self.entity_description.channel_index] = brightness

            await self.hass.async_add_executor_job(self._device.set_ha_value, ha_val)
