# =========================================================
# HINTERGRUND – einfaches Gras-Gitter
# =========================================================
def draw_background(surface):
    surface.fill(DARK_GREEN)
    for gx in range(0, WIDTH, 40):
        pygame.draw.line(surface, (0, 60, 0), (gx, 0), (gx, HEIGHT))
    for gy in range(0, HEIGHT, 40):
        pygame.draw.line(surface, (0, 60, 0), (0, gy), (WIDTH, gy))
