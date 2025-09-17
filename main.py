import pygame
import sys
from player import Player
from dataclasses import dataclass, field

# 初始化
pygame.init()
WIDTH, HEIGHT = 960, 540
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("密室逃脫")
clock = pygame.time.Clock()
player = Player(600, 350, True)
# 顏色與字型
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 140, 220)
YELLOW = (240, 200, 60)
BROWN = (120, 90, 60)
LIGHT_PURPLE = (132, 112, 255)
RED = (255, 0, 0)
GRAY = (80, 80, 80)
LIGHT_GRAY = (150, 150, 150)
FONT = pygame.font.SysFont("Microsoft JhengHei", 22)
SMALL = pygame.font.SysFont("Microsoft JhengHei", 18)
BIG = pygame.font.SysFont("Microsoft JhengHei", 42)

# 工具函式
def draw_text(surf, text, pos, color=WHITE, font=FONT, center=False):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surf.blit(img, rect)

# 物品
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
    border_radius = 10
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
            pygame.draw.rect(surf, c, self.rect, border_radius= 10)
            pygame.draw.rect(surf, BLACK, self.rect, 2, border_radius=10)
            draw_text(surf, self.name, (self.rect.x + 8, self.rect.y + 6), BLACK, SMALL)

    def on_click(self, game):
        if not self.visible:
            return ""
        if self.name == "門":  # 第一間房間
            if self.locked:
                if game.held_item and game.held_item.name == "鑰匙":
                    self.locked = False
                    return "你使用了鑰匙，門已解鎖！"
                return "門被鎖住了，好像需要鑰匙。"
            else:
                game.enter_room2()
                return "你打開門進入了下一間房間！"

        if self.name == "木門":  # 第二間房間
            if self.locked:
                if game.held_item and game.held_item.name == "斧頭":
                    self.locked = False
                    return "你用斧頭砍開了木門！"
                return "木門緊閉著，似乎需要工具。"
            else:
                game.win = True
                return "你推開了木門，成功逃出第二間房間！"

        if self.name == "抽屜":
            if self.locked:
                game.open_code_panel(self)
                player.visible = False
                return "抽屜有三位數密碼鎖。"
            else:
                if self.contains:
                    item = self.contains.pop(0)
                    game.add_to_inventory(item)
                    return f"你從抽屜拿到『{item.name}』。"
                return "抽屜是空的。"
        if self.name == "放大鏡":
            if self.visible:
                game.add_to_inventory(Item("放大鏡", "這個是甚麼東西", icon_color = BLUE))
                self.visible = False
                return "你撿起了放大鏡"
        if self.name == "便條紙":
            if self.visible:
                game.add_to_inventory(Item("便條紙", "上面寫著 3-1-4。", icon_color=YELLOW))
                game.show_note_image = True
                player.visible = False
                self.visible = False
                return "你撿起了便條紙。"
        if self.name == "神秘鑰匙":
            if self.visible:
                self.visible = False
                game.add_to_inventory(Item("神秘鑰匙", icon_color=YELLOW))
                return "這把鑰匙是不是最後一道門的鎖"
        if self.name == "書櫃":
            return "一排舊書。其中一本書的書背特別厚…"
        if self.name == "盒子":
            if self.locked:
                if game.held_item and game.held_item.name == "神秘鑰匙":
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

# 物品欄 UI
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
                #inflate用來放大或縮小矩形的尺寸
                pygame.draw.rect(surf, item.icon_color, r.inflate(-20,-24), border_radius=8)
                #讓文字靠又且靠底部
                draw_text(surf, item.name, (r.x+6, r.bottom-24), BLACK, SMALL)
        if held_item:
            draw_text(surf, f"手上物件：{held_item.name}", (20, HEIGHT-86), WHITE)

    def handle_click(self, pos) -> Item | None:
        for i, r in enumerate(self.slot_rects):
            if r.collidepoint(pos) and i < len(self.items):
                return self.items[i]
        return None

    def add(self, item: Item) -> bool:
        if item not in self.items:
            self.items.append(item)
        if len(self.items) >= self.capacity:
            return False
        return True
    
    def remove(self, item: Item) -> bool:
        if item in self.items:
            self.items.remove(item)

    def has(self, item):
        return item in self.items

# 密碼輸入面板
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
            player.visible = True
            return
        if key == pygame.K_BACKSPACE:
            self.buffer = self.buffer[:-1]
            return
        if key == pygame.K_RETURN:
            self.submit(game)
            player.visible = True
            return
        if pygame.K_0 <= key <= pygame.K_9 and len(self.buffer)<self.length:
            self.buffer += chr(key)

    def submit(self, game):
        if self.buffer == self.target.code:
            self.target.locked = False
            game.message = "密碼正確！抽屜解鎖了。"
        else:
            game.message = "密碼錯誤。"
            game.trigger_shake(frames = 15, intensity = 8)
        game.close_code_panel()



