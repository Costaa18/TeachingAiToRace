import pygame
import time
import math
from utils import scale_image, rotated_car
import neat


def make_ai_cars(population, config, count=5):
    cars = []

    for _, genome in population.population.items():
        car = AICar(4, 4, RED_CAR, genome, config)
        cars.append(car)

        if len(cars) >= count:
            break

    return cars


config = neat.Config(
    neat.DefaultGenome,
    neat.DefaultReproduction,
    neat.DefaultSpeciesSet,
    neat.DefaultStagnation,
    "config-feedforward.txt",
)

population = neat.Population(config)


SENSOR_ANGLES = [-90, -45, 0, 45, 90]
MAX_SENSOR_DISTANCE = 150
SENSOR_STEP = 5

CHECKPOINTS = [
    pygame.Rect(240, 212, 90, 30),
    pygame.Rect(472, 35, 30, 90),
    pygame.Rect(700, 165, 90, 30),
]

pygame.font.init()
my_font = pygame.font.SysFont("Comic Sans MS", 30)


GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)

TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 220)

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()

WIN = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption("Race Game!")


class GameInfo:
    def __init__(self):
        self.cars = []
        self.started = False
        self.start_time = 0
        self.finish_time = 0
        self.finished = False
        self.lap_time = 0

    def reset(self):
        self.started = False
        self.start_time = 0

    def start_game(self):
        self.started = True
        self.start_time = time.time()

    def finish_game(self):
        self.finished = True
        self.finish_time = time.time()

    def get_lap_time(self):
        if not self.finished:
            return None
        return self.finish_time - self.start_time


class Car:
    def __init__(self, max_vel, rotation_vel, img):
        self.img = img
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 180
        self.x, self.y = self.START_POS
        self.accelaration = 0.1
        self.fitness = 0
        self.checkpoint = 0
        self.checkpoint_times = []
        self.start_time = 0
        self.finish_time = 0
        self.lap_time = 0
        self.alive = True
        self.brain = None
        self.is_human = False

    def get_sensor_distance(self, angle_offset, max_distance=MAX_SENSOR_DISTANCE):
        angle = math.radians(self.angle + angle_offset)
        center_x = self.x + self.img.get_width() / 2
        center_y = self.y + self.img.get_height() / 2

        for distance in range(0, max_distance, SENSOR_STEP):
            x = int(center_x - math.sin(angle) * distance)
            y = int(center_y - math.cos(angle) * distance)

            if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
                return distance / max_distance

            if TRACK_BORDER_MASK.get_at((x, y)):
                return distance / max_distance

        return 1

    def get_inputs(self):
        return [self.get_sensor_distance(offset) for offset in SENSOR_ANGLES]

    def rotate(self, left=False, right=False):
        if self.alive != True:
            return
        if self.vel != 0:
            if left:
                self.angle += self.rotation_vel
            elif right:
                self.angle -= self.rotation_vel

    def draw_sensors(self, win):
        center_x = self.x + self.img.get_width() / 2
        center_y = self.y + self.img.get_height() / 2

        for offset in SENSOR_ANGLES:
            angle = math.radians(self.angle + offset)

            for distance in range(0, MAX_SENSOR_DISTANCE, SENSOR_STEP):
                x = int(center_x - math.sin(angle) * distance)
                y = int(center_y - math.cos(angle) * distance)

                if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
                    break

                pygame.draw.circle(win, (0, 255, 0), (x, y), 2)

                if TRACK_BORDER_MASK.get_at((x, y)):
                    pygame.draw.circle(win, (255, 0, 0), (x, y), 4)
                    break

    def draw(self, win):
        rotated_image, rect = rotated_car(self)
        win.blit(rotated_image, rect.topleft)

        self.draw_sensors(win)

        # blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.accelaration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.accelaration, -self.max_vel / 2)
        self.move()

    def move(self):
        if self.alive != True:
            return

        radians = math.radians(self.angle)

        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def apply_drag(self):
        self.vel = max(self.vel - self.accelaration / 2, 0)
        self.move()

    def collide(self, mask, x=0, y=0):

        rotated_image, rect = rotated_car(self)
        car_mask = pygame.mask.from_surface(rotated_image)
        offset = (int(rect.x - x), int(rect.y - y))
        poi = mask.overlap(car_mask, offset)  # point of intersection
        return poi

    def update_checkpoint(self):
        if self.checkpoint >= len(CHECKPOINTS):
            return

        rotated_image, rect = rotated_car(self)
        if rect.colliderect(CHECKPOINTS[self.checkpoint]):
            self.checkpoint += 1
            self.fitness += 1

    def bounce(self):
        self.vel = -self.vel / 2
        self.move()

    def kill(self):
        self.alive = False

    def hit_wall(self):
        if self.collide(TRACK_BORDER_MASK) != None:
            self.kill()

    def cross_finish(self):
        finish_poi_collide = self.collide(FINISH_MASK, *FINISH_POSITION)
        if finish_poi_collide != None:
            if finish_poi_collide[1] > 0:
                self.kill()
            else:
                self.complete_finish()

    def complete_finish(self):
        self.finish_time = time.time()
        self.fitness += 10

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 180
        self.vel = 0

    def control_by_network(self):
        outputs = self.brain.activate(self.get_inputs())

        if outputs[0] > 0.5:
            self.rotate(left=True)
        if outputs[1] > 0.5:
            self.rotate(right=True)
        if outputs[2] > 0.5:
            self.move_forward()
        if outputs[3] > 0.5:
            self.move_backward()

    def update_stuck_state(self, current_time):
        if not self.alive:
            return

        if abs(self.vel) < 0.05:
            if not hasattr(self, "stuck_since"):
                self.stuck_since = current_time

            if current_time - self.stuck_since > 5:
                self.kill()
        else:
            self.stuck_since = None


