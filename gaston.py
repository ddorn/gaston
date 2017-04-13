"""
A module to visualise G(E) for a given E in the problem 2 of the TFJM2017. 
"""

from time import time

import pygame
from pygame import gfxdraw
from pygame.locals import *

pygame.init()

# colors
WHITE = [255, 255, 255]
BLACK = [0, 0, 0]
GREY_75 = [64, 64, 64]
GREY_25 = [192, 192, 192]
GREY_10 = [220, 220, 220]
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

FONT = pygame.font.Font('segoeuil.ttf', 20)


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
    return lower[:-1] + upper[:-1]


def calculate_deltalines(e):
    if len(e) > 1:
        g_lines = []
        for A, B in segments(e):
            a = int(A[1] - B[1])
            b = int(B[0] - A[0])
            c = int(A[0] * B[1] - B[0] * A[1])

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
    e_lines = [(a, b, c - 1) for a, b, c in g_lines]

    g = []
    if g_lines:
        for x in range(SCREEN_SIZE[0] // GRID_SIZE + 2):
            for y in range(SCREEN_SIZE[1] // GRID_SIZE + 2):

                if in_poly(x, y, g_lines) and not in_poly(x, y, e_lines):
                    g.append((x, y))

    # E is a point
    elif len(E) == 1:
        a, b = E[0]
        for x in range(SCREEN_SIZE[0] // GRID_SIZE + 2):
            for y in range(SCREEN_SIZE[1] // GRID_SIZE + 2):
                if gcd(abs(x - a), abs(y - b)) == 1:
                    g.append((x, y))

    return g


def in_poly(x, y, lines_eq):
    in_poly = True
    for a, b, c in lines_eq:
        if a * x + b * y + c < 0:
            in_poly = False

    return in_poly


def segments(points):
    return zip(points, points[1:] + points[:1])


def area(points):
    return 0.5 * abs(sum(x0 * y1 - x1 * y0 for ((x0, y0), (x1, y1)) in segments(points)))


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

            if abs(m) < 1:

                point1 = m * 0 + p
                point2 = m * (SCREEN_SIZE[0] / GRID_SIZE) + p

                point1 *= GRID_SIZE
                point2 *= GRID_SIZE

                gfxdraw.line(screen, 0, int(point1), SCREEN_SIZE[0], int(point2), D_COLOR)

            else:
                point1 = - p / m
                point2 = (SCREEN_SIZE[1] / GRID_SIZE - p) / m

                point1 *= GRID_SIZE
                point2 *= GRID_SIZE

                gfxdraw.line(screen, int(point1), 0, int(point2), SCREEN_SIZE[1], D_COLOR)

        else:
            gfxdraw.vline(screen, int(-c / a * GRID_SIZE), 0, SCREEN_SIZE[0], D_COLOR)


def draw_poly_e(screen, e):
    if len(e) > 2:
        points = [(GRID_SIZE * x, GRID_SIZE * y) for x, y in e]
        gfxdraw.filled_polygon(screen, points, E_COLOR)
        gfxdraw.aapolygon(screen, points, BLACK)

    # if E is a line
    elif len(e) == 2:
        a, b = e

        x1 = int(a[0] * GRID_SIZE)
        y1 = int(a[1] * GRID_SIZE)
        x2 = int(b[0] * GRID_SIZE)
        y2 = int(b[1] * GRID_SIZE)

        gfxdraw.line(screen, x1, y1, x2, y2, BLACK)


def draw_dots(screen, vertices, points_color):
    for x, y in vertices:
        x = int(x * GRID_SIZE)
        y = int(y * GRID_SIZE)
        gfxdraw.filled_circle(screen, x, y, 4, points_color)
        gfxdraw.aacircle(screen, x, y, 4, BLACK)


def to_tikz(e, deltas, g):
    s = r"""
    \begin{figure}[h!]
    \begin{center}
    \begin{tikzpicture}[line cap=round,line join=round,>=triangle 45,x=1cm,y=1cm]
    \draw [color=cqcqcq,, xstep=1,ystep=1] (-0.5, -0.5) grid""" + "({0}, {1});".format(SCREEN_SIZE[0] // GRID_SIZE-0.5,
                                                                                 SCREEN_SIZE[1] // GRID_SIZE-0.5)
    s += '\n'
    s += r"\clip (-0.5, -0.5) rectangle ({0}, {1});".format(SCREEN_SIZE[0] // GRID_SIZE - 0.5,
                                                    SCREEN_SIZE[1] // GRID_SIZE - 0.5)
    s += '\n'

    # draw forest
    for x in range(SCREEN_SIZE[0] // GRID_SIZE):
        for y in range(SCREEN_SIZE[1] // GRID_SIZE):

            if not in_poly(x, y, deltas):
                s += r"\draw [fill=eqeqeq] ({x}, {y}) circle (2.5pt);".format(x=x, y=y)
                s += '\n'

    # draw D-lines
    for a, b, c in deltas:
        domain = '-0.5:' + str(SCREEN_SIZE[0]//GRID_SIZE - 0.5)
        if b:
            m = -a/b
            p = -c/b
            equation = str(m) + r'*\x + ' + str(p)

            s += r"\draw [dash pattern=on 5pt off 5pt,domain=" + domain + r"] plot(\x,{" + equation + "});"
        else:
            x = -c/a
            s += r"\draw [dash pattern=on 5pt off 5pt] ({x}, {y_a}) -- ({x}, {y_b});".format(x=x,
                                                                                             y_a = -0.5,
                                                                                             y_b = SCREEN_SIZE[1] // GRID_SIZE - 0.5)

        s += '\n'

    # draw E
    # E's middle
    r = ') -- ('.join([str(x) + ', ' + str(y) for x, y in e])
    s += r"\fill[line width=0.pt,,color=wqwqwq,fill=wqwqwq,fill opacity=0.4] (" + r + ") -- cycle;" + '\n'

    # E's name
    bary_x = str(sum([x for x, _ in e]))
    bary_y = str(sum([y for _, y in e]))
    s += r"\draw (" + bary_x + ', ' + bary_y + ') node {$E$};' + '\n'

    # E's border
    for a, b in segments(e):
        s += r'\draw [line width=1pt] ({a_x}, {a_y})-- ({b_x}, {b_y});'.format(a_x=a[0],
                                                                                a_y=a[1],
                                                                                b_x=b[0],
                                                                                b_y=b[1])
        s += '\n'

    # E's vertices
    for x, y in e:
        s += r"\draw [fill=black] ({x}, {y}) circle (2.5pt);".format(x=x, y=y)
        s += '\n'

    # G's vertices
    for x, y in g:
        s += r"\draw [fill=red] ({x}, {y}) circle (2.5pt);".format(x=x, y=y)
        s += '\n'

    s += r"\end{tikzpicture}" + '\n'
    s += r"\end{center}" + '\n'
    s += r'\caption{G(E) when E is... }' + '\n'
    s += r"\end{figure}"

    print('\n'*3)
    print(s)

    # We put the string in the clipboard, for an easy use
    pygame.scrap.init()
    pygame.scrap.put(SCRAP_TEXT, s.encode())


def gui():
    global GRID_SIZE, E, G, MARKERS, DELTAS, SCREEN_SIZE

    screen = pygame.display.set_mode(SCREEN_SIZE, RESIZABLE)

    auto_g = 0

    running = True
    while running:

        # mouse pos
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x += GRID_SIZE // 2
        mouse_y += GRID_SIZE // 2

        # checking for events
        event_list = pygame.event.get()
        for event in event_list:
            if event.type == QUIT:
                running = False

            # resize the screen
            elif event.type == VIDEORESIZE:
                SCREEN_SIZE = event.size
                screen = pygame.display.set_mode(SCREEN_SIZE, RESIZABLE)

            elif event.type == KEYDOWN:
                # quit
                if event.key == K_ESCAPE:
                    running = False

                # E = Conv(G(E))
                if event.key == K_g:
                    E = convex_hull(G)
                    DELTAS = calculate_deltalines(E)
                    G = calculate_g_e(DELTAS)

                # auto g
                if event.key == K_a:
                    if auto_g:  # already on
                        auto_g = 0
                    else:
                        auto_g = int(time())

                # save picture
                if event.key == K_s:
                    name = 'Gaston' + str(int(time())) + ".png"
                    pygame.image.save(screen, name)
                    print("Image saved to " + name)

                # generate Tikz
                if event.key == K_t:
                    to_tikz(E, DELTAS, G)

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
                    new_point = mouse_x // GRID_SIZE, mouse_y // GRID_SIZE
                    if new_point in E:
                        E.remove(new_point)
                    else:
                        E.append(new_point)

                    E = convex_hull(E)
                    DELTAS = calculate_deltalines(E)
                    G = calculate_g_e(DELTAS)

                # right click --> marker point
                if event.button == 3:
                    new_point = mouse_x // GRID_SIZE, mouse_y // GRID_SIZE
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
                    if GRID_SIZE < SCREEN_SIZE[1] // 6:
                        GRID_SIZE += 1

        # auto G
        if auto_g and auto_g < time() - 1:
            auto_g = time()
            E = convex_hull(G)
            DELTAS = calculate_deltalines(E)
            G = calculate_g_e(DELTAS)

        screen.fill(WHITE)

        screen.fill(GREY_10, (0, 0, 130, 100))

        draw_poly_e(screen, E)
        draw_grid(screen)

        # draw |G(E)|, |E|, A(E)
        size_ge = FONT.render('|G(E)| = ' + str(len(G)), True, BLACK)
        size_e = FONT.render('|E| = ' + str(len(E)), True, BLACK)
        area_e = FONT.render('A(E) = ' + str(area(E)), True, BLACK)
        screen.blit(size_ge, (10, 10))
        screen.blit(size_e, (10, 35))
        screen.blit(area_e, (10, 60))

        # draw E, grid, D-lines, G(E) and markers

        draw_d_lines(screen, DELTAS)
        draw_dots(screen, E, BLUE)
        draw_dots(screen, G, RED)
        draw_dots(screen, MARKERS, M_COLOR)

        # draw mouse
        gfxdraw.aacircle(screen, int(mouse_x // GRID_SIZE * GRID_SIZE), int(mouse_y // GRID_SIZE * GRID_SIZE), 5, BLUE)

        pygame.display.flip()


if __name__ == '__main__':
    gui()
