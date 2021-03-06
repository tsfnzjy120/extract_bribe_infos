# -*- coding:utf-8 -*-

import re

# path constant

# for paper_iterator() in parser.py
PAPER_NUMS = 20110
DATA_PATH = ""
# for endure_error() in parser_tools.py
ENDURE_ERROR = 'endure_error'
ENDURE_ERROR_PATH = 'endure_error.txt'
ENDURE_ERROR_PRINT = False
ENDURE_ERROR_WRITE = False
# for re_arrange_paper() in dynamic_paper.py
TRASH_PATH = ""

# regex constant
split_sentences = re.compile(r'[。！？]')
paper_mark_pattern = re.compile(r'书.+?号')  # for get_paper_mark() in pre_extract.py
# for paper_divider() in pre_extract.py
slzj_pattern = re.compile(r'审理终结。')
slcm_pattern = re.compile(r'[经本院]*审理查明[，：]*')
byrw_pattern = re.compile(r'本院认为[，：]?')
pjrx_pattern = re.compile(r'判[决处]如下：?')
spz_pattern = re.compile(r'审判[长员]：?')

special_court_pattern = re.compile(r'铁路|军事|海事|森林')  # for get_court_grade() in intro_info.py
change_to_normal_pattern = re.compile(r'(?:转|变更)为(?:适用)?普通程序')  # for get_tag_simple_procedure() in intro_info.py
designate_pattern = re.compile(r'指定.*?院管辖')  # for get_tag_designate() in intro_info.py
# for get_gongsu_infos in intro_info.py
p_name_pattern = re.compile(r'(.+?)以')
p_time_pattern = re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日')
crime_p_pattern = re.compile(r'犯(.+?)[，。于向一]')
change_sue_pattern = re.compile(r'变更|追加|撤销')

# for get_punish_infos() in penalty.py
crime_c_pattern = re.compile(r'犯.+?罪')
juyi_pattern = re.compile(r'拘役(.+?)个月')
tuxing_pattern = re.compile(r'有期徒刑(([一二三四五六七八九十]{1,2}年)?又?([一二三四五六七八九十]{1,2}个?月)?)')
tuxing_year_pattern = re.compile(r'([一二三四五六七八九十]{1,2})年')
tuxing_month_pattern = re.compile(r'([一二三四五六七八九十]{1,2})个?月')
fajin_pattern = re.compile(r'罚金(?:人民币)?(.+?)元')
moshou_pattern = re.compile(r'没收(?:个人)?财产(?:人民币)?(.+?)元')
boduo_pattern = re.compile(r'剥夺政治权利([一二三四五六七八九十])年')
huanxing_pattern = re.compile(r'缓[刑期](([一二三四五六七八九十]{1,2}年)?又?([一二三四五六七八九十]{1,2}个?月)?)')
# for get_punish_factors() in penalty.py
zishou_pattern = re.compile(r'自首')
ligong_pattern = re.compile(r'立功')
tanbai_pattern = re.compile(r'坦白|认罪|如实供述')
suohui_pattern = re.compile(r'索[贿要求取]')
tuizang_pattern = re.compile(r'退赃')
peihe_pattern = re.compile(r'配合')
shyx_pattern = re.compile(r'社会影响')
# for get_gongfan() in penalty.py
congfan_pattern = re.compile(r'[系是属为]从犯')
zhufan_pattern = re.compile(r'[系是属为]主犯')
zhucong_pattern = re.compile(r'不宜?区分主、?从犯')

