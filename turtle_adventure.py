"""
The turtle_adventure module maintains all classes related to the Turtle's
adventure game.
"""
from turtle import RawTurtle
from gamelib import Game, GameElement
import random, math


class TurtleGameElement(GameElement):
    """
    An abstract class representing all game elemnets related to the Turtle's
    Adventure game
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__game: "TurtleAdventureGame" = game

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game


class Waypoint(TurtleGameElement):
    """
    Represent the waypoint to which the player will move.
    """

    def __init__(self, game: "TurtleAdventureGame"):
        super().__init__(game)
        self.__id1: int
        self.__id2: int
        self.__active: bool = False

    def create(self) -> None:
        self.__id1 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")
        self.__id2 = self.canvas.create_line(0, 0, 0, 0, width=2, fill="green")

    def delete(self) -> None:
        self.canvas.delete(self.__id1)
        self.canvas.delete(self.__id2)

    def update(self) -> None:
        # there is nothing to update because a waypoint is fixed
        pass

    def render(self) -> None:
        if self.is_active:
            self.canvas.itemconfigure(self.__id1, state="normal")
            self.canvas.itemconfigure(self.__id2, state="normal")
            self.canvas.tag_raise(self.__id1)
            self.canvas.tag_raise(self.__id2)
            self.canvas.coords(self.__id1, self.x - 10, self.y - 10,
                               self.x + 10, self.y + 10)
            self.canvas.coords(self.__id2, self.x - 10, self.y + 10,
                               self.x + 10, self.y - 10)
        else:
            self.canvas.itemconfigure(self.__id1, state="hidden")
            self.canvas.itemconfigure(self.__id2, state="hidden")

    def activate(self, x: float, y: float) -> None:
        """
        Activate this waypoint with the specified location.
        """
        self.__active = True
        self.x = x
        self.y = y

    def deactivate(self) -> None:
        """
        Mark this waypoint as inactive.
        """
        self.__active = False

    @property
    def is_active(self) -> bool:
        """
        Get the flag indicating whether this waypoint is active.
        """
        return self.__active


class Home(TurtleGameElement):
    """
    Represent the player's home.
    """

    def __init__(self, game: "TurtleAdventureGame", pos: tuple[int, int],
                 size: int):
        super().__init__(game)
        self.__id: int
        self.__size: int = size
        x, y = pos
        self.x = x
        self.y = y

    @property
    def size(self) -> int:
        """
        Get or set the size of Home
        """
        return self.__size

    @size.setter
    def size(self, val: int) -> None:
        self.__size = val

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, outline="brown",
                                                 width=2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)

    def update(self) -> None:
        # there is nothing to update, unless home is allowed to moved
        pass

    def render(self) -> None:
        self.canvas.coords(self.__id,
                           self.x - self.size / 2,
                           self.y - self.size / 2,
                           self.x + self.size / 2,
                           self.y + self.size / 2)

    def contains(self, x: float, y: float):
        """
        Check whether home contains the point (x, y).
        """
        x1, x2 = self.x - self.size / 2, self.x + self.size / 2
        y1, y2 = self.y - self.size / 2, self.y + self.size / 2
        return x1 <= x <= x2 and y1 <= y <= y2


class Player(TurtleGameElement):
    """
    Represent the main player, implemented using Python's turtle.
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 turtle: RawTurtle,
                 speed: float = 5):
        super().__init__(game)
        self.__speed: float = speed
        self.__turtle: RawTurtle = turtle

    def create(self) -> None:
        turtle = RawTurtle(self.canvas)
        turtle.getscreen().tracer(False)  # disable turtle's built-in animation
        turtle.shape("turtle")
        turtle.color("green")
        turtle.penup()

        self.__turtle = turtle

    @property
    def speed(self) -> float:
        """
        Give the player's current speed.
        """
        return self.__speed

    @speed.setter
    def speed(self, val: float) -> None:
        self.__speed = val

    def delete(self) -> None:
        pass

    def update(self) -> None:
        # check if player has arrived home
        if self.game.home.contains(self.x, self.y):
            self.game.game_over_win()
        turtle = self.__turtle
        waypoint = self.game.waypoint
        if self.game.waypoint.is_active:
            turtle.setheading(turtle.towards(waypoint.x, waypoint.y))
            turtle.forward(self.speed)
            if turtle.distance(waypoint.x, waypoint.y) < self.speed:
                waypoint.deactivate()

    def render(self) -> None:
        self.__turtle.goto(self.x, self.y)
        self.__turtle.getscreen().update()

    # override original property x's getter/setter to use turtle's methods
    # instead
    @property
    def x(self) -> float:
        return self.__turtle.xcor()

    @x.setter
    def x(self, val: float) -> None:
        self.__turtle.setx(val)

    # override original property y's getter/setter to use turtle's methods
    # instead
    @property
    def y(self) -> float:
        return self.__turtle.ycor()

    @y.setter
    def y(self, val: float) -> None:
        self.__turtle.sety(val)


