import tkinter as tk
import random
import math

WIDTH, HEIGHT = 1000, 700
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 100
BALL_SIZE = 20
PADDLE_SPEED = 20
BALL_SPEED = 8
WINNING_SCORE = 5

BG_COLOR = "#0f0f23"
PADDLE_COLOR = "#64c8ff"
BALL_COLOR = "#ff6496"
TEXT_COLOR = "#c8c8ff"
GLOW_COLOR = "#9696ff"
LINE_COLOR = "#282850"

class Particle:
    def __init__(self, canvas, x, y, color):
        self.canvas = canvas
        self.x = x
        self.y = y
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.life = 20
        self.size = 5
        self.id = canvas.create_oval(x, y, x + self.size, y + self.size, fill=color, outline="")
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3
        self.life -= 1
        
        if self.life > 0:
            size = int(self.size * (self.life / 20))
            self.canvas.coords(self.id, self.x, self.y, self.x + size, self.y + size)
            return True
        else:
            self.canvas.delete(self.id)
            return False

class Paddle:
    def __init__(self, canvas, x, y, color):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.color = color
        self.id = canvas.create_rectangle(x, y, x + PADDLE_WIDTH, y + PADDLE_HEIGHT, 
                                         fill=color, outline="white", width=2)
        self.glow_id = None
        
    def move(self, dy):
        self.y = max(0, min(HEIGHT - PADDLE_HEIGHT, self.y + dy))
        self.canvas.coords(self.id, self.x, self.y, 
                          self.x + PADDLE_WIDTH, self.y + PADDLE_HEIGHT)
        
    def show_glow(self):
        if self.glow_id:
            self.canvas.delete(self.glow_id)
        self.glow_id = self.canvas.create_rectangle(
            self.x - 3, self.y - 3,
            self.x + PADDLE_WIDTH + 3, self.y + PADDLE_HEIGHT + 3,
            outline=GLOW_COLOR, width=3
        )
        self.canvas.after(100, self.hide_glow)
        
    def hide_glow(self):
        if self.glow_id:
            self.canvas.delete(self.glow_id)
            self.glow_id = None

class Ball:
    def __init__(self, canvas):
        self.canvas = canvas
        self.reset()
        self.id = canvas.create_oval(0, 0, BALL_SIZE, BALL_SIZE, 
                                     fill=BALL_COLOR, outline="white", width=2)
        
    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        angle = random.uniform(-math.pi/4, math.pi/4)
        if random.random() > 0.5:
            angle += math.pi
        self.vx = math.cos(angle) * BALL_SPEED
        self.vy = math.sin(angle) * BALL_SPEED
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        if self.y <= 0 or self.y >= HEIGHT - BALL_SIZE:
            self.vy *= -1
            self.y = max(0, min(HEIGHT - BALL_SIZE, self.y))
        
        self.canvas.coords(self.id, self.x, self.y, 
                          self.x + BALL_SIZE, self.y + BALL_SIZE)

