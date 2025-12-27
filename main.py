import pygame
from math import dist as math_dist


class CombinationLogic:

    def __init__(self):

        self.current_combination = []
        self.min_value = 3
        self.wrong_tries = 0
        self.wait = False
        self.unlocked = False
        self.wait_time = WAIT_TIME
        self.wrong_pattern = None
        self.load_graphics()

    def load_graphics(self):

        self.points_surf = pygame.Surface([POINT_OFFSET*3+POINT_RADIUS]*2, pygame.SRCALPHA)
        for p in range(1,10):
            pygame.draw.circle(self.points_surf, (255, 255, 255), self.get_pos(p, False), POINT_RADIUS)

        self.selected_point_surf = pygame.Surface([SELECTION_RADIUS*2]*2, pygame.SRCALPHA)
        self.overlay_circle_surf = self.selected_point_surf.copy()
        pygame.draw.circle(self.selected_point_surf, (255, 255, 255), [SELECTION_RADIUS]*2, SELECTION_RADIUS, 2)
        pygame.draw.circle(self.overlay_circle_surf, (255, 255, 255, 100), [SELECTION_RADIUS]*2, SELECTION_RADIUS)

    @staticmethod
    def get_pos(index, on_screen=True):

        index-= 1
        return ((index%3)*POINT_OFFSET+DRAW_OFFSET[0], (index//3)*POINT_OFFSET+DRAW_OFFSET[1]) if on_screen else ((index%3)*POINT_OFFSET+POINT_RADIUS, (index//3)*POINT_OFFSET+POINT_RADIUS)

    @staticmethod
    def get_points(p1, p2):
        x1, y1 = p1
        x2, y2 = p2
        points = []
        n = int(math_dist((x1, y1), (x2, y2)))
        for i in range(n):
            pos = int(x1 + i * (x2 - x1) / n), int(y1 + i * (y2 - y1) / n)
            points.append(pos)
        return points

    def check_combination(self):

        if self.current_combination == COMBINATION:
            enter_sound.play()
            self.unlocked = True
        elif (l:=len(self.current_combination)) <= self.min_value:
            if l:
                self.wrong_pattern = self.current_combination.copy()
                pygame.time.set_timer(WRONG_PATTERN_TIMER, 300, loops=1)
                error_sound.play()
        else:
            error_sound.play()
            self.wrong_tries += 1
            self.wrong_pattern = self.current_combination.copy()
            pygame.time.set_timer(WRONG_PATTERN_TIMER, 300, loops=1)
            if self.wrong_tries >= 5:
                self.wrong_tries = 0
                self.wait = True
                pygame.time.set_timer(TIMER, 1000, loops=15)
        self.current_combination = []

    def check_mouse(self):

        if self.unlocked:
            return 

        mouse_pos = pygame.mouse.get_pos()
        for p in range(1,10):
            if math_dist(self.get_pos(p), mouse_pos) <= SELECTION_RADIUS:
                screen.blit(self.overlay_circle_surf, (self.get_pos(p)[0]-SELECTION_RADIUS, self.get_pos(p)[1]-SELECTION_RADIUS))
                if pygame.mouse.get_pressed()[0] and not self.wait:
                    if p not in self.current_combination:
                        self.current_combination.append(p)
                        try:
                            for point in self.get_points(self.get_pos(self.current_combination[-2]), self.get_pos(self.current_combination[-1])):
                                for p_again in range(1,10):
                                    if math_dist(point, self.get_pos(p_again)) <= POINT_RADIUS and p_again != self.current_combination[-1]:
                                        if p_again not in self.current_combination:
                                            self.current_combination.insert(-1, p_again)
                                            break
                        except IndexError: pass
                        break
            
    def draw(self):

        if not self.unlocked:

            screen.blit(self.points_surf, (DRAW_OFFSET[0]-POINT_RADIUS, DRAW_OFFSET[1]-POINT_RADIUS))
            combo = self.wrong_pattern if self.wrong_pattern else self.current_combination
            combo = [self.get_pos(p) for p in combo]

            for p in combo:
                screen.blit(self.selected_point_surf, (p[0]-SELECTION_RADIUS, p[1]-SELECTION_RADIUS))

            if self.wrong_pattern:
                try:
                    pygame.draw.lines(screen, (200, 80, 20), False, combo, POINT_RADIUS)
                except ValueError: pass
            else:
                combo.append((pygame.mouse.get_pos()))
                try:
                    pygame.draw.lines(screen, (10, 200, 55), False, combo, POINT_RADIUS)
                except ValueError: pass

            if self.wait:
                screen.blit(font.render(f"Try again in {self.wait_time} seconds", True, (255, 255, 255)), (180, 100))

        else:
            screen.fill('#7A36B1')
            screen.blit(font.render("Unlocked", True, (255, 255, 255)), (245, 400))


pygame.init()
SCREEN_SIZE = 600, 800
screen = pygame.display.set_mode(SCREEN_SIZE)

TIMER = pygame.USEREVENT + 1
WRONG_PATTERN_TIMER = pygame.USEREVENT + 2
WAIT_TIME = 15
POINT_RADIUS = 4 # can be changed
SELECTION_RADIUS = 64 # can be changed
POINT_OFFSET = 150 # can be changed
DRAW_OFFSET = (SCREEN_SIZE[0]-POINT_OFFSET*2)//2, (SCREEN_SIZE[1]-POINT_OFFSET*2)//2

COMBINATION = [1, 2, 3, 4, 5, 6, 7, 8, 9] # to be altered
error_sound = pygame.mixer.Sound("data/error.wav")
enter_sound = pygame.mixer.Sound("data/enter.wav")
font = pygame.font.SysFont("Arial", 30)

main = CombinationLogic()

while True:

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if main.wait and event.type == TIMER:
            main.wait_time -= 1
            if main.wait_time <= 0:
                main.wait = False
                main.wait_time = WAIT_TIME
        if event.type == WRONG_PATTERN_TIMER:
            main.wrong_pattern = None

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and not main.wait and not main.unlocked:
            main.check_combination()
            
            
    screen.fill((70, 80, 90))
    main.draw()
    main.check_mouse()
