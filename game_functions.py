import sys
import pygame
from bullet import Bullet
from alien import Alien
from time import sleep


def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            check_keydown_events(event, ai_settings, stats, sb, screen, ship, aliens, bullets)
        elif event.type == pygame.KEYUP:
            check_keyup_events(event, ai_settings, stats, screen, ship, bullets)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y)
            if stats.game_active:
                fire_bullet(ai_settings, screen, ship, bullets)


def check_keydown_events (event, ai_settings, stats, sb, screen, ship, aliens, bullets):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = True
    elif event.key == pygame.K_d:
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        ship.moving_left = True
    elif event.key == pygame.K_a:
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
        ship.charging_gun = True
    elif event.key == pygame.K_q:
        with open(ai_settings.high_score_filename, 'w' ) as score_store:
            score_store.write(str(stats.high_score))
        sys.exit()
    elif event.key == pygame.K_p:
        if not stats.game_active:
            start_game(ai_settings, screen, stats, sb, ship, aliens, bullets)


def check_keyup_events (event, ai_settings, stats, screen, ship, bullets):
    if event.key == pygame.K_RIGHT:
        ship.moving_right = False
    elif event.key == pygame.K_d:
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        ship.moving_left = False
    elif event.key == pygame.K_a:
        ship.moving_left = False
    elif event.key == pygame.K_SPACE and stats.game_active:
        ship.charging_gun = False
        if ship.gun_charge > ship.charge_limit:
            ship.gun_charged = True
            fire_charged_bullet(ai_settings, screen, ship, bullets)
            ship.gun_charge = 0
        else:
            ship.gun_charge = 0


def check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y):
    button_clicked =  play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_clicked and not stats.game_active:
        start_game(ai_settings, screen, stats, sb, ship, aliens, bullets)


def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button):
    screen.fill(ai_settings.bg_color)
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)
    sb.show_score()
    if not stats.game_active:
        play_button.draw_button()
        
    pygame.display.flip()


def update_ship(ai_settings, ship):
    if ship.moving_right and ship.rect.right < ship.screen_rect.right:
        ship.center += ship.ai_settings.ship_speed_factor

    if ship.moving_left and ship.rect.left > 0:
        ship.center -= ship.ai_settings.ship_speed_factor

    if ship.charging_gun:
        ship.gun_charge += ai_settings.charge_speed
        if ship.gun_charge > ship.charge_limit:
            print("CANNONS CHARGED!!!!!!")
    ship.rect.centerx = ship.center


def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    bullets.update()
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)

    check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets)


def fire_bullet(ai_settings, screen, ship, bullets):
    if len(bullets) < ai_settings.bullets_allowed:
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def fire_charged_bullet(ai_settings, screen, ship, bullets):
    new_bullet = Bullet(ai_settings, screen, ship)
    new_bullet.charged_shot = True
    new_bullet.color = ai_settings.charged_bullet_color
    bullets.add(new_bullet)
    ship.gun_charged = False


def create_fleet(ai_settings, screen, ship, aliens):
    alien = Alien(ai_settings,screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)
    for row_number in range(number_rows):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number, row_number)


def get_number_aliens_x(ai_settings, alien_width):
    available_space_x = ai_settings.screen_width - 2 * alien_width
    number_aliens_x = int(available_space_x / (2 *alien_width))
    return number_aliens_x


def get_number_rows(ai_settings, ship_height, alien_height):
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)


def update_aliens(ai_settings, stats, sb, screen, ship, aliens, bullets):
    check_fleet_edges(ai_settings, aliens)
    aliens.update()
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets)
    
    check_aliens_bottom(ai_settings, stats, sb, screen, ship, aliens, bullets)


def check_fleet_edges(ai_settings, aliens):
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.alien_drop_speed
    ai_settings.fleet_direction *= -1


def check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets):
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)

    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(stats, sb)
    if len(aliens) == 0:
        start_new_level(ai_settings, screen, stats, sb, ship, aliens, bullets)


def start_new_level(ai_settings, screen, stats, sb, ship, aliens, bullets):
    bullets.empty()
    ai_settings.increase_speed()
    create_fleet(ai_settings, screen, ship, aliens)
    stats.level += 1
    sb.prep_level()


def ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets):
    if stats.ships_left > 0:
        stats.ships_left -= 1
    
        aliens.empty()
        bullets.empty()
    
        sb.prep_ships()
        
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()
        sleep(0.5)
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)


def check_aliens_bottom(ai_settings, stats, sb, screen, ship, aliens, bullets):
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets)
            break


def start_game(ai_settings, screen, stats, sb, ship, aliens, bullets):
        ai_settings.initialize_dynamic_settings()
        pygame.mouse.set_visible(False)
        stats.reset_stats()
        stats.game_active = True    

        aliens.empty()
        bullets.empty()
    
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()
        sb.prep_hud()


def check_high_score(stats, sb):
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()