class Enemy(TurtleGameElement):
    """
    Define an abstract enemy for the Turtle's adventure game
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game)
        self.__size = size
        self.__color = color

    @property
    def size(self) -> float:
        """
        Get the size of the enemy
        """
        return self.__size

    @property
    def color(self) -> str:
        """
        Get the color of the enemy
        """
        return self.__color

    def hits_player(self):  # return bool
        """
        Check whether the enemy is hitting the player
        """
        return (
                (
                            self.x - self.size / 2 < self.game.player.x < self.x + self.size / 2)
                and
                (
                            self.y - self.size / 2 < self.game.player.y < self.y + self.size / 2)
        )


# TODO
# * Define your enemy classes
# * Implement all methods required by the GameElement abstract class
# * Define enemy's update logic in the update() method
# * Check whether the player hits this enemy, then call the
#   self.game.game_over_lose() method in the TurtleAdventureGame class.
class DemoEnemy(Enemy):
    """
    Demo enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str):
        super().__init__(game, size, color)
        self.__id = None
        self.direction = 1  # Initial direction

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        self.x += 1  # walk straight
        self.y += 1

        if self.x >= self.game.screen_width or self.x <= 0:
            self.direction *= -1
        if self.y >= self.game.screen_height or self.y <= 0:
            self.direction *= -1

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id, self.x - self.size / 2,
                           self.y - self.size / 2, self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        # self.canvas.delete(self.__id)
        pass


