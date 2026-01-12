from localize import lang

class SkillDamageInfo:
    def __init__(self):
        self.damage = []
        self.damage_by_multiplier_type = {}
        self.total_damage = 0
        self.average = 0


class DamageCalculator:
    def __init__(self, language):
        self.language = language
        self.langset = lang.get(language)
        self.total_damage = 0

        self.first_timestamp_ms = 0
        self.last_timestamp_ms = 0
        self.time_passed_from_start_ms = 0
        self.average_per_time = 0
        self.moving_average = 0

        self.damage_data = []
        self.by_skills = {}


    def process_damage(self, damage_list, now):
        # data will be cutted by moving average window further
        self.damage_data += damage_list

        if self.first_timestamp_ms == 0:
            self.first_timestamp_ms = now
        self.time_passed_from_start_ms = now - self.first_timestamp_ms

        for damage_info in damage_list:
            self.total_damage += damage_info.damage

            if damage_info.skill_name not in self.by_skills:
                self.by_skills[damage_info.skill_name] = SkillDamageInfo()
            skill_damage_info = self.by_skills[damage_info.skill_name]
            skill_damage_info.damage.append(damage_info.damage)
            skill_damage_info.total_damage += damage_info.damage
            skill_damage_info.average = skill_damage_info.total_damage / len(skill_damage_info.damage)

            # do not take additional damage into account
            if damage_info.skill_name != self.langset['str_additional_damage']:
                if damage_info.multiplier_type not in skill_damage_info.damage_by_multiplier_type:
                    skill_damage_info.damage_by_multiplier_type[damage_info.multiplier_type] = {
                        "damage": [],
                        "total_damage": 0
                    }
                multiplier_type_damage_info = skill_damage_info.damage_by_multiplier_type[damage_info.multiplier_type]
                multiplier_type_damage_info["damage"].append(damage_info.damage)
                multiplier_type_damage_info["total_damage"] += damage_info.damage

        time_passed_from_start_sec = self.time_passed_from_start_ms / 1000
        self.average_per_time = (self.total_damage / time_passed_from_start_sec) if time_passed_from_start_sec != 0 else 0
        self.moving_average = self._moving_average_by_time(now)
        self.last_timestamp_ms = now

        print("=", now, " total:", self.total_damage, "dps:", round(self.moving_average, 2), "avg:", round(self.average_per_time, 2))


    def _moving_average_by_time(self, now, window_ms=1000):
        self.damage_data = [d for d in self.damage_data if d.timestamp >= now - window_ms]

        window_size = len(self.damage_data)
        if window_size == 0:
            return 0

        total_damage = sum(d.damage for d in self.damage_data)
        return total_damage