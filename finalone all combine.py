import pygame
import random
import sys
import os

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Alien Invasion with Power-up Buffs and Miniboss")
clock = pygame.time.Clock()

# Load the background image
background_image = pygame.image.load("C:\\Users\\vignan\\Desktop\\team\\BGgs.jpg").convert()
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Colors (for fallback)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 150, 255)
YELLOW = (255, 255, 0)
DARK_GRAY = (30, 30, 30)
HEALTH_BAR_BG = (100, 0, 0)
HEALTH_BAR_FG = (0, 200, 0)

FONT = pygame.font.SysFont('Arial', 30)
BIG_FONT = pygame.font.SysFont('Arial', 60)

PLAYER_WIDTH, PLAYER_HEIGHT = 60, 48
PLAYER_SPEED = 7
PLAYER_MAX_HEALTH = 100

BULLET_WIDTH, BULLET_HEIGHT = 25, 50
BULLET_SPEED = 10

ALIEN_WIDTH, ALIEN_HEIGHT = 50, 40
INITIAL_ALIEN_HEALTH = 1
ALIEN_SPEED = 1
ALIEN_DROP = 40

ALIEN_BULLET_WIDTH, ALIEN_BULLET_HEIGHT = 5, 10
ALIEN_BULLET_SPEED = 5

POWERUP_SIZE = 30
POWERUP_FALL_SPEED = 3

ASSISTANT_WIDTH, ASSISTANT_HEIGHT = 50, 30

MINIBOSS_WIDTH, MINIBOSS_HEIGHT = 120, 90
MINIBOSS_HEALTH = 50
MINIBOSS_BULLET_SPEED = 7
MINIBOSS_SHOOT_COOLDOWN = 800

POWERUPS_PER_STAGE = 6
SCORE_PER_ALIEN = 81

# Initialize mixer for sounds
pygame.mixer.init()

# Load background music files
bg_music_normal = "C:\\Users\\vignan\\Desktop\\team\\bgmusic.mp3"
bg_music_miniboss = "C:\\Users\\vignan\\Desktop\\team\\bg_miniboss.mp3"
bg_music_low_health = "C:\\Users\\vignan\\Desktop\\team\\low_health.mp3"
stage_clear_sound = "C:\\Users\\vignan\\Desktop\\team\\stage_clear.mp3"  # Add this file
game_over_sound = "C:\\Users\\vignan\\Desktop\\team\\game_over.mp3"  # Add this file
start_game_sound = "C:\\Users\\vignan\\Desktop\\team\\start_game.mp3"  # Add this file

# Load bullet sounds
try:
    bullet_sound_normal = pygame.mixer.Sound("C:\\Users\\vignan\\Desktop\\team\\bullet_normal.wav")
except FileNotFoundError:
    bullet_sound_normal = None
    print("Warning: bullet_normal.wav not found.")
try:
    bullet_sound_power = pygame.mixer.Sound("C:\\Users\\vignan\\Desktop\\team\\bullet_power.mp3")
