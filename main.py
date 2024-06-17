import json
import pygame

from menu_manager import MenuManager


def read_current_game_state(key):
    try:
        with open("saved_data/current_game_state.json", "r") as file:
            data = json.load(file)
            return data.get(key)
    except FileNotFoundError:
        print("File 'current_game_state' not found.")
        return "menu"  # Return "menu" as default state if file not found or JSON parsing fails


def write_current_game_state(key, value):
    try:
        with open("saved_data/current_game_state.json", "r+") as file:
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
        self.scene = Scene("Castle", screen)

    def update(self, events):
        self.scene.update(events)
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Check if Escape key is pressed
                    self.menu()  # Open the menu
                if event.key == pygame.K_w or event.key == pygame.K_UP:  # Check if W key or Up arrow key is pressed
                    self.update_movement("up", True)
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:  # Check if A key or Left arrow key is pressed
                    self.update_movement("left", True)
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:  # Check if D key or Right arrow key is pressed
                    self.update_movement("right", True)
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:  # Check if S key or Down arrow key is pressed
                    self.update_movement("down", True)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w or event.key == pygame.K_UP:  # Check if W key or Up arrow key is pressed
                    self.update_movement("up", False)
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:  # Check if A key or Left arrow key is pressed
                    self.update_movement("left", False)
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:  # Check if D key or Right arrow key is pressed
                    self.update_movement("right", False)
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:  # Check if S key or Down arrow key is pressed
                    self.update_movement("down", False)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Check if left mouse button is clicked
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    print(f"Left click at (x={mouse_x}, y={mouse_y})")

    def draw(self):
        self.scene.draw()

    def write_file(self, file_name, key, value):
        try:
            with open(file_name, "r+") as file:
                data = json.load(file)
                data[key] = value
                file.seek(0)  # Move the file pointer to the beginning
                json.dump(data, file, indent=4)
                file.truncate()  # Remove any remaining content after writing
                print(f"file: '{file_name}' updated: {key} = {value}")
        except FileNotFoundError:
            print(f"file: '{file_name}' not found.")

    def menu(self):
        self.write_file("saved_data/current_game_state.json", "current_state", "menu")  # Example usage

    def update_movement(self, current_input, value):
        self.write_file("saved_data/current_user_input.json", current_input, value)  # Example usage


class SpriteAnimation:

    def __init__(self, obj_data):
        self.name = obj_data.get("name", "")
        self.width = obj_data.get("width", 10)
        self.image_path = obj_data.get("image", "")
        self.animation_speed = obj_data.get("animation_speed", 10)
        self.cells = obj_data.get("cells", 1)
        self.current_frame = 0
        self.frame_counter = 0

        if obj_data.get("repeat", False):
            pass
        else:
            try:
                self.sprite_strip = pygame.image.load(self.image_path).convert_alpha()
                original_width = self.sprite_strip.get_width() // self.cells
                original_height = self.sprite_strip.get_height()
                target_width = self.width  # Desired final width after reduction

                relative_height = (original_height * target_width) / original_width
                self.sprite_strip = pygame.transform.scale(self.sprite_strip, (self.width * self.cells, relative_height))
                self.frame_width = self.sprite_strip.get_width() // self.cells
                self.frame_height = self.sprite_strip.get_height()
            except pygame.error as e:
                print(f"Unable to load sprite image '{self.image_path}': {e}")
                self.sprite_strip = None  # Handle this case in the draw method
            except FileNotFoundError as e:
                print(e)
                self.sprite_strip = None  # Handle this case in the draw method

    def update(self):
        # Add sprite animation or any other update logic here
        self.frame_counter += 1
        if self.frame_counter >= self.animation_speed:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % self.cells

    def draw(self, screen, x, y):
        try:
            frame_x = self.current_frame * self.frame_width
            screen.blit(self.sprite_strip, (x, y), (frame_x, 0, self.frame_width, self.frame_height))
        except:
            print("Could not draw image")


class Sprite:
    def __init__(self, obj_data):
        self.animation_name = "base"
        self.name = obj_data.get("name", "")
        self.type = obj_data.get("type", "")
        self.x = obj_data.get("x", 0)
        self.y = obj_data.get("y", 0)
        self.animations = []
        print(f"this is the images {obj_data.get('images', [])}")
        for image in obj_data.get("images", []):
            print(f"This is the image object {image}")
            self.animations.append(SpriteAnimation(image))

    def update(self):
        for animation in self.animations:
            if animation.name == self.animation_name:
                animation.update()

    def draw(self, screen):
        for animation in self.animations:
            if animation.name == self.animation_name:
                animation.draw(screen, self.x, self.y)


class Item(Sprite):
    def __init__(self, obj_data):
        super().__init__(obj_data)


class Background(Sprite):
    def __init__(self, obj_data):
        super().__init__(obj_data)


class NPC(Sprite):
    def __init__(self, obj_data):
        super().__init__(obj_data)


class Player(Sprite):
    def __init__(self, obj_data):
        super().__init__(obj_data)

    def update(self):
        super().update()
        user_input = self.current_input()
        if user_input["up"]:
            self.y -= 1
            self.animation_name = "up_movement"
        if user_input["down"]:
            self.y += 1
            self.animation_name = "down_movement"
        if user_input["left"]:
            self.x -= 1
        if user_input["right"]:
            self.x += 1
        if not user_input["right"] and not user_input["left"] and not user_input["down"] and not user_input["up"]:
            self.animation_name = "base"

    def current_input(self):
        try:
            with open("saved_data/current_user_input.json", "r") as file:
                return json.load(file)
        except FileNotFoundError:
            print("File 'saved_data/current_user_input.json' not found.")
            return None


class Scene:
    def __init__(self, scene_name, screen):
        self.scene_data = self.load_scene_data(scene_name)
        self.screen = screen
        self.sprites = []

        # Load objects with animated sprites
        for background in self.scene_data.get("backgrounds", []):
            sprite = Background(background)
            self.sprites.append(sprite)
        for npc in self.scene_data.get("npcs", []):
            sprite = NPC(npc)
            self.sprites.append(sprite)
        for item in self.scene_data.get("items", []):
            sprite = Item(item)
            self.sprites.append(sprite)

        self.sprites.append(Player(self.scene_data.get("player", {})))

    def load_scene_data(self, scene_name):
        try:
            with open("scenes/scene_data.json", "r") as file:
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
