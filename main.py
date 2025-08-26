# -*- coding: utf-8 -*-
"""
完整 Pygame 密室逃脫 - 雙房間範例
"""

import pygame
import sys
from dataclasses import dataclass, field

# ----------------------
# 初始化
# ----------------------
pygame.init()
WIDTH, HEIGHT = 960, 540
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("密室逃脫 - 雙房間範例")
clock = pygame.time.Clock()

# 顏色與字型
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 140, 220)
YELLOW = (240, 200, 60)
BROWN = (120, 90, 60)
LIGHT_PURPLE = (132, 112, 255)
GRAY = (80, 80, 80)
LIGHT_GRAY = (150, 150, 150)
FONT = pygame.font.SysFont("Microsoft JhengHei", 22)
SMALL = pygame.font.SysFont("Microsoft JhengHei", 18)
BIG = pygame.font.SysFont("Microsoft JhengHei", 42)

# ----------------------
# 工具函式
# ----------------------
def draw_text(surf, text, pos, color=WHITE, font=FONT, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surf.blit(img, rect)

# ----------------------
# 物品與物件
# ----------------------
@dataclass
class Item:
    name: str
    desc: str = ""
    icon_color: tuple = (230, 230, 230)

@dataclass
class GameObject:
    name: str
    rect: pygame.Rect
    color: tuple
    hover_color: tuple
    visible: bool = True
    locked: bool = False
    code: str = ""
    contains: list[Item] = field(default_factory=list)
    image: pygame.Surface | None = None

    def draw(self, surf, hover=False):
        if not self.visible:
            return
        if self.image:
            surf.blit(self.image, self.rect.topleft)
        else:
            c = self.hover_color if hover else self.color
            pygame.draw.rect(surf, c, self.rect, border_radius=8)
            pygame.draw.rect(surf, BLACK, self.rect, 2, border_radius=8)
            draw_text(surf, self.name, (self.rect.x + 8, self.rect.y + 6), BLACK, SMALL)

    def on_click(self, game):
        if not self.visible:
            return ""
        if self.name == "門":
            if self.locked:
                if game.held_item and game.held_item.name == "鑰匙":
                    self.locked = False
                    return "你使用了鑰匙，門已解鎖！"
                return "門被鎖住了，好像需要鑰匙。"
            else:
                if game.room == 1:
                    game.enter_room2()
                    return "你打開門進入了下一間房間！"
                else:
                    game.win = True
                    return "你推開了門，成功逃出第二間房間！"
        if self.name == "抽屜":
            if self.locked:
                game.open_code_panel(self)
                return "抽屜有三位數密碼鎖。"
            else:
                if self.contains:
                    item = self.contains.pop(0)
                    game.add_to_inventory(item)
                    return f"你從抽屜拿到『{item.name}』。"
                return "抽屜是空的。"
        if self.name == "便條紙":
            if self.visible:
                game.add_to_inventory(Item("便條紙", "上面寫著 3-1-4。", icon_color=YELLOW))
                self.visible = False
                return "你撿起了便條紙。"
        if self.name == "書櫃":
            return "一排舊書。其中一本書的書背特別厚…"
        if self.name == "盒子":
            if self.locked:
                if game.held_item and game.held_item.name == "鑰匙":
                    self.locked = False
                    return "盒子打開了，裡面有一把斧頭！"
                return "盒子鎖住了，裡面似乎有東西。"
            else:
                if self.contains:
                    item = self.contains.pop(0)
                    game.add_to_inventory(item)
                    return f"你從盒子拿到『{item.name}』。"
                return "盒子是空的。"
        return ""

# ----------------------
# 物品欄 UI
# ----------------------
class Inventory:
    def __init__(self, capacity=6):
        self.capacity = capacity
        self.items: list[Item] = []
        self.slot_rects = []
        margin = 12
        slot_w = 88
        x = (WIDTH - (slot_w + margin) * capacity + margin) // 2
        y = HEIGHT - 100
        for i in range(capacity):
            r = pygame.Rect(x + i * (slot_w + margin), y, slot_w, 80)
            self.slot_rects.append(r)

    def draw(self, surf, held_item: Item | None):
        pygame.draw.rect(surf, (30,30,35), (0, HEIGHT-120, WIDTH, 120))
        pygame.draw.line(surf, (50,50,60), (0, HEIGHT-120), (WIDTH, HEIGHT-120), 2)
        draw_text(surf, "物品欄", (20, HEIGHT-116), LIGHT_GRAY)
        for i, r in enumerate(self.slot_rects):
            pygame.draw.rect(surf, (55,55,65), r, border_radius=10)
            pygame.draw.rect(surf, (10,10,10), r, 2, border_radius=10)
            if i < len(self.items):
                item = self.items[i]
                pygame.draw.rect(surf, item.icon_color, r.inflate(-20,-24), border_radius=8)
                draw_text(surf, item.name, (r.x+6, r.bottom-24), BLACK, SMALL)
        if held_item:
            draw_text(surf, f"手上物件：{held_item.name}", (20, HEIGHT-86), WHITE)

    def handle_click(self, pos) -> Item | None:
        for i, r in enumerate(self.slot_rects):
            if r.collidepoint(pos) and i < len(self.items):
                return self.items[i]
        return None

    def add(self, item: Item) -> bool:
        if len(self.items) >= self.capacity:
            return False
        self.items.append(item)
        return True

# ----------------------
# 密碼輸入面板
# ----------------------
class CodePanel:
    def __init__(self, target: GameObject, length=3):
        self.target = target
        self.length = length
        self.buffer = ""
        self.active = True

    def draw(self, surf):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,150))
        surf.blit(overlay, (0,0))
        win = pygame.Rect(0,0,420,240)
        win.center = (WIDTH//2, HEIGHT//2)
        pygame.draw.rect(surf, (240,240,240), win, border_radius=16)
        pygame.draw.rect(surf, BLACK, win, 3, border_radius=16)
        draw_text(surf, "輸入三位數密碼", (win.centerx, win.y+20), BLACK, BIG, center=True)
        draw_text(surf, "提示：看看房間裡有沒有線索…", (win.centerx, win.y+70), BLACK, SMALL, center=True)
        box = pygame.Rect(0,0,240,60)
        box.center = (win.centerx, win.centery+10)
        pygame.draw.rect(surf, WHITE, box, border_radius=10)
        pygame.draw.rect(surf, BLACK, box, 2, border_radius=10)
        s = self.buffer + "_"*(self.length - len(self.buffer))
        draw_text(surf, s, (box.centerx, box.centery-16), BLACK, BIG, center=True)
        draw_text(surf, "Enter 確認, Backspace 刪除, Esc 取消", (win.centerx, win.bottom-34), BLACK, SMALL, center=True)

    def handle_key(self, game, key):
        if key == pygame.K_ESCAPE:
            game.close_code_panel()
            return
        if key == pygame.K_BACKSPACE:
            self.buffer = self.buffer[:-1]
            return
        if key == pygame.K_RETURN:
            self.submit(game)
            return
        if pygame.K_0 <= key <= pygame.K_9 and len(self.buffer)<self.length:
            self.buffer += chr(key)
        if pygame.K_KP0 <= key <= pygame.K_KP9 and len(self.buffer)<self.length:
            self.buffer += str(key - pygame.K_KP0)

    def submit(self, game):
        if self.buffer == self.target.code:
            self.target.locked = False
            game.message = "密碼正確！抽屜解鎖了。"
        else:
            game.message = "密碼錯誤。"
        game.close_code_panel()

# ----------------------
# 主遊戲
# ----------------------
class Game:
    def __init__(self):
        self.inventory = Inventory(capacity=7)
        self.objects: list[GameObject] = []
        self.message = "醒來時，你身處陌生的房間。試著找線索逃出去。"
        self.held_item: Item | None = None
        self.code_panel: CodePanel | None = None
        self.win = False
        self.room = 1
        self.setup_room1()

    # 第一房間
    def setup_room1(self):
        door_img = pygame.Surface((120,240))
        door_img.fill(BLUE)
        door = GameObject("門", door_img.get_rect(topleft=(WIDTH-160,120)), BLUE, (90,170,250), locked=True, image=door_img)
        drawer_img = pygame.Surface((160,100))
        drawer_img.fill(BROWN)
        drawer = GameObject("抽屜", drawer_img.get_rect(topleft=(180,300)), BROWN, (150,120,90), locked=True, code="314", image=drawer_img)
        drawer.contains.append(Item("鑰匙", "可以打開門的鑰匙", icon_color=YELLOW))
        bookshelf_img = pygame.Surface((220,160))
        bookshelf_img.fill((110,80,50))
        bookshelf = GameObject("書櫃", bookshelf_img.get_rect(topleft=(80,120)), (110,80,50), (140,100,70), image=bookshelf_img)
        note_img = pygame.Surface((80,40))
        note_img.fill(YELLOW)
        note = GameObject("便條紙", note_img.get_rect(topleft=(360,180)), YELLOW, (255,230,90), image=note_img)
        self.objects = [door, drawer, bookshelf, note]

    # 第二房間範例
    def setup_room2(self):
        self.room = 2
        # 門（通往勝利）
        door_img = pygame.Surface((120,240))
        door_img.fill(BLUE)
        door = GameObject("門", door_img.get_rect(topleft=(WIDTH-160,120)), BLUE, (90,170,250), locked=False, image=door_img)
        # 盒子（含斧頭）
        box_img = pygame.Surface((160,100))
        box_img.fill(LIGHT_PURPLE)
        box = GameObject("盒子", box_img.get_rect(topleft=(300,300)), LIGHT_PURPLE, (123,104,238), locked=True, image=box_img)
        box.contains.append(Item("斧頭", "可以打破障礙物", icon_color=LIGHT_PURPLE))
        self.objects = [door, box]
        self.message = "你進入了第二間房間，似乎還有物品可以探索。"

    def enter_room2(self):
        self.setup_room2()
        self.held_item = None
        self.code_panel = None

    # 物品欄操作
    def add_to_inventory(self, item: Item):
        if self.inventory.add(item):
            self.message = f"獲得物品：{item.name}"
        else:
            self.message = "物品欄已滿。"

    # CodePanel
    def open_code_panel(self, target: GameObject):
        self.code_panel = CodePanel(target, length=3)

    def close_code_panel(self):
        self.code_panel = None

    # 手上物件使用
    def use_item_on(self, item: Item, obj: GameObject) -> str:
        if item.name == "鑰匙" and obj.name == "門":
            if obj.locked:
                obj.locked = False
                return "你用鑰匙把門解鎖了。"
            return "門已經是開鎖狀態。"
        if item.name == "便條紙":
            return "便條紙上寫著 3-1-4，也許是密碼。"
        if item.name == "斧頭" and obj.name == "門":
            obj.locked = False
            return "你用斧頭砍開了門！"
        return "這個物品不能用在這裡。"

    # 畫面
    def draw(self, surf):
        surf.fill((35,38,48))
        pygame.draw.rect(surf, (60,65,80), (0,0,WIDTH, HEIGHT-120))
        mx,my = pygame.mouse.get_pos()
        for obj in self.objects:
            hover = obj.rect.collidepoint((mx,my))
            obj.draw(surf, hover=hover)
        pygame.draw.rect(surf, (25,26,34), (0, HEIGHT-160, WIDTH,40))
        pygame.draw.line(surf, (55,58,70), (0, HEIGHT-160), (WIDTH, HEIGHT-160), 2)
        draw_text(surf, self.message, (16, HEIGHT-148), WHITE)
        self.inventory.draw(surf, self.held_item)
        if self.code_panel:
            self.code_panel.draw(surf)
        if self.win:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            surf.blit(overlay, (0,0))
            draw_text(surf, "你逃出了房間！", (WIDTH//2, HEIGHT//2-20), WHITE, BIG, center=True)
            draw_text(surf, "恭喜通關！按 ESC 結束", (WIDTH//2, HEIGHT//2+30), WHITE, FONT, center=True)

    # 滑鼠操作
    def handle_mouse_down(self, pos):
        if self.code_panel:
            return
        item = self.inventory.handle_click(pos)
        if item:
            self.held_item = item
            self.message = f"手上物件：{item.name}"
            return
        for obj in self.objects:
            if obj.visible and obj.rect.collidepoint(pos):
                if self.held_item:
                    self.message = self.use_item_on(self.held_item, obj)
                else:
                    self.message = obj.on_click(self)
                return
        if self.held_item:
            self.message = "收起了手上物件。"
        self.held_item = None

    def handle_key_down(self, key):
        if self.code_panel:
            self.code_panel.handle_key(self, key)
            return
        if key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
    def update(self):
        pass

class Game2:
    def __init__(self):
        self.inventory = Inventory(capacity=7)
        self.objects: list[GameObject] = []
        self.message = "好不容易逃出來了，怎麼還有....."
        self.held_item: Item | None = None
        self.code_panel: CodePanel | None = None
        self.win = False
        self.setup_room()

    def setup_room(self):
        door1_img = pygame.surface((240, 120))
        door1_img.fill(BLUE)
        door = GameObject("門", door1_img.get_rect(top = (HEIGHT + 50, 240)), BLUE, (90, 170, 250), locked = True, image = door1_img)
        box_img = pygame.Surface((160, 100))
        box_img.fill(LIGHT_PURPLE)
        box = GameObject("盒子", box_img.get_rect(topleft = (300, 300)), LIGHT_PURPLE, (123, 104, 238), locked = True, image = box_img)


# ----------------------
# 主迴圈
# ----------------------
def main():
    game = Game()
    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.handle_mouse_down(event.pos)
            elif event.type == pygame.KEYDOWN:
                game.handle_key_down(event.key)
        game.update()
        game.draw(screen)
        pygame.display.flip()

if __name__ == "__main__":
    main()
