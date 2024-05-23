import arcade
import random

# Константы для настройки игры
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Dodge the Fairies"
PLAYER_SCALING = 0.5
FAIRY_SCALING = 0.5
BAT_SCALING = 0.5
DRAGON_SCALING = 1.0
PLAYER_MOVEMENT_SPEED = 5
PLAYER_JUMP_SPEED = 15
GRAVITY = 1

LEVELS = [
    {'fairy_speed': 2, 'fairy_count': 5, 'background': 'path/to/your/background1.png'},
    {'fairy_speed': 3, 'fairy_count': 10, 'bat_count': 5, 'background': 'path/to/your/background2.png'},
    {'fairy_speed': 4, 'fairy_count': 0, 'dragon': True, 'background': 'path/to/your/background3.png'},
]

class Fairy(arcade.Sprite):
    def __init__(self, speed, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.speed = speed

    def update(self):
        self.center_x -= self.speed
        if self.right < 0:
            self.kill()

class Bat(arcade.Sprite):
    def __init__(self, speed, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.speed = speed

    def update(self):
        self.center_x -= self.speed
        if self.right < 0:
            self.kill()

class Dragon(arcade.Sprite):
    def __init__(self, speed, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.speed = speed

    def update(self):
        self.center_x -= self.speed
        if self.right < 0:
            self.kill()

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.player_sprite = None
        self.fairy_list = None
        self.bat_list = None
        self.dragon = None
        self.platform_list = None
        self.physics_engine = None
        self.score = 0
        self.level = 0
        self.total_fairies = 0
        self.total_bats = 0
        self.background = None

    def setup(self):
        self.player_sprite = arcade.Sprite(":resources:images/animated_characters/male_person/malePerson_idle.png", PLAYER_SCALING)
        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = 150

        self.fairy_list = arcade.SpriteList()
        self.bat_list = arcade.SpriteList()
        self.dragon = None

        self.platform_list = arcade.SpriteList()
        self.create_platforms()

        self.total_fairies = 0
        self.total_bats = 0
        self.score = 0
        self.background = arcade.load_texture(LEVELS[self.level]['background'])
        self.create_entities()

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.platform_list, gravity_constant=GRAVITY)

    def create_platforms(self):
        platform = arcade.Sprite(":resources:images/tiles/grassMid.png", 1)
        platform.center_x = SCREEN_WIDTH // 2
        platform.center_y = 50
        self.platform_list.append(platform)

    def create_entities(self):
        level_config = LEVELS[self.level]
        fairy_speed = level_config.get('fairy_speed', 0)
        fairy_count = level_config.get('fairy_count', 0)
        bat_count = level_config.get('bat_count', 0)
        dragon_present = level_config.get('dragon', False)

        for _ in range(fairy_count):
            self.create_fairy(fairy_speed)

        for _ in range(bat_count):
            self.create_bat(fairy_speed)

        if dragon_present:
            self.create_dragon(fairy_speed)

    def create_fairy(self, speed):
        fairy = Fairy(speed, ":resources:images/enemies/fly.png", FAIRY_SCALING)
        fairy.center_x = random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100)
        fairy.center_y = random.randint(20, SCREEN_HEIGHT - 20)
        self.fairy_list.append(fairy)
        self.total_fairies += 1

    def create_bat(self, speed):
        bat = Bat(speed, ":resources:images/enemies/bat.png", BAT_SCALING)
        bat.center_x = random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100)
        bat.center_y = random.randint(20, SCREEN_HEIGHT - 20)
        self.bat_list.append(bat)
        self.total_bats += 1

    def create_dragon(self, speed):
        self.dragon = Dragon(speed, ":resources:images/enemies/dragon.png", DRAGON_SCALING)
        self.dragon.center_x = random.randint(SCREEN_WIDTH + 20, SCREEN_WIDTH + 100)
        self.dragon.center_y = SCREEN_HEIGHT // 2

    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)

        self.platform_list.draw()
        self.player_sprite.draw()
        self.fairy_list.draw()
        self.bat_list.draw()
        if self.dragon:
            self.dragon.draw()

        arcade.draw_text(f"Score: {self.score}", 10, 20, arcade.color.WHITE, 14)
        arcade.draw_text(f"Level: {self.level + 1}", 10, 40, arcade.color.WHITE, 14)

    def on_update(self, delta_time):
        self.physics_engine.update()
        self.fairy_list.update()
        self.bat_list.update()
        if self.dragon:
            self.dragon.update()

        if arcade.check_for_collision_with_list(self.player_sprite, self.fairy_list) or \
           arcade.check_for_collision_with_list(self.player_sprite, self.bat_list) or \
           (self.dragon and arcade.check_for_collision(self.player_sprite, self.dragon)):
            arcade.close_window()

        self.score += 1

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.UP and self.physics_engine.can_jump():
            self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.H:
            self.next_level()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def next_level(self):
        self.level += 1
        if self.level < len(LEVELS):
            self.setup()
        else:
            arcade.draw_text("You Win!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, arcade.color.WHITE, 54, anchor_x="center")
            arcade.finish_render()
            arcade.pause(3)
            arcade.close_window()

def main():
    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