# for get_defendant_infos() in defendant_info.py
d_name_pattern = re.compile(r'被告人(.+?)[，。（]')
d_volk_pattern = re.compile(r'(汉|壮|回|满|维吾尔|苗)族')
d_birthday_after_pattern = re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日出?生')
d_birthday_before_pattern = re.compile(r'生于(\d{4})年(\d{1,2})月(\d{1,2})日')
d_place_registered_a = re.compile(r'户籍(?:所在)?地(.+?)[，。]')  # 户籍(所在)地...
d_place_registered_b = re.compile(r'[日月年]出生于(.+?)[，]')  # 出生于...
d_place_registered_not_ren_before = re.compile(r'(被告|负责|代表|辩护|法|残疾|工|成年|证)人')  # for get_d_place_registered_ren() in defendant_info.py
d_place_registered_not_ren_after = re.compile(r'人[员大民事力]')  # for get_d_place_registered_ren() in defendant_info.py
d_place_current_not_zhu = re.compile(r'住[房宅建]')
d_place_current = re.compile(r'住所?地?(.+?)[。，]')
# for get_job_infos() in defendant_info.py
job_name_pattern_for_intro = re.compile(r'(?<![主责])[任系原](.+?)[，。；）]')
job_name_pattern_for_af = re.compile(r'(?<![主责时放到])[任](.+?)(?:期|至|以|职务|时|的|，|。|；|）)')
not_job_name_pattern = re.compile(r'任[职某命何免务用教由]')
# for get_lawyer_infos() in defendant_info.py
# for info_format.py
number_pattern = re.compile(r'\d')
brackets_pattern = re.compile(r'（.*?）')
format_job_name_pattern = re.compile(r'年|审判|律师|辩护|公诉')

# for fact_and_evidence.py
sum_pattern = re.compile(r'[币计款]([1-9][0-9.，万]{1,14})[元。]')
sum_total_pattern = re.compile(r'[合共总]')
duoci_pattern = re.compile(r'[多数屡]次')


# iterable constant

FIELD_DICT = {
	# 在此设置要素序号和要素名之间的对应关系
	# 比如：'paper_id': 0
}

PROVINCE_DICT = {
	'北京': 11, '天津': 12, '河北': 13, '山西': 14, '内蒙古': 15,
	'辽宁': 21, '吉林': 22, '黑龙江': 23,
	'上海': 31, '江苏': 32, '浙江': 33, '安徽': 34, '福建': 35, '江西': 36, '山东': 37,
	'河南': 41, '湖北': 42, '湖南': 43, '广东': 44, '广西': 45, '海南': 46,
	'重庆': 50, '四川': 51, '贵州': 52, '云南': 53, '西藏': 54,
	'陕西': 61, '甘肃': 62, '青海': 63, '宁夏': 64, '新疆': 65
}
VOLK_DICT = {
	'汉': 1, '壮': 8, '回': 3, '满': 11, '维吾尔': 5, '苗': 6
}

TIME_KEYWORD = (
	'零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '元', '冬', '腊'
)
TIME_YEAR_DICT = {
	'二零零一': '2001', '二零零二': '2002', '二零零三': '2003', '二零零四': '2004',
	'二零零五': '2005', '二零零六': '2006', '二零零七': '2007', '二零零八': '2008',
	'二零零九': '2009', '二零一零': '2010', '二零一一': '2011', '二零一二': '2012',
	'二零一三': '2013', '二零一四': '2014', '二零一五': '2015', '二零一六': '2016',
	'二零一七': '2017', '二零一八': '2018',
}
TIME_MONTH_DICT = {
	'一': '01', '二': '02', '三': '03', '四': '04', '五': '05', '六': '06',
	'七': '07', '八': '08', '九': '09', '十': '10', '十一': '11', '十二': '12',
	'元': '01', '冬': '11', '腊': '12'
}
TIME_DAY_DICT = {
	'一': '01', '二': '02', '三': '03', '四': '04', '五': '05',
	'六': '06', '七': '07', '八': '08', '九': '09', '十': '10',
	'十一': '11', '十二': '12', '十三': '13', '十四': '14', '十五': '15',
	'一十一': '11', '一十二': '12', '一十三': '13', '一十四': '14', '一十五': '15',
	'十六': '16', '十七': '17', '十八': '18', '十九': '19',
	'一十六': '16', '一十七': '17', '一十八': '18', '一十九': '19',
	'二十': '20', '二十一': '21', '二十二': '22', '二十三': '23', '二十四': '24', '二十五': '25',
	'二十六': '26', '二十七': '27', '二十八': '28', '二十九': '29', '三十': '30', '三十一': '31'
}

