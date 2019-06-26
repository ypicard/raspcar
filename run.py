from math import atan2, sqrt, cos, sin
import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN_TITLE = "Drive.ai"


class Dashboard():
    WIDTH = 200
    HEIGHT = 100
    BACKGROUND_COLOR = arcade.color.WHITE

    def __init__(self, car):
        self._car = car

    def draw(self):
        arcade.draw_polygon_filled([(SCREEN_WIDTH - self.WIDTH, SCREEN_HEIGHT - self.HEIGHT),
                                    (SCREEN_WIDTH - self.WIDTH, SCREEN_HEIGHT),
                                    (SCREEN_WIDTH, SCREEN_HEIGHT),
                                    (SCREEN_WIDTH, SCREEN_HEIGHT - self.HEIGHT)], self.BACKGROUND_COLOR)
        arcade.draw_text(f"""
- pos : ({self._car.center_x:.2f}, {self._car.center_y:.2f})
- speed : {self._car.speed:.2f}
- acc : {self._car.acc:.2f}
- collides : {self._car.collides} 
""", SCREEN_WIDTH - self.WIDTH, SCREEN_HEIGHT - self.HEIGHT, arcade.color.BLACK)


class Radar():
    RADAR_SIZE = 250

    def __init__(self, car, radians_offset=0):
        self.car = car
        self.radians_offset = radians_offset
        self.radians = self.car.radians + self.radians_offset
        self.color = arcade.color.RED
        self.start_x = self.car.center_x
        self.start_y = self.car.center_y
        self.end_x = self.car.center_x + cos(self.radians) * self.RADAR_SIZE
        self.end_y = self.car.center_y + sin(self.radians) * self.RADAR_SIZE

    def update(self):
        self.radians = self.car.radians + self.radians_offset
        self.start_x = self.car.center_x
        self.start_y = self.car.center_y
        self.end_x = self.car.center_x + cos(self.radians) * self.RADAR_SIZE
        self.end_y = self.car.center_y + sin(self.radians) * self.RADAR_SIZE

    def _get_points(self):
        return [(self.start_x, self.start_y), (self.end_x, self.end_y)]

    def bip(self, objects):
        collides = False
        for o in objects:
            if arcade.are_polygons_intersecting(self._get_points(), o):
                collides = True
                break
        return collides

    def draw(self):
        arcade.draw_line(self.start_x, self.start_y,
                         self.end_x, self.end_y, self.color)


class Car(arcade.Sprite):
    CAR_WIDTH = 50
    CAR_LENGTH = 100
    MAX_SPEED = 5
    MAX_ACC = 3
    HORSE_POWER = 0.1
    STEER = 0.05

    def __init__(self):
        super().__init__('images/car.png', scale=1, center_x=50, center_y=100)
        self.acc = 0
        self.speed = 0
        self.radars = [Radar(self), Radar(self, 0.523), Radar(self, -0.523)]
        self.bips = [0] * len(self.radars)
        self.collides = False

    def _compute_speed(self):
        return sqrt(self.change_x * self.change_x + self.change_y * self.change_y)

    def throttle(self, val):
        """
        Increase or decrease car speed
        val = 1 : speed up
        val = 0 : constant
        val = -1 : slow down
        """
        self.acc = val * self.HORSE_POWER
        # max acceleration
        if self.acc > self.MAX_ACC:
            self.acc = self.MAX_ACC
        # No negative acceleration if no speed
        if self.acc < 0 and self.speed <= 0:
            self.acc = 0

        speed = self._compute_speed()
        self.change_x = (speed + self.acc) * cos(self.radians)
        self.change_y = (speed + self.acc) * sin(self.radians)

        # max speed
        if speed > self.MAX_SPEED:
            self.change_x = self.MAX_SPEED * \
                cos(atan2(self.change_y, self.change_x))
            self.change_y = self.MAX_SPEED * \
                sin(atan2(self.change_y, self.change_x))
        # No negative speed
        if self.change_x * cos(self.radians) + self.change_y * sin(self.radians) < 0:
            self.change_x = 0
            self.change_y = 0
        self.speed = self._compute_speed()

    def turn(self, val):
        """
        Turn car left or right
        val = 1 : right
        val = 0 : straight
        val = -1 : left
        """
        self.radians -= val * self.STEER

    def update(self):
        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.center_x < 0:
            self.center_x = 0
        if self.center_x > SCREEN_WIDTH:
            self.center_x = SCREEN_WIDTH
        if self.center_y < 0:
            self.center_y = 0
        if self.center_y > SCREEN_HEIGHT:
            self.center_y = SCREEN_HEIGHT

        for radar in self.radars:
            radar.update()

    def draw(self):
        """ Override Sprite draw method """
        super(Car, self).draw()
        for radar in self.radars:
            radar.draw()

    def run_radars(self, objects):
        self.collides = False
        self.bips = [0] * 3
        for idx, radar in enumerate(self.radars):
            if radar.bip(objects):
                self.collides = True
                self.bips[idx] = 1

    def metadata(self):
        return { 'speed': self.speed,
                'speed_x': self.change_x,
                'speed_y': self.change_y,
                'x': self.center_x,
                'y': self.center_y,
                'acc': self.acc,
                'radians': self.radians,
                'collides': self.collides,
                'bips': self }


class MyGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.AMAZON)

        # If you have sprite lists, you should create them here,
        # and set them to None
        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.car = None
        self.test_polygon = None
        # self.dashboard = None

    def setup(self):
        self.car = Car()
        self.test_polygon = [(400, 400), (500, 400), (500, 500), (400, 500)]
        # self.dashboard = Dashboard(self.car)

    def on_draw(self):
        """ Render the screen. """

        arcade.start_render()  # Clear screen
        self.car.draw()
        arcade.draw_polygon_filled(self.test_polygon, arcade.color.BLUE)
        # self.dashboard.draw()

    def update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        # throttle
        throttle = 0
        if self.up_pressed:
            throttle = 1
        elif self.down_pressed:
            throttle = -1
        # turn
        turn = 0
        if self.right_pressed:
            turn = 1
        elif self.left_pressed:
            turn = -1

        self.car.turn(turn)
        self.car.throttle(throttle)
        self.car.update()
        self.car.run_radars([self.test_polygon])
        metadata = self.car.metadata()
        if metadata['collides']:
            self.setup()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP:
            self.up_pressed = True
        elif key == arcade.key.DOWN:
            self.down_pressed = True
        elif key == arcade.key.LEFT:
            self.left_pressed = True
        elif key == arcade.key.RIGHT:
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP:
            self.up_pressed = False
        elif key == arcade.key.DOWN:
            self.down_pressed = False
        elif key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.RIGHT:
            self.right_pressed = False


def main():
    """ Main method """
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
