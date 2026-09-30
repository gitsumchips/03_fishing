"""
GameEngine: owns the hook and the fish, and runs one frame's worth of
game logic.
"""

import pygame

from game.hook import Hook, IDLE
from game.fish import Fish
from game.catch import check_catch
from game.renderer import WIDTH, SURFACE_Y, MAX_DEPTH_Y


class GameEngine:
    def __init__(self):
        self.round_duration = 30
        self.time_remaining = self.round_duration
        self.round_active = True
        self.round_start_time = pygame.time.get_ticks()

        self.hook = Hook(
            x=WIDTH / 2,
            surface_y=SURFACE_Y,
            max_depth_y=MAX_DEPTH_Y,
            speed=5
        )

        self.fish_list = [
            # Slow, low-value fish
            Fish(
                x=100, y=180,
                speed=1,
                width=30, height=15,
                point_value=10,
                color=(80, 180, 220)
            ),

            # Medium-speed, medium-value fish
            Fish(
                x=400, y=280,
                speed=-2,
                width=36, height=18,
                point_value=20,
                color=(80, 220, 120)
            ),

            # Fast, high-value fish
            Fish(
                x=250, y=380,
                speed=4,
                width=44, height=22,
                point_value=50,
                color=(220, 100, 80)
            ),
        ]

        self.hooked_fish = None
        self.score = 0

    def handle_input(self, event):
        """Handle player input."""

        if event.type != pygame.KEYDOWN:
            return

        # Restart after the round has ended
        if event.key == pygame.K_r and not self.round_active:
            self.reset_round()
            return

        # Start a cast only when the hook is idle
        if event.key == pygame.K_SPACE:
            if self.round_active and self.hook.state == IDLE:
                self.hook.start_cast()

    def reset_round(self):
        """Start a new 30-second round."""

        self.hook = Hook(
            x=WIDTH / 2,
            surface_y=SURFACE_Y,
            max_depth_y=MAX_DEPTH_Y,
            speed=5
        )

        self.fish_list = [
            Fish(
                x=100, y=180,
                speed=1,
                width=30, height=15,
                point_value=10,
                color=(80, 180, 220)
            ),
            Fish(
                x=400, y=280,
                speed=-2,
                width=36, height=18,
                point_value=20,
                color=(80, 220, 120)
            ),
            Fish(
                x=250, y=380,
                speed=4,
                width=44, height=22,
                point_value=50,
                color=(220, 100, 80)
            ),
        ]

        self.hooked_fish = None
        self.score = 0
        self.time_remaining = self.round_duration
        self.round_active = True
        self.round_start_time = pygame.time.get_ticks()

    def update(self):
        """Update one frame of game logic."""

        # Do nothing once the round has ended
        if not self.round_active:
            return

        # Calculate remaining time
        elapsed = (
            pygame.time.get_ticks() - self.round_start_time
        ) / 1000.0

        self.time_remaining = max(
            0,
            self.round_duration - elapsed
        )

        # End the round when the timer reaches zero
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.round_active = False

            # Stop any active hook/catch
            self.hook.state = IDLE
            self.hooked_fish = None

            return

        # Update hook
        self.hook.update()

        # Update fish
        for fish in self.fish_list:
            fish.update(WIDTH)

        # Move caught fish with hook
        if self.hooked_fish is not None:
            self.hooked_fish.x = self.hook.x
            self.hooked_fish.y = self.hook.y

            # Score only when hook reaches the surface
            if self.hook.state == IDLE:
                self.score += self.hooked_fish.point_value
                self.hooked_fish = None

        # Check for new catch
        else:
            caught = check_catch(
                self.hook,
                self.fish_list
            )

            if caught is not None:
                self.fish_list.remove(caught)
                self.hooked_fish = caught

                self.hooked_fish.x = self.hook.x
                self.hooked_fish.y = self.hook.y

                self.hook.catch_fish()

    def draw(self, surface, font):
        """Draw the game."""

        from game import renderer

        draw_list = list(self.fish_list)

        if self.hooked_fish is not None:
            draw_list.append(self.hooked_fish)

        renderer.draw_scene(
            surface,
            self.hook,
            draw_list
        )

        # Score
        renderer.draw_text(
            surface,
            font,
            f"Score: {self.score}",
            (10, 10)
        )

        # Timer
        renderer.draw_text(
            surface,
            font,
            f"Time: {int(self.time_remaining)}",
            (WIDTH - 120, 10)
        )

        # Game over message
        if not self.round_active:
            renderer.draw_banner(
                surface,
                font,
                f"ROUND OVER! Final Score: {self.score} - Press R to restart"
            )