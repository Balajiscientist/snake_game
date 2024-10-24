import pygame
from pygame.locals import *
import time
import random
import os

SIZE = 40
BACKGROUND_COLOR = (110, 110, 5)


class Apple:
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen
        self.image = pygame.image.load("resources/apple.jpg").convert()
        self.move()  # Start at random position

    def draw(self):
        self.parent_screen.blit(self.image, (self.x, self.y))

    def move(self):
        # Ensure apple doesn't spawn too close to edges
        self.x = random.randint(1, 23) * SIZE
        self.y = random.randint(1, 18) * SIZE


class Snake:
    def __init__(self, parent_screen):
        self.parent_screen = parent_screen
        self.image = pygame.image.load("resources/block (1).jpg").convert()
        self.direction = 'right'

        # Start with length 1 at center-ish of screen
        self.length = 1
        self.x = [SIZE * 5]  # Start more towards center
        self.y = [SIZE * 5]  # Start more towards center

        # Store the last direction to prevent 180-degree turns
        self.last_direction = self.direction

    def increase_length(self):
        self.length += 1
        # Add new segment at current last position
        self.x.append(self.x[-1])
        self.y.append(self.y[-1])

    def move_left(self):
        if self.last_direction != 'right':
            self.direction = 'left'

    def move_right(self):
        if self.last_direction != 'left':
            self.direction = 'right'

    def move_up(self):
        if self.last_direction != 'down':
            self.direction = 'up'

    def move_down(self):
        if self.last_direction != 'up':
            self.direction = 'down'

    def walk(self):
        # Store last direction before updating
        self.last_direction = self.direction

        # Update body segments
        for i in range(self.length - 1, 0, -1):
            self.x[i] = self.x[i - 1]
            self.y[i] = self.y[i - 1]

        # Update head
        if self.direction == 'left':
            self.x[0] -= SIZE
        if self.direction == 'right':
            self.x[0] += SIZE
        if self.direction == 'up':
            self.y[0] -= SIZE
        if self.direction == 'down':
            self.y[0] += SIZE

    def draw(self):
        for i in range(self.length):
            self.parent_screen.blit(self.image, (self.x[i], self.y[i]))


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake game By balaj")

        self.surface = pygame.display.set_mode((1000, 800))
        self.surface.fill(BACKGROUND_COLOR)

        # Initialize mixer for sounds
        pygame.mixer.init()
        self.music_playing = False  # Track music state
        self.play_background_music()

        # Create snake and apple
        self.snake = Snake(self.surface)
        self.apple = Apple(self.surface)

        # Load background
        self.background = pygame.image.load("resources/background.jpg").convert()

    def play_background_music(self):
        try:
            if not self.music_playing:  # Only play if music isn't already playing
                pygame.mixer.music.load('resources/1_snake_game_resources_master.mp3')
                pygame.mixer.music.play(-1, 0)
                self.music_playing = True
        except:
            pass

    def stop_background_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False

    def play_sound(self, sound_name):
        try:
            sound = pygame.mixer.Sound(f"resources/{sound_name}.mp3")
            pygame.mixer.Sound.play(sound)
        except:
            pass

    def reset(self):
        self.snake = Snake(self.surface)
        self.apple = Apple(self.surface)
        # Don't automatically restart music on reset

    def start_new_game(self):
        self.reset()
        self.play_background_music()  # Only start music when explicitly starting new game

    def is_collision(self, x1, y1, x2, y2):
        return (abs(x1 - x2) < SIZE and abs(y1 - y2) < SIZE)

    def render_background(self):
        self.surface.blit(self.background, (0, 0))

    def play(self):
        self.render_background()
        self.snake.walk()
        self.snake.draw()
        self.apple.draw()
        self.display_score()
        pygame.display.flip()

        # Check for apple collision
        if self.is_collision(self.snake.x[0], self.snake.y[0], self.apple.x, self.apple.y):
            self.play_sound("ding")
            self.snake.increase_length()
            self.apple.move()

        # Check for self collision
        if self.snake.length > 2:
            for i in range(3, self.snake.length):
                if self.is_collision(self.snake.x[0], self.snake.y[0], self.snake.x[i], self.snake.y[i]):
                    self.play_sound('crash')
                    self.stop_background_music()
                    raise Exception("Collision with self")

        # Check for boundary collision
        if (self.snake.x[0] < 0 or
                self.snake.x[0] >= 1000 - SIZE or
                self.snake.y[0] < 0 or
                self.snake.y[0] >= 800 - SIZE):
            self.play_sound('crash')
            self.stop_background_music()
            raise Exception("Hit the boundary")

    def display_score(self):
        font = pygame.font.SysFont('arial', 30)
        score = font.render(f"Score: {self.snake.length - 1}", True, (200, 200, 200))
        self.surface.blit(score, (850, 10))

    def show_game_over(self):
        self.render_background()
        font = pygame.font.SysFont('arial', 30)
        line1 = font.render(f"Game Over! Score: {self.snake.length - 1}", True, (255, 255, 255))
        line2 = font.render("Press Enter to play again or Escape to exit", True, (255, 255, 255))
        self.surface.blit(line1, (200, 300))
        self.surface.blit(line2, (200, 350))
        pygame.display.flip()

    def run(self):
        running = True
        pause = False

        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_RETURN:
                        if pause:  # Only start new game if we're paused (game over state)
                            self.start_new_game()
                            pause = False
                    elif not pause:
                        if event.key == K_LEFT:
                            self.snake.move_left()
                        elif event.key == K_RIGHT:
                            self.snake.move_right()
                        elif event.key == K_UP:
                            self.snake.move_up()
                        elif event.key == K_DOWN:
                            self.snake.move_down()
                elif event.type == QUIT:
                    running = False

            try:
                if not pause:
                    self.play()
            except Exception as e:
                print(f"Game Over: {str(e)}")
                self.show_game_over()
                pause = True

            time.sleep(0.2)

        self.stop_background_music()


if __name__ == '__main__':
    game = Game()
    game.run()
