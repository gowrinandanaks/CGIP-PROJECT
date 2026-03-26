import tkinter as tk
import random
import math
import time
import os

WIDTH = 900
HEIGHT = 600
MAX_TARGETS = 8

root = tk.Tk()
root.title("🎯 Ultimate Shooting Game")

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT)
canvas.pack()

# ================= VARIABLES =================
score = 0
lives = 3
level = 1
game_running = False
paused = False
targets = []
clouds = []
boss_active = False

# ================= HIGH SCORE =================
def load_highscore():
    if os.path.exists("highscore.txt"):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0
    return 0

def save_highscore(new_score):
    with open("highscore.txt", "w") as f:
        f.write(str(new_score))

best_score = load_highscore()

# ================= DDA LINE =================
def dda_line(x1, y1, x2, y2, color="black"):
    dx = x2 - x1
    dy = y2 - y1
    steps = int(max(abs(dx), abs(dy)))

    if steps == 0:
        canvas.create_line(x1, y1, x1+1, y1+1, fill=color)
        return

    x_inc = dx / steps
    y_inc = dy / steps

    x = x1
    y = y1

    for _ in range(steps):
        canvas.create_line(x, y, x+1, y+1, fill=color)
        x += x_inc
        y += y_inc

# ================= MIDPOINT CIRCLE =================
def midpoint_circle(cx, cy, r, color="black"):
    x = 0
    y = r
    p = 1 - r

    while x <= y:
        points = [
            (cx+x, cy+y),(cx-x, cy+y),
            (cx+x, cy-y),(cx-x, cy-y),
            (cx+y, cy+x),(cx-y, cy+x),
            (cx+y, cy-x),(cx-y, cy-x)
        ]
        for px, py in points:
            canvas.create_line(px, py, px+1, py+1, fill=color)

        x += 1
        if p < 0:
            p += 2*x + 1
        else:
            y -= 1
            p += 2*(x - y) + 1

# ================= TARGET =================
class Target:
    def __init__(self, boss=False):
        self.boss = boss
        self.r = 60 if boss else random.randint(20, 35)
        self.x = random.randint(100, WIDTH-100)
        self.y = random.randint(100, HEIGHT-200)
        self.speed = random.randint(2, 4) + level
        self.color = "purple" if boss else random.choice(["red","yellow","green","orange"])
        self.health = 8 if boss else 1

    def move(self):
        self.x += self.speed
        if self.x > WIDTH or self.x < 0:
            self.speed *= -1

    def draw(self):
        midpoint_circle(self.x, self.y, self.r, self.color)

# ================= CLOUD =================
class Cloud:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(50, 200)
        self.speed = random.uniform(0.5, 1.5)

    def move(self):
        self.x += self.speed
        if self.x > WIDTH:
            self.x = -50

    def draw(self):
        midpoint_circle(self.x, self.y, 20, "white")

# ================= SKY =================
def get_sky_color():
    t = time.time() % 20
    ratio = abs(t-10)/10
    r = int(135 + 120*ratio)
    g = int(206 - 150*ratio)
    b = int(235 - 200*ratio)
    return f'#{r:02x}{g:02x}{b:02x}'

# ================= GAME FUNCTIONS =================
def spawn_target():
    if len(targets) < MAX_TARGETS:
        targets.append(Target())

def shoot(event):
    global score, lives, boss_active
    if not game_running or paused:
        return

    hit = False
    for target in targets[:]:
        dist = math.sqrt((event.x-target.x)**2 + (event.y-target.y)**2)
        if dist <= target.r:
            hit = True
            target.health -= 1
            if target.health <= 0:
                score += 50 if target.boss else 10
                targets.remove(target)
                spawn_target()
            break

    if not hit:
        lives -= 1

def update_game():
    global best_score, level, boss_active, game_running

    if not game_running:
        return

    if paused:
        canvas.create_text(WIDTH//2, HEIGHT//2,
                           text="PAUSED",
                           font=("Arial",40,"bold"),
                           fill="blue")
        root.after(100, update_game)
        return

    canvas.delete("all")
    canvas.config(bg=get_sky_color())

    for cloud in clouds:
        cloud.move()
        cloud.draw()

    for target in targets:
        target.move()
        target.draw()

    canvas.create_text(80,30,text=f"Score:{score}",font=("Arial",14,"bold"))
    canvas.create_text(200,30,text=f"Best:{best_score}",font=("Arial",14,"bold"))
    canvas.create_text(320,30,text=f"Lives:{lives}",font=("Arial",14,"bold"))
    canvas.create_text(450,30,text=f"Level:{level}",font=("Arial",14,"bold"))

    if score > best_score:
        best_score = score
        save_highscore(best_score)

    if score >= 150 and not boss_active:
        targets.append(Target(boss=True))
        boss_active = True

    if score >= level * 200:
        level += 1

    if lives <= 0:
        game_over()
        return

    root.after(30, update_game)

def game_over():
    global game_running
    game_running = False
    canvas.create_text(WIDTH//2, HEIGHT//2,
                       text="GAME OVER",
                       font=("Arial",40,"bold"),
                       fill="red")
    root.after(2000, show_menu)

# ================= MENU SYSTEM =================
def show_menu():
    global game_running
    canvas.delete("all")
    game_running = False

    canvas.create_text(WIDTH//2,150,
                       text="🎯 Shooting Game",
                       font=("Arial",40,"bold"))

    tk.Button(root,text="Start Game",
              command=start_game,width=20,bg="lightgreen").place(x=350,y=250)

    tk.Button(root,text="Score Board",
              command=show_score,width=20,bg="lightblue").place(x=350,y=300)

    tk.Button(root,text="Exit",
              command=root.destroy,width=20,bg="red").place(x=350,y=350)

def show_score():
    canvas.delete("all")
    canvas.create_text(WIDTH//2,200,
                       text=f"🏆 High Score: {best_score}",
                       font=("Arial",30,"bold"))
    tk.Button(root,text="Back",
              command=show_menu,width=15).place(x=380,y=300)

def start_game():
    global score, lives, level, boss_active, game_running, targets, clouds

    for widget in root.place_slaves():
        widget.destroy()

    score = 0
    lives = 3
    level = 1
    boss_active = False
    targets.clear()
    clouds.clear()

    for _ in range(5):
        spawn_target()
    for _ in range(4):
        clouds.append(Cloud())

    game_running = True
    update_game()

# ================= PAUSE SYSTEM =================
def toggle_pause(event):
    global paused
    if game_running:
        paused = not paused

root.bind("<p>", toggle_pause)
canvas.bind("<Button-1>", shoot)

# ================= START =================
show_menu()

root.mainloop()
