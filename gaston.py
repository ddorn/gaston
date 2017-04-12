"""
A module to visualise G(E) for a given E
"""
from time import time

try:
    import pygame
    from pygame import gfxdraw
    from pygame.locals import *
    from pygame.math import Vector2
except ImportError:
    print("Pygame isn't installed")
    input("Press ENTER to quit...")
    quit()

    Vector2 = lambda *args: None

pygame.init()

WHITE = [255, 255, 255]
BLACK = [0, 0, 0]
GREY_75 = [64, 64, 64]
GREY_25 = [192, 192, 192]
RED = [255, 0, 0]
BLUE = [0, 0, 255]
GREEN = [0, 255, 0]
E_COLOR = [28, 197, 216]
D_COLOR = [229, 148, 9]
M_COLOR = [255, 218, 38]

SCREEN_SIZE = (700, 700)
GRID_SIZE = 30

E = []
G = []
DELTAS = []
MARKERS = []
CONFIGS = [[] for _ in range(10)]

FONT = pygame.font.Font(None, 30)

def gcd(a, b, *args):
    if not (a and b):  # one is zero
        if args:
            return gcd(a + b, *args)
        return a + b

    a = abs(a)
    b = abs(b)

    if a < b:
        a, b = b, a

    while a % b and b % a:
        b, a = a % b, b

    if args:
        return gcd(b, *args)

    return b


def convex_hull(points):
    """Computes the convex hull of a set of 2D points.

    Input: an iterable sequence of (x, y) pairs representing the points.
    Output: a list of vertices of the convex hull in counter-clockwise order,
      starting from the vertex with the lexicographically smallest coordinates.
    Implements Andrew's monotone chain algorithm. O(n log n) complexity.
    """

    # Sort the points lexicographically (tuples are compared lexicographically).
    # Remove duplicates to detect the case we have just one unique point.
    points = [(x, y) for x, y in points]
    points = sorted(set(points))

    # Boring case: no points or a single point, possibly repeated multiple times.
    if len(points) <= 1:
        return points

    # 2D cross product of OA and OB vectors, i.e. z-component of their 3D cross product.
    # Returns a positive value, if OAB makes a counter-clockwise turn,
    # negative for clockwise turn, and zero if the points are collinear.
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    # Build lower hull
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    # Build upper hull
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    # Concatenation of the lower and upper hulls gives the convex hull.
    # Last point of each list is omitted because it is repeated at the beginning of the other list.
    return [Vector2(v) for v in lower[:-1] + upper[:-1]]


def calculate_deltalines(e):
    if len(e) > 2:
        g_lines = []
        for A, B in zip(e, e[1:] + e[:1]):
            a = int(A.y - B.y)
            b = int(B.x - A.x)
            c = int(A.x * B.y - B.x * A.y)

            gcdivisor = gcd(a, b, c)

            a = a // gcdivisor
            b = b // gcdivisor
            c = c // gcdivisor + 1

            # print(f"{a}x + {b}y + {c} = 0")
            g_lines.append([a, b, c])

        return g_lines
    else:
        return []


