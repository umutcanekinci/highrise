from typing import TYPE_CHECKING, Any

import pygame
import webbrowser


class GameEventsMixin:
    if TYPE_CHECKING:
        # Attributes / methods supplied by the host class (Game).
        def __getattr__(self, name: str) -> Any: ...

    def _activate(self, button, event) -> bool:
        """True when the button was activated (click or focused-Space/Enter).
        Plays the button's `on_click_sound` (or the default click) on success."""
        activated = (
            button.is_clicked(event, self.mouse.position)
            or (event.type == pygame.KEYUP
                and event.key in (pygame.K_SPACE, pygame.K_RETURN)
                and getattr(button, "focused", False))
        )
        if activated:
            sound = getattr(button, "on_click_sound", None) or self.click_sound_path
            if sound is not None:
                self.audio.play_sfx(str(sound))
        return activated

    def handle_menu_events(self, event: pygame.event.Event) -> None:
        panel = self.panel_manager["menu"]
        if self._activate(panel["play_button"], event):
            self.play()
            return
        navigations = (
            ("settings_button",  "settings"),
            ("developer_button", "developer"),
            ("exit_button",      "exit"),
        )
        for button_name, dest in navigations:
            if self._activate(panel[button_name], event):
                self.open_panel(dest)

    def handle_play_events(self, event: pygame.event.Event) -> None:
        panel = self.panel_manager["play"]
        if self._activate(panel["new_game_button"], event):
            self.new_game()
        elif self._activate(panel["continue_button"], event):
            self.open_panel("game")
        elif self._activate(panel["play_back_button"], event):
            self.open_panel("menu")

    def handle_settings_events(self, event: pygame.event.Event) -> None:
        panel = self.panel_manager["settings"]
        navigations = (
            ("display_settings_button", "display_settings"),
            ("audio_settings_button",   "audio_settings"),
            ("game_settings_button",    "game_settings"),
            ("settings_back_button",    "menu"),
        )
        for button_name, dest in navigations:
            if self._activate(panel[button_name], event):
                if dest == "audio_settings":
                    self.old_music_volume = self.audio.music_volume()
                    self.old_sfx_volume = self.audio.sfx_volume()
                self.open_panel(dest)

    def handle_display_settings_events(self, event: pygame.event.Event) -> None:
        panel = self.panel_manager["display_settings"]

        if panel["window_mode_minus_button"].is_clicked(event, self.mouse.position):
            self.cycle_window_mode(-1)
            self.set_window_mode_label()
            self.set_window_size_label()
        elif panel["window_mode_plus_button"].is_clicked(event, self.mouse.position):
            self.cycle_window_mode(1)
            self.set_window_mode_label()
            self.set_window_size_label()
        elif panel["window_size_minus_button"].is_clicked(event, self.mouse.position):
            self.cycle_resolution(-1)
            self.set_window_size_label()
        elif panel["window_size_plus_button"].is_clicked(event, self.mouse.position):
            self.cycle_resolution(1)
            self.set_window_size_label()
        elif self._activate(panel["display_back_button"], event):
            self.open_panel("settings")

    def handle_audio_settings_events(self, event: pygame.event.Event) -> None:
        panel = self.panel_manager["audio_settings"]

        if panel["music_volume_plus_button"].is_clicked(event, self.mouse.position):
            new_vol = self.audio.music_volume() + 0.1
            self.audio.set_music_volume(new_vol); self.set_music_label(new_vol)
        elif panel["music_volume_minus_button"].is_clicked(event, self.mouse.position):
            new_vol = self.audio.music_volume() - 0.1
            self.audio.set_music_volume(new_vol); self.set_music_label(new_vol)
        elif panel["sfx_volume_plus_button"].is_clicked(event, self.mouse.position):
            new_vol = self.audio.sfx_volume() + 0.1
            self.audio.set_sfx_volume(new_vol); self.set_sfx_label(new_vol)
        elif panel["sfx_volume_minus_button"].is_clicked(event, self.mouse.position):
            new_vol = self.audio.sfx_volume() - 0.1
            self.audio.set_sfx_volume(new_vol); self.set_sfx_label(new_vol)
        elif self._activate(panel["cancel_button"], event):
            self.audio.set_music_volume(self.old_music_volume); self.set_music_label(self.old_music_volume)
            self.audio.set_sfx_volume(self.old_sfx_volume);   self.set_sfx_label(self.old_sfx_volume)
            self.open_panel("settings")
        elif self._activate(panel["save_button"], event):
            self.save_audio_settings()
            self.open_panel("settings")

    def handle_game_settings_events(self, event: pygame.event.Event) -> None:
        panel = self.panel_manager["game_settings"]
        if self._activate(panel["game_settings_back_button"], event):
            self.open_panel("settings")

    def handle_developer_events(self, event: pygame.event.Event) -> None:
        panel = self.panel_manager["developer"]
        if self._activate(panel["github_button"], event):
            webbrowser.open("https://www.github.com/umutcanekinci/")
        elif self._activate(panel["linkedin_button"], event):
            webbrowser.open("https://www.linkedin.com/in/umutcanekinci/")
        elif self._activate(panel["developer_back_button"], event):
            self.open_panel("menu")

    def handle_game_events(self, event: pygame.event.Event) -> None:
        panel = self.panel_manager["game"]

        if self.tile_selector.is_active:
            self.tile_selector.update_selection()

        if panel["info_panel"].active:
            if self._activate(panel["sell_button"], event):
                self.buildings.remove(self.info_panel.building)
                self.player.earn(self.info_panel.building.sell_price)
                self.info_panel.close()
                self.update_button_texts()
            elif self._activate(panel["close_button"], event):
                self.info_panel.close()
            return

        info_button = panel["selection_mode_button"]
        if self._activate(info_button, event):
            self.tile_selector.is_active = not self.tile_selector.is_active
            info_button.set_base_state("on" if self.tile_selector.is_active else "off")

        if self.tile_selector.is_active and event.type == pygame.MOUSEBUTTONUP:
            building = self.tile_selector.get_selected_building()
            if building:
                self.info_panel.refresh(building)
                self.info_panel.open()
                self.audio.play_sfx(str(self.click_sound_path))

        # Note: expand/build/next_age call methods that play their own sfx,
        # so we keep raw is_clicked here to avoid double-playing.
        if panel["expand_button"].is_clicked(event, self.mouse.position):
            self.expand()
        elif panel["build_button"].is_clicked(event, self.mouse.position):
            self.create_building()
        elif panel["next_age_button"].is_clicked(event, self.mouse.position):
            self.next_age()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                self.create_building()
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.move_buildings("right")
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.move_buildings("left")
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.move_buildings("up")
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.move_buildings("down")