import config
import turtle
import random
import search_algorithm
import helper as helpers
import tkinter as tk


class boardGUI:
    def __init__(self, board_grid, board_dimensions, board_obstacles, player_start_pos, opponent_start_pos):
        self.board_grid = board_grid
        self.board_dimensions = board_dimensions  # rows, columns.
        self.board_obstacles = board_obstacles
        self.opponent_start_pos = self.opponent_pos = opponent_start_pos
        self.opponent_path = None
        self.show_path = True
        self.player_start_pos = self.player_pos = player_start_pos
        self.treasure_pos = (0, 0)
        self.algorithm = "astar"
        self.player_score = 0
        self.opponent_score = 0
        self.player_direction = "stop"
        self.doing_path = False
        self.playing = False

        # Turtle Window
        self.screen = turtle.Screen()
        # self.screen.setup(config.WIDTH, config.HEIGHT)
        self.screen.setup(width=1.0, height=1.0)  # For full screen.
        self.screen.title("Finding path with Python Turtle Graphics")
        self.canvas = self.screen.getcanvas()

        # Prepare screen and start game.
        self.init_screen()
        self.reset()

    def init_screen(self):
        # Create screen and controls
        self.screen.bgcolor("white")
        self.screen.tracer(0)  # Disable animation - we will update screen manually.
        self.create_controls()
        self.screen.listen()

        # Builder
        self.builder = turtle.Turtle()
        self.builder.shape("square")
        self.builder.color("black")
        self.builder.hideturtle()
        self.builder.penup()

        # Player
        self.player = turtle.Turtle()
        self.player.shape("circle")
        self.player.color("purple")
        self.player.penup()

        # Opponent
        self.opponent = turtle.Turtle()
        self.opponent.shape("circle")
        self.opponent.color("blue")
        self.opponent.shapesize(18 / 20)
        self.opponent.penup()

        # Treasure
        self.treasure = turtle.Turtle()
        shape = ((0, 0), (10, 10), (20, 0), (10, -10))
        turtle.register_shape('diamond', shape)
        self.treasure.shape("diamond")
        self.treasure.color("red")
        self.treasure.penup()

        # Score turtle
        self.score_turtle = turtle.Turtle()
        self.score_turtle.hideturtle()
        self.score_turtle.color("pink")
        self.score_turtle.penup()

        # Draw game objects and board walls
        self.draw_board(self.board_obstacles)  # Draw board walls

    def reset(self, reset_score=False):
        # Stop any existing movement and clear trail/score.
        self.playing = False
        self.opponent.clearstamps()
        self.opponent_path = None

        # Position and draw game objects
        self.player_pos = self.player_start_pos
        self.opponent_pos = self.opponent_start_pos
        self.treasure_pos, self.opponent_path = self.place_treasure_and_get_path()
        self.draw_piece(self.opponent, self.opponent_start_pos)
        self.draw_piece(self.treasure, self.treasure_pos)
        self.draw_piece(self.player, self.player_start_pos)

        # Display initial object positions
        self.player_direction = "stop"
        self.screen.onkey(self.start_round, "s")
        self.bind_direction_keys()
        self.screen.update()

        # Scoring
        if reset_score:
            self.player_score = self.opponent_score = 0
        self.update_score_display()

        # Start message
        self.score_turtle.goto(0, 20)
        self.score_turtle.write("Press S to start", align="center", font=config.SCORE_FONT)
        self.score_turtle.goto(0, -350)

    def bind_direction_keys(self):
        self.screen.onkey(lambda: self.set_player_direction("up"), "Up")
        self.screen.onkey(lambda: self.set_player_direction("down"), "Down")
        self.screen.onkey(lambda: self.set_player_direction("left"), "Left")
        self.screen.onkey(lambda: self.set_player_direction("right"), "Right")

    def unbind_direction_keys(self):
        self.screen.onkey(lambda: None, "Up")
        self.screen.onkey(lambda: None, "Down")
        self.screen.onkey(lambda: None, "Left")
        self.screen.onkey(lambda: None, "Right")

    def create_controls(self):
        self.reset_button = tk.Button(
            self.canvas.master,
            width=5,
            text="Reset",
            background="green",
            foreground="red",
            bd=0,
            activebackground="green",
            activeforeground="white",
            font=config.BUTTON_FONT,
            command=lambda: self.reset(reset_score=True),
        )
        self.path_button = tk.Button(
            self.canvas.master,
            width=5,
            text="Path",
            background="green",
            foreground="red",
            bd=0,
            activebackground="green",
            activeforeground="white",
            font=config.BUTTON_FONT,
            command=self.toggle_show_path,
        )

        self.dfs_button = tk.Button(
            self.canvas.master,
            width=5,
            text="DFS",
            background="green",
            foreground="red",
            bd=0,
            activebackground="green",
            activeforeground="white",
            font=config.BUTTON_FONT,
            command=lambda: self.update_algorithm("dfs"),
        )

        self.bfs_button = tk.Button(
            self.canvas.master,
            width=5,
            text="BFS",
            background="green",
            foreground="red",
            bd=0,
            activebackground="green",
            activeforeground="white",
            font=config.BUTTON_FONT,
            command=lambda: self.update_algorithm("bfs"),
        )

        self.a_star_button = tk.Button(
            self.canvas.master,
            width=5,
            text="A*",
            background="green",
            foreground="red",
            bd=0,
            activebackground="green",
            activeforeground="white",
            font=config.BUTTON_FONT,
            command=lambda: self.update_algorithm("astar"),
        )

        self.canvas.create_window(-120, -340, window=self.reset_button)
        self.canvas.create_window(-60, -340, window=self.path_button)
        self.canvas.create_window(0, -340, window=self.dfs_button)
        self.canvas.create_window(60, -340, window=self.bfs_button)
        self.canvas.create_window(120, -340, window=self.a_star_button)

    def update_score_display(self):
        self.score_turtle.clear()
        self.score_turtle.goto(0, -350)
        self.score_turtle.write("Player score:{:2} Opponent Score:{:2}".format(self.player_score, self.opponent_score),
                                align="center",
                                font=config.GAME_OVER_FONT)

    def game_over(self):
        self.score_turtle.goto(0, 0)
        self.score_turtle.write("GAME OVER", align="center", font=config.SCORE_FONT)
        self.canvas.after(2000)
        self.reset(reset_score=True)

    def toggle_show_path(self):
        self.show_path = not self.show_path
        if self.show_path:
            self.path_button.config(fg="red")
        else:
            self.path_button.config(fg="white")

    def update_algorithm(self, alg):
        self.algorithm = alg
        buttons = [self.dfs_button, self.bfs_button, self.a_star_button]
        for button in buttons:
            button.config(fg="white")
        if alg == "dfs":
            self.dfs_button.config(fg="red")
        elif alg == "bfs":
            self.bfs_button.config(fg="red")
        elif alg == "a_star":
            self.a_star_button.config(fg="red")
        self.reset(reset_score=False)

    def draw_board(self, obstacles):
        for obstacle in obstacles:
            self.builder.goto(helpers.screen_coordinates_from_grid_position(obstacle, self.board_dimensions))
            self.builder.stamp()

    def draw_piece(self, piece, pos, stamp=False):
        piece.goto(helpers.screen_coordinates_from_grid_position(pos, self.board_dimensions))
        if stamp:
            piece.stamp()

    def place_treasure_and_get_path(self):
        while True:
            i = random.randrange(self.board_dimensions[0])
            j = random.randrange(self.board_dimensions[1])
            if not (i, j) in self.board_obstacles and (i, j) != self.player_pos and (i, j) != self.opponent_pos:
                potential_pos = (i, j)
                path = self.calculate_path(potential_pos)
                if path is None:
                    continue
                return (i, j), path

    def calculate_path(self, treasure_pos):
        if self.algorithm == "dfs":
            return search_algorithm.dfs(self.board_grid, self.opponent_start_pos, treasure_pos)
        elif self.algorithm == "bfs":
            return search_algorithm.bfs(self.board_grid, self.opponent_start_pos, treasure_pos)
        elif self.algorithm == "astar":
            return search_algorithm.astar(self.board_grid, self.opponent_start_pos, treasure_pos)
        else:
            return None

    def move_opponent(self):
        # Get next position in path
        try:
            next_pos = self.opponent_path.pop(0)
        except IndexError:
            return
        # Move opponent to next position
        self.draw_piece(self.opponent, next_pos, self.show_path)
        # Check for collision with treasure
        if next_pos == self.treasure_pos:
            # Player has found treasure
            self.playing = False
            self.screen.update()  # Show opponent in same cell as treasure
            self.opponent_score += 1
            self.update_score_display()
            if self.opponent_score == config.TARGET_SCORE:
                self.game_over()
            else:
                self.canvas.after(1000)
                self.reset()

    def set_player_direction(self, direction):
        if self.playing:
            new_pos = (self.player_pos[0] + config.offset_parameter[direction][0],
                       self.player_pos[1] + config.offset_parameter[direction][1])  # Repeated in move_player.
            if new_pos not in self.board_obstacles:
                self.player_direction = direction

    def start_round(self):
        self.update_score_display()
        self.screen.onkey(None, "s")  # Unbind (s)tart key to prevent event stacking.
        self.playing = True
        self.game_loop()

    def move_player(self):
        # Calculate potential new position
        if self.player_direction != "stop":
            new_pos = (self.player_pos[0] + config.offset_parameter[self.player_direction][0],
                       self.player_pos[1] + config.offset_parameter[self.player_direction][1])

            # if new pos is legal, move player
            if 0 <= new_pos[0] < self.board_dimensions[0] and 0 <= new_pos[1] < self.board_dimensions[1]:
                if new_pos not in self.board_obstacles:
                    self.player_pos = new_pos
                    self.draw_piece(self.player, self.player_pos)

            # check for treasure collision
            if new_pos == self.treasure_pos:
                # Player has found treasure
                self.playing = False
                self.screen.update()  # Show player in same cell as treasure
                self.player_score += 1
                self.update_score_display()
                if self.player_score == config.TARGET_SCORE:
                    self.game_over()
                else:
                    self.canvas.after(1000)
                    self.reset()

    def game_loop(self):
        if self.playing:
            self.move_player()
            self.move_opponent()
            self.screen.update()
            turtle.ontimer(self.game_loop, config.GAME_SPEED)


if __name__ == "__main__":
    board_grid, board_dimensions, board_obstacles, player_start_pos, opponent_start_pos = helpers.read_board_from_file(
        config.BOARD_FILE)
    boardGUI(board_grid, board_dimensions, board_obstacles, player_start_pos, opponent_start_pos)
    turtle.done()