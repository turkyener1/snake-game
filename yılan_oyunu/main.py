import cv2
import mediapipe as mp
import numpy as np
import turtle
import random

# Constants for screen size
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

class SnakeGame:
    def __init__(self):
        # Initialize the Snake game window
        self.wn = turtle.Screen()
        self.wn.title("Hand-Controlled Snake Game")
        self.wn.bgcolor("black")
        self.wn.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)

        # Create the Snake
        self.snake = turtle.Turtle()
        self.snake.speed(0)
        self.snake.shape("square")
        self.snake.color("white")
        self.snake.penup()
        self.snake.goto(0, 0)
        self.snake.direction = "stop"

        # Create the food for the Snake
        self.food = turtle.Turtle()
        self.food.speed(0)
        self.food.shape("circle")
        self.food.color("red")
        self.food.penup()
        self.food.goto(0, 100)

        # Create a list to store the snake's body segments
        self.segments = []

    def add_segment(self):
        # Create a new body segment for the snake
        segment = turtle.Turtle()
        segment.speed(0)
        segment.shape("square")
        segment.color("white")
        segment.penup()
        self.segments.append(segment)

    def move(self):
        # Handle Snake movement logic based on its direction
        if self.snake.direction == "up":
            y = self.snake.ycor()
            self.snake.sety(y + 12)
        elif self.snake.direction == "down":
            y = self.snake.ycor()
            self.snake.sety(y - 12)
        elif self.snake.direction == "left":
            x = self.snake.xcor()
            self.snake.setx(x - 12)
        elif self.snake.direction == "right":
            x = self.snake.xcor()
            self.snake.setx(x + 12)

        # Check if the snake crosses the screen boundaries and wrap around
        if self.snake.xcor() > SCREEN_WIDTH / 2:
            self.snake.setx(-SCREEN_WIDTH / 2)
        elif self.snake.xcor() < -SCREEN_WIDTH / 2:
            self.snake.setx(SCREEN_WIDTH / 2)
        if self.snake.ycor() > SCREEN_HEIGHT / 2:
            self.snake.sety(-SCREEN_HEIGHT / 2)
        elif self.snake.ycor() < -SCREEN_HEIGHT / 2:
            self.snake.sety(SCREEN_HEIGHT / 2)

        # Check if the snake eats the food
        if self.snake.distance(self.food) < 20:
            # Move the food to a random position
            self.food.goto(random.randint(-SCREEN_WIDTH / 2, SCREEN_WIDTH / 2), random.randint(-SCREEN_HEIGHT / 2, SCREEN_HEIGHT / 2))

            # Add a new segment to the snake
            self.add_segment()

        # Move the snake's body
        for i in range(len(self.segments) - 1, 0, -1):
            x = self.segments[i - 1].xcor()
            y = self.segments[i - 1].ycor()
            self.segments[i].goto(x, y)

        if len(self.segments) > 0:
            x = self.snake.xcor()
            y = self.snake.ycor()
            self.segments[0].goto(x, y)

    def go_up(self):
        if self.snake.direction != "down":  # Snake cannot go directly from down to up
            self.snake.direction = "up"

    def go_down(self):
        if self.snake.direction != "up":  # Snake cannot go directly from up to down
            self.snake.direction = "down"

    def go_left(self):
        if self.snake.direction != "right":  # Snake cannot go directly from right to left
            self.snake.direction = "left"

    def go_right(self):
        if self.snake.direction != "left":  # Snake cannot go directly from left to right
            self.snake.direction = "right"

class HandTracker:
    def __init__(self):
        # Initialize the hand-tracking system
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5, max_num_hands=1)
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, image):
        # Resize the image to a smaller resolution (e.g., 320x240)
        image = cv2.resize(image, (320, 240))

        # Process the video frame and detect hands
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(image_rgb)

        # Draw hand landmarks on the image
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(image, hand_landmarks,
                                            self.mp_hands.HAND_CONNECTIONS)
        return image

    def find_position(self):
        lm_list = []
        if self.results.multi_hand_landmarks:
            hand_landmarks = self.results.multi_hand_landmarks[0]
            for id, lm in enumerate(hand_landmarks.landmark):
                lm_list.append(lm)
        return lm_list

def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    game = SnakeGame()

    while True:
        success, image = cap.read()
        image = tracker.find_hands(image)

        # Get the positions of hand landmarks
        lm_list = tracker.find_position()

        if lm_list:
            # Calculate the average x and y positions of multiple fingers
            avg_x = sum(lm.x for lm in lm_list) / len(lm_list)
            avg_y = sum(lm.y for lm in lm_list) / len(lm_list)

            # Map average finger position to snake direction
            if avg_x < 0.35:
                game.go_left()
            elif avg_x > 0.65:
                game.go_right()
            elif avg_y < 0.35:
                game.go_down()  # If fingers point down, snake should go down to eat the meal
            else:
                game.go_up()

        game.move()
        cv2.imshow("Video", image)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
