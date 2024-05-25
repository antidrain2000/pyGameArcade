import arcade
import random

# Константы для настройки игры
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Dodge the Fairies"
PLAYER_SCALING = 1
FAIRY_SCALING = 0.5
BAT_SCALING = 0.5
DRAGON_SCALING = 1.0
PLAYER_MOVEMENT_SPEED = 5
PLAYER_JUMP_SPEED = 15
GRAVITY = 1
PLAYER_HEALTH = 4
DRAGON_HEALTH = 5

LEVELS = [
    {'fairy_speed': 2, 'fairy_count': 5, 'bat_count': 0, 'background': 'background1.png', 'story_image': 'story1.png'},
    {'fairy_speed': 0, 'fairy_count': 0, 'bat_speed': 3, 'bat_count': 10, 'background': 'background2.png',
     'story_image': 'story2.png'},
    {'fairy_speed': 0, 'fairy_count': 0, 'bat_count': 0, 'dragon': True, 'background': 'background3.png',
     'story_image': 'story3.png'},
]


class HealthBar(arcade.Sprite):
    def __init__(self, image_list, max_health, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.textures = [arcade.load_texture(image) for image in image_list]
        self.max_health = max_health
        self.health = max_health
        self.set_texture(self.health - 1)

    def set_health(self, health):
        self.health = health
        health_index = max(0, min(self.max_health - 1, self.max_health - health))
        self.set_texture(health_index)

    def draw(self):
        super().draw()
        self.set_texture(self.health - 1)


class Fairy(arcade.Sprite):
    def __init__(self, speed, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.speed = speed
        self.damage = 1

    def update(self):
        self.center_x -= self.speed
        if self.right < 0:
            self.kill()


class Bat(arcade.Sprite):
    def __init__(self, speed, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.speed = speed
        self.damage = 1

    def update(self):
        self.center_x -= self.speed
        if self.right < 0:
            self.kill()


class Dragon(arcade.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fire_textures = []
        self.current_fire_texture = 0
        self.fire_timer = 0
        self.damage = 1

    def update(self):
        self.fire_timer += 1
        if self.fire_timer > 60:  # Change texture every second
            self.fire_timer = 0
            self.current_fire_texture += 1
            if self.current_fire_texture >= len(self.fire_textures):
                self.current_fire_texture = 0
            self.texture = self.fire_textures[self.current_fire_texture]


class StoryScreen(arcade.Sprite):
    def __init__(self, image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.texture = arcade.load_texture(image)


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
        self.story_screen = None
        self.story_index = -1
        self.health_bars = []

    def setup(self):
        # Устанавливаем игрока
        self.player_sprite = arcade.AnimatedWalkingSprite()
        self.player_sprite.stand_right_textures = [arcade.load_texture("player.png")]
        self.player_sprite.stand_left_textures = [arcade.load_texture("player.png", mirrored=True)]
        self.player_sprite.walk_right_textures = [
            arcade.load_texture("player_walk1.png"),
            arcade.load_texture("player_walk2.png")
        ]
        self.player_sprite.walk_left_textures = [
            arcade.load_texture("player_walk1.png", mirrored=True),
            arcade.load_texture("player_walk2.png", mirrored=True)
        ]
        self.player_sprite.jump_texture = arcade.load_texture("player_jump1.png")
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 150
        self.player_sprite.scale = PLAYER_SCALING

        self.fairy_list = arcade.SpriteList()
        # Создаем и добавляем экземпляры фей в список
        for i in range(LEVELS[self.level]['fairy_count']):
            fairy = Fairy("fly.png", LEVELS[self.level]['fairy_speed'])
            fairy.center_x = random.randrange(SCREEN_WIDTH)
            fairy.center_y = random.randrange(SCREEN_HEIGHT)
            self.fairy_list.append(fairy)

        # Создаем список летучих мышей
        self.bat_list = arcade.SpriteList()
        # Создаем и добавляем экземпляры летучих мышей в список
        for i in range(LEVELS[self.level]['bat_count']):
            bat = Bat("bat.png", LEVELS[self.level]['bat_speed'])
            bat.center_x = random.randrange(SCREEN_WIDTH)
            bat.center_y = random.randrange(SCREEN_HEIGHT)
            self.bat_list.append(bat)

        # Создаем список платформ
        self.platform_list = arcade.SpriteList()
        # Создаем и добавляем экземпляры платформ в список
        for x in range(0, SCREEN_WIDTH, 64):
            platform = Platform("ground.png")
            platform.center_x = x
            platform.center_y = 32
            self.platform_list.append(platform)

        # Устанавливаем дракона
        self.dragon = Dragon()
        self.dragon.textures = [arcade.load_texture("dragon_texture1.png")]
        self.dragon.fire_textures = [
            arcade.load_texture("dragon_fire.png"),
        ]
        self.dragon.scale = DRAGON_SCALING
        self.dragon.center_x = SCREEN_WIDTH // 2
        self.dragon.center_y = SCREEN_HEIGHT // 2

        # Устанавливаем фон
        self.background = arcade.load_texture(LEVELS[self.level]['background'])

        # Устанавливаем физический движок
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.platform_list,
                                                             gravity_constant=GRAVITY)

        # Устанавливаем предысторию
        self.story_screen = StoryScreen(LEVELS[self.level]['story_image'])
        self.story_screen.center_x = SCREEN_WIDTH // 2
        self.story_screen.center_y = SCREEN_HEIGHT // 2

        # Устанавливаем индикаторы здоровья
        self.health_bars = [
            HealthBar(["health_4.png", "health_3.png", "health_2.png", "health_1.png"], PLAYER_HEALTH,
                       "health_1.png",
                      scale=0.25, center_x=40, center_y=SCREEN_HEIGHT - 20),
            HealthBar(["dragon_health5.png", "dragon_health4.png", "dragon_health3.png", "dragon_health2.png",
                       "dragon_health1.png"], DRAGON_HEALTH,
                       "dragon_health.png", scale=0.25, center_x=40, center_y=SCREEN_HEIGHT - 60)
        ]

    def on_draw(self):
        arcade.start_render()

        # Рисуем фон
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, SCREEN_WIDTH, SCREEN_HEIGHT,
                                      self.background)

        if self.story_index >= 0:
            self.story_screen.draw()
            return

        # Рисуем платформы
        self.platform_list.draw()

        # Рисуем игрока
        self.player_sprite.draw()

        # Рисуем фей и летучих мышей
        self.fairy_list.draw()
        self.bat_list.draw()

        # Рисуем дракона
        if self.level == 2:
            self.dragon.draw()

        # Рисуем индикаторы здоровья
        for health_bar in self.health_bars:
            health_bar.draw()

    def on_update(self, delta_time):
        if self.story_index >= 0:
            return

        # Обновляем игрока
        self.physics_engine.update()

        # Обновляем фей и летучих мышей
        self.fairy_list.update()
        self.bat_list.update()

        # Проверяем столкновение игрока с феями и летучими мышами
        for fairy in self.fairy_list:
            if arcade.check_for_collision(self.player_sprite, fairy):
                self.player_health -= fairy.damage
                fairy.kill()

        for bat in self.bat_list:
            if arcade.check_for_collision(self.player_sprite, bat):
                self.player_health -= bat.damage
                bat.kill()

        # Проверяем столкновение игрока с огнем дракона
        if self.level == 2 and arcade.check_for_collision(self.player_sprite, self.dragon):
            self.player_health -= self.dragon.damage

        # Проверяем выигрыш или проигрыш
        if self.player_health <= 0:
            self.setup()
        elif self.level == 2 and self.dragon_health <= 0:
            self.setup()

        # Обновляем индикаторы здоровья
        self.health_bars[0].set_health(self.player_health)
        if self.level == 2:
            self.health_bars[1].set_health(self.dragon_health)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP and self.physics_engine.can_jump():
            self.player_sprite.change_y = PLAYER_JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.H and self.level != 2:
            self.level += 1
            self.setup()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

def main():
        window = MyGame()
        window.setup()
        arcade.run()

if __name__ == "__main__":
    main()