except FileNotFoundError:
    bullet_sound_power = None
    print("Warning: bullet_power.wav not found.")

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=10)
        
        text_surf = FONT.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
        
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("C:\\Users\\vignan\\Desktop\\team\\playern.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 10))
        self.speed = PLAYER_SPEED
        self.health = PLAYER_MAX_HEALTH

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        self.rect.clamp_ip(screen.get_rect())

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def heal(self, amount):
        self.health = min(self.health + amount, PLAYER_MAX_HEALTH)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, powered_up=False):
        super().__init__()
        if powered_up:
            try:
                self.image = pygame.image.load("C:\\Users\\vignan\\Desktop\\team\\BB.png").convert_alpha()
            except FileNotFoundError:
                print("Warning: Power-up bullet image not found. Using default bullet image.")
                self.image = pygame.image.load("C:\\Users\\vignan\\Desktop\\team\\unnamed.png").convert_alpha()
        else:
            self.image = pygame.image.load("C:\\Users\\vignan\\Desktop\\team\\unnamed.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (BULLET_WIDTH, BULLET_HEIGHT))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.speed = BULLET_SPEED

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.kill()


class AlienBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=ALIEN_BULLET_SPEED):
        super().__init__()
        self.image = pygame.image.load("C:\\Users\\vignan\\Desktop\\team\\mm.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (ALIEN_BULLET_WIDTH, ALIEN_BULLET_HEIGHT))
        self.rect = self.image.get_rect(midtop=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Alien(pygame.sprite.Sprite):
    def __init__(self, x, y, health):
        super().__init__()
        self.image = pygame.image.load("C:\\Users\\vignan\\Desktop\\team\\ALIEN.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (ALIEN_WIDTH, ALIEN_HEIGHT))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = ALIEN_SPEED
        self.frozen = False
        self.health = health

    def update(self, direction):
        if not self.frozen:
            self.rect.x += self.speed * direction

    def drop_down(self):
        if not self.frozen:
            self.rect.y += ALIEN_DROP

    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0


class Miniboss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("C:\\Users\\vignan\\Desktop\\team\\ENE.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (MINIBOSS_WIDTH, MINIBOSS_HEIGHT))
        self.rect = self.image.get_rect(midtop=(SCREEN_WIDTH // 2, 30))
        self.health = MINIBOSS_HEALTH
        self.speed = 2
        self.direction = 1
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right >= SCREEN_WIDTH or self.rect.left <= 0:
            self.direction *= -1

    def shoot(self, alien_bullets_group):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= MINIBOSS_SHOOT_COOLDOWN:
            bullet_center = AlienBullet(self.rect.centerx, self.rect.bottom, speed=MINIBOSS_BULLET_SPEED)
            bullet_left = AlienBullet(self.rect.centerx - 20, self.rect.bottom, speed=MINIBOSS_BULLET_SPEED)
            bullet_right = AlienBullet(self.rect.centerx + 20, self.rect.bottom, speed=MINIBOSS_BULLET_SPEED)
            alien_bullets_group.add(bullet_center, bullet_left, bullet_right)
            self.last_shot = now


class PowerUp(pygame.sprite.Sprite):
    def __init__(self, kind, x, y):
        super().__init__()
        self.kind = kind
        image_path = f"C:\\Users\\vignan\\Desktop\\team\\box_{kind}.png"
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except FileNotFoundError:
            print(f"Warning: Image for power-up '{kind}' not found. Using default.")
            self.image = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE))
            self.image.fill(WHITE)
        self.image = pygame.transform.scale(self.image, (POWERUP_SIZE, POWERUP_SIZE))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = POWERUP_FALL_SPEED

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class AssistantShip(pygame.sprite.Sprite):
    def __init__(self, player, offset):
        super().__init__()
        self.image = pygame.image.load("C:\\Users\\vignan\\Desktop\\team\\player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (ASSISTANT_WIDTH, ASSISTANT_HEIGHT))
        self.rect = self.image.get_rect(center=(player.rect.centerx + offset, player.rect.centery - 40))
        self.player = player
        self.offset = offset

    def update(self):
        self.rect.centerx = self.player.rect.centerx + self.offset
        self.rect.bottom = self.player.rect.top - 10

    def shoot(self):
        return Bullet(self.rect.centerx, self.rect.top, powered_up=game.double_bullet if hasattr(game, 'double_bullet') else False)


class Game:
    def __init__(self):
        self.player = Player()
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.bullets = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.assistants = pygame.sprite.Group()
        self.miniboss = None
        self.stage = 1
        self.stage_start_time = pygame.time.get_ticks()
        self.stage_displaying = True
        self.direction = 1
        self.speed_multiplier = 1.0
        self.alien_health_increment = 0
        self.current_bg_music = None
        self.low_health_music_playing = False
        self.game_state = "menu"  # menu, playing, game_over
        self.high_score = self.load_high_score()
        self.start_button = Button(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 50, "START GAME", GREEN, BLUE)
        self.spawn_stage_enemies()
        self.powerup_active = None
        self.powerup_timer = 0
        self.double_bullet = False
        self.freeze_timer = 0
        self.assistant_timer = 0
        self.score = 0
        self.powerups_spawned_in_stage = 0

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except (FileNotFoundError, ValueError):
            return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(max(self.score, self.high_score)))

    def play_bg_music_normal(self):
        if self.current_bg_music != 'normal' and not self.low_health_music_playing:
            try:
                pygame.mixer.music.load(bg_music_normal)
                pygame.mixer.music.play(-1)
                self.current_bg_music = 'normal'
                self.low_health_music_playing = False
            except:
                print("Warning: Could not load normal background music")

    def play_bg_music_miniboss(self):
        if self.current_bg_music != 'miniboss' and not self.low_health_music_playing:
            try:
                pygame.mixer.music.load(bg_music_miniboss)
                pygame.mixer.music.play(-1)
                self.current_bg_music = 'miniboss'
                self.low_health_music_playing = False
            except:
                print("Warning: Could not load miniboss background music")

    def play_bg_music_low_health(self):
        if not self.low_health_music_playing:
            try:
                pygame.mixer.music.load(bg_music_low_health)
                pygame.mixer.music.play(-1)
                self.low_health_music_playing = True
                self.current_bg_music = None
            except:
                print("Warning: Could not load low health background music")

    def play_stage_clear_sound(self):
        try:
            sound = pygame.mixer.Sound(stage_clear_sound)
            sound.play()
        except:
            print("Warning: Could not load stage clear sound")

    def play_game_over_sound(self):
        try:
            pygame.mixer.music.stop()
            sound = pygame.mixer.Sound(game_over_sound)
            sound.play()
        except:
            print("Warning: Could not load game over sound")

    def play_start_game_sound(self):
        try:
            sound = pygame.mixer.Sound(start_game_sound)
            sound.play()
        except:
            print("Warning: Could not load start game sound")

    def check_low_health_music(self):
        if self.player.health <= PLAYER_MAX_HEALTH * 0.3:
            if not self.low_health_music_playing:
                self.play_bg_music_low_health()
        else:
            if self.low_health_music_playing:
                self.low_health_music_playing = False
                if self.miniboss:
                    self.play_bg_music_miniboss()
                else:
                    self.play_bg_music_normal()

    def spawn_stage_enemies(self):
        self.aliens.empty()
        self.miniboss = None
        alien_health = INITIAL_ALIEN_HEALTH + self.alien_health_increment
        if self.stage % 3 == 0:
            self.miniboss = Miniboss()
            self.play_bg_music_miniboss()
        else:
            cols = 10
            rows = 4
            padding = 10
            start_x = (SCREEN_WIDTH - (ALIEN_WIDTH + padding) * cols) // 2
            start_y = 60
            for row in range(rows):
                for col in range(cols):
                    alien = Alien(start_x + col * (ALIEN_WIDTH + padding), start_y + row * (ALIEN_HEIGHT + padding), alien_health)
                    self.aliens.add(alien)
            self.play_bg_music_normal()
        self.powerups_spawned_in_stage = 0

    def activate_powerup(self, kind):
        self.powerup_active = kind
        self.powerup_timer = pygame.time.get_ticks()
        if kind == "double":
            self.double_bullet = True
        elif kind == "assistant":
            self.assistants.add(AssistantShip(self.player, -70), AssistantShip(self.player, 70))
            self.assistant_timer = pygame.time.get_ticks()
        elif kind == "freeze":
            for alien in self.aliens:
                alien.frozen = True
            if self.miniboss:
                self.miniboss.speed = 0
            self.freeze_timer = pygame.time.get_ticks()
        elif kind == "heal":
            self.player.heal(25)
            self.powerup_active = None

    def check_powerup_expiry(self):
        now = pygame.time.get_ticks()
        if self.powerup_active == "double" and now - self.powerup_timer > 3000:
            self.double_bullet = False
            self.powerup_active = None
        elif self.powerup_active == "assistant" and now - self.assistant_timer > 2000:
            self.assistants.empty()
            self.powerup_active = None
        elif self.powerup_active == "freeze" and now - self.freeze_timer > 3000:
            for alien in self.aliens:
                alien.frozen = False
            if self.miniboss:
                self.miniboss.speed = 2
            self.powerup_active = None

    def show_menu(self):
        screen.blit(background_image, (0, 0))
        
        title = BIG_FONT.render("ALIEN INVASION", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, SCREEN_HEIGHT//4))
        
        high_score_text = FONT.render(f"High Score: {self.high_score}", True, WHITE)
        screen.blit(high_score_text, (SCREEN_WIDTH//2 - high_score_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        mouse_pos = pygame.mouse.get_pos()
        self.start_button.check_hover(mouse_pos)
        self.start_button.draw(screen)
        
        pygame.display.flip()

    def show_game_over(self):
        screen.fill(BLACK)
        
        # Update high score if current score is higher
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()
        
        game_over_text = BIG_FONT.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 60))
        
        score_text = FONT.render(f"Your Score: {self.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
        
        high_score_text = FONT.render(f"High Score: {self.high_score}", True, YELLOW)
        screen.blit(high_score_text, (SCREEN_WIDTH//2 - high_score_text.get_width()//2, SCREEN_HEIGHT//2 + 40))
        
        restart_text = FONT.render("Press ENTER to restart", True, GREEN)
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 100))
        
        pygame.display.flip()

    def reset_game(self):
        self.player = Player()
        self.player_group = pygame.sprite.GroupSingle(self.player)
        self.bullets.empty()
        self.alien_bullets.empty()
        self.aliens.empty()
        self.powerups.empty()
        self.assistants.empty()
        self.miniboss = None
        self.stage = 1
        self.stage_start_time = pygame.time.get_ticks()
        self.stage_displaying = True
        self.direction = 1
        self.speed_multiplier = 1.0
        self.alien_health_increment = 0
        self.score = 0
        self.spawn_stage_enemies()
        self.play_bg_music_normal()

    def run(self):
        running = True
        shoot_cooldown = 400
        last_shot_time = pygame.time.get_ticks()
        alien_shoot_cooldown = 1500
        last_alien_shot = pygame.time.get_ticks()

        global game
        game = self

        while running:
            dt = clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                
                if self.game_state == "menu":
                    mouse_pos = pygame.mouse.get_pos()
                    if self.start_button.is_clicked(mouse_pos, event):
                        self.play_start_game_sound()
                        self.game_state = "playing"
                        self.play_bg_music_normal()
                
                elif self.game_state == "game_over" and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.game_state = "playing"
                        self.play_bg_music_normal()

            if self.game_state == "menu":
                self.show_menu()
                continue
            elif self.game_state == "game_over":
                self.show_game_over()
                continue

            # Check and handle low health music
            self.check_low_health_music()

            if self.stage_displaying:
                if pygame.time.get_ticks() - self.stage_start_time < 2000:
                    screen.blit(background_image, (0, 0))
                    text = BIG_FONT.render(f"Stage {self.stage}", True, WHITE)
                    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
                    pygame.display.flip()
                    continue
                else:
                    self.stage_displaying = False

            screen.blit(background_image, (0, 0))

            keys = pygame.key.get_pressed()
            self.player.update(keys)

            if self.player.health <= 0:
                self.play_game_over_sound()
                self.game_state = "game_over"
                continue

            if keys[pygame.K_SPACE] and pygame.time.get_ticks() - last_shot_time > shoot_cooldown:
                # Play bullet sound
                if self.double_bullet:
                    self.bullets.add(Bullet(self.player.rect.centerx - 10, self.player.rect.top, powered_up=True),
                                     Bullet(self.player.rect.centerx + 10, self.player.rect.top, powered_up=True))
                    if bullet_sound_power:
                        bullet_sound_power.play()
                else:
                    self.bullets.add(Bullet(self.player.rect.centerx, self.player.rect.top))
                    if bullet_sound_normal:
                        bullet_sound_normal.play()
                for assistant in self.assistants:
                    self.bullets.add(Bullet(assistant.rect.centerx, assistant.rect.top, powered_up=self.double_bullet))
                    # Play bullet sound for assistants as well
                    if self.double_bullet:
                        if bullet_sound_power:
                            bullet_sound_power.play()
                    else:
                        if bullet_sound_normal:
                            bullet_sound_normal.play()
                last_shot_time = pygame.time.get_ticks()

            self.bullets.update()
            if self.miniboss:
                self.miniboss.update()
                self.miniboss.shoot(self.alien_bullets)
            else:
                self.aliens.update(self.direction)

            self.assistants.update()
            self.alien_bullets.update()
            self.powerups.update()
            self.check_powerup_expiry()

            if not self.miniboss and self.aliens:
                leftmost = min(alien.rect.left for alien in self.aliens)
                rightmost = max(alien.rect.right for alien in self.aliens)
                if leftmost <= 0 or rightmost >= SCREEN_WIDTH:
                    self.direction *= -1
                    for alien in self.aliens:
                        alien.drop_down()

            now = pygame.time.get_ticks()
            if not self.miniboss and now - last_alien_shot > alien_shoot_cooldown:
                if self.aliens:
                    shooter = random.choice(self.aliens.sprites())
                    self.alien_bullets.add(AlienBullet(shooter.rect.centerx, shooter.rect.bottom))
                last_alien_shot = now

            if not self.miniboss:
                hits = pygame.sprite.groupcollide(self.bullets, self.aliens, True, False)
                for bullet, hit_aliens in hits.items():
                    for alien in hit_aliens:
                        dead = alien.take_damage(1)
                        if dead:
                            alien.kill()
                            self.score += SCORE_PER_ALIEN
                            if self.powerups_spawned_in_stage < POWERUPS_PER_STAGE and random.random() < 0.15:
                                kind = random.choice(["double", "assistant", "freeze", "heal"])
                                self.powerups.add(PowerUp(kind, alien.rect.centerx, alien.rect.centery))
                                self.powerups_spawned_in_stage += 1

            else:
                hits = pygame.sprite.spritecollide(self.miniboss, self.bullets, True)
                for _ in hits:
                    self.miniboss.health -= 1
                if self.miniboss.health <= 0:
                    self.play_stage_clear_sound()
                    self.miniboss = None
                    self.stage += 1
                    self.stage_start_time = pygame.time.get_ticks()
                    self.stage_displaying = True
                    self.speed_multiplier += 0.02
                    global ALIEN_SPEED
                    ALIEN_SPEED += 0.02
                    self.alien_health_increment += 1  # Increment alien health after miniboss defeated
                    self.spawn_stage_enemies()

            if pygame.sprite.spritecollideany(self.player, self.alien_bullets):
                self.player.take_damage(10)
                for bullet in pygame.sprite.spritecollide(self.player, self.alien_bullets, True):
                    bullet.kill()

            for powerup in pygame.sprite.spritecollide(self.player, self.powerups, True):
                self.activate_powerup(powerup.kind)

            if not self.miniboss and not self.aliens:
                self.play_stage_clear_sound()
                self.stage += 1
                self.stage_start_time = pygame.time.get_ticks()
                self.stage_displaying = True
                self.speed_multiplier += 0.02
                ALIEN_SPEED += 0.02
                self.spawn_stage_enemies()

            if not self.miniboss:
                for alien in self.aliens:
                    if alien.rect.colliderect(self.player.rect) or alien.rect.bottom >= SCREEN_HEIGHT:
                        self.play_game_over_sound()
                        self.game_state = "game_over"

            self.player_group.draw(screen)
            self.bullets.draw(screen)
            if self.miniboss:
                screen.blit(self.miniboss.image, self.miniboss.rect)
                bar_width = MINIBOSS_WIDTH
                bar_height = 10
                health_ratio = self.miniboss.health / MINIBOSS_HEALTH
                pygame.draw.rect(screen, RED, (self.miniboss.rect.left, self.miniboss.rect.top - 15, bar_width, bar_height))
                pygame.draw.rect(screen, GREEN, (self.miniboss.rect.left, self.miniboss.rect.top - 15, bar_width * health_ratio, bar_height))
            else:
                self.aliens.draw(screen)
            self.assistants.draw(screen)
            self.alien_bullets.draw(screen)
            self.powerups.draw(screen)

            pygame.draw.rect(screen, HEALTH_BAR_BG, (10, 10, 200, 20))
            pygame.draw.rect(screen, HEALTH_BAR_FG, (10, 10, 200 * self.player.health / PLAYER_MAX_HEALTH, 20))

            # Score left under health bar
            score_text = FONT.render(f"Score: {self.score}", True, YELLOW)
            screen.blit(score_text, (10, 40))

            # Stage display top right
            stage_text = FONT.render(f"Stage: {self.stage}", True, WHITE)
            screen.blit(stage_text, (SCREEN_WIDTH - stage_text.get_width() - 10, 10))

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()