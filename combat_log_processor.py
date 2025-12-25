import re

from pathlib import Path

from utils import fuzzy_string_match, format_timestamp


class ParserConfig:
    def __init__(self, pattern, skill_name_group=-1, target_name_group=-1, damage_group=-1, multiplier_type_group=-1):
        self.pattern = pattern
        self.skill_name_group = skill_name_group
        self.target_name_group = target_name_group
        self.damage_group = damage_group
        self.multiplier_type_group = multiplier_type_group


damage_pattern = re.compile(r"Used (.*?) against (.*?) and dealt ([0-9]+[0-9.]*) (\[?Perfect]?|\[?Critical]?|\[?Smite]?|\[?Double Critical]?|\[?Perfect Critical]?|) *damage.")
additional_damage_pattern = re.compile(r"Dealt additional damage of ([0-9]+[0-9.]*) to (.*).")

damage_matches = [
    ParserConfig(pattern=damage_pattern, skill_name_group=1, target_name_group=2, damage_group=3, multiplier_type_group=4),
    ParserConfig(pattern=additional_damage_pattern, damage_group=1, target_name_group=2),
]

class DamageInfo:
    def __init__(self, timestamp, skill_name, target_name, damage, multiplier_type):
        self.timestamp = timestamp
        self.skill_name = skill_name
        self.target_name = target_name
        self.damage = damage
        self.multiplier_type = multiplier_type


class CombatLogParser:
    def __init__(self):
        self.prev_logs = []
        self.damage_log = False
        self.show_ignored = False
        self.save_combat_log = False
        self.log_file_path = Path("./logs/combat_log.log")
        self.log_file_path.parent.mkdir(exist_ok=True, parents=True)


    def set_debug(self, damage_log, show_ignored):
        self.damage_log = damage_log
        self.show_ignored = show_ignored


    def set_write_log(self, save_log):
        self.save_combat_log = save_log

    def _save_logs_to_file(self, logs, timestamp):
        try:
            formatted_time = format_timestamp(timestamp)
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                for log in logs:
                    f.write(f"[{formatted_time}] {log}\n")
        except Exception as e:
            print(f"Error saving combat log: {e}")



    def parse_combat_log(self, text, timestamp, seq_id):
        text = self._preprocess_text(text)
        damage_list = self._get_new_damage(text, timestamp)
        return damage_list


    def _preprocess_text(self, text):
        entries = []
        for entry in text.split(".\n")[1:-1]: # ignore first and last to avoid half parsed lines
            entry = entry.replace("\n", " ")
            entry = entry.strip()
            if entry == "":
                continue
            entry = entry + "."
            entries.append(entry)
        return entries


    def _detect_new_logs(self, logs):
        if len(logs) == 0 or len(self.prev_logs) == 0:
            self.prev_logs = logs
            return logs

        # find anchor in current logs
        anchor = []
        anchor_cur_end_pos = 0
        if len(logs) < 2:
            anchor = logs
        else:
            # find anchor/pattern
            for i in range(1, len(logs)):
                if not fuzzy_string_match(logs[i - 1], logs[i], 6):
                    anchor.append(logs[i - 1])
                    anchor.append(logs[i])
                    anchor_cur_end_pos = i + 1
                    break
        if len(anchor) == 0:
            anchor = logs[:2]

        if len(self.prev_logs) < len(anchor):
            return logs

        # find the same anchor in prev_logs
        anchor_prev_found = False
        anchor_prev_end_pos = len(self.prev_logs)
        for i in range(0, len(self.prev_logs) - 1):
            if fuzzy_string_match(self.prev_logs[i], anchor[0]):
                if len(anchor) == 1:
                    anchor_prev_end_pos = i + 1
                    anchor_prev_found = True
                    break
                if fuzzy_string_match(self.prev_logs[i + 1], anchor[1]):
                    anchor_prev_end_pos = i + 2
                    anchor_prev_found = True
                    break

        # calc equal pos count and then remove from incoming logs
        same_length = len(self.prev_logs) - anchor_prev_end_pos
        result = logs[anchor_cur_end_pos + same_length:] if anchor_prev_found else logs

        self.prev_logs = logs

        return result


    def _filter_damage(self, logs, timestamp):
        result = []
        for log in logs:
            matched = False
            for match in damage_matches:
                m = match.pattern.search(log)
                if m:
                    result.append(DamageInfo(
                        timestamp=timestamp,
                        skill_name=m.group(match.skill_name_group) if match.skill_name_group > 0 else "Additional Damage",
                        target_name=m.group(match.target_name_group) if match.target_name_group > 0 else "",
                        damage=int(m.group(match.damage_group).replace(".", "")) if match.damage_group > 0 else 0,
                        multiplier_type=m.group(match.multiplier_type_group) if match.multiplier_type_group > 0 else "",
                    ))
                    matched = True
                    break
            if self.show_ignored and not matched:
                print("-", log)
        return result


    def _get_new_damage(self, logs, timestamp):
        new_logs = self._detect_new_logs(logs)
        if len(new_logs) != 0:
            if self.save_combat_log:
                self._save_logs_to_file(new_logs, timestamp)


        damage = self._filter_damage(new_logs, timestamp)
        if len(damage) != 0 and self.damage_log:
            for dmg in damage:
                print(">", dmg.timestamp, ": To", dmg.target_name, dmg.skill_name, dmg.multiplier_type, dmg.damage)

        return damage
