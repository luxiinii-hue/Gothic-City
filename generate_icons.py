import pygame
import os

pygame.init()

# Ensure directories exist
icon_dir = os.path.join("character assets", "UI", "icons")
os.makedirs(icon_dir, exist_ok=True)

def create_surface(size=32):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    return surf

def draw_shadow(surf, draw_func, color, offset=(2, 2)):
    # Simple hack: draw shadow first
    draw_func(surf, (20, 20, 30))
    # Then draw main
    pass

# ---- STAT ICONS (16x16 or 24x24, we'll do 24x24) ----
def make_heart():
    s = create_surface(24)
    # Simple pixel-ish heart
    color = (220, 40, 40)
    pygame.draw.circle(s, color, (7, 8), 5)
    pygame.draw.circle(s, color, (17, 8), 5)
    pygame.draw.polygon(s, color, [(2, 10), (22, 10), (12, 20)])
    pygame.draw.polygon(s, (150, 20, 20), [(12, 20), (22, 10), (12, 10)]) # shadow side
    pygame.image.save(s, os.path.join(icon_dir, "heart.png"))

def make_coin():
    s = create_surface(24)
    color = (255, 215, 0)
    pygame.draw.circle(s, (180, 140, 0), (12, 12), 10)
    pygame.draw.circle(s, color, (12, 12), 8)
    pygame.draw.rect(s, (255, 240, 100), (10, 6, 4, 12), border_radius=2)
    pygame.image.save(s, os.path.join(icon_dir, "coin.png"))

def make_sword():
    s = create_surface(24)
    pygame.draw.line(s, (200, 200, 200), (6, 18), (18, 6), 4)
    pygame.draw.line(s, (150, 150, 150), (6, 18), (18, 6), 2)
    pygame.draw.line(s, (100, 50, 20), (4, 20), (10, 14), 3) # Crossguard
    pygame.image.save(s, os.path.join(icon_dir, "sword.png"))

def make_shield():
    s = create_surface(24)
    pygame.draw.polygon(s, (100, 150, 200), [(4, 4), (20, 4), (20, 12), (12, 22), (4, 12)])
    pygame.draw.polygon(s, (200, 200, 200), [(4, 4), (20, 4), (20, 12), (12, 22), (4, 12)], width=2)
    pygame.image.save(s, os.path.join(icon_dir, "shield.png"))

def make_boot():
    s = create_surface(24)
    pygame.draw.rect(s, (139, 69, 19), (8, 6, 8, 12), border_radius=2)
    pygame.draw.rect(s, (139, 69, 19), (8, 14, 12, 6), border_radius=2)
    pygame.draw.rect(s, (80, 40, 10), (8, 18, 12, 2))
    pygame.image.save(s, os.path.join(icon_dir, "boot.png"))

# ---- MAP ICONS (32x32) ----
def make_combat():
    s = create_surface(32)
    pygame.draw.line(s, (220, 80, 80), (8, 24), (24, 8), 4)
    pygame.draw.line(s, (220, 80, 80), (8, 8), (24, 24), 4)
    pygame.image.save(s, os.path.join(icon_dir, "node_combat.png"))

def make_elite():
    s = create_surface(32)
    pygame.draw.polygon(s, (220, 140, 40), [(16, 4), (26, 12), (20, 26), (12, 26), (6, 12)])
    pygame.draw.circle(s, (0, 0, 0), (12, 14), 2)
    pygame.draw.circle(s, (0, 0, 0), (20, 14), 2)
    pygame.image.save(s, os.path.join(icon_dir, "node_elite.png"))

def make_boss():
    s = create_surface(32)
    pygame.draw.polygon(s, (200, 40, 40), [(16, 2), (30, 10), (24, 28), (8, 28), (2, 10)])
    pygame.draw.circle(s, (0, 0, 0), (12, 16), 3)
    pygame.draw.circle(s, (0, 0, 0), (20, 16), 3)
    pygame.draw.rect(s, (0, 0, 0), (12, 22, 8, 2))
    pygame.image.save(s, os.path.join(icon_dir, "node_boss.png"))

def make_shop():
    s = create_surface(32)
    pygame.draw.circle(s, (60, 180, 60), (16, 20), 10)
    pygame.draw.rect(s, (60, 180, 60), (12, 8, 8, 12))
    pygame.draw.line(s, (200, 200, 100), (10, 12), (22, 12), 2) # tie
    pygame.image.save(s, os.path.join(icon_dir, "node_shop.png"))

def make_treasure():
    s = create_surface(32)
    pygame.draw.rect(s, (200, 150, 50), (4, 12, 24, 16), border_radius=2)
    pygame.draw.rect(s, (150, 100, 30), (4, 12, 24, 6), border_radius=2)
    pygame.draw.rect(s, (255, 255, 255), (14, 16, 4, 4)) # lock
    pygame.image.save(s, os.path.join(icon_dir, "node_treasure.png"))

def make_rest():
    s = create_surface(32)
    # logs
    pygame.draw.line(s, (100, 50, 20), (8, 26), (24, 20), 4)
    pygame.draw.line(s, (100, 50, 20), (8, 20), (24, 26), 4)
    # fire
    pygame.draw.polygon(s, (255, 100, 0), [(16, 6), (22, 20), (10, 20)])
    pygame.draw.polygon(s, (255, 200, 0), [(16, 12), (20, 20), (12, 20)])
    pygame.image.save(s, os.path.join(icon_dir, "node_rest.png"))

def make_event():
    s = create_surface(32)
    pygame.draw.circle(s, (160, 80, 200), (16, 16), 14)
    font = pygame.font.Font(None, 36)
    q = font.render("?", True, (255, 255, 255))
    s.blit(q, q.get_rect(center=(16, 16)))
    pygame.image.save(s, os.path.join(icon_dir, "node_event.png"))

make_heart()
make_coin()
make_sword()
make_shield()
make_boot()

make_combat()
make_elite()
make_boss()
make_shop()
make_treasure()
make_rest()
make_event()

print("Icons generated successfully!")
pygame.quit()
