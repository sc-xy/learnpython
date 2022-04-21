import sys
from time import sleep
import pygame
import json

from settings import Settings
from game_stasts import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """管理游戏资源和行为的类"""

    def __init__(self):
        """初始化游戏并创建游戏资源"""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        self.filename = 'data.json'
        self.stats = GameStats(self)
        self._load_data()
        self.sb = Scoreboard(self)

        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()  # 类似列表的编组
        self.aliens = pygame.sprite.Group()  # 类似列表的编组

        self._create_fleet()
        self.play_button = Button(self, "Play")
        
    def _load_data(self):
        try:
            with open(self.filename) as f:
                tmp = json.load(f)
        except FileNotFoundError:
            pass
        else:
            tmp_int = int(tmp)
            self.stats.high_score = tmp_int

    def ship_hit(self):
        if self.stats.ship_left > 0:
            self.stats.ship_left -= 1
            self.sb.prep_ships()
            self.aliens.empty()
            self.bullets.empty()
            self._create_fleet()
            self.ship.center_ship()

            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _load_high_score(self):
        try:
            with open(self.filename) as f:
                tmp_str = json.load(f)
                tmp = int(tmp_str)
        except FileNotFoundError:
            to_beload = self.stats.high_score
            to_beload_str = str(to_beload)
            with open(self.filename, 'w') as f:
                json.dump(to_beload_str, f)                
        else:
            high_score = self.stats.high_score
            if tmp < high_score:
                tmp_str = str(high_score)
                with open(self.filename, 'w') as f:
                    json.dump(tmp_str, f)
        
    def _check_aliens_bottom(self):
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self.ship_hit()
                break

    def _create_fleet(self):
        """创建外星人群"""
        # 创建一个外星人，并判断一行最多多少外星人
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # 计算屏幕可容纳多少行外星人
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)
        # 创建外星人群
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """创建一个外星人并把它放在当前行"""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien_height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """检测有无外星人触碰边界并做出相应措施"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """整群外星人下移，并改变他们的方向"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.alien_drop_speed
        self.settings.fleet_direction *= -1

    def _fire_bullte(self):
        """创建一颗新子弹，并将其加入编组bulltes中"""
        if len(self.bullets) < self.settings.bullet_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
    
    def _update_bulltes(self):
        """更新子弹位置并删除界外子弹"""
        self.bullets.update() # 编组会对每一个成员执行其内部定义的update方法
        for bullet in self.bullets.copy():
            if bullet.rect.y <= 0:
                self.bullets.remove(bullet)
        self._check_alien_collisions()
    
    def _check_alien_collisions(self):
        """响应子弹和外星人碰撞"""
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_point * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
        if not self.aliens:
            # 如果一个外星人群已经被清除，删除现有子弹并创建一群外星人
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # 提升等级
            self.stats.level += 1
            self.sb.prep_level()

    def _check_events(self):
        # 监视键盘和鼠标事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._load_high_score()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_play_button(self, mouse_pos):
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self._start_game()

    def _start_game(self):
        """开始游戏"""
        self.stats.game_active = True
        # 重置游戏统计信息
        self.settings.initialize_dynamic_settings()
        self.stats.reset_stats()
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()

        # 清空余下的外星人和子弹
        self.aliens.empty()
        self.bullets.empty()

        # 创建一群外星人并让飞船居中
        self._create_fleet()
        self.ship.center_ship()

        # 隐藏鼠标光标
        pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """响应按键"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            self._load_high_score()
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullte()
        elif event.key == pygame.K_p:
            self._start_game()
            
    def _check_keyup_events(self, event):
        """响应松开"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _update_screen(self):
        # 每次循环时都重绘屏幕
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme() # 绘制飞船
        for bullet in self.bullets.sprites(): # 绘制子弹
            bullet.draw_bullet()
        self.aliens.draw(self.screen) # 绘制外星人
        # 之所以绘制外星人直接调用 aliens.draw 而子弹使用for循环调用
        # 因为draw对每一个编组成员需要一个self.image实参（在超类sprite初始化时都初始化了
        # 但是bullet的image是空的，无法调用
        self.sb.show_score()

        # 让最近绘制的屏幕可见
        if not self.stats.game_active:
            self.play_button.draw_button()
        pygame.display.flip()

    def _update_aliens(self):
        """更新所有外星人位置"""
        self._check_fleet_edges()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self.ship_hit()
        self._check_aliens_bottom()

    def run_game(self):
        """开始游戏的主循环"""
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bulltes()
                self._update_aliens()
            self._update_screen()        
            
if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()