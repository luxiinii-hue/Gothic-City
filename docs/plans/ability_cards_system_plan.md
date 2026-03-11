# Plan: Ability Cards System

## Objective
Transition from hardcoded or linearly unlocked abilities to a dynamic "Ability Cards" system. Players can discover class-specific abilities during events, manage a roster of abilities for each character, and equip up to 3 active abilities at a time.

## 1. Data Structure Updates
### characters.json
- Remove the static bilities array.
- Add ctive_abilities (max 3) and bility_roster (unlocked pool).
- Include class/archetype tags (e.g., "Magic", "Fighter") to determine eligible ability card drops.

### bilities.json
- Add a "card_drop" boolean or "rarity" to abilities meant to be discovered.
- Add "class_requirement" to tie abilities to specific character archetypes (e.g., "Fireball" -> "Magic", "Sweep" -> "Fighter").

## 2. Event & Reward Integration
- Update 
ewards.json and src/states/reward_state.py to include a new "ability_card" reward type.
- During loot generation, filter available ability cards based on the classes of the current party members.
- When an ability card is chosen, add its ID to the specific character's bility_roster.

## 3. Roster & Loadout UI
- Create a new UI overlay or dedicated state (AbilityRosterState).
- **Access:** Accessible from the Map Screen (e.g., right-clicking a character in the sidebar, or a dedicated "Camp/Roster" button).
- **Layout:**
  - Left panel: The character's active loadout (3 empty or filled slots).
  - Right panel: A grid of the character's available bility_roster.
- **Interaction:** Drag-and-drop or click-to-swap logic to move abilities between the active loadout and the roster.

## 4. Specific Ability Reallocation
- Migrate existing unique character unlockables (like Nightfang's "Abyssal Smash") to become guaranteed or high-weight Ability Cards specific to that character.
