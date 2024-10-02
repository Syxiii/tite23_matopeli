import sys
import random
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene
from PySide6.QtGui import QPainter, QPen, QBrush, QFont
from PySide6.QtCore import Qt, QTimer

# vakiot
CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 15

class SnakeGame(QGraphicsView):
    def __init__(self):
        super().__init__()

        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setSceneRect(0, 0, CELL_SIZE * GRID_WIDTH, CELL_SIZE * GRID_HEIGHT)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.game_started = False
        self.init_screen()

    def init_screen(self):
        self.scene().clear()
        start_text = self.scene().addText("Valitse vaikeustaso:\n1. Helppo\n2. Keskivaikea\n3. Vaikea", QFont("Arial", 18))
        text_width = start_text.boundingRect().width()
        text_x = (self.width() - text_width) / 2
        start_text.setPos(text_x, GRID_HEIGHT * CELL_SIZE / 2)

    def draw_board_limits(self):
        pen = QPen(Qt.black)
        self.scene().addRect(0, 0, CELL_SIZE * GRID_WIDTH, CELL_SIZE * GRID_HEIGHT, pen)

    def keyPressEvent(self, event):
        key = event.key()

        if not self.game_started:
            if key == Qt.Key_1:
                self.difficulty = 'helppo'
                self.game_speed = 300
            elif key == Qt.Key_2:
                self.difficulty = 'keskivaikea'
                self.game_speed = 200
            elif key == Qt.Key_3:
                self.difficulty = 'vaikea'
                self.game_speed = 100
            else:
                # Ohitetaan muut näppäimet
                return

            self.scene().clear()  # Tyhjennetään näyttö
            self.start_game()
            self.game_started = True
            self.game_over_flag = False  # Nollataan peli

        elif self.game_over_flag:  # Uuden pelin aloitus Game Over -tilanteessa
            if key in (Qt.Key_1, Qt.Key_2, Qt.Key_3):
                # Käsitellään vaikeustason valinta
                if key == Qt.Key_1:
                    self.difficulty = 'helppo'
                    self.game_speed = 300
                elif key == Qt.Key_2:
                    self.difficulty = 'keskivaikea'
                    self.game_speed = 200
                elif key == Qt.Key_3:
                    self.difficulty = 'vaikea'
                    self.game_speed = 100

                self.scene().clear()
                self.start_game()
                self.game_over_flag = False
                self.game_started = True
            else:
                # Ei tehdä mitään muilla näppäimillä
                pass

        elif key in (Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down):
            # päivitetään suunta vain jos se ei ole vastakkainen valitulle suunnalle
            if key == Qt.Key_Left and self.direction != Qt.Key_Right:
                self.direction = key
            elif key == Qt.Key_Right and self.direction != Qt.Key_Left:
                self.direction = key
            elif key == Qt.Key_Up and self.direction != Qt.Key_Down:
                self.direction = key
            elif key == Qt.Key_Down and self.direction != Qt.Key_Up:
                self.direction = key

    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                return x, y

    def update_game(self):
        head_x, head_y = self.snake[0]

        if self.direction == Qt.Key_Left:
            new_head = (head_x - 1, head_y)
        elif self.direction == Qt.Key_Right:
            new_head = (head_x + 1, head_y)
        elif self.direction == Qt.Key_Up:
            new_head = (head_x, head_y - 1)
        elif self.direction == Qt.Key_Down:
            new_head = (head_x, head_y + 1)

        # Tarkista, törmääkö mato itseensä tai pelialueen rajaan
        if (new_head in self.snake or
            new_head[0] < 0 or new_head[0] >= GRID_WIDTH or
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            self.game_over()
            return

        # Jos mato söi ruokaa, pidennä matoa
        if new_head == self.food:
            self.snake.insert(0, new_head)
            self.food = self.spawn_food()
            self.score += 1  # Kasvata pistemäärää
        else:
            # Jos ei syönyt ruokaa, liikuta matoa eteenpäin
            self.snake.insert(0, new_head)
            self.snake.pop()

        self.print_game()

    def print_game(self):
        self.scene().clear()
        self.draw_board_limits()  # Piirretään rajat uudelleen
        for segment in self.snake:
            x, y = segment
            self.scene().addRect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE, QPen(Qt.black), QBrush(Qt.black))

        self.scene().addText(f"Pisteet: {self.score}", QFont("Arial", 12))
        fx, fy = self.food
        self.scene().addRect(fx * CELL_SIZE, fy * CELL_SIZE, CELL_SIZE, CELL_SIZE, QPen(Qt.black), QBrush(Qt.red))

    def place_food(self):
        # Aseta ruoka satunnaiseen paikkaan
        self.food = self.spawn_food()
        food_x, food_y = self.food
        self.scene().addRect(food_x * CELL_SIZE, food_y * CELL_SIZE, CELL_SIZE, CELL_SIZE, QPen(Qt.red), QBrush(Qt.red))

    def start_game(self):
        self.direction = Qt.Key_Right

        # Luo satunnainen aloituspaikka madolle, varmistaen että mato mahtuu pelikentälle
        start_x = random.randint(3, GRID_WIDTH - 4)  # Jotta mato ei ylitä rajoja
        start_y = random.randint(3, GRID_HEIGHT - 4)

        # Alusta mato kolmen segmentin pituiseksi
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]

        self.score = 0  # Alusta pistelasku
        self.place_food()  # Aseta ruoka pelikentälle
        self.timer.start(self.game_speed)

    def game_over(self):
        # Näytä "Game Over" -teksti pelin päätyttyä
        game_over_text = self.scene().addText("Peli ohi\nPaina 1, 2 tai 3 aloittaaksesi uuden pelin", QFont("Arial", 18))
        text_width = game_over_text.boundingRect().width()
        text_x = (self.width() - text_width) / 2
        game_over_text.setPos(text_x, GRID_HEIGHT * CELL_SIZE / 2)
        self.timer.stop()
        self.game_over_flag = True  # Asetetaan peli päättyneeksi
        self.game_started = False  # Nollataan peli aloitettavaksi uudelleen

def main():
    app = QApplication(sys.argv)
    game = SnakeGame()
    game.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
