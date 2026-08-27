import pygame

def scale_image(img, factor): 
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)

def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = top_left).center)
    win.blit(rotated_image, new_rect.topleft)

def rotated_car(player_car):
    rotated_image = pygame.transform.rotate(player_car.img, player_car.angle)
    rect = rotated_image.get_rect(center=player_car.img.get_rect(topleft=(player_car.x, player_car.y)).center)
    return rotated_image, rect