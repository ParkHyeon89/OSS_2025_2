    def draw_result_overlay(self, text):
        if not text:
            return
        # 화면 어둡게
        overlay = pygame.Surface((config.width, config.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, config.result_overlay_alpha))
        self.screen.blit(overlay, (0, 0))
        # 큰 결과 텍스트 (GAME CLEAR / GAME OVER)
        label = self.result_font.render(text, True, config.color_result)
        rect = label.get_rect(center=(config.width // 2, config.height // 2))
        self.screen.blit(label, rect)
        # HighScore 텍스트 (노란색으로!)
        if text == "GAME CLEAR" and self.highscore is not None:
            hs = self.highscore
            mm = int(hs // 60)
            ss = int(hs % 60)
            score_text = f"High Score: {mm:02}m {ss:02}s"
            sub_label = self.font.render(score_text, True, config.color_result)  # ← 색 변경!
            sub_rect = sub_label.get_rect(
                center=(config.width // 2, (config.height // 2) + 45)
            )
            self.screen.blit(sub_label, sub_rect)