NUM_CHARS = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
SUM_CHARS = (
	'零', '一', '二', '三', '四', '五', '六', '七', '八', '九',
	'〇', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖', '幺', '两'
	'０', '１', '２', '３', '４', '５', '６', '７', '８', '９',
	'0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
	'十', '百', '千', '万', '亿', '拾', '佰', '仟', '萬', '億',
	'.'
)
CHINESE_ARABIC_MAP = {
	# 数字
	'零': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9,
	'〇': 0, '壹': 1, '贰': 2, '叁': 3, '肆': 4, '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9,
	'幺': 1, '两': 2,
	'０': 0, '１': 1, '２': 2, '３': 3, '４': 4, '５': 5, '６': 6, '７': 7, '８': 8, '９': 9,
	'0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
	# 单位
	'十': 10, '百': 10**2, '千': 10**3, '万': 10**4, '亿': 10**8,
	'拾': 10, '佰': 10**2, '仟': 10**3, '萬': 10**4, '億': 10**8,
}


CRIME_DICT = {
	'职务侵占罪': 271, '贪污罪': 382, '挪用公款罪': 384, '受贿罪': 385,
	'利用影响力受贿罪': 388, '行贿罪': 389, '介绍贿赂罪': 392, '巨额财产来源不明罪': 395,
	'私分国有财产罪': 396, '玩忽职守罪': 397, '滥用职权罪': 397,
}


REGION_GRADE_RANKED = (
	'中国', '全国', '中央',
	'省', '自治区', '北京市', '天津市', '上海市', '重庆市',
	'广州市', '武汉市', '哈尔滨市', '沈阳市', '成都市', '南京市', '西安市',
	'长春市', '济南市', '杭州市', '大连市', '青岛市', '深圳市', '厦门市', '宁波市',
	'盟', '州', '市', '区', '县', '旗',  # 区在3级最前面
	'镇', '乡', '街道', '苏木', '公所',
	'村',
)

REGION_GRADE_DICT = {
	'中国': 5, '全国': 5, '中央': 5,  # 中央需特别处理
	'省': 4, '自治区': 4, '北京市': 4, '天津市': 4, '上海市': 4, '重庆市': 4,
	'广州市': 4, '武汉市': 4, '哈尔滨市': 4, '沈阳市': 4, '成都市': 4, '南京市': 4, '西安市': 4,
	'长春市': 4, '济南市': 4, '杭州市': 4, '大连市': 4, '青岛市': 4, '深圳市': 4, '厦门市': 4, '宁波市': 4,
	'盟': 3, '州': 3, '市': 3, '区': 2, '县': 2, '旗': 2,  # 市、区需特殊处理
	'镇': 1, '乡': 1, '街道': 1, '苏木': 1, '公所': 1,
	'村': 0,
}


JOB_DOMAIN_POS_RANKED = (
	# 军队-0
	'军',
	# 群众自治组织-1
	'村民', '村委', '居民', '居委',
	# 公检法司-2
	'公安', '法院', '检察院', '司法', '执法', '监狱', '派出所', '看守所', '拘留所',
	# 人大、政协-3
	'政协', '政治协商', '人大', '人民代表',
	# 国有企业-4
	'公司', '厂', '银行', '供电',
	# 事业单位、人民团体-5
	'中心', '所', '站', '大队', '院', '学', '馆',
	'报社', '电台', '电视台', '库', '幼儿园',
	# 行政机关-6
	'局', '厅', '司', '处', '科', '政府', '领导小组', '街道办', '管理', '管委会', '监督',
	'计生', '卫计', '计划生育', '发改委', '发展和改革', '海关',
	# 党的部门-7
	'中共', '党', '总支', '支部', '省委', '市委', '县委', '区委', '地委', '州委',
	'纪委', '纪律检查', '组织', '宣传', '统战', '工委', '武装',
)