class RandomWalkEnemy(Enemy):
    """
    Random walk enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed: float = 3):
        super().__init__(game, size, color)
        self.__id = None
        self.speed = speed
        self.direction = random.randint(0, 360)

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        self.x += self.speed * math.cos(math.radians(self.direction))
        self.y += self.speed * math.sin(math.radians(self.direction))

        # horizontal frame
        if (self.x + self.size / 2 >= self.game.screen_width or
                self.x - self.size / 2 <= 0):
            self.direction = 180 - self.direction
            # flip direction if hits

            # adjust position to prevent going out of bounds
            if self.x + self.size / 2 >= self.game.screen_width:
                self.x = self.game.screen_width - self.size / 2
            elif self.x - self.size / 2 <= 0:
                self.x = self.size / 2

        # vertical frame
        if (self.y + self.size / 2 >= self.game.screen_height or
                self.y - self.size / 2 <= 0):
            self.direction = -self.direction

            # adjust the position to prevent going out of bounds
            if self.y + self.size / 2 >= self.game.screen_height:
                self.y = self.game.screen_height - self.size / 2
            elif self.y - self.size / 2 <= 0:
                self.y = self.size / 2

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id, self.x - self.size / 2,
                           self.y - self.size / 2, self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class ChasingEnemy(Enemy):
    """
    Chasing enemy
    """

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed: float = 2):
        super().__init__(game, size, color)
        self.__id = None
        self.speed = speed  # Enemy's speed is 1

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        player_x, player_y = self.game.player.x, self.game.player.y
        direction = math.atan2(player_y - self.y, player_x - self.x)
        self.x += math.cos(direction) * self.speed
        self.y += math.sin(direction) * self.speed

        # Check if the enemy is going out of the screen boundaries
        if self.x - self.size / 2 < 0:
            self.x = self.size / 2  # prevent going out of bounds
        elif self.x + self.size / 2 > self.game.screen_width:
            self.x = self.game.screen_width - self.size / 2
        if self.y - self.size / 2 < 0:
            self.y = self.size / 2
        elif self.y + self.size / 2 > self.game.screen_height:
            self.y = self.game.screen_height - self.size / 2

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id, self.x - self.size / 2,
                           self.y - self.size / 2, self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class FencingEnemy(Enemy):
    """
    *walk around the home in a square-like pattern* enemy
    """
    HOME_OFFSET = 20

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed: float = 1):
        super().__init__(game, size, color)
        self.__directions = [(1, 0), (0, 1), (-1, 0),
                             (0, -1)]  # right, down, left, up
        self.__current_direction_index = 0
        self.__home_x = self.game.home.x
        self.__home_y = self.game.home.y
        self.__offset = self.HOME_OFFSET + self.game.home.size / 2
        self.x = self.__home_x - self.__offset
        self.y = self.__home_y - self.__offset
        self.speed = speed

    def create(self) -> None:
        self.__id = self.canvas.create_oval(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        dx, dy = self.__directions[self.__current_direction_index]
        self.x += dx * self.speed
        self.y += dy * self.speed

        if self.x >= self.__home_x + self.__offset and dx == 1:  # right border
            self.__current_direction_index \
                = (self.__current_direction_index + 1) % 4
        elif self.x <= self.__home_x - self.__offset and dx == -1:  # left border
            self.__current_direction_index \
                = (self.__current_direction_index + 1) % 4
        elif self.y >= self.__home_y + self.__offset and dy == 1:  # bottom border
            self.__current_direction_index \
                = (self.__current_direction_index + 1) % 4
        elif self.y <= self.__home_y - self.__offset and dy == -1:  # top border
            self.__current_direction_index \
                = (self.__current_direction_index + 1) % 4

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id, self.x - self.size / 2,
                           self.y - self.size / 2, self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)


class SinEnemy(Enemy):
    """Sin enemy"""

    def __init__(self,
                 game: "TurtleAdventureGame",
                 size: int,
                 color: str,
                 speed: float = 1):
        super().__init__(game, size, color)
        self.__amplitude = 50
        self.__frequency = 0.02
        self.__speed = speed
        self.__angle = 0
        self.__id = None

        self.x = 0
        self.y = self.game.screen_height / 4

    def create(self) -> None:
        self.__id = self.canvas.create_rectangle(0, 0, 0, 0, fill=self.color)

    def update(self) -> None:
        self.x += self.__speed
        self.y += self.__amplitude * math.sin(self.__frequency * self.x)

        if self.x - self.size / 2 < 0:
            self.x = self.size / 2
            self.__speed *= -1
        elif self.x + self.size / 2 > self.game.screen_width:
            self.x = self.game.screen_width - self.size / 2
            self.__speed *= -1

        if self.y - self.size / 2 < 0:
            self.y = self.size / 2
        elif self.y + self.size / 2 > self.game.screen_height:
            self.y = self.game.screen_height - self.size / 2

        if self.hits_player():
            self.game.game_over_lose()

    def render(self) -> None:
        self.canvas.coords(self.__id, self.x - self.size / 2,
                           self.y - self.size / 2, self.x + self.size / 2,
                           self.y + self.size / 2)

    def delete(self) -> None:
        self.canvas.delete(self.__id)


# Complete the EnemyGenerator class by inserting code to generate enemies
# based on the given game level; call TurtleAdventureGame's add_enemy() method
# to add enemies to the game at certain points in time.
#
# Hint: the 'game' parameter is a tkinter's frame, so it's after()
# method can be used to schedule some future events.

class EnemyGenerator:
    """
    An EnemyGenerator instance is responsible for creating enemies of various
    kinds and scheduling them to appear at certain points in time.
    """

    def __init__(self, game: "TurtleAdventureGame", level: int):
        self.__game: TurtleAdventureGame = game
        self.__level: int = level
        self.__fencing_enemy_count: int = 0
        self.__sin_enemy_count: int = 0

        # example
        self.__game.after(100, self.create_enemy)

    @property
    def game(self) -> "TurtleAdventureGame":
        """
        Get reference to the associated TurtleAnvengerGame instance
        """
        return self.__game

    @property
    def level(self) -> int:
        """
        Get the game level
        """
        return self.__level

    def create_enemy(self) -> None:
        """
        Create a new enemy, possibly based on the game level
        """
        new_enemy = DemoEnemy(self.__game, 20, "red")
        new_enemy.x = 100
        new_enemy.y = 100
        self.game.add_element(new_enemy)

        randomwalk_enemy = RandomWalkEnemy(self.__game, 15, "pink")
        randomwalk_enemy.x = random.randint(0, 800)
        randomwalk_enemy.y = random.randint(0, 500)
        self.game.add_element(randomwalk_enemy)

        chasing_enemy = ChasingEnemy(self.__game, 30, "skyblue")
        chasing_enemy.x = random.randint(0, 800)
        chasing_enemy.y = random.randint(0, 500)
        self.game.add_element(chasing_enemy)

        if self.__fencing_enemy_count < 7:
            fencing_enemy = FencingEnemy(self.__game, 10, "lightgreen")
            fencing_enemy.x = self.game.home.x
            fencing_enemy.y = self.game.home.y
            self.game.add_element(fencing_enemy)
            self.__fencing_enemy_count += 1

        if self.__sin_enemy_count < 10:
            random_x = random.randint(0, self.game.screen_width)

            sin_enemy = SinEnemy(self.__game, 20, "Lightyellow")
            sin_enemy.x = random_x
            sin_enemy.y = self.game.screen_height / 4
            self.game.add_element(sin_enemy)

            self.__sin_enemy_count += 1

            # Call the method again for continuous enemy generation
            self.__game.after(1000, self.create_enemy)


class TurtleAdventureGame(Game):  # pylint: disable=too-many-ancestors
    """
    The main class for Turtle's Adventure.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, screen_width: int, screen_height: int,
                 level: int = 1):
        self.level: int = level
        self.screen_width: int = screen_width
        self.screen_height: int = screen_height
        self.waypoint: Waypoint
        self.player: Player
        self.home: Home
        self.enemies: list[Enemy] = []
        self.enemy_generator: EnemyGenerator
        super().__init__(parent)

    def init_game(self):
        self.canvas.config(width=self.screen_width, height=self.screen_height)
        turtle = RawTurtle(self.canvas)
        # set turtle screen's origin to the top-left corner
        turtle.screen.setworldcoordinates(0, self.screen_height - 1,
                                          self.screen_width - 1, 0)

        self.waypoint = Waypoint(self)
        self.add_element(self.waypoint)
        self.home = Home(self,
                         (self.screen_width - 100, self.screen_height // 2),
                         20)
        self.add_element(self.home)
        self.player = Player(self, turtle)
        self.add_element(self.player)
        self.canvas.bind("<Button-1>",
                         lambda e: self.waypoint.activate(e.x, e.y))

        self.enemy_generator = EnemyGenerator(self, level=self.level)

        self.player.x = 50
        self.player.y = self.screen_height // 2

    def add_enemy(self, enemy: Enemy) -> None:
        """
        Add a new enemy into the current game
        """
        self.enemies.append(enemy)
        self.add_element(enemy)

    def game_over_win(self) -> None:
        """
        Called when the player wins the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width / 2,
                                self.screen_height / 2,
                                text="You Win",
                                font=font,
                                fill="green")

    def game_over_lose(self) -> None:
        """
        Called when the player loses the game and stop the game
        """
        self.stop()
        font = ("Arial", 36, "bold")
        self.canvas.create_text(self.screen_width / 2,
                                self.screen_height / 2,
                                text="You Lose",
                                font=font,
                                fill="red")
