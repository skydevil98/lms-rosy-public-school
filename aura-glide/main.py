# main.py
import pygame
import sys
import random
from settings import *
from particles import ParticleSystem
from entities import Player, Obstacle
from ui import Button, TextRenderer, draw_panel

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Aura Glide")
        self.clock = pygame.time.Clock()
        self.texter = TextRenderer()
        self.state = "MAIN_MENU"

        # Game entities
        self.player = None
        self.obstacles = []
        self.particles = ParticleSystem()
        self.score = 0
        self.high_score = 0
        self.spawn_timer = 0

        self.setup_audio()
        self.setup_ui()

    def setup_audio(self):
        # Audio feature - properly structured for future integration
        # You can add real sound files to 'assets/sounds/' and load them here:
        # self.sounds = {
        #     'flap': pygame.mixer.Sound('assets/sounds/flap.wav'),
        #     'score': pygame.mixer.Sound('assets/sounds/score.wav'),
        #     'crash': pygame.mixer.Sound('assets/sounds/crash.wav'),
        # }
        self.sounds = {}
        # Play bgm natively if available
        # pygame.mixer.music.load('assets/sounds/bgm.ogg')
        # pygame.mixer.music.play(-1)

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def setup_ui(self):
        button_w, button_h = 240, 65
        btn_x = WIDTH // 2 - button_w // 2
        
        self.play_btn = Button(btn_x, HEIGHT // 2 + 20, button_w, button_h, "PLAY", self.texter.menu_font)
        self.quit_btn = Button(btn_x, HEIGHT // 2 + 100, button_w, button_h, "QUIT", self.texter.menu_font)
        
        self.resume_btn = Button(btn_x, HEIGHT // 2 - 20, button_w, button_h, "RESUME", self.texter.menu_font)
        self.restart_btn = Button(btn_x, HEIGHT // 2 + 60, button_w, button_h, "RESTART", self.texter.menu_font)
        self.menu_btn = Button(btn_x, HEIGHT // 2 + 140, button_w, button_h, "MENU", self.texter.menu_font)

    def reset_game(self):
        self.player = Player()
        self.obstacles = [Obstacle(WIDTH + 200)]
        self.particles = ParticleSystem()
        self.score = 0
        self.spawn_timer = 0
        self.state = "PLAYING"

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == "PLAYING":
                        self.player.flap()
                        self.play_sound("flap")
                    elif self.state == "MAIN_MENU":
                        self.reset_game()
                    elif self.state == "GAME_OVER":
                        self.reset_game()
                if event.key == pygame.K_ESCAPE:
                    if self.state == "PLAYING":
                        self.state = "PAUSED"
                    elif self.state == "PAUSED":
                        self.state = "PLAYING"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == "MAIN_MENU":
                    if self.play_btn.rect.collidepoint(mouse_pos):
                        self.reset_game()
                    if self.quit_btn.rect.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()
                elif self.state == "PLAYING":
                    self.player.flap()
                    self.play_sound("flap")
                elif self.state == "PAUSED":
                    if self.resume_btn.rect.collidepoint(mouse_pos):
                        self.state = "PLAYING"
                    if self.restart_btn.rect.collidepoint(mouse_pos):
                        self.reset_game()
                    if self.menu_btn.rect.collidepoint(mouse_pos):
                        self.state = "MAIN_MENU"
                elif self.state == "GAME_OVER":
                    if self.restart_btn.rect.collidepoint(mouse_pos):
                        self.reset_game()
                    if self.menu_btn.rect.collidepoint(mouse_pos):
                        self.state = "MAIN_MENU"

    def check_collisions(self):
        # Ground / ceiling check
        if self.player.y > HEIGHT - self.player.radius or self.player.y < self.player.radius:
            return True
        for obs in self.obstacles:
            # Simple collision using rects
            if self.player.rect.colliderect(obs.top_rect) or self.player.rect.colliderect(obs.bottom_rect):
                return True
        return False

    def update(self):
        mouse_pos = pygame.mouse.get_pos()

        if self.state == "MAIN_MENU":
            self.play_btn.update(mouse_pos)
            self.quit_btn.update(mouse_pos)
            
            # Subtle background ambient particles
            if random.random() < 0.1:
                self.particles.particles.append(
                    __import__("particles").Particle(random.randint(0, WIDTH), HEIGHT + 10, speed_y=random.uniform(-3, -1), color=(60, 70, 90), shrink_rate=0.015, radius=random.uniform(2,5))
                )
            self.particles.update()

        elif self.state == "PLAYING":
            self.player.update()
            
            # Emit trail
            if self.player.velocity < -1:
                self.particles.emit_trail(self.player.x, self.player.y + self.player.radius, PLAYER_COLOR)

            self.spawn_timer += self.clock.get_time()
            if self.spawn_timer > OBSTACLE_SPAWN_TIME:
                self.obstacles.append(Obstacle(WIDTH))
                self.spawn_timer = 0

            for obs in self.obstacles:
                obs.update()
                # Check passing
                if not obs.passed and obs.x + obs.width < self.player.x:
                    obs.passed = True
                    self.score += 1
                    self.play_sound("score")

            # Remove off-screen obstacles
            self.obstacles = [obs for obs in self.obstacles if obs.x + obs.width > 0]
            self.particles.update()

            if self.check_collisions():
                self.play_sound("crash")
                self.particles.emit_explosion(self.player.x, self.player.y, PLAYER_COLOR, 40)
                if self.score > self.high_score:
                    self.high_score = self.score
                self.state = "GAME_OVER"
                
                # Make game over buttons slightly offset for aesthetics
                self.restart_btn.rect.centery = HEIGHT // 2 + 50
                self.menu_btn.rect.centery = HEIGHT // 2 + 130
                # Adjust rects to be centered properly
                self.restart_btn.rect.centerx = WIDTH // 2
                self.menu_btn.rect.centerx = WIDTH // 2

        elif self.state == "PAUSED":
            self.resume_btn.update(mouse_pos)
            self.restart_btn.update(mouse_pos)
            self.menu_btn.update(mouse_pos)
        
        elif self.state == "GAME_OVER":
            self.restart_btn.update(mouse_pos)
            self.menu_btn.update(mouse_pos)
            self.particles.update()

    def draw(self):
        self.screen.fill(BG_COLOR)

        if self.state == "MAIN_MENU":
            self.particles.draw(self.screen)
            self.texter.draw_text(self.screen, "AURA GLIDE", self.texter.title_font, (WIDTH//2, HEIGHT//3 - 30))
            self.play_btn.draw(self.screen)
            self.quit_btn.draw(self.screen)

        elif self.state in ["PLAYING", "PAUSED", "GAME_OVER"]:
            for obs in self.obstacles:
                obs.draw(self.screen)
            
            self.particles.draw(self.screen)
            
            if self.state != "GAME_OVER":
                self.player.draw(self.screen)

            self.texter.draw_text(self.screen, str(self.score), self.texter.score_font, (WIDTH//2, 80))

            if self.state == "PAUSED":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 160))
                self.screen.blit(overlay, (0, 0))
                self.texter.draw_text(self.screen, "PAUSED", self.texter.title_font, (WIDTH//2, HEIGHT//4))
                self.resume_btn.draw(self.screen)
                self.restart_btn.draw(self.screen)
                self.menu_btn.draw(self.screen)

            elif self.state == "GAME_OVER":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 120))
                self.screen.blit(overlay, (0, 0))

                panel_w, panel_h = 320, 180
                panel_rect = pygame.Rect(WIDTH//2 - panel_w//2, HEIGHT//4 - 20, panel_w, panel_h)
                draw_panel(self.screen, panel_rect, radius=15)
                
                self.texter.draw_text(self.screen, "GAME OVER", self.texter.title_font, (WIDTH//2, HEIGHT//4 + 20))
                self.texter.draw_text(self.screen, f"SCORE: {self.score}", self.texter.menu_font, (WIDTH//2, HEIGHT//4 + 80))
                self.texter.draw_text(self.screen, f"BEST: {self.high_score}", self.texter.menu_font, (WIDTH//2, HEIGHT//4 + 120))

                self.restart_btn.draw(self.screen)
                self.menu_btn.draw(self.screen)

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    try:
        Game().run()
    except Exception as e:
        print(f"Error starting game: {e}")
