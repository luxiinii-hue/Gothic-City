# Plan: UI Polish & Map Redesign

## 1. UI & UX Polish
### Reward Screen Interactions
**Problem:** In 
eward_state.py, if a player selects a stat buff (which prompts choosing a specific character), clicking outside the character portraits does nothing. It's easy to get "stuck" if the wrong buff was clicked.
**Solution:**
- In RewardState.handle_events(), when self.awaiting_char_select is True and a MOUSEBUTTONDOWN event occurs:
- Check if the mouse position collides with any rect in self.char_rects.
- If it does **not** collide, intercept the click to cancel the selection:
  `python
  self.awaiting_char_select = False
  self.selected = None
  `
- This cleanly reverts the UI back to the 3-card buff selection.

### Character Selection Logic
**Problem:** In the team select/roster screens, clicking a different character doesn't auto-swap the selection if a character is already actively selected or placed.
**Solution:**
- Update 	eam_select_state.py (or related roster states).
- In the selection event handler, if the user clicks an unselected character portrait while another is already active, immediately clear the previous selection state and assign the newly clicked character as active.

## 4. Map Perspective Redesign
### Horizontal Map Layout
**Problem:** The current map moves top-down (vertical progression), which can feel at odds with the side-scrolling ATB combat that moves left-to-right.
**Solution:**
- In src/map/map_generator.py:
  - Swap the X and Y coordinate generation logic.
  - Nodes will be organized into "columns" (X-axis) instead of "rows" (Y-axis).
  - Adjust col_spacing and 
ow_spacing parameters to fit the 1280x720 screen horizontally. (e.g., layer_spacing_x = 180, 
ode_spacing_y = 130).
- In src/map/path_renderer.py & src/states/map_state.py:
  - Update bezier curve control points. The mid_x / mid_y offset logic should push control points vertically (offset Y) instead of horizontally (offset X) to create natural bowing between left-to-right nodes.
  - Ensure the "start" node is on the far left and the "boss" node is on the far right.
