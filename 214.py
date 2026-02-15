import pygame
import math
import random
import colorsys  # 引入色彩空间转换，用来做高能发光特效

pygame.init()
WIDTH, HEIGHT = 1000, 750
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("终极星海能量爱心 - 大爆炸交互版")
clock = pygame.time.Clock()

def heart_math(t):
    """基础爱心参数方程"""
    x = 16 * math.sin(t) ** 3
    y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
    return x, y

class Particle:
    def __init__(self):
        t = random.uniform(0, 2 * math.pi)
        hx, hy = heart_math(t)
        
        # 让粒子向心聚集，边缘略微散开
        distance = random.uniform(0, 1) ** 0.6 
        
        self.base_x = hx * 16 * distance
        self.base_y = hy * 16 * distance
        
        # 初始依然在全屏随机，制造开场聚拢效果
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        
        self.vx = 0
        self.vy = 0
        self.base_size = random.uniform(1.2, 3.5)
        
        # 基础色相：0.9~1.0 大致是 骚粉 到 正红
        self.hue = random.uniform(0.9, 1.05) 
        if self.hue > 1.0: 
            self.hue -= 1.0
            
    def update(self, scale, mouse_x, mouse_y, click_explode):
        tx = WIDTH // 2 + self.base_x * scale
        ty = HEIGHT // 2 + self.base_y * scale
        
        # 1. 鼠标悬浮排斥力
        dx = self.x - mouse_x
        dy = self.y - mouse_y
        dist = math.hypot(dx, dy)
        if 0 < dist < 150:
            force = (150 - dist) / 150
            tx += (dx / dist) * force * 280
            ty += (dy / dist) * force * 280
            
        # 2. 🌟 终极大招：鼠标点击，瞬间核爆！
        if click_explode:
            angle = random.uniform(0, 2 * math.pi)
            burst_speed = random.uniform(30, 120)  # 爆炸初速度极大
            self.vx += math.cos(angle) * burst_speed
            self.vy += math.sin(angle) * burst_speed
        
        # 3. 物理弹簧引力：无论怎么被拉扯炸开，最终都要回到爱心位置
        ax = (tx - self.x) * 0.05 
        ay = (ty - self.y) * 0.05
        
        # 减少摩擦力 (0.85)，让粒子运动更加飘逸、有流体感
        self.vx = (self.vx + ax) * 0.85 
        self.vy = (self.vy + ay) * 0.85
        
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface, beat):
        speed = math.hypot(self.vx, self.vy)
        
        # 🌈 核心高能光效：速度越快，亮度越高，色彩越接近纯白
        lightness = min(1.0, 0.5 + speed * 0.015)
        saturation = max(0.0, 1.0 - speed * 0.015)
        
        # 将 HLS 转化为 RGB
        r, g, b = colorsys.hls_to_rgb(self.hue, lightness, saturation)
        color = (int(r * 255), int(g * 255), int(b * 255))
        
        # 粒子大小也会随着速度和心跳扩张
        current_size = self.base_size + beat * 2.5 + speed * 0.05
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), max(1, int(current_size)))

# 粒子数量拉满到 5000 个！
particles = [Particle() for _ in range(5000)]

fade_surface = pygame.Surface((WIDTH, HEIGHT))
fade_surface.fill((0, 0, 0))
fade_surface.set_alpha(45) # 数值调低至 45，光影拖尾时间更长，极度沉浸

running = True
start_time = pygame.time.get_ticks()

while running:
    click_explode = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
        # 监听鼠标点击事件，触发核爆开关
        if event.type == pygame.MOUSEBUTTONDOWN:
            click_explode = True

    # 绘制半透明黑色蒙版，制造尾迹
    screen.blit(fade_surface, (0, 0))
    mx, my = pygame.mouse.get_pos()

    t = (pygame.time.get_ticks() - start_time) / 1000.0
    beat = math.fabs(math.sin(t * 3.5)) ** 6 
    scale = 1 + beat * 0.15

    # 更新并绘制所有粒子
    for p in particles:
        p.update(scale, mx, my, click_explode)
        p.draw(screen, beat)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()