JOB_DOMAIN_POS_DICT = {
	# 军队-0
	'军': 0,
	# 群众自治组织-1
	'村民': 1, '村委': 1, '居民': 1, '居委': 1,
	# 公检法司-2
	'公安': 2, '法院': 2, '检察院': 2, '司法': 2, '执法': 2, '监狱': 2, '派出所': 2, '看守所': 2, '拘留所': 2,
	# 人大、政协-3
	'政协': 3, '政治协商': 3, '人大': 3, '人民代表': 3,
	# 国有企业-4
	'公司': 4, '厂': 4, '银行': 4, '供电': 4,
	# 事业单位、人民团体-5
	'中心': 5, '所': 5, '站': 5, '大队': 5, '院': 5, '学': 5, '馆': 5,
	'报社': 5, '电台': 5, '电视台': 5, '库': 5, '幼儿园': 5,
	# 行政机关-6
	'局': 6, '厅': 6, '司': 6, '处': 6, '科': 6, '政府': 6, '领导小组': 6,
	'街道办': 6, '管理': 6, '管委会': 6, '监督': 6,
	'计生': 6, '卫计': 6, '计划生育': 6, '发改委': 6, '发展和改革': 6, '海关': 6,
	# 党的部门-7
	'中共': 7, '党': 7, '总支': 7, '支部': 7,
	'省委': 7, '市委': 7, '县委': 7, '区委': 7, '地委': 7, '州委': 7,
	'纪委': 7, '纪律检查': 7, '组织': 7, '宣传': 7, '统战': 7, '工委': 7, '武装': 7,
}

JOB_DOMAIN_TITLE_DICT = {
	# 军队-0
	'司令': 0, '指挥': 0, '参谋': 0, '政委': 0, '排长': 0, '连长': 0, '营长': 0, '团长': 0,
	'旅长': 0, '师长': 0,
	# 群众自治组织-1
	'村': 1,
	# 公检法司-2
	'法官': 2, '书记员': 2, '法警': 2, '检察官': 2,
	'警察': 2, '民警': 2, '刑警': 2, '交警': 2, '狱警': 2, '协警': 2, '协勤': 2,
	# 国有企业-4
	'经理': 4, '董事': 4, '监事': 4, '行长': 4, '法人': 4, '法定代表人': 4,
	# 行政机关-6
	'省长': 6, '市长': 6, '县长': 6, '乡长': 6, '镇长': 6, '股长': 6,
	'股员': 6, '办事员': 6, '调研员': 6, '巡视员': 6, '秘书长': 6, '公务员': 6,
	'协管': 6,
	# 党的部门-7
	'书记': 7, '常委': 7,
}

JOB_GRADE_TITLE_DICT = {
	# 国家级-5
	'总书记': 5, '政治局': 5, '总理': 5, '军事委员会': 5,
	# 省部级-4
	'省委书记': 4, '省长': 4, '军长': 4, '司令': 4,
	# 厅局级-3
	'司长': 3, '厅长': 3, '巡视员': 3, '师长': 3, '旅长': 3,
	# 县处级-2
	'县长': 2, '县委书记': 2, '处长': 2, '调研员': 2, '团长': 2,
	# 乡科级-1
	'镇党委书记': 1, '镇长': 1, '乡党委书记': 1, '乡长': 1, '科长': 1, '科员': 1, '营长': 1,
	# 乡科级以下-0
	'股长': 0, '股员': 0, '办事员': 0, '排长': 0,
	'警察': 0, '民警': 0, '刑警': 0, '交警': 0, '狱警': 0, '协警': 0, '协勤': 0, '协管': 0,
	'管理员': 0, '干警': 0,
}

JOB_GRADE_REVISE = {
	'村': -3, '员工': -3, '人大代表': -3,
	'科': -2, '处': -2, '警': -2, '人员': -2, '负责人': -2, '队长': -2, '厂长': -2, '站长': -2, '所长': -2,
	'室': -1, '庭': -1, '主任': -1, '经理': -1, '行长': -1, '法人代表': -1, '法定代表': -1,
	'秘书长': -1, '校长': -1, '院长': -1, '社长': -1, '台长': -1, '园长': -1,
}

