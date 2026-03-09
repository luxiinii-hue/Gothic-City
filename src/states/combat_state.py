"""Auto-battle combat screen state."""

import random
import pygame
from src.states.base_state import BaseState
from src.core.state_machine import GameState
from src.entities.enemy import EnemyData
from src.combat.ability import AbilityRegistry
from src.combat.unit import CombatUnit
from src.combat.auto_battle import AutoBattle, BattleAction
from src.animation.idle_animator import IdleAnimator
from src.animation.combat_animator import CombatAnimator
from src.animation.particles import (
    ParticleEmitter, ABILITY_PARTICLES,
    spawn_hit_sparks, spawn_death_burst,
)
from src.animation.ability_animator import AbilityAnimator
from src.ui.button import Button
from src.ui.health_bar import draw_health_bar
from src.ui.text_renderer import draw_text
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GRAY, GOLD, RED, BLUE, GREEN,
    DARK_GRAY, PANEL_BG, PANEL_BORDER,
    FONT_SIZE_SMALL, FONT_SIZE_MEDIUM, FONT_SIZE_LARGE,
    AUTO_BATTLE_ACTION_DELAY, AUTO_BATTLE_FAST_DELAY,
)


class CombatScreenState(BaseState):
    def enter(self, **kwargs):
        self.tier = kwargs.get("tier", "normal")
        self.difficulty = kwargs.get("difficulty", 1)
        am = self.game.asset_manager
        run = self.game.run_manager

        # Load ability registry
        self.ability_registry = AbilityRegistry()
        self.ability_registry.load(am.load_json("abilities.json"))

        # Create player combat units
        self.player_units: list[CombatUnit] = []
        self.player_animators: list[IdleAnimator] = []

        for char in run.get_alive_team():
            hp_override = run.team_hp[char.id]
            unit = CombatUnit.from_character(
                char,
                ability_mods=run.ability_mods.get(char.id, []),
                stat_boosts=run.stat_boosts.get(char.id, {}),
            )
            unit.hp = hp_override
            unit.max_hp = run.team_max_hp[char.id]
            self.player_units.append(unit)

            # Create idle animator
            img = am.load_image(char.sprite)
            sprite_h = 140
            aspect = img.get_width() / img.get_height()
            sprite_w = int(sprite_h * aspect)
            scaled = am.get_scaled(char.sprite, sprite_w, sprite_h)
            self.player_animators.append(IdleAnimator(scaled, char.idle_config))

        # Load and create enemy units
        enemies_data = am.load_json("enemies.json")
        all_enemies = [EnemyData.from_dict(e) for e in enemies_data]

        # Filter by tier
        tier_enemies = [e for e in all_enemies if e.tier == self.tier]
        if not tier_enemies:
            tier_enemies = [e for e in all_enemies if e.tier == "normal"]

        # Pick 1-3 enemies based on difficulty
        num_enemies = min(3, max(1, self.difficulty))
        if self.tier == "boss":
            num_enemies = 1
            tier_enemies = [e for e in all_enemies if e.tier == "boss"]
            if not tier_enemies:
                tier_enemies = [e for e in all_enemies if e.tier == "elite"]

        chosen = []
        for _ in range(num_enemies):
            chosen.append(random.choice(tier_enemies))

        self.enemy_units: list[CombatUnit] = [CombatUnit.from_enemy(e) for e in chosen]
        self.enemy_data = chosen

        # Create enemy idle animators from sprites
        self.enemy_animators: list[IdleAnimator] = []
        for edata in chosen:
            if edata.sprite:
                img = am.load_image(edata.sprite)
                sprite_h = 140
                # Boss sprites are larger
                if edata.tier == "boss":
                    sprite_h = int(140 * 1.3)
                aspect = img.get_width() / img.get_height()
                sprite_w = int(sprite_h * aspect)
                scaled = am.get_scaled(edata.sprite, sprite_w, sprite_h)
                self.enemy_animators.append(IdleAnimator(scaled, edata.idle_config))
            else:
                # Fallback: no sprite, will draw procedural
                self.enemy_animators.append(None)

        # Apply relic: start_block
        for relic in run.relics:
            if relic.get("effect") == "start_block":
                for unit in self.player_units:
                    unit.block += int(relic.get("value", 0))

        # Auto-battle engine
        self.battle = AutoBattle(self.player_units, self.enemy_units,
                                 self.ability_registry)

        # Combat animator
        self.combat_animator = CombatAnimator()

        # Particle emitter
        self.particle_emitter = ParticleEmitter()
        self.ability_animator = AbilityAnimator()

        # Unit positions — populated during draw for particle targeting
        self.unit_positions: dict[str, tuple] = {}

        # Action log
        self.action_log: list[tuple[str, float]] = []  # (message, age)
        self.max_log_lines = 6

        # Timing
        self.action_timer = 0.0
        self.speed_multiplier = 1.0
        self.paused = False
        self.action_delay = AUTO_BATTLE_ACTION_DELAY

        # Enemy animation
        self.enemy_time = 0.0

        # End state
        self.end_delay = 0.0
        self.transitioning = False

        # UI buttons
        self.pause_btn = Button(
            SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT - 50, "Pause",
            width=100, height=35,
            on_click=self._toggle_pause,
        )
        self.speed_btn = Button(
            SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT - 50, "2x Speed",
            width=100, height=35,
            on_click=self._toggle_speed,
        )

    def _toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.text = "Resume" if self.paused else "Pause"

    def _toggle_speed(self):
        if self.speed_multiplier == 1.0:
            self.speed_multiplier = 2.0
            self.speed_btn.text = "1x Speed"
        else:
            self.speed_multiplier = 1.0
            self.speed_btn.text = "2x Speed"

    def update(self, dt: float):
        # Update animators
        for animator in self.player_animators:
            animator.update(dt)
        for animator in self.enemy_animators:
            if animator:
                animator.update(dt)
        self.combat_animator.update(dt)
        self.particle_emitter.update(dt)
        self.ability_animator.update(dt)
        self.enemy_time += dt

        # Age action log
        for i in range(len(self.action_log)):
            msg, age = self.action_log[i]
            self.action_log[i] = (msg, age + dt)
        # Remove old entries
        self.action_log = [(m, a) for m, a in self.action_log if a < 8.0]

        # Handle end transition
        if self.transitioning:
            self.end_delay -= dt
            if self.end_delay <= 0:
                run = self.game.run_manager
                if self.battle.result == "victory":
                    # Update HP back to run manager
                    hp_map = {u.id: u.hp for u in self.player_units}
                    run.update_hp_after_combat(hp_map)
                    # Add gold
                    total_gold = sum(e.gold_reward for e in self.enemy_data)
                    run.gold += total_gold
                    run.enemies_defeated += len(self.enemy_data)

                    # Check if boss defeated
                    if self.tier == "boss":
                        self.game.state_machine.transition(
                            GameState.RESULT, result="win")
                    else:
                        self.game.state_machine.transition(GameState.REWARD)
                else:
                    self.game.state_machine.transition(
                        GameState.RESULT, result="lose")
            return

        # Check for end
        if self.battle.result and not self.transitioning:
            self.transitioning = True
            self.end_delay = 2.0
            return

        # Auto-battle step
        if not self.paused:
            self.action_timer += dt * self.speed_multiplier
            delay = AUTO_BATTLE_FAST_DELAY if self.speed_multiplier > 1 else AUTO_BATTLE_ACTION_DELAY
            if self.action_timer >= delay:
                self.action_timer = 0.0
                actions = self.battle.step()
                for action in actions:
                    self._process_action(action)

    def _process_action(self, action: BattleAction):
        """Add action to log, trigger animations and particles."""
        self.action_log.append((action.message, 0.0))
        if len(self.action_log) > self.max_log_lines:
            self.action_log = self.action_log[-self.max_log_lines:]

        if action.type == "summon":
            # Target contains the enemy_id to spawn
            enemy_id = action.target
            num_to_spawn = max(1, action.damage)
            am = self.game.asset_manager
            all_enemies = am.load_json("enemies.json")
            from src.entities.enemy import EnemyData
            all_enemy_data = [EnemyData.from_dict(e) for e in all_enemies]
            template = next((e for e in all_enemy_data if e.id == enemy_id), None)
            if template:
                for _ in range(num_to_spawn):
                    # Make a unique name
                    spawn_name = f"{template.name} {len(self.enemy_units)+1}"
                    template_copy = EnemyData.from_dict(next(e for e in all_enemies if e["id"] == enemy_id))
                    template_copy.name = spawn_name
                    new_unit = CombatUnit.from_enemy(template_copy)
                    self.enemy_units.append(new_unit)
                    self.enemy_data.append(template_copy)
                    # Add to battle
                    self.battle.enemy_units.append(new_unit)
                    # Create animator
                    if template.sprite:
                        img = am.load_image(template.sprite)
                        sprite_h = 140
                        aspect = img.get_width() / img.get_height()
                        sprite_w = int(sprite_h * aspect)
                        scaled = am.get_scaled(template.sprite, sprite_w, sprite_h)
                        self.enemy_animators.append(IdleAnimator(scaled, template.idle_config))
                    else:
                        self.enemy_animators.append(None)
            # Spawn summon animation at source position
            source_pos = self.unit_positions.get(action.source)
            if source_pos:
                summon_ability = self.ability_registry.get("summon_cultist")
                if summon_ability and summon_ability.animation:
                    self.ability_animator.spawn_from_config(
                        source_pos[0], source_pos[1], summon_ability.animation)
            return

        # Trigger combat animations
        if action.type in ("attack", "ability") and action.damage > 0:
            target_key = action.target
            self.combat_animator.add_shake(target_key, intensity=4, duration=0.2)
            self.combat_animator.add_flash(target_key, color=(255, 255, 200), duration=0.15)

            # Spawn particles at target position
            pos = self.unit_positions.get(target_key)
            if pos:
                tx, ty = pos
                if action.type == "ability" and action.ability_name in ABILITY_PARTICLES:
                    ABILITY_PARTICLES[action.ability_name](self.particle_emitter, tx, ty)
                else:
                    spawn_hit_sparks(self.particle_emitter, tx, ty)

                # Spawn sprite-based ability animation
                if action.type == "ability" and action.ability_name:
                    ability_def = self.ability_registry.get_by_name(action.ability_name)
                    if ability_def and ability_def.animation:
                        self.ability_animator.spawn_from_config(tx, ty, ability_def.animation)

                # Floating damage number
                self.particle_emitter.add_floating_number(
                    tx, ty - 20, str(action.damage), (255, 80, 80))

            # Floating heal number
            if action.heal > 0:
                source_pos = self.unit_positions.get(action.source)
                if source_pos:
                    self.particle_emitter.add_floating_number(
                        source_pos[0], source_pos[1] - 20,
                        f"+{action.heal}", (80, 255, 80))

        if action.type == "defeat":
            self.combat_animator.add_flash(action.target, color=(255, 0, 0), duration=0.4)
            pos = self.unit_positions.get(action.target)
            if pos:
                spawn_death_burst(self.particle_emitter, pos[0], pos[1])

        if action.type == "dodge":
            self.combat_animator.add_flash(action.target, color=(100, 200, 255), duration=0.2)

    def _get_bg(self) -> pygame.Surface:
        if not hasattr(self, "_bg_cache"):
            bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            try:
                img = self.game.asset_manager.get_scaled(
                    "Potential assets/backgrounds/background 1/orig.png",
                    SCREEN_WIDTH, SCREEN_HEIGHT)
                bg.blit(img, (0, 0))
                # Very heavy darkening for combat readability
                dark = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                dark.fill((5, 5, 15, 200))
                bg.blit(dark, (0, 0))
            except Exception:
                bg.fill((20, 18, 25))
            self._bg_cache = bg
        return self._bg_cache

    def draw(self, surface: pygame.Surface):
        surface.blit(self._get_bg(), (0, 0))

        # Draw player units (left side, stacked vertically)
        self._draw_player_side(surface)

        # Draw enemy units (right side)
        self._draw_enemy_side(surface)

        # Particles (drawn after units, before result overlay)
        self.particle_emitter.draw(surface)
        self.ability_animator.draw(surface)

        # Action log
        self._draw_action_log(surface)

        # Turn indicator
        draw_text(surface, f"Round {self.battle.turn}",
                  SCREEN_WIDTH // 2, 15,
                  size=FONT_SIZE_SMALL, color=GRAY, center=True)

        # Speed controls
        if not self.transitioning:
            self.pause_btn.draw(surface)
            self.speed_btn.draw(surface)

        # Result overlay
        if self.battle.result:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            surface.blit(overlay, (0, 0))
            if self.battle.result == "victory":
                result_text = "VICTORY!"
                result_color = GOLD
            else:
                result_text = "DEFEAT..."
                result_color = RED
            draw_text(surface, result_text, SCREEN_WIDTH // 2,
                      SCREEN_HEIGHT // 2,
                      size=FONT_SIZE_LARGE, color=result_color, center=True, font_type="title")

    def _draw_player_side(self, surface: pygame.Surface):
        """Draw player units stacked on the left."""
        num = len(self.player_units)
        start_y = 150
        spacing = min(200, (SCREEN_HEIGHT - 300) // max(num, 1))

        for i, (unit, animator) in enumerate(zip(self.player_units, self.player_animators)):
            cx = 180
            foot_y = start_y + i * spacing + 100

            # Store position for particle targeting
            self.unit_positions[unit.name] = (cx, foot_y - 50)

            # Combat animator offset
            ox, oy = self.combat_animator.get_offset(unit.name)

            if unit.alive:
                animator.draw(surface, int(cx + ox), int(foot_y + oy))
            else:
                # Draw greyed out
                grey_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
                grey_surf.fill((60, 60, 60, 100))
                surface.blit(grey_surf, (cx - 40, foot_y - 80))

            # Name
            name_color = WHITE if unit.alive else DARK_GRAY
            draw_text(surface, unit.name, cx, foot_y + 15,
                      size=FONT_SIZE_SMALL, color=name_color, center=True)

            # HP bar
            hp_color = RED if unit.alive else DARK_GRAY
            draw_health_bar(surface, cx - 60, foot_y + 30, 120, 14,
                            unit.hp, unit.max_hp, color=hp_color)

            # Block indicator
            if unit.block > 0:
                pygame.draw.circle(surface, BLUE, (cx - 70, foot_y + 37), 12)
                draw_text(surface, str(unit.block), cx - 70, foot_y + 37,
                          size=FONT_SIZE_SMALL, color=WHITE, center=True)

            # Flash overlay
            flash = self.combat_animator.get_flash(unit.name)
            if flash:
                flash_surf = pygame.Surface((160, 160), pygame.SRCALPHA)
                flash_surf.fill(flash)
                surface.blit(flash_surf, (cx - 80, foot_y - 120))

    def _draw_enemy_side(self, surface: pygame.Surface):
        """Draw enemy units stacked on the right — using sprite animators."""
        import math
        num = len(self.enemy_units)
        start_y = 150
        spacing = min(200, (SCREEN_HEIGHT - 300) // max(num, 1))

        for i, (unit, edata, animator) in enumerate(
                zip(self.enemy_units, self.enemy_data, self.enemy_animators)):
            cx = SCREEN_WIDTH - 220
            foot_y = start_y + i * spacing + 100

            # Store position for particle targeting
            self.unit_positions[unit.name] = (cx, foot_y - 50)

            ox, oy = self.combat_animator.get_offset(unit.name)

            if unit.alive:
                if animator:
                    # Draw sprite with idle animation
                    animator.draw(surface, int(cx + ox), int(foot_y + oy))
                else:
                    # Fallback procedural drawing for enemies without sprites
                    t = self.enemy_time + i * 0.5
                    base_w, base_h = 80, 65
                    squish = 1.0 + 0.03 * math.sin(t * 2.5)
                    w = int(base_w * squish)
                    h = int(base_h / squish)

                    color = edata.color
                    body_rect = pygame.Rect(int(cx - w // 2 + ox),
                                            int(foot_y - h + oy), w, h)
                    pygame.draw.ellipse(surface, color, body_rect)
                    darker = tuple(max(0, c - 40) for c in color)
                    pygame.draw.ellipse(surface, darker, body_rect, width=2)

                    # Eyes
                    eye_y = int(foot_y - h * 0.65 + oy)
                    eye_l = (int(cx - 12 + ox), eye_y)
                    eye_r = (int(cx + 12 + ox), eye_y)
                    pygame.draw.circle(surface, WHITE, eye_l, 6)
                    pygame.draw.circle(surface, WHITE, eye_r, 6)
                    pygame.draw.circle(surface, (20, 20, 20), eye_l, 3)
                    pygame.draw.circle(surface, (20, 20, 20), eye_r, 3)
            else:
                grey_surf = pygame.Surface((80, 65), pygame.SRCALPHA)
                grey_surf.fill((60, 60, 60, 100))
                surface.blit(grey_surf, (cx - 40, foot_y - 65))

            # Name
            name_color = WHITE if unit.alive else DARK_GRAY
            draw_text(surface, unit.name, cx, foot_y + 10,
                      size=FONT_SIZE_SMALL, color=name_color, center=True)

            # HP bar
            hp_color = RED if unit.alive else DARK_GRAY
            draw_health_bar(surface, cx - 60, foot_y + 25, 120, 14,
                            unit.hp, unit.max_hp, color=hp_color)

            # Block
            if unit.block > 0:
                pygame.draw.circle(surface, BLUE, (cx + 70, foot_y + 32), 12)
                draw_text(surface, str(unit.block), cx + 70, foot_y + 32,
                          size=FONT_SIZE_SMALL, color=WHITE, center=True)

            # Flash
            flash = self.combat_animator.get_flash(unit.name)
            if flash:
                flash_surf = pygame.Surface((140, 140), pygame.SRCALPHA)
                flash_surf.fill(flash)
                surface.blit(flash_surf, (cx - 70, foot_y - 100))

    def _draw_action_log(self, surface: pygame.Surface):
        """Draw action log at bottom center."""
        log_x = SCREEN_WIDTH // 2
        log_y = SCREEN_HEIGHT - 160
        for i, (msg, age) in enumerate(reversed(self.action_log)):
            alpha = max(0, min(255, int(255 * (1.0 - age / 8.0))))
            if alpha <= 0:
                continue
            color = (*WHITE[:3], alpha) if alpha < 255 else WHITE
            draw_text(surface, msg, log_x, log_y + i * 18,
                      size=FONT_SIZE_SMALL, color=color, center=True)

    def handle_event(self, event: pygame.event.Event):
        if self.transitioning:
            return
        self.pause_btn.handle_event(event)
        self.speed_btn.handle_event(event)
