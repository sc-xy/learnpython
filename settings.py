class Settings:
    """游戏画面的基础设置"""
    
    def __init__(self):
        self.screen_width = 1200
        self.screen_height = 750
        self.bg_color = (230, 230, 230)

        # 飞船设置
        self.ship_limit = 3

        # 子弹设置
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color = (60, 60, 60)
        self.bullet_allowed = 20

        # 外星人设置
        self.alien_drop_speed = 10
        self.alien_point = 50

        # 加快游戏节奏的速度
        self.speedup_scale = 1.1
        # 外星人分数提高速度
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """初始化随游戏进行而变化的设置。"""
        self.ship_speed = 1.5
        self.bullet_speed = 3.0
        self.alien_speed = 1.0

        # fleet_direction 为1表示向右，为-1表示向左
        self.fleet_direction = 1

    def increase_speed(self):
        """提高速度设置"""
        self.ship_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_point = int(self.alien_point * self.score_scale)