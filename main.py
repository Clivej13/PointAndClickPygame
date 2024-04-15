import json
import math
import pygame
from menu_manager import MenuManager

def read_current_game_state(key):
    try:
        with open("current_game_state.json", "r") as file:
            data = json.load(file)
            return data.get(key)
    except FileNotFoundError:
        print("File 'current_game_state' not found.")
        return "menu"  # Return "menu" as default state if file not found or JSON parsing fails

def write_current_game_state(key, value):
    try:
        with open("current_game_state.json", "r+") as file:
            data = json.load(file)
            data[key] = value
            file.seek(0)  # Move the file pointer to the beginning
            json.dump(data, file, indent=4)
            file.truncate()  # Remove any remaining content after writing
            print(f"Game state updated: {key} = {value}")
    except FileNotFoundError:
        print("File 'current_game_state.json' not found.")

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.scene = Scene("test", screen)

    def update(self, events):
        self.scene.update(events)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Check if Escape key is pressed
                    self.menu()  # Open the menu

    def draw(self):
        self.scene.draw()

    def write_current_game_state(self, key, value):
        try:
            with open("current_game_state.json", "r+") as file:
                data = json.load(file)
                data[key] = value
                file.seek(0)  # Move the file pointer to the beginning
                json.dump(data, file, indent=4)
                file.truncate()  # Remove any remaining content after writing
                print(f"Game state updated: {key} = {value}")
        except FileNotFoundError:
            print("File 'current_game_state.json' not found.")

    def menu(self):
        self.write_current_game_state("current_state", "menu")  # Example usage

class Sprite:
    def __init__(self, obj_data):
        self.current_frame = 0
        self.x = obj_data.get("x")
        self.y = obj_data.get("y")
        self.cells = 1  # Default number of cells
        self.cell_width = 0
        self.cell_height = 0
        self.animation_speed = 1  # Default animation speed
        self.frame_counter = 0
        self.movement = obj_data.get("movement")
        self.current_point_index = 0
        self.current_speed = 0
        self.image = None  # Placeholder for the moving image

        if self.movement:
            self.points = self.movement.get("points", [])
            self.set_next_point()
        else:
            self.image = pygame.image.load(obj_data.get("image")).convert_alpha()
            self.cells = obj_data.get("cells")
            self.cell_width = self.image.get_width() // self.cells
            self.cell_height = self.image.get_height()
            self.animation_speed = obj_data.get("animation_speed")

    def set_next_point(self):
        if self.points:
            point = self.points[self.current_point_index]
            if "x" in point and "y" in point and "speed" in point:
                self.target_x = point["x"]
                self.target_y = point["y"]
                self.current_speed = point["speed"]


            # Load image for this movement point
            self.image = pygame.image.load(point["image"]).convert_alpha()
            self.cells = point.get("cells", 1)
            self.cell_width = self.image.get_width() // self.cells
            self.cell_height = self.image.get_height()
            self.animation_speed = point.get("animation_speed", 1)




    def move_to_next_point(self):
        if self.points:
            point = self.points[self.current_point_index]
            timer = 0
            if "x" in point and "y" in point and "speed" in point:
                dx = self.target_x - self.x
                dy = self.target_y - self.y
                distance = math.sqrt(dx ** 2 + dy ** 2)
                if distance > self.current_speed:
                    self.x += dx * self.current_speed / distance
                    self.y += dy * self.current_speed / distance
                else:
                    self.x = self.target_x
                    self.y = self.target_y
                    self.current_point_index = (self.current_point_index + 1) % len(self.points)
                    self.set_next_point()
            elif "time" in point:
                timer += 1
                if timer > point["time"]:
                    self.set_next_point()


    def update(self):
        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % self.cells

        if self.movement:
            self.move_to_next_point()

    def draw(self, screen):
        frame_x = self.current_frame * self.cell_width
        frame_rect = pygame.Rect(frame_x, 0, self.cell_width, self.cell_height)

        screen.blit(self.image, (self.x, self.y), frame_rect)

class Scene:
    def __init__(self, scene_name, screen):
        self.scene_data = self.load_scene_data(scene_name)
        self.screen = screen
        self.background_image = pygame.image.load(self.scene_data["background1"]).convert()
        self.background_image = pygame.transform.scale(self.background_image, self.screen.get_size())
        self.sprites = []

        # Load objects with animated sprites
        for obj_data in self.scene_data.get("objects", []):
            sprite = Sprite(obj_data)
            self.sprites.append(sprite)

    def load_scene_data(self, scene_name):
        try:
            with open("scene_data.json", "r") as file:
                data = json.load(file)
                return data.get(scene_name)
        except FileNotFoundError:
            print("File 'scene_data' not found.")
            return None

    def update(self, events):
        # Update sprites
        for sprite in self.sprites:
            sprite.update()

    def draw(self):
        # Draw background image
        self.screen.blit(self.background_image, (0, 0))

        # Draw sprites
        for sprite in self.sprites:
            sprite.draw(self.screen)

if __name__ == "__main__":
    write_current_game_state("current_state", "menu")
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    menu_manager = MenuManager("menus", "main_menu")
    game = Game(screen)
    menu_manager.load_menus()

    running = True
    clock = pygame.time.Clock()
    FPS = 60

    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        if read_current_game_state("current_state") == "menu":
            menu_manager.update(events)
            menu_manager.draw(screen)
        elif read_current_game_state("current_state") == "game":
            menu_manager.current_menu = "in_game_menu"
            game.update(events)
            game.draw()

        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()