class PlayerCar(Car):
    START_POS = (180, 250)

    def __init__(self, max_vel, rotation_vel, img):
        super().__init__(max_vel, rotation_vel, img)
        self.is_human = True
        self.brain = None


class AICar(Car):
    START_POS = (180, 250)

    def __init__(self, max_vel, rotation_vel, img=None, genome=None, config=None):
        if img is None:
            img = RED_CAR

        super().__init__(max_vel, rotation_vel, img)
        self.is_human = False
        self.brain = None

        if genome is not None and config is not None:
            self.brain = neat.nn.FeedForwardNetwork.create(genome, config)


def move_player(car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        car.rotate(left=True)
    if keys[pygame.K_d]:
        car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        car.move_backward()
    if not moved:
        car.apply_drag()


def draw_track(WIN):
    WIN.blit(GRASS, (0, 0))
    WIN.blit(TRACK, (0, 0))
    WIN.blit(FINISH, FINISH_POSITION)

    draw_checkpoints(WIN)

    WIN.blit(TRACK_BORDER, (0, 0))


def draw_checkpoints(win):

    for checkpoint in CHECKPOINTS:
        pygame.draw.rect(
            win,
            (0, 0, 255),
            (checkpoint[0], checkpoint[1], checkpoint[2], checkpoint[3]),
            0,
        )


FPS = 60
run = True
clock = pygame.time.Clock()
# Apenas cria os carros para teste inicial.
game = GameInfo()
game.cars = make_ai_cars(population, config, count=5)
# for i in range(5):
#    skin = GREEN_CAR if i % 2 == 0 else RED_CAR
#    car = PlayerCar(4, 4, skin)
#   game.cars.append(car)

# winner = population.run(eval_genomes, 50)

while run:
    clock.tick(FPS)

    draw_track(WIN)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    alive_count = sum(1 for car in game.cars if car.alive)
    status = my_font.render(
        f"cars alive {alive_count} / {len(game.cars)}", False, (0, 0, 0)
    )
    WIN.blit(status, (400, 31))

    for car in game.cars:
        car.draw(WIN)
        if not car.alive:
            continue

        if car.is_human:
            move_player(car)
        elif car.brain is not None:
            car.control_by_network()

        car.hit_wall()
        car.update_checkpoint()
        car.cross_finish()
        car.update_stuck_state(time.time())


    if alive_count == 0:
        run = False

    pygame.display.update()

pygame.quit()
