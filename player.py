import pygame, math


class Player:
    def __init__(self, x, y):
        #載入圖片
        super().__init__()
        self.stand_image = pygame.image.load("assets/person1.png").convert_alpha()
        self.stand_image.set_colorkey((35, 38, 47))
        walk_images = [
            pygame.image.load("assets/person2.png").convert_alpha(),
            pygame.image.load("assets/person3.png").convert_alpha(),
            pygame.image.load("assets/person4.png").convert_alpha()
        ]
        walk_right_images = [
            pygame.image.load("assets/person6.png").convert_alpha(),
            pygame.image.load("assets/person5.png").convert_alpha(),
            pygame.image.load("assets/person8.png").convert_alpha()
        ]
        walk_up_images = [
            pygame.image.load("assets/person10.png").convert_alpha(),
            pygame.image.load("assets/person9.png").convert_alpha(),
            pygame.image.load("assets/person12.png").convert_alpha()
        ]

        walk_left_images = [
            pygame.image.load("assets/person14.png").convert_alpha(),
            pygame.image.load("assets/person13.png").convert_alpha(),
            pygame.image.load("assets/person16.png").convert_alpha()
        ]
        self.stand_image = pygame.transform.scale(self.stand_image, (30, 60))
        self.walk_images = [pygame.transform.scale(img, (30, 60)) for img in walk_images]
        self.walk_right_images = [pygame.transform.scale(img, (30, 60)) for img in walk_right_images]
        self.walk_up_images = [pygame.transform.scale(img, (30, 60)) for img in walk_up_images]
        self.walk_left_images = [pygame.transform.scale(img, (30, 60)) for img in walk_left_images]

        #初始位置
        self.x = x
        self.y = y
        self.speed = 2
        
        #滑鼠點擊的位置
        self.target = None
        
        #動畫控制
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.15
        self.direction = "right"

    def update(self):
        if self.target:
            dx = self.target[0] - self.x
            dy = self.target[1] - self.y
            dist = math.hypot(dx, dy)

            if dist > self.speed:
                self.x += self.speed * dx / dist
                self.y += self.speed * dy / dist

                #判斷方向
                if abs(dx) > abs(dy):
                    self.direction = "right" if dx > 0 else "left"
                else:
                    self.direction = "down" if dy > 0 else "up"

                self.animation_timer += self.animation_speed
                if self.animation_timer >= 1:
                    self.animation_timer = 0
                    self.current_frame = (self.current_frame + 1) % 3
            else:
                self.x, self.y = self.target
                self.target = None
                self.current_frame = 0
                self.animation_timer = 0
    
    def draw(self,screen):
        if self.target:
            if self.direction == "down":
                img = self.walk_images[self.current_frame]
            elif self.direction == "right":
                img = self.walk_right_images[self.current_frame]
            elif self.direction == "up":
                img = self.walk_up_images[self.current_frame]
            elif self.direction == "left":
                img = self.walk_left_images[self.current_frame]
        else:
            if self.direction == "down":
                img = self.stand_image
            elif self.direction == "up":
                img = self.walk_up_images[1]
            elif self.direction == "left":
                img = self.walk_left_images[1]
            else:
                img = self.walk_right_images[1]

        rect = img.get_rect(center = (self.x, self.y))
        screen.blit(img, rect)

    def set_target(self, pos):
        self.target = pos