# main
class Game:
    def __init__(self):
        self.dark_room = True
        self.light_radius = 150
        self.shake_frames = 0
        self.shake_intensity = 5
        self.messages_to_type = [
            "頭好痛。。。。這裡是哪裡。。。。",
            "這裡怎麼特別的簡陋阿。。。。怪了。。。。。",
        ]
        self.main_message = "醒來時，你身處陌生的房間。試著找線索逃出去。"
        self.current_message_index = 0
        self.typed_message = ""
        self.message_stage = "intro"
        self.type_speed = 2
        self.type_index = 0
        self.eye_phase = 0
        self.message_done = False
        self.eye_progress = 0
        self.eye_done = False
        self.current_room = 1
        self.show_note_image = False
        raw_note = pygame.image.load("assets/Note.png").convert_alpha() 
        self.note_image = pygame.transform.smoothscale(raw_note, (400, 300))
        self.room_solve = False
        self.inventory = Inventory(capacity=7)
        self.objects: list[GameObject] = []
        self.held_item: Item | None = None
        self.code_panel: CodePanel | None = None
        self.win = False
        self.rooms = {
            1: {"objects": None, "message": None},
            2: {"objects": None, "message": None}
        }
        self.setup_room1()
        self.setup_room2()
        self.switch_room(1)
        self.eye_opening = True
        self.eye_alpha = 255
        self.combinations = {
            tuple(sorted(["便條紙", "放大鏡"])): "解碼便條紙",
            tuple(sorted(["key_part1", "key_part2"])): "完整鑰匙"
        }

    def trigger_shake(self, frames = 10, intensity = 5):
        self.shake_frames = frames
        self.shake_intensity = intensity

    def get_shake_offset(self):
        if self.shake_frames > 0:
            import random
            offset = (random.randint(-self.shake_intensity, self.shake_intensity),
                      random.randint(-self.shake_intensity, self.shake_intensity))
            self.shake_frames -= 1
            return offset
        return (0, 0)

    def try_combine(self, item1_name, item2_name):
        pair = tuple(sorted([item1_name, item2_name]))
        if pair in self.combinations:
            new_item_name = self.combinations[pair]

        # 移除原本物品
            for item in self.inventory.items[:]:
                if item.name in pair:
                    self.inventory.remove(item)

        # 新增新物品
            new_item = Item(new_item_name, icon_color=(200, 200, 0))
            self.inventory.add(new_item)

            self.message = f"你組合了 {item1_name} 和 {item2_name}，得到 {new_item_name}！"
            return True
        else:
            self.message = f"{item1_name} 和 {item2_name} 無法組合。"
            return False

    # 一房間
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

        magnifier_img = pygame.Surface((160, 20))
        magnifier_img.fill(BLUE)
        magnifier = GameObject("放大鏡", magnifier_img.get_rect(topleft = (160, 30)), BLUE, (0, 255, 0), image = magnifier_img)

        note_img = pygame.Surface((80,40))
        note_img.fill(YELLOW)
        note = GameObject("便條紙", note_img.get_rect(topleft=(360,180)), YELLOW, (255,230,90), image=note_img)
        
        inventory_rect = pygame.Rect(0, HEIGHT-159, WIDTH, 159) 

        self.rooms[1]["objects"] = [magnifier, door, drawer, bookshelf, note]
        self.rooms[1]["message"] = "醒來時，你身處陌生的房間。試著找線索逃出去。"
        self.rooms[1]["obstacles"] = [door.rect, bookshelf.rect, drawer.rect] + [inventory_rect]
        
    # 二房間
    def setup_room2(self):
        door_img = pygame.Surface((360,50))
        door_img.fill(BLUE)
        door = GameObject("木門", door_img.get_rect(topleft = (350,10)), BLUE, (90,170,250), locked=True, image=door_img)

        box_img = pygame.Surface((160,100))
        box_img.fill(LIGHT_PURPLE)
        box = GameObject("盒子", box_img.get_rect(topleft=(300,300)), LIGHT_PURPLE, (123,104,238), locked=True, image=box_img)
        box.contains.append(Item("斧頭", "可以打破障礙物", icon_color=RED))

        key_img = pygame.Surface((40, 40))
        key_img.fill(YELLOW)
        key = GameObject("神秘鑰匙", key_img.get_rect(topleft = (20, 20)), YELLOW, (255,230,90), image = key_img)

        inventory_rect = pygame.Rect(0, HEIGHT-159, WIDTH, 159) 

        self.rooms[2]["objects"] = [door, box, key]
        self.rooms[2]["message"] = "你進入了第二間房間，似乎還有物品可以探索。"
        self.rooms[2]["obstacles"] = [door.rect, box.rect] + [inventory_rect]
        
    def enter_room2(self):
        self.switch_room(2)
        self.held_item = None
        self.code_panel = None

    def switch_room(self, room_number: int):
        global obstacles
        if room_number in self.rooms:
            self.current_room = room_number
            self.objects = self.rooms[room_number]["objects"]
            self.message = self.rooms[room_number]["message"]
            obstacles = self.rooms[room_number]["obstacles"]
            self.code_panel = None
            self.held_item = None
            

    # 物品欄操作
    def add_to_inventory(self, item: Item):
        if self.inventory.add(item):
            self.message = f"獲得物品：{item.name}"
        else:
            self.message = "物品欄已滿。"

    # 密碼輸入
    def open_code_panel(self, target: GameObject):
        self.code_panel = CodePanel(target, length=3)

    def close_code_panel(self):
        self.code_panel = None

    # 手上物件使用
    def use_item_on(self, item: Item, obj: GameObject) -> str:
        if item.name == "鑰匙" and obj.name == "門":
            if obj.locked:
                obj.locked = False
                self.room_solve = True
                return "你用鑰匙把門解鎖了。"
            return "門已經是開鎖狀態。"
        if item.name == "便條紙":
            return "便條紙上寫著 3-1-4，也許是密碼。"
        if item.name == "神秘鑰匙" and obj.name == "盒子":
            if obj.locked:
                obj.locked = False
                return "你用神秘鑰匙把盒子打開了"
            return "裡面似乎有一把斧頭"
        if item.name == "斧頭" and obj.name == "木門":
            obj.locked = False
            return "你用斧頭砍開了門！"
        return "這個物品不能用在這裡。"

    # 畫面
    def draw(self, surf):
        surf.fill((35,38,48))
        pygame.draw.rect(surf, (60,65,80), (0,0,WIDTH, HEIGHT-120))

        if not self.eye_done:
            self.draw_eye_animation(surf)
            return
        mx,my = pygame.mouse.get_pos()
        hovered_name = None
        hovered_rect = None
        for obj in self.objects:
            hover = obj.rect.collidepoint((mx,my))
            obj.draw(surf, hover=hover)
            if hover:
                hovered_name = obj.name
                hovered_rect = obj.rect
        
        if hovered_name and hovered_rect:
            text_surf = FONT.render(hovered_name, True, WHITE)
            text_rect = text_surf.get_rect(center=(hovered_rect.centerx, hovered_rect.top - 15))

            bg_rect = text_rect.inflate(10, 6)
            overlay = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            surf.blit(overlay, bg_rect.topleft)

            surf.blit(text_surf, text_rect)

        offset = self.get_shake_offset()
        screen.blit(surf, offset)
        if self.dark_room:
            mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            mask.fill((0,0,0,200))
            # 光圈中心使用 player.x, player.y
            pygame.draw.circle(mask, (0,0,0,0), (int(player.x), int(player.y)), self.light_radius)
            screen.blit(mask, (0,0))
        
        player.draw(screen)



        pygame.draw.rect(surf, (25,26,34), (0, HEIGHT-160, WIDTH,40))
        pygame.draw.line(surf, (55,58,70), (0, HEIGHT-160), (WIDTH, HEIGHT-160), 2)
        self.inventory.draw(surf, self.held_item)
        if self.message_stage in ("main", "intro"):
            draw_text(surf, self.typed_message, (16, HEIGHT - 148), WHITE)
        elif self.message_stage == "done":
            draw_text(surf, self.message, (16, HEIGHT - 149), WHITE)
        if self.code_panel:
            self.code_panel.draw(surf)
        if self.show_note_image:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            surf.blit(overlay, (0, 0))

            img = self.note_image.get_rect(center = (WIDTH // 2 - 10, HEIGHT // 2 - 10))
            surf.blit(self.note_image, img)
            draw_text(surf, "按 ESC 關閉", (WIDTH//2, HEIGHT//2 + img.height//2 + 20), WHITE, FONT, center=True)
        if self.win:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0,160))
            surf.blit(overlay, (0,0))
            draw_text(surf, "你逃出了房間！", (WIDTH//2, HEIGHT//2-20), WHITE, BIG, center=True)
            draw_text(surf, "恭喜通關！按 ESC 結束", (WIDTH//2, HEIGHT//2+30), WHITE, FONT, center=True)
    
    def draw_eye_animation(self, surf):
        if self.eye_done:
            return

        if self.eye_phase == 0 and self.eye_progress == 0:
            player.visible = False
        clock.tick(54)
        mask = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        mask.fill((0, 0, 0, 255))

        max_h = HEIGHT * 0.6
        min_h = HEIGHT * 0.1
        w = WIDTH * 0.9

        if self.eye_phase == 0:
            h = min_h + (max_h - min_h) * self.eye_progress
        elif self.eye_phase == 1:
            h = max_h - (max_h - min_h) * self.eye_progress
        else:
            h = min_h + (max_h - min_h) * self.eye_progress
        
        
        ellipse_rect = pygame.Rect(0, 0, w, h)
        ellipse_rect.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.ellipse(mask, (255, 255, 255), ellipse_rect)
        mask.set_colorkey((255, 255, 255))
        draw_text(surf, self.typed_message, (WIDTH // 2, HEIGHT - 80), WIDTH, FONT, center = True)
        surf.blit(mask, (0, 0))

        self.eye_progress += 0.02
        if self.eye_progress >= 1:
            self.eye_progress = 0
            self.eye_phase += 1
            if self.eye_phase > 2:
                self.eye_done = True
                player.visible = True
        draw_text(surf, self.typed_message, (WIDTH // 2, HEIGHT - 80), WHITE, FONT, center=True)



    # 滑鼠操作
    def handle_mouse_down(self, pos):
        if self.code_panel:
            return
        item = self.inventory.handle_click(pos)
        if item:
            if self.held_item:
                if self.try_combine(self.held_item.name, item.name):
                    self.held_item = None
                else:
                    self.message = f"無法組合 {self.held_item.name}和{item.name}"
                    self.held_item = None
            else:
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
        if self.show_note_image:
            if key == pygame.K_ESCAPE:
                self.show_note_image = False
                player.visible = True
            return
        if self.code_panel:
            self.code_panel.handle_key(self, key)
            return
        if key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if key == pygame.K_r:
            # 不重置，直接切換房間
            if self.current_room == 1:
                if self.room_solve:
                    self.switch_room(2)
                else:
                    self.message = "門還鎖著，必須先解開謎題"
            else:
                self.switch_room(1)
    def update(self):
        if not self.eye_done:
            if self.message_stage == "intro":
                current_text = self.messages_to_type[self.type_index] if self.type_index < len(self.messages_to_type) else ""
                if self.type_index < len(self.messages_to_type):
                    if len(self.typed_message) < len(current_text):
                        if pygame.time.get_ticks() % self.type_speed == 0:
                            self.typed_message += current_text[len(self.typed_message)]
                    else:
                        self.type_index += 1
                        self.typed_message = ""
                else:
                    self.message_stage = "main"
                    self.typed_message = ""
                    self.type_index = 0
            return
        if self.message_stage == "main":
            if len(self.typed_message) < len(self.main_message):
                self.typed_message += self.main_message[len(self.typed_message)]
        else:
            self.message_stage = "done"

class Game2(Game):
    def setup_room(self):
        # 清空原本物件
        self.objects = []

        # 房間物件示例
        door_img = pygame.Surface((120,240))
        door_img.fill(BLUE)
        door = GameObject("木門", door_img.get_rect(topleft=(WIDTH-160,120)), BLUE, (90,170,250), locked=True, image=door_img)

        box_img = pygame.Surface((160,100))
        box_img.fill(LIGHT_PURPLE)
        box = GameObject("盒子", box_img.get_rect(topleft=(200,300)), LIGHT_PURPLE, (180,160,250), locked=True, image=box_img)

        axe_img = pygame.Surface((60,40))
        axe_img.fill(255, 0, 0)
        axe = GameObject("斧頭", axe_img.get_rect(topleft=(500,350)), RED, (255,100,100), image=axe_img)

        # 添加到物件列表
        self.objects = [door, box, axe]

        # 添加提示物件標示
        box.desc = "盒子鎖住了，裡面可能有線索。"
        door.desc = "這是出口，你需要找到方法開門。"
        axe.desc = "看起來可以用來破壞門或障礙物。"

# 主迴圈
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
                player.set_target(event.pos)
            elif event.type == pygame.KEYDOWN:
                game.handle_key_down(event.key)

        player.update(obstacles)  
        game.update()                 
        game.draw(screen)        
        game.draw_eye_animation(screen)
        player.draw(screen)    
        pygame.display.flip()

if __name__ == "__main__":
    main()
