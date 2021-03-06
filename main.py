# SIDE SCROLLER WITH PYGAME - CODING WITH RUSS
# https://www.youtube.com/watch?v=DHgj5jhMJKg
# 26.04.2022 - part 4, 12:26
# STATE OF THE GAME:
# A player sprite is created, can run left and right as well as jump.
# It can also shoot makeshift bullets.
# TODO:
#  1. Shoot bullets (IN PROGRESS)
#  2. Grenades and projectiles
#  3. Explosions
#  4. Collectibles
#  5. AI
#  6. Loading levels
#  7. Collision
#  8. Screen scrolling
#  9. Main menu and restart level
#  10. Music/SFX and screen transitions


# IMPORT PYGAME AND OS
import pygame
import os

# INITIALIZE PYGAME
pygame.init()

# CREATE IN-GAME WINDOW
# Set screen width and height
SCREEN_WIDTH = 800
# Height must be adjustable and must be converted to int
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)
# Set the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# Set the screen caption
pygame.display.set_caption('Shooter')

# SET THE CLOCK AND FRAME RATE
# Create the clock
clock = pygame.time.Clock()
# Set the frame rate to 60 fps
FPS = 60

# DEFINE GAME VARIABLES
GRAVITY = 0.75

# DEFINE PLAYER ACTION VARIABLES
moving_left = False
moving_right = False
shoot = False

# LOAD IMAGES
# Bullet image load (convert alpha necessary!)
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()

# DEFINE COLOURS
# Background colour
BG = (144, 201, 120)
RED = (255, 0, 0)

# CREATE A FUNCTION FOR DRAWING BACKGROUND
def draw_bg():
    screen.fill(BG)
    # Draw a temporary line, args: (screen, colour, (coordinates of beginning),
    #                               (coordinates of end))
    pygame.draw.line(screen, RED, (0, 300), (SCREEN_WIDTH, 300))


# CREATE SOLDIER CLASS (FOR PLAYER AND ENEMY) INHERITING FROM PYGAME'S SPRITE CLASS
class Soldier(pygame.sprite.Sprite):
    # Create the constructor for the Soldier class
    # (args: char_type -> type of character,
    #        x, y -> coordinates,
    #        scale -> image scale,
    #        speed -> speed in px)
    def __init__(self, char_type, x, y, scale, speed):
        # Initialize the Sprite class
        pygame.sprite.Sprite.__init__(self)
        # Set a marker for being alive
        self.alive = True
        # Set the character type
        self.char_type = char_type
        # Set the character's speed
        self.speed = speed
        # Set the direction of the character (1 -> looking to the right)
        self.direction = 1
        # Set the vertical velocity (speed of jumping)
        self.vel_y = 0
        # Set the jump marker
        self.jump = False
        # Set a marker if the player is in the air. We assume he's in the air
        # until he lands on something. This is to prevent double-jumping: if
        # a player is in the air, he shouldn't be allowed to jump once more
        # (see the #jump section in the Soldier.move() method)
        self.in_air = True
        # Set a marker for where the character is facing (is the character flipped)
        self.flip = False
        # Create an animation list (it'll be a list of lists)
        self.animation_list = []
        # Set a frame index for choosing frame from the animation list (at first, it's 0)
        self.frame_index = 0
        # Set action marker (0 - idle, 1 - running, 2 - jumping...
        self.action = 0
        # Set update time (for updating animation (get baseline for animation sequence)
        self.update_time = pygame.time.get_ticks()

        # Load all images for the players
        # Specify animation types
        animation_types = ['Idle', 'Run', 'Jump']
        # Loop through animation types and create a list of animation frames for each
        for animation in animation_types:
            # Create/reset a temporary list of frames
            temp_list = []
            # Count number of files in the folder - use "os" library
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}/'))
            # Loop every folder for all frames
            for i in range(num_of_frames):
                # Load i-th image from "Idle" directory
                img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                # Transform the image according to the scale
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                # Add the image to the list as the next frame
                temp_list.append(img)
                # Append the "Idle" frame list to the animation list of lists
            self.animation_list.append(temp_list)

        # Set current self image - get the frame from the animation_list of lists:
        # list [self.action] at index [self.frame_index]
        self.image = self.animation_list[self.action][self.frame_index]
        # Get rectangle (for controlling positions)
        self.rect = self.image.get_rect()
        # Position the rectangle at (x, y) - the center will be there
        self.rect.center = (x, y)

    # Add a method for moving a player around
    def move(self, moving_left: bool, moving_right: bool):
        # Set/reset movement variables (dx, dy -> delta x, y)
        dx = 0
        dy = 0

        # Assign movement variables if moving left or right (add or subtract speed to the coordinates)
        if moving_left:
            # Change dx according to movement (decrease x by 1 speed unit)
            dx = -self.speed
            # Set the character's is flipped (faces left)
            self.flip = True
            # Set the direction to -1 (left)
            self.direction = -1
        if moving_right:
            # Change dx according to movement (increase x by 1 speed unit)
            dx = self.speed
            # Indicate that the character is not flipped (faces right)
            self.flip = False
            # Set the direction to 1 (right)
            self.direction = 1

        # Jump
        # Check for jumping state
        if self.jump and not self.in_air:
            # If the character jumps, give him velocity on y axis -11 px
            self.vel_y = -11
            # Reset the jump marker
            self.jump = False
            # Reset the in_air marker
            self.in_air = True

        # Apply gravity (the velocity shouldn't exceed 10)
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        # Change delta y accordingly (it changes if the player jumps)
        dy += self.vel_y

        # Check collision with floor (landing)
        if self.rect.bottom + dy > 300:
            # If there's collision, the delta y must be equal to the difference
            # between 300 (the floor level) and the bottom of the player's feet.
            dy = 300 - self.rect.bottom
            # The player is not in the air anymore
            self.in_air = False

        # Move the player rectangle (update its position)
        self.rect.x += dx
        self.rect.y += dy

    # Define a method for updating animation
    def update_animation(self):
        # Change the animation's index after a short time.
        # Set the speed of animation cooldown
        ANIMATION_COOLDOWN = 100
        # Update image depending on current action and frame index
        self.image = self.animation_list[self.action][self.frame_index]
        # Check if enough time has passed since the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            # Reset the animation timer
            self.update_time = pygame.time.get_ticks()
            # Add 1 to frame index to choose the next animation frame
            self.frame_index += 1
        # If the animation list for current action has run out of frames,
        # reset frame index back to 0
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    # Define a method for updating action
    def update_action(self, new_action):
        # Check if the new action is different than the previous one
        # And if so - set new action
        if new_action != self.action:
            self.action = new_action
            # Update animation settings
            # Reset frame index to 0
            self.frame_index = 0
            # Set current time as the update time
            self.update_time = pygame.time.get_ticks()

    # Define a method for drawing the Soldier instance on the screen
    def draw(self):
        # We use .blit method for our screen
        # (blit args: image - flipped or not (args: surface -> image, flip_x, flip_y (booleans),
        #             rectangle of the image)
        screen.blit(pygame.transform.flip(surface=self.image, flip_x=self.flip, flip_y=False), self.rect)


