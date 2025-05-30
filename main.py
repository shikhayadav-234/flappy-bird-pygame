import random
import sys
import pygame
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.display.set_caption('Flappy Bird by Shikha')

# Fullscreen setup
SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREENWIDTH, SCREENHEIGHT = SCREEN.get_size()
GROUNDY = int(SCREENHEIGHT * 0.8)
FPSCLOCK = pygame.time.Clock()

GAME_SPRITES = {}
GAME_SOUNDS = {}

# Paths
PLAYER = 'C:/Users/yadav/OneDrive/Desktop/Flappy bird/gallery/sprites/bird.png'
BACKGROUND = 'C:/Users/yadav/OneDrive/Desktop/Flappy bird/gallery/sprites/bg.png'
PIPE = 'C:/Users/yadav/OneDrive/Desktop/Flappy bird/gallery/sprites/pipe.png'
BASE = 'C:/Users/yadav/OneDrive/Desktop/Flappy bird/gallery/sprites/base.png'

def load_assets():
    try:
        bg = pygame.image.load(BACKGROUND).convert()
        GAME_SPRITES['background'] = pygame.transform.scale(bg, (SCREENWIDTH, SCREENHEIGHT))

        player = pygame.image.load(PLAYER).convert_alpha()
        GAME_SPRITES['player'] = pygame.transform.scale(player, (int(SCREENWIDTH * 0.07), int(SCREENHEIGHT * 0.07)))

        base = pygame.image.load(BASE).convert_alpha()
        GAME_SPRITES['base'] = pygame.transform.scale(base, (SCREENWIDTH, int(SCREENHEIGHT * 0.2)))

        pipe_img = pygame.image.load(PIPE).convert_alpha()
        pipe_width = int(SCREENWIDTH * 0.09)
        pipe_height = int(SCREENHEIGHT * 0.62)
        pipe_img = pygame.transform.scale(pipe_img, (pipe_width, pipe_height))
        GAME_SPRITES['pipe'] = (
            pygame.transform.rotate(pipe_img, 180),
            pipe_img
        )

        GAME_SPRITES['numbers'] = tuple(
            pygame.transform.scale(
                pygame.image.load(f'C:/Users/yadav/OneDrive/Desktop/Flappy bird/gallery/sprites/{i}.png').convert_alpha(),
                (int(SCREENWIDTH * 0.035), int(SCREENHEIGHT * 0.06))
            ) for i in range(10)
        )

        GAME_SOUNDS['die'] = pygame.mixer.Sound('C:/Users/yadav/OneDrive/Desktop/Flappy bird/gallery/audio/die.wav')
        GAME_SOUNDS['hit'] = pygame.mixer.Sound('C:/Users/yadav/OneDrive/Desktop/Flappy bird/gallery/audio/hit.wav')
        GAME_SOUNDS['point'] = pygame.mixer.Sound('C:/Users/yadav/OneDrive/Desktop/Flappy bird/gallery/audio/point.wav')
        GAME_SOUNDS['wing'] = pygame.mixer.Sound('C:/Users/yadav/OneDrive/Desktop/Flappy bird/gallery/audio/wing.wav')

        for sound in GAME_SOUNDS.values():
            sound.set_volume(1.0)

    except Exception as e:
        print(f"[Error] Failed to load assets: {e}")
        sys.exit()

def wait_for_enter():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_RETURN:
                return
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        text_font = pygame.font.SysFont(None, int(SCREENHEIGHT * 0.06))
        text = text_font.render("Press ENTER to start", True, (255, 255, 255))
        SCREEN.blit(text, ((SCREENWIDTH - text.get_width()) // 2, SCREENHEIGHT // 2))
        pygame.display.update()
        FPSCLOCK.tick(30)

def main_game():
    score = 0
    playerx = int(SCREENWIDTH / 5)
    playery = int(SCREENHEIGHT / 2)
    basex = 0

    newPipe1 = get_random_pipe()
    newPipe2 = get_random_pipe()

    upperPipes = [{'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
                  {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']}]
    lowerPipes = [{'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
                  {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']}]

    pipeVelX = -4
    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1
    playerFlapAccv = -8
    playerFlapped = False

    pipes_passed = []  # Track pipes passed for scoring sound

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if playery > 0:
                    playerVelY = playerFlapAccv
                    playerFlapped = True
                    # Stop wing sound before playing to avoid overlap
                    GAME_SOUNDS['wing'].stop()
                    GAME_SOUNDS['wing'].play()

        if is_collide(playerx, playery, upperPipes, lowerPipes):
            GAME_SOUNDS['hit'].play()
            GAME_SOUNDS['die'].play()
            return

        playerMidPos = playerx + GAME_SPRITES['player'].get_width() / 2
        for i, pipe in enumerate(upperPipes):
            pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4 and i not in pipes_passed:
                score += 1
                GAME_SOUNDS['point'].play()
                pipes_passed.append(i)

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False

        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)

        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        if 0 < upperPipes[0]['x'] < 5:
            newPipe = get_random_pipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)
            # Also remove from pipes_passed the earliest pipe (optional cleanup)
            if pipes_passed and pipes_passed[0] == 0:
                pipes_passed.pop(0)
            # Decrement all indices by 1 to stay synced with pipes list
            pipes_passed = [x - 1 for x in pipes_passed]

        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))

        myDigits = [int(x) for x in list(str(score))]
        width = sum(GAME_SPRITES['numbers'][digit].get_width() for digit in myDigits)
        Xoffset = (SCREENWIDTH - width) / 2
        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()

        pygame.display.update()
        FPSCLOCK.tick(32)

def is_collide(playerx, playery, upperPipes, lowerPipes):
    if playery > GROUNDY - 25 or playery < 0:
        return True
    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width():
            return True
    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y'] and
            abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            return True
    return False

def get_random_pipe():
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT / 3
    base_height = GAME_SPRITES['base'].get_height()
    max_height = SCREENHEIGHT - base_height - 1.2 * offset
    if max_height <= 0:
        max_height = 1

    y2 = offset + random.randrange(0, int(max_height))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    return [{'x': pipeX, 'y': -y1}, {'x': pipeX, 'y': y2}]

# Run the game
if __name__ == "__main__":
    load_assets()
    wait_for_enter()  # Show message: Press Enter to Start
    while True:
        main_game()
        wait_for_enter()
