lang = {
    'en': {
        #Pattern recognition section
        'ocr_lang': 'eng',
        'damage_pattern': r"Used (.*?) against (.*?) and dealt ([0-9]+[0-9.]*) (\[?Perfect]?|\[?Critical]?|\[?Smite]?|\[?Double Critical]?|\[?Perfect Critical]?|) *damage.",
        'damage_pattern_groups': dict(skill_name_group=1, target_name_group=2, damage_group=3, multiplier_type_group=4),
        'additional_damage_pattern': r"Dealt additional damage of ([0-9]+[0-9.]*) to (.*).",
        'additional_damage_pattern_groups': dict(damage_group=1, target_name_group=2),
        #Additional localization strings section
        'str_additional_damage': "Additional Damage",
        'str_normal': "Normal",
        #Plot localization strings sections
        "str_xlabel": 'Time (sec)',
        "str_ylabel": 'Damage',
        "str_header": 'Damage Per Second',
        "str_skills_header": 'Skills Statistics',
        "str_skills_cols": ['Skill Name', 'Count', 'Total', 'Average'],
        'str_no_data_skill': 'No skill data available yet',
        "str_hittypes_header": 'Hit Types',
        "str_hittypes_cols": ['Type', 'Count', 'Percentage'],
        'str_no_data_mult': 'No multiplier data available yet',
        'str_moving_avg': 'Moving Average',
        'str_avg': 'Average',
        
    },
    'ko': {
        'ocr_lang': 'kor',
        'damage_pattern': r"(.*?)에게 (.*?)[을를] 사용해 (\[?완벽]?|\[?치명타]?|\[?강타]?|\[?강타 치명타]?|\[?완벽 치명타]?|)([0-9]+[0-9.]*) *의 대미지를 줬습니다.",
        'damage_pattern_groups': dict(target_name_group=1, skill_name_group=2,multiplier_type_group=3, damage_group=4),
        'additional_damage_pattern': r"(.*)에게 ([0-9]+[0-9.]*)의 추가 대미지를 줬습니다.",
        'additional_damage_pattern_groups': dict(target_name_group=1, damage_group=2),
        'str_additional_damage': "추가 대미지",
        'str_normal': "일반",
        "str_xlabel": '시간 (초)',
        "str_ylabel": '데미지',
        "str_header": '초당 데미지(DPS)',
        "str_skills_header": '스킬 통계',
        "str_skills_cols": ['스킬 이름', '횟수', '총합', '평균'],
        'str_no_data_skill': '스킬 데이터가 아직 없습니다',
        "str_hittypes_header": '타격 유형',
        "str_hittypes_cols": ['유형', '횟수', '비율'],
        'str_no_data_mult': '배율 데이터가 아직 없습니다',
        'str_moving_avg': '이동 평균',
        'str_avg': '평균',
        
    }
}