# CREATE THE BULLET CLASS (ALSO INHERITS FROM SPRITE)
class Bullet(pygame.sprite.Sprite):
    # Create the constructor for the Bullet class
    # (args: x, y -> coordinates,
    #        direction -> where the bullet goes)
    def __init__(self, x, y, direction):
        # Initialize Sprite
        pygame.sprite.Sprite.__init__(self)
        # Set speed (in this case all bullets have the same speed)
        self.speed = 10
        # Define image
        self.image = bullet_img
        # Create rectangle for bullet
        self.rect = self.image.get_rect()
        # Set position of the rectangle's center
        self.rect.center = (x, y)
        # Set direction
        self.direction = direction

    def update(self):
        self.rect.x += (self.speed * self.direction)


# CREATE GROUPS OF SPRITES
# This allows to control many sprites calling one method for all
bullet_group = pygame.sprite.Group()


# INSTANTIATE SOLDIERS: PLAYER, ENEMY
player = Soldier(char_type='player', x=200, y=200, scale=3, speed=5)
enemy = Soldier(char_type='enemy', x=300, y=200, scale=3, speed=2)

# MAIN LOOP
run = True
while run:
    # Set the clock for 60 fps
    clock.tick(FPS)

    # Draw the background (so that the moving figures don't leave a trail!)
    draw_bg()
    # Update the player animation
    player.update_animation()
    # Put the player on the screen
    player.draw()
    # Put the enemy on the screen
    enemy.draw()

    # Update and draw groups
    bullet_group.update()
    bullet_group.draw(screen)

    # Update player action - as long as the player is alive
    if player.alive:
        # Shoot bullets - instantiate Bullet next to the barrel of the gun
        # centerx, centery -> the middle of the player
        # player.rect.size[0] -> width of the player
        # player direction is 1 or -1
        if shoot:
            bullet = Bullet(player.rect.centerx + (0.6 * player.rect.size[0] * player.direction),
                            player.rect.centery,
                            player.direction)
            # Add the bullet to the bullet group
            bullet_group.add(bullet)
        # Jump
        if player.in_air:
            player.update_action(2) # 2 -> jump
        # Move
        elif moving_left or moving_right:
            player.update_action(1) # 1 -> run
        # Stay idle
        else:
            player.update_action(0) # 0 -> idle

    # Move the player
    player.move(moving_left=moving_left,
                moving_right=moving_right)

    # Call in the event handler (listen for events)
    for event in pygame.event.get():
        # Quitting game.
        # If someone closes the game window, run gets False
        if event.type == pygame.QUIT:
            run = False

        # Player control.
        # Are any keyboard buttons pressed?
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_UP and player.alive:
                player.jump = True
            if event.key == pygame.K_SPACE:
                shoot = True
            # Quitting by Esc key
            if event.key == pygame.K_ESCAPE:
                run = False
        # Are any keyboard buttons released?
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
    # Update display
    pygame.display.update()

pygame.quit()
