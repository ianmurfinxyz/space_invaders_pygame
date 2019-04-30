
from enum import Enum
import random
import pygame

class WorldState (Enum):
    WORLD_SPAWN = 0,
    WORLD_PLAY = 1,
    WORLD_OVER = 2

class SpaceInvaders:
    def __init__(self):
        # init all pygame systems...
        pygame.init()
        pygame.mixer.init()

        # display data
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600

        # create the display... note: must do before load images
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

        # load all images...
        self.sprite_ply = pygame.image.load("assets/player.png").convert()
        self.sprite_ply_boom = ([pygame.image.load("assets/player_boom_F0.png").convert(), pygame.image.load("assets/player_boom_F1.png").convert()])
        for i in range(2):
            self.sprite_ply_boom[i].set_colorkey((255, 0, 0))
        self.sprite_ui_life = pygame.image.load("assets/life_symbol.png").convert()
        self.sprite_ui_life.set_colorkey((255, 0, 0))
        self.sprite_ply.set_colorkey((0, 0, 0))
        self.sprite_alien = {
                0:[pygame.image.load("assets/alien_0_F0.png").convert(), pygame.image.load("assets/alien_0_F1.png").convert()],
                1:[pygame.image.load("assets/alien_1_F0.png").convert(), pygame.image.load("assets/alien_1_F1.png").convert()],
                2:[pygame.image.load("assets/alien_2_F0.png").convert(), pygame.image.load("assets/alien_2_F1.png").convert()],
                3:[pygame.image.load("assets/boom_0_F0.png").convert(), pygame.image.load("assets/boom_0_F1.png").convert()]
                }
        for i in range(4):
            for j in range(2):
                self.sprite_alien[i][j].set_colorkey((255, 0, 0))
        self.sprite_special = pygame.image.load("assets/special.png").convert()
        self.sprite_special.set_colorkey((255, 0, 0))

        # set the image dimensions for each resource... note: used for collisions
        self.sprite_alien_dims = {
                0:[24, 24],
                1:[33, 24],
                2:[33, 24],
                3:[24, 24]
                }

        # load the background...
        self.sprite_background = pygame.image.load("assets/background.jpg").convert()

        # load all sounds...
        self.sound_ply_fire = pygame.mixer.Sound("assets/player_fire.wav")
        self.sound_ply_boom = pygame.mixer.Sound("assets/player_boom.wav")
        self.sound_ply_respawn = pygame.mixer.Sound("assets/player_respawn.wav")
        self.sound_alien_fire = pygame.mixer.Sound("assets/alien_fire.wav")
        self.sound_alien_boom = pygame.mixer.Sound("assets/alien_boom.wav")
        self.sound_special_death = pygame.mixer.Sound("assets/special_death.wav")
        self.sound_die_scream = pygame.mixer.Sound("assets/die_scream.wav")
        
        # load the music and start it playing
        pygame.mixer.music.load("assets/vintage_elecro_pop_loop.mp3")
        pygame.mixer.music.play(-1)

        # load the fonts...
        self.score_font = pygame.font.Font("assets/space_invaders.ttf", 20)
        self.game_over_font = pygame.font.Font("assets/space_invaders.ttf", 80)
        self.special_death_font = pygame.font.Font("assets/space_invaders.ttf", 16)

        # main game clock
        self.clock = pygame.time.Clock()
        self.frame_period_ms = 60

        # player data
        self.PLY_WIDTH_PX = 60
        self.PLY_HEIGHT_PX = 32
        self.PLY_BOOM_ANIMATION_DURATION_MS = 2000 # total time duration of animation
        self.PLY_BOOM_ANIMATION_PERIOD_MS = 500 # period between frame changes
        self.PLY_RESPAWN_TIME_MS = 4000 # time it takes to respawn; must be longer than PLY_BOOM_ANIMATION_DURATION_MS
        self.PLY_SPAWN_POS_X_PX = 300
        self.PLY_SPAWN_POS_Y_PX = 520

        self.ply_rect = pygame.Rect(0, 0, self.PLY_WIDTH_PX, self.PLY_HEIGHT_PX)
        self.ply_move_dis_px = 5   # displacement of player per frame when moving
        self.ply_fire_period_ms = 500 # min time between firing
        self.ply_fire_timer_ms = 0  # keeps track of time since last fired
        self.ply_life_count = 3
        self.ply_is_dead = False
        self.ply_boom_timer_ms = 0
        self.ply_respawn_timer_ms = 0
        self.ply_score = 0

        # set the player initial position (note has to be the center position)...
        self.ply_rect.centerx = self.PLY_SPAWN_POS_X_PX
        self.ply_rect.centery = self.PLY_SPAWN_POS_Y_PX

        # player missiles
        self.PLY_MISS_SPAWN_HEIGHT_PX = -10

        self.ply_miss_list = list() # list of pygame.Rects representing the missiles
        self.ply_miss_move_dis_px = -10 # displacemnet of player missiles per frame while moving
        self.ply_miss_color = tuple((244, 66, 182))

        # alien missiles
        self.ALIEN_MISS_WIDTH_PX = 4
        self.ALIEN_MISS_HEIGHT_PX = 8
        self.ALIEN_MISS_SPAWN_HEIGHT_PX = 14

        self.alien_miss_move_dis_px = 10 # displacement of alien missile movements per frame
        self.alien_miss_list = list()
        
        # missile data
        self.MISS_WIDTH_PX = 4
        self.MISS_HEIGHT_PX = 8

        # aliens data
        self.ALIEN_CELL_SIZE_PX = 48 # width and height of cells in the alien grid
        self.ALIEN_WIDTH_PX = 24 # note: small than cell size, positioned in the center
        self.ALIEN_HEIGHT_PX = 24
        self.ALIEN_GRID_WIDTH_CELLS = 12
        self.ALIEN_GRID_HEIGHT_CELLS = 5
        self.ALIEN_DROP_DIS_PX = 20 # distance grid drops when at edge of screen
        self.ALIEN_BOOM_ANIMATION_PERIOD_MS = 500 # time between changes of boom animation
        self.ALIEN_BOOM_ANIMATION_DURATION_MS = 2000
        self.ALIEN_TYPE_SCORE_VALUE = tuple((40, 20, 10)) # score value of each alien type
        self.ALIEN_SPAWN_MOVE_DIS_PX = 10 # displacement per frame when the alien are dropping into start position - this MUST meet the condition: spawn_pos_y + (n*dis) == start_pos_y, where n is an integer 
        self.ALIEN_GRID_SPAWN_POS_X_PX = (self.SCREEN_WIDTH - (self.ALIEN_CELL_SIZE_PX * 10)) * 0.5
        self.ALIEN_GRID_SPAWN_POS_Y_PX = -500
        self.ALIEN_GRID_START_POS_Y_PX = 100

        self.alien_move_period_ms = 2000 # period between alien movements
        self.alien_move_timer_ms = 0
        self.alien_move_dis_px = 5 # displacement the aliens move horizontally
        self.alien_move_direction = 1 # must = 1 or -1 (multiplied by move displacement)
        self.alien_last_move_was_drop = False # prevents dropping down twice in a row
        self.alien_animation_frame = False # cast to either 0 or 1 

        self.alien_fire_list = dict() # a dictionary of all aliens that can fire at a given time (bottom most alive)
        self.alien_fire_delay_base_ms = 2000 # reduce to increase base fire rate
        self.alien_fire_delay_increment_ms = 50 # best kept constant; reduce range instead to increase fire rate
        self.alien_fire_delay_increment_range = 100 # reduce range to increase fire rate
        self.alien_fire_delay_ms = self.alien_fire_delay_base_ms # normally=base+(increment*rand_num); all variables can change
        self.alien_fire_timer_ms = 0

        self.alien_grid_pos_x_px = self.ALIEN_GRID_SPAWN_POS_X_PX # x coordinate of top,left corner of grid
        self.alien_grid_pos_y_px = self.ALIEN_GRID_SPAWN_POS_Y_PX # y coordinate of top,left corner of grid
        self.alien_2d_grid = list() # 2d jagged array of pygame.Rects with size[5][10]

        self.alien_pop_count = self.ALIEN_GRID_WIDTH_CELLS * self.ALIEN_GRID_HEIGHT_CELLS # how many aliens alive

        # special mothership data
        self.SPECIAL_START_POS_X_PX = -50
        self.SPECIAL_START_POS_Y_PX = 60
        self.SPECIAL_SCORE_VALUE = 100
        self.SPECIAL_MOVE_DIS_PX = 4 # displacement the special moves each frame
        self.SPECIAL_SIGN_DURATION_MS = 1000 # how the long the score sign shows for

        self.special_rect = pygame.Rect(0, 0, 64, 28) # must match the dimensions of the sprite
        self.special_delay_base_ms = 20000 # base time between spawns of mothership (should be longer than it takes the special to travel the screen width)
        self.special_delay_increment_ms = 1000
        self.special_delay_ms = 20000 # normally=base+(increment*rand_num); all variables can change
        self.special_delay_timer_ms = 0 # keeps track of time since last spawn
        self.special_is_dead = True
        self.special_delay_increment_range = 60
        self.special_boom_timer_ms = 100000

        # create the 2d array of aliens...
        for row_num in range(self.ALIEN_GRID_HEIGHT_CELLS):
            row = list()
            for col_num in range(self.ALIEN_GRID_WIDTH_CELLS):
                is_dead = False
                boom_timer_ms = 0
                if row_num == 0:
                    type_index = 0  # indexes into images array to select the image to draw for this alien
                elif row_num < 3:
                    type_index = 1
                elif row_num <= 5:
                    type_index = 2
                alien_rect = pygame.Rect(0, 0, self.sprite_alien_dims[type_index][0], self.sprite_alien_dims[type_index][1])
                alien_rect.centerx = self.alien_grid_pos_x_px + (col_num * self.ALIEN_CELL_SIZE_PX) + (self.ALIEN_CELL_SIZE_PX * 0.5)
                alien_rect.centery = self.alien_grid_pos_y_px + (row_num * self.ALIEN_CELL_SIZE_PX) + (self.ALIEN_CELL_SIZE_PX * 0.5)
                row.append(list((is_dead, type_index, alien_rect, boom_timer_ms)))
            self.alien_2d_grid.append(row)

        # set the alien firing list... note: initially just the bottom row
        # note: firing list is a dictionary where the keys are of the form tuple((row_num, col_num)), i.e. the tuple is used as unique id for the alien
        for col_num in range(self.ALIEN_GRID_WIDTH_CELLS):
            self.alien_fire_list[tuple((self.ALIEN_GRID_HEIGHT_CELLS - 1, col_num))] = self.alien_2d_grid[self.ALIEN_GRID_HEIGHT_CELLS - 1][col_num]

        # UI data
        self.UI_LOWER_LINE_POS_Y_PX = self.SCREEN_HEIGHT - 50 # position of start of lower ui

        self.score_rect = pygame.Rect(self.SCREEN_WIDTH - 150, 10, 0, 0) # position of score on screen
        self.ui_color = tuple((0, 255, 110))
        self.ui_fill_color = pygame.Color(0, 0, 0, 200)
        self.ui_life_rects = list() #45x24 px
        for i in range(3):
            rect = pygame.Rect(0, 0, 0, 0)
            rect.x = 15 + (i * 45) + (i * 5) # 45 is the width of the image
            rect.y = self.SCREEN_HEIGHT - 40
            self.ui_life_rects.append(rect)
        self.special_death_sign = self.special_death_font.render("150", False, self.ui_color)

        # world data
        self.world_state = WorldState.WORLD_SPAWN

    def respawn_alien_grid(self):
        # reset the alien grid...
        self.alien_grid_pos_x_px = self.ALIEN_GRID_SPAWN_POS_X_PX # x coordinate of top,left corner of grid
        self.alien_grid_pos_y_px = self.ALIEN_GRID_SPAWN_POS_Y_PX # y coordinate of top,left corner of grid
        self.alien_pop_count = self.ALIEN_GRID_WIDTH_CELLS * self.ALIEN_GRID_HEIGHT_CELLS

        # reset the aliens in the grid...
        for row_num in range(self.ALIEN_GRID_HEIGHT_CELLS):
            for col_num in range(self.ALIEN_GRID_WIDTH_CELLS):
                is_dead = False
                boom_timer_ms = 0
                if row_num == 0:
                    type_index = 0  # indexes into images array to select the image to draw for this alien
                elif row_num < 3:
                    type_index = 1
                elif row_num <= 5:
                    type_index = 2
                alien_rect = pygame.Rect(0, 0, self.sprite_alien_dims[type_index][0], self.sprite_alien_dims[type_index][1])
                alien_rect.centerx = self.alien_grid_pos_x_px + (col_num * self.ALIEN_CELL_SIZE_PX) + (self.ALIEN_CELL_SIZE_PX * 0.5)
                alien_rect.centery = self.alien_grid_pos_y_px + (row_num * self.ALIEN_CELL_SIZE_PX) + (self.ALIEN_CELL_SIZE_PX * 0.5)
                alien_cell = self.alien_2d_grid[row_num][col_num]
                alien_cell[0] = is_dead
                alien_cell[1] = type_index
                alien_cell[2] = alien_rect
                alien_cell[3] = boom_timer_ms

        # reset the alien fire list...
        self.alien_fire_list.clear()
        for col_num in range(self.ALIEN_GRID_WIDTH_CELLS):
            self.alien_fire_list[tuple((self.ALIEN_GRID_HEIGHT_CELLS - 1, col_num))] = self.alien_2d_grid[self.ALIEN_GRID_HEIGHT_CELLS - 1][col_num]

        # delete all player missiles so they dont interfere with the new aliens...
        self.ply_miss_list.clear()     

    def update_player(self):
        # update the player...
        if self.ply_is_dead:
            # respawn...
            if self.ply_life_count > 0:
                self.ply_respawn_timer_ms += self.frame_period_ms
                if self.ply_respawn_timer_ms > self.PLY_RESPAWN_TIME_MS:
                    self.ply_is_dead = False
                    self.ply_rect.centerx = self.PLY_SPAWN_POS_X_PX
                    self.ply_rect.centery = self.PLY_SPAWN_POS_Y_PX
                    self.ply_life_count -= 1
                    # play the sound effect...
                    self.sound_ply_respawn.play()
        else:
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_a] or keys[pygame.K_LEFT]) and self.ply_rect.centerx > 50:
                self.ply_rect.centerx -= self.ply_move_dis_px

            elif (keys[pygame.K_d] or keys[pygame.K_RIGHT]) and self.ply_rect.centerx < (self.SCREEN_WIDTH - 50):
                self.ply_rect.centerx += self.ply_move_dis_px
            
    def update_player_firing(self):
        if not self.ply_is_dead:
            keys = pygame.key.get_pressed()
            self.ply_fire_timer_ms += self.frame_period_ms
            if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and (self.ply_fire_timer_ms > self.ply_fire_period_ms):
                miss_rect = pygame.Rect(0, 0, self.MISS_WIDTH_PX, self.MISS_HEIGHT_PX)
                miss_rect.centerx = self.ply_rect.centerx
                miss_rect.centery = self.ply_rect.centery + self.PLY_MISS_SPAWN_HEIGHT_PX
                self.ply_miss_list.append(miss_rect)
                self.ply_fire_timer_ms = 0
                self.sound_ply_fire.play()

    def spawn_update(self):
        # move the aliens down until they reach the start position...
        self.alien_grid_pos_y_px += self.ALIEN_SPAWN_MOVE_DIS_PX
        for row_num in range(self.ALIEN_GRID_HEIGHT_CELLS):
            for col_num in range(self.ALIEN_GRID_WIDTH_CELLS):
                alien_cell = self.alien_2d_grid[row_num][col_num] # a tuple
                alien_cell[2].centery += self.ALIEN_SPAWN_MOVE_DIS_PX
        if self.alien_grid_pos_y_px == self.ALIEN_GRID_START_POS_Y_PX:  # NOTE: this condition will break if displacement, start and spawn positions are not set correctly!
            self.world_state = WorldState.WORLD_PLAY

        # update the player (but not firing)...
        self.update_player()

    def normal_update(self):
        # update the player...
        self.update_player()
        self.update_player_firing()

        # update the missiles...
        # update the player missiles...
        for missile in self.ply_miss_list:
            missile.centery += self.ply_miss_move_dis_px
            if missile.centery < -20:
                self.ply_miss_list.remove(missile)

        # update the alien missile...
        for missile in self.alien_miss_list:
            missile.centery += self.alien_miss_move_dis_px
            if missile.centery > self.UI_LOWER_LINE_POS_Y_PX - 10:
                self.alien_miss_list.remove(missile)

        # update the alien grid...
        self.alien_move_timer_ms += self.frame_period_ms
        if self.alien_move_timer_ms > self.alien_move_period_ms:
            # if we have not already dropped and we reached the screen margins, then drop
            if not self.alien_last_move_was_drop and (self.alien_grid_pos_x_px < 20 or (self.alien_grid_pos_x_px + (self.ALIEN_CELL_SIZE_PX * self.ALIEN_GRID_WIDTH_CELLS) > (self.SCREEN_WIDTH - 20))):
                self.alien_grid_pos_y_px += self.ALIEN_DROP_DIS_PX
                for row_num in range(self.ALIEN_GRID_HEIGHT_CELLS):
                    for col_num in range(self.ALIEN_GRID_WIDTH_CELLS):
                        alien_cell = self.alien_2d_grid[row_num][col_num] # a tuple
                        alien_cell[2].centery += self.ALIEN_DROP_DIS_PX
                self.alien_move_direction *= -1
                self.alien_last_move_was_drop = True
            else: # else move horizonatally
                self.alien_grid_pos_x_px += (self.alien_move_dis_px * self.alien_move_direction)
                for row_num in range(self.ALIEN_GRID_HEIGHT_CELLS):
                    for col_num in range(self.ALIEN_GRID_WIDTH_CELLS):
                        alien_cell = self.alien_2d_grid[row_num][col_num] # a tuple
                        alien_cell[2].centerx += (self.alien_move_dis_px * self.alien_move_direction)
                self.alien_last_move_was_drop = False
            # moved so reset the clock
            self.alien_move_timer_ms = 0
            self.alien_animation_frame = not self.alien_animation_frame

        # handle alien firing...
        if not self.ply_is_dead: # stop firing if dead so dont keep dying on respawn
            self.alien_fire_timer_ms += self.frame_period_ms
            if self.alien_fire_timer_ms > self.alien_fire_delay_ms:
                # pick a random alien from the fire list to fire.
                alien_cell = self.alien_fire_list[random.choice(list(self.alien_fire_list.keys()))]
                # make the alien fire...
                alien_miss = pygame.Rect(0, 0, self.ALIEN_MISS_WIDTH_PX, self.ALIEN_MISS_HEIGHT_PX)
                alien_miss.centerx = alien_cell[2].centerx + (self.ALIEN_MISS_WIDTH_PX * 0.5)
                alien_miss.centery = alien_cell[2].centery + self.ALIEN_MISS_SPAWN_HEIGHT_PX
                self.alien_miss_list.append(alien_miss)
                # play the sound effect...
                self.sound_alien_fire.play()
                # set the next fire time...
                self.alien_fire_delay_ms = self.alien_fire_delay_base_ms + (self.alien_fire_delay_increment_ms * random.randint(0, self.special_delay_increment_range))
                # dont forget to reset the clock!
                self.alien_fire_timer_ms = 0

        # handle special spawning...
        self.special_delay_timer_ms += self.frame_period_ms
        if self.special_delay_timer_ms > self.special_delay_ms:
            #spawn the special...
            self.special_is_dead = False
            self.special_rect.centerx = self.SPECIAL_START_POS_X_PX
            self.special_rect.centery = self.SPECIAL_START_POS_Y_PX
            # set the time when the next one will spawn (should be longer than it takes this one to move across the screen)
            self.special_delay_ms = self.special_delay_base_ms + (self.special_delay_increment_ms * random.randint(0, self.alien_fire_delay_increment_range))
            self.special_delay_timer_ms = 0

        # update the special...
        if not self.special_is_dead:
            self.special_rect.centerx += self.SPECIAL_MOVE_DIS_PX
            if self.special_rect.centerx > self.SCREEN_WIDTH + 50:
                self.special_is_dead = True

    def handle_collisions(self):
        # handle collisions between player missiles and aliens...
        for missile in self.ply_miss_list:
            for row_num in range(self.ALIEN_GRID_HEIGHT_CELLS):
                for col_num in range(self.ALIEN_GRID_WIDTH_CELLS):
                    alien_cell = self.alien_2d_grid[row_num][col_num]
                    if alien_cell[0] is True: # if dead move on
                        continue
                    if missile.colliderect(alien_cell[2]):
                        # destroy the missile...
                        # BUG? will this BUGger (yes i went there) up the loop? ans: NO!
                        self.ply_miss_list.remove(missile)
                        # add the player score...
                        self.ply_score += self.ALIEN_TYPE_SCORE_VALUE[alien_cell[1]]
                        # destroy the alien and make a pretty explode animation...
                        alien_cell[0] = True # set to dead
                        alien_cell[1] = 3 # set type_index to 3; the explosion type
                        # decrement the population counter...
                        self.alien_pop_count -= 1
                        if not self.alien_pop_count == 0:   # if still some left update the fire list
                            # if this alien is in the fire list then first remove it...
                            for key in self.alien_fire_list.keys():
                                if key == tuple((row_num, col_num)):
                                    self.alien_fire_list.pop(key)
                                    break
                            # find the next alien above that is not dead and add that to the list...
                            above_row_num = row_num - 1
                            while above_row_num >= 0:
                                above_alien_cell = self.alien_2d_grid[above_row_num][col_num]
                                if above_alien_cell[0] is False: # if not dead
                                    self.alien_fire_list[tuple((above_row_num, col_num))] = above_alien_cell
                                    break
                                above_row_num -= 1
                        else: # all dead so respawn...
                            self.world_state = WorldState.WORLD_SPAWN
                            self.respawn_alien_grid()
                            # scream die! they wont die!
                            self.sound_die_scream.play()
                        # play the boom death sound...
                        self.sound_alien_boom.play()

        # handle collisions between player missiles and special motherships...
        if not self.special_is_dead:
            for missile in self.ply_miss_list:
                if missile.colliderect(self.special_rect):
                    self.ply_miss_list.remove(missile)
                    self.ply_score += self.SPECIAL_SCORE_VALUE
                    self.special_is_dead = True
                    self.sound_special_death.play()
                    self.special_boom_timer_ms = 0

        # handle collisions between alien missiles and player...
        for missile in self.alien_miss_list:
            if self.ply_rect.colliderect(missile):
                self.alien_miss_list.remove(missile)
                # kill the player and play death animation...
                self.ply_is_dead = True
                self.ply_boom_timer_ms = 0
                self.ply_respawn_timer_ms = 0
                # play the death sound...
                self.sound_ply_boom.play()
                # dead and no lives left
                if self.ply_life_count == 0:
                    self.world_state = WorldState.WORLD_OVER
                    # start playing the game over music...
                    pygame.mixer.music.load("assets/game_over.wav")
                    pygame.mixer.music.play(-1)

    def draw_player(self):
        # draw the player...
        if not self.ply_is_dead:
            self.screen.blit(self.sprite_ply, self.ply_rect)
        else:
            if self.ply_boom_timer_ms < self.PLY_BOOM_ANIMATION_DURATION_MS:
                self.ply_boom_timer_ms += self.frame_period_ms
                animation_frame = int(self.ply_boom_timer_ms / self.PLY_BOOM_ANIMATION_PERIOD_MS) % 2
                self.screen.blit(self.sprite_ply_boom[animation_frame], self.ply_rect)

    def draw_alien_grid(self):
         # draw the aliens...
        for row_num in range(self.ALIEN_GRID_HEIGHT_CELLS):
            for col_num in range(self.ALIEN_GRID_WIDTH_CELLS):
                alien_cell = self.alien_2d_grid[row_num][col_num]
                if alien_cell[0] is False: # if not dead
                    self.screen.blit(self.sprite_alien[alien_cell[1]][int(self.alien_animation_frame)], alien_cell[2])
                else: # if dead
                    if alien_cell[3] < self.ALIEN_BOOM_ANIMATION_DURATION_MS: # if boom not expired
                        alien_cell[3] += self.frame_period_ms
                        animation_frame = int(alien_cell[3] / self.ALIEN_BOOM_ANIMATION_PERIOD_MS) % 2
                        self.screen.blit(self.sprite_alien[alien_cell[1]][animation_frame], alien_cell[2])

    def spawn_draw(self):
        self.draw_player()
        self.draw_alien_grid()

    def normal_draw(self):
        self.draw_player()

        # draw the player missiles...
        for missile in self.ply_miss_list:
            pygame.draw.rect(self.screen, self.ply_miss_color, missile)

        # draw the alien missiles...
        for missile in self.alien_miss_list:
            pygame.draw.rect(self.screen, (66, 244, 238), missile)

        self.draw_alien_grid()

        # draw the special...
        if not self.special_is_dead:
            self.screen.blit(self.sprite_special, self.special_rect)
        else:
            if self.special_boom_timer_ms < self.SPECIAL_SIGN_DURATION_MS:
                self.special_boom_timer_ms += self.frame_period_ms
                #animation_frame = int(self.special_boom_timer_ms / self.ALIEN_BOOM_ANIMATION_PERIOD_MS) % 2
                #self.screen.blit(self.sprite_alien[3][animation_frame], self.special_rect)
                self.screen.blit(self.special_death_sign, self.special_rect)

        # draw the UI...
        # draw the score...
        score_text = "Score: " + str(self.ply_score)
        score_sign = self.score_font.render(score_text, False, self.ui_color)
        self.screen.blit(score_sign, self.score_rect)

    def over_draw(self):
        # draw the game over sign...
        game_over_sign = self.game_over_font.render("GAME OVER!", False, self.ui_color)
        sign_size = game_over_sign.get_size()
        game_over_rect = pygame.Rect(int((self.SCREEN_WIDTH - sign_size[0]) * 0.5), int((self.SCREEN_HEIGHT - sign_size[1]) * 0.5), 0, 0)
        self.screen.blit(game_over_sign, game_over_rect)
        # draw the score below the sign...
        score_text = "Score: " + str(self.ply_score)
        score_sign = self.score_font.render(score_text, False, self.ui_color)
        sign_size_2 = score_sign.get_size()
        game_over_score_rect = pygame.Rect(int((self.SCREEN_WIDTH - sign_size_2[0]) * 0.5), int(((self.SCREEN_HEIGHT - sign_size_2[1]) * 0.5) + sign_size[1]), 0, 0)
        self.screen.blit(score_sign, game_over_score_rect)
    

    def run(self):
        done = False
        while not done:
            self.clock.tick(self.frame_period_ms)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                # add cheats for debugging...
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                    self.ply_life_count = 3

            # update the game...

            if self.world_state == WorldState.WORLD_SPAWN:
                self.spawn_update()
            elif self.world_state == WorldState.WORLD_PLAY:
                self.normal_update()
                self.handle_collisions()

            # draw the game...

            self.screen.blit(self.sprite_background, pygame.Rect(0, 0, 0, 0))

            if self.world_state == WorldState.WORLD_SPAWN:
                self.spawn_draw()
            elif self.world_state == WorldState.WORLD_PLAY:
                self.normal_draw()
            elif self.world_state == WorldState.WORLD_OVER:
                self.over_draw()
            
            # draw the the UI lines...
            pygame.draw.line(self.screen, self.ui_color, (0, self.UI_LOWER_LINE_POS_Y_PX), (self.SCREEN_WIDTH, self.UI_LOWER_LINE_POS_Y_PX), 2)

            # draw the player lives...
            for x in range(self.ply_life_count):
                self.screen.blit(self.sprite_ui_life, self.ui_life_rects[x])
            
            pygame.display.flip()

    
if __name__ == "__main__":
    SpaceInvaders().run()
 