class PingPongGame:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ Neon Ping Pong ✨")
        self.root.configure(bg=BG_COLOR)
        
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, 
                               bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack()
        
        self.draw_background()
        
        self.paddle_left = Paddle(self.canvas, 30, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_COLOR)
        self.paddle_right = Paddle(self.canvas, WIDTH - 30 - PADDLE_WIDTH, 
                                   HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_COLOR)
        self.ball = Ball(self.canvas)
        
        self.score_left = 0
        self.score_right = 0
        self.particles = []
        
        self.score_left_text = self.canvas.create_text(WIDTH // 4, 50, 
                                                       text="0", fill=TEXT_COLOR, 
                                                       font=("Arial", 48, "bold"))
        self.score_right_text = self.canvas.create_text(3 * WIDTH // 4, 50, 
                                                        text="0", fill=TEXT_COLOR, 
                                                        font=("Arial", 48, "bold"))
        
        self.menu_frame = tk.Frame(self.canvas, bg=BG_COLOR)
        self.menu_title = tk.Label(self.menu_frame, text="NEON PING PONG", 
                                   fg=TEXT_COLOR, bg=BG_COLOR, 
                                   font=("Arial", 48, "bold"))
        self.menu_title.pack(pady=50)
        
        self.menu_text = tk.Label(self.menu_frame, 
                                 text="Player 1: W / S\nPlayer 2: ↑ / ↓\n\nPress SPACE to start", 
                                 fg=TEXT_COLOR, bg=BG_COLOR, 
                                 font=("Arial", 20))
        self.menu_text.pack()
        
        self.menu_window = self.canvas.create_window(WIDTH // 2, HEIGHT // 2, 
                                                     window=self.menu_frame)
        
        self.game_over_frame = None
        self.game_over_window = None
        
        self.game_state = "menu"
        self.keys_pressed = set()
        
        self.root.bind("<KeyPress>", self.key_press)
        self.root.bind("<KeyRelease>", self.key_release)
        
        self.game_loop()
        
    def draw_background(self):
        for i in range(0, HEIGHT, 30):
            self.canvas.create_rectangle(WIDTH // 2 - 3, i, WIDTH // 2 + 3, i + 20, 
                                        fill=LINE_COLOR, outline="")
    
    def key_press(self, event):
        self.keys_pressed.add(event.keysym)
        
        if event.keysym == "space":
            if self.game_state == "menu":
                self.game_state = "playing"
                self.canvas.itemconfig(self.menu_window, state="hidden")
            elif self.game_state == "game_over":
                self.reset_game()
    
    def key_release(self, event):
        if event.keysym in self.keys_pressed:
            self.keys_pressed.remove(event.keysym)
    
    def create_particles(self, x, y):
        colors = ["#ff96c8", "#96c8ff", "#c896ff"]
        for _ in range(10):
            color = random.choice(colors)
            self.particles.append(Particle(self.canvas, x, y, color))
    
    def handle_collision(self):
        ball_left = self.ball.x
        ball_right = self.ball.x + BALL_SIZE
        ball_top = self.ball.y
        ball_bottom = self.ball.y + BALL_SIZE
        ball_center_y = self.ball.y + BALL_SIZE // 2
        
        if (ball_left <= self.paddle_left.x + PADDLE_WIDTH and
            ball_right >= self.paddle_left.x and
            ball_center_y >= self.paddle_left.y and
            ball_center_y <= self.paddle_left.y + PADDLE_HEIGHT and
            self.ball.vx < 0):
            
            self.ball.vx *= -1.1
            self.ball.x = self.paddle_left.x + PADDLE_WIDTH
            
            hit_pos = (ball_center_y - self.paddle_left.y) / PADDLE_HEIGHT
            self.ball.vy = (hit_pos - 0.5) * 15
            
            self.paddle_left.show_glow()
            self.create_particles(self.ball.x + BALL_SIZE // 2, self.ball.y + BALL_SIZE // 2)
        
        if (ball_right >= self.paddle_right.x and
            ball_left <= self.paddle_right.x + PADDLE_WIDTH and
            ball_center_y >= self.paddle_right.y and
            ball_center_y <= self.paddle_right.y + PADDLE_HEIGHT and
            self.ball.vx > 0):
            
            self.ball.vx *= -1.1
            self.ball.x = self.paddle_right.x - BALL_SIZE
            
            hit_pos = (ball_center_y - self.paddle_right.y) / PADDLE_HEIGHT
            self.ball.vy = (hit_pos - 0.5) * 15
            
            self.paddle_right.show_glow()
            self.create_particles(self.ball.x + BALL_SIZE // 2, self.ball.y + BALL_SIZE // 2)
    
    def check_score(self):
        if self.ball.x < 0:
            self.score_right += 1
            self.canvas.itemconfig(self.score_right_text, text=str(self.score_right))
            self.ball.reset()
            self.create_particles(WIDTH // 2, HEIGHT // 2)
            
        if self.ball.x > WIDTH:
            self.score_left += 1
            self.canvas.itemconfig(self.score_left_text, text=str(self.score_left))
            self.ball.reset()
            self.create_particles(WIDTH // 2, HEIGHT // 2)
        
        if self.score_left >= WINNING_SCORE or self.score_right >= WINNING_SCORE:
            self.game_state = "game_over"
            self.show_game_over()
    
    def show_game_over(self):
        winner = "Player 1" if self.score_left >= WINNING_SCORE else "Player 2"
        winner_color = PADDLE_COLOR if self.score_left >= WINNING_SCORE else BALL_COLOR
        
        self.game_over_frame = tk.Frame(self.canvas, bg=BG_COLOR)
        
        winner_label = tk.Label(self.game_over_frame, text=f"{winner} wins!", 
                               fg=winner_color, bg=BG_COLOR, 
                               font=("Arial", 48, "bold"))
        winner_label.pack(pady=30)
        
        restart_label = tk.Label(self.game_over_frame, 
                                text="Press SPACE for new game", 
                                fg=TEXT_COLOR, bg=BG_COLOR, 
                                font=("Arial", 24))
        restart_label.pack()
        
        self.game_over_window = self.canvas.create_window(WIDTH // 2, HEIGHT // 2, 
                                                          window=self.game_over_frame)
    
    def reset_game(self):
        self.score_left = 0
        self.score_right = 0
        self.canvas.itemconfig(self.score_left_text, text="0")
        self.canvas.itemconfig(self.score_right_text, text="0")
        self.ball.reset()
        self.paddle_left.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.paddle_right.y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.particles = []
        self.game_state = "playing"
        
        if self.game_over_window:
            self.canvas.delete(self.game_over_window)
            self.game_over_frame.destroy()
            self.game_over_window = None
            self.game_over_frame = None
    
    def game_loop(self):
        if self.game_state == "playing":
            if "w" in self.keys_pressed:
                self.paddle_left.move(-PADDLE_SPEED)
            if "s" in self.keys_pressed:
                self.paddle_left.move(PADDLE_SPEED)
            if "Up" in self.keys_pressed:
                self.paddle_right.move(-PADDLE_SPEED)
            if "Down" in self.keys_pressed:
                self.paddle_right.move(PADDLE_SPEED)
            
            self.ball.update()
            self.handle_collision()
            self.check_score()
            
            self.particles = [p for p in self.particles if p.update()]
        
        self.root.after(16, self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    game = PingPongGame(root)
    root.mainloop()