def calculate_g_e(g_lines):
    g = []
    for x in range(SCREEN_SIZE[0] // GRID_SIZE + 2):
        for y in range(SCREEN_SIZE[1] // GRID_SIZE + 2):
            in_d_poly = True
            in_e_poly = True
            for a, b, c in g_lines:
                if a * x + b * y + c < 0:
                    in_d_poly = False

                if a * x + b * y + c - 1 < 0:
                    in_e_poly = False

            if in_d_poly and not in_e_poly:
                g.append(Vector2(x, y))

    return g


def draw_grid(screen):
    for x in range(GRID_SIZE, SCREEN_SIZE[0], GRID_SIZE):
        gfxdraw.vline(screen, x, 0, SCREEN_SIZE[1], GREY_25)

    for y in range(GRID_SIZE, SCREEN_SIZE[1], GRID_SIZE):
        gfxdraw.hline(screen, 0, SCREEN_SIZE[0], y, GREY_25)


def draw_d_lines(screen, l_eq):
    for a, b, c in l_eq:
        if b != 0:
            m = -a / b
            p = -c / b
            point1 = m * 0 + p
            point2 = m * (SCREEN_SIZE[1] / GRID_SIZE) + p

            point1 *= GRID_SIZE
            point2 *= GRID_SIZE

            gfxdraw.line(screen, 0, int(point1), SCREEN_SIZE[0], int(point2), D_COLOR)
        else:
            gfxdraw.vline(screen, int(-c / a * GRID_SIZE), 0, SCREEN_SIZE[0], D_COLOR)


def draw_poly_e(screen, E):
    if len(E) > 2:
        points = [(GRID_SIZE * x, GRID_SIZE * y) for x, y in E]
        gfxdraw.filled_polygon(screen, points, E_COLOR)
        gfxdraw.aapolygon(screen, points, BLACK)

    # if E is a line
    elif len(E) == 2:
        A, B = E
        gfxdraw.line(screen, int(A.x * GRID_SIZE), int(A.y * GRID_SIZE), int(B.x * GRID_SIZE), int(B.y * GRID_SIZE),
                     BLACK)


def draw_dots(screen, vertices, color):
    for x, y in vertices:
        x = int(x * GRID_SIZE)
        y = int(y * GRID_SIZE)
        gfxdraw.filled_circle(screen, x, y, 4, color)
        gfxdraw.aacircle(screen, x, y, 4, BLACK)


def main():
    global GRID_SIZE, E, G, MARKERS, DELTAS
    screen = pygame.display.set_mode(SCREEN_SIZE)

    running = True
    while running:

        # checking for events
        mouse_x, mouse_y = Vector2(pygame.mouse.get_pos()) + Vector2(GRID_SIZE, GRID_SIZE) // 2

        event_list = pygame.event.get()
        for event in event_list:
            if event.type == QUIT:
                running = False

            elif event.type == KEYDOWN:
                # quit
                if event.key == K_ESCAPE:
                    running = False

                # E = Conv(G(E))
                if event.key == K_g:
                    E = convex_hull(G)
                    DELTAS = calculate_deltalines(E)
                    G = calculate_g_e(DELTAS)

                # save picture
                if event.key == K_s:
                    name = f"{int(time())}.png"
                    pygame.image.save(screen, name)
                    print(f"Image saved to {name}")

                # delete the drawing
                if event.key == K_DELETE:
                    E = []
                    DELTAS = []
                    G = []

                # take back or save a config
                if event.unicode.isdigit():
                    place = int(event.unicode)

                    # save
                    if event.mod & KMOD_ALT:
                        CONFIGS[place] = list(E)

                    # take
                    else:
                        E = list(CONFIGS[place])
                        DELTAS = calculate_deltalines(E)
                        G = calculate_g_e(DELTAS)

            elif event.type == MOUSEBUTTONUP:

                # place or remove a point of E
                if event.button == 1:
                    new_point = Vector2(mouse_x, mouse_y) // GRID_SIZE
                    if new_point in E:
                        E.remove(new_point)
                    else:
                        E.append(new_point)

                    E = convex_hull(E)
                    DELTAS = calculate_deltalines(E)
                    G = calculate_g_e(DELTAS)

                # right click --> marker point
                if event.button == 3:
                    new_point = Vector2(mouse_x, mouse_y) // GRID_SIZE
                    if new_point in MARKERS:
                        MARKERS.remove(new_point)
                    else:
                        MARKERS.append(new_point)

            elif event.type == MOUSEBUTTONDOWN:
                # change the size of the grid
                if event.button == 4:
                    if GRID_SIZE > 5:
                        GRID_SIZE -= 1
                elif event.button == 5:
                    if GRID_SIZE < SCREEN_SIZE[0] // 6:
                        GRID_SIZE += 1

        screen.fill(WHITE)

        # draw E, grid, D-lines, G(E) and markers
        draw_poly_e(screen, E)
        draw_grid(screen)
        draw_d_lines(screen, DELTAS)
        draw_dots(screen, E, BLUE)
        draw_dots(screen, G, RED)
        draw_dots(screen, MARKERS, M_COLOR)

        ge = FONT.render('|G(E)| = ' + str(len(G)), True, BLACK)
        pygame.Surface.blit(screen, ge, (10, 10))

        # draw mouse
        gfxdraw.aacircle(screen, int(mouse_x // GRID_SIZE * GRID_SIZE), int(mouse_y // GRID_SIZE * GRID_SIZE), 5, BLUE)

        pygame.display.flip()


if __name__ == '__main__':
    main()
