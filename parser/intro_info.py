# -*- coding:utf-8 -*-

# 案件基本信息部分

import re
import extract_bribe_infos.tools as tools
import extract_bribe_infos.constant as constant
import extract_bribe_infos.info_format as info_format
from extract_bribe_infos.parser.pre_extract import paper_dict_generator
from extract_bribe_infos.excel_output import output_to_excel


EXCEL_TAG = False  # 提取之后是否直接输出
PAPER_DICT_KEYS = ['paper_id', 'head', 'intro', 'judges_info']


def get_court_grade(court_name):
	"""
	get court_grade from court_name
	:param court_name: <str> court_name
	:return: <int> court_grade
	"""
	court_grade = 0
	if constant.special_court_pattern.search(court_name):
		court_grade = 4
	elif '中级' in court_name:
		court_grade = 1
	elif '高级' in court_name:
		court_grade = 2
	elif '最高' in court_name:
		court_grade = 3

	return court_grade


def get_court_location(court_name):
	"""
	get court_location from court_name
	:param court_name: <str> court_name
	:return: <str> court_location
	"""
	court_loation = re.sub(r'中级|高级|最高|人民法院|铁路运输法院|军事法院|海事法院|森林法院', '', court_name)

	return court_loation


# 算法修改中，暂不可用
def get_court_location_label():
	"""
	get court_location_label from court_location
	:return: <int> court_location_label
	"""
	pass

	return 0


def get_court_info(head):
	"""
	get court_name, court_grade, court_location, court_location_label
	:param head: <str> paper_head
	:return: <dict> court_info {court_name, court_grade, court_location, court_location_label}
	"""
	# 寻找法院名称信息
	xspjs_id = head.index('刑事判决书')
	court_in_head = head[:xspjs_id]
	court_name = info_format.court_name_format(court_in_head)
	# 寻找法院级别信息
	court_grade = get_court_grade(court_name)
	# 寻找法院所在地信息
	court_location = get_court_location(court_name)
	court_location_label = get_court_location_label()
	# 组合court_info字典
	court_info = {
		'court_name': court_name,
		'court_grade': court_grade,
		'court_location': court_location,
		'court_location_label': court_location_label,
	}

	return court_info


def get_tag_simple_procedure(intro):
	"""
	get_tag_simple_procedure
	:param intro: <str> paper_into
	:return: <int> tag_simple_procedure
	"""
	tag_simple_procedure = 0
	if '适用简易程序' in intro or '独任审判' in intro:
		if not constant.change_to_normal_pattern.search(intro):
			tag_simple_procedure = 1

	return tag_simple_procedure


def get_tag_designate(intro):
	"""
	get tag_designate
	:param intro: <str> paper_intro
	:return: <int> tag_designate
	"""
	tag_designate = 0
	if constant.designate_pattern.search(intro):
		tag_designate = 1

	return tag_designate


def get_tag_delay(intro):
	"""
	get tag_delay
	:param intro: <str> paper_intro
	:return: <int> tag_delay
	"""
	tag_delay = 0
	if '延长审理'in intro or '延期审理' in intro:
		tag_delay = 1

	return tag_delay


def get_tag_investi_plus(intro):
	"""
	get tag_investi_plus
	:param intro: <str> paper_intro
	:return: <int> tag_investi_plus
	"""
	tag_investi_plus = 0
	if '补充侦查' in intro:
		tag_investi_plus = 1

	return tag_investi_plus


# 算法修改中，暂不可用
def get_judge_names_list():
	"""
	get judge_names_list from judges_info
	:return: <list> judge_names_list [name1, name2, ... ] or []
	"""
	pass

	return []


# 算法修改中，暂不可用
def get_judge_time():
	"""
	get judge_time from judges_info
	:return: <str> judge_time YYYY-MM-DD or constant.ENDURE_ERROR
	"""
	pass

	return ''


# 算法修改中，暂不可用
def get_tag_juror():
	"""
	get tag_juror from judges_info
	:return: <int> number of jurors
	"""
	pass

	return 0


# 算法修改中，暂不可用
def get_judges_info(judges_info):
	"""
	get chief_judge_name, judge_names, judge_time, tag_juror
	:param judges_info: <str> paper_judges_info
	:param segmentor <pyltp.Segmentor()> ltp_api
	:param postagger <pyltp.Postagger()> ltp_api
	:return: <dict> judges_info_dict {chief_judge_name: '', judge_names: '', judge_time: '', tag_juror: 0}
	"""
	# 除去附件信息
	end_index = judges_info.find('书记员')
	judges_info = judges_info[:end_index]
	# 格式化'零' + 除去标点
	judges_info = tools.remove_punctuation(judges_info.replace('Ｏ', '零').replace('０', '零'))
	judges_info_dict = {
		'chief_judge_name': constant.ENDURE_ERROR,
		'judge_names': constant.ENDURE_ERROR,
		'judge_time': constant.ENDURE_ERROR,
		'tag_juror': 0,
	}
	# 寻找姓名
	judge_names_list = get_judge_names_list()
	if len(judge_names_list) > 0:
		judges_info_dict['chief_judge_name'] = judge_names_list[0]
		judges_info_dict['judge_names'] = '+'.join(judge_names_list)
	# 寻找时间
	judges_info_dict['judge_time'] = get_judge_time()
	# 陪审员标志
	judges_info_dict['tag_juror'] = get_tag_juror()

	return judges_info_dict


def get_procuratorate_name(gongsu_sentence):
	"""
	get prosecute_time from gongsu_sentence
	:param intro: <str> gongsu_sentence
	:return: <str> procuratorate_name
	"""
	p_name = ''
	p_name_match = constant.p_name_pattern.search(gongsu_sentence)
	if p_name_match:
		p_name = p_name_match.group(1)

	return info_format.p_name_format(p_name)


def get_prosecute_time(gongsu_sentence):
	"""
	get prosecute_time from gongsu_sentence
	:param gongsu_sentence: <str> gongsu_sentence
	:return: <str> YYYY-MM-DD
	"""
	p_time = ''
	p_time_match = constant.p_time_pattern.search(gongsu_sentence)
	if p_time_match:
		year = p_time_match.group(1)
		month = p_time_match.group(2)
		day = p_time_match.group(3)
		p_time = info_format.birth_time_format(year, month, day)

	return p_time


def get_crime_p(gongsu_sentence):
	"""
	get prosecute_time from gongsu_sentence
	:param gongsu_sentence: <str> gongsu_sentence
	:return: <int> crime_p(385)
	"""
	crime_p_str = ''
	crime_p_match = constant.crime_p_pattern.search(gongsu_sentence)
	if crime_p_match:
		crime_p_list = crime_p_match.group(1).split('、')
		for cp in crime_p_list:
			if '罪' not in cp:
				continue
			else:
				crime_p_str += '{0}+'.format(constant.CRIME_DICT.get(cp, 999))

	return crime_p_str[:-1]


def get_tag_change_sue(intro):
	"""
	get tag_change_sue from paper_intro
	:param intro: <str> paper_intro
	:return: <int> 0 for no, 1 for yes
	"""
	tag_change_sue = 0
	if constant.change_sue_pattern.search(intro):
		tag_change_sue = 1

	return tag_change_sue


def get_gongsu_infos(intro):
	"""
	get gongsu_infos from paper_intro
	:param intro: <str> paper_intro
	:return: <dict> gongsu_infos {
		procuratorate_name: '', prosecute_time: '', crime_p: '', tag_change_sue: 0
	}
	"""
	gongsu_sentence = ''
	# 定位公诉语句gongsu_sentence
	intro_sentences = tools.cut_into_sentences(intro)
	for sentence in intro_sentences:
		if '提起公诉' in sentence:
			gongsu_sentence = sentence
			break
	# 组合gongsu_infos字典
	gongsu_infos = {
		'procuratorate_name': get_procuratorate_name(gongsu_sentence),
		'prosecute_time': get_prosecute_time(gongsu_sentence),
		'crime_p': get_crime_p(gongsu_sentence),
		'tag_change_sue': get_tag_change_sue(intro)
	}

	return gongsu_infos


def intro_info_main():
	"""
	test every def in intro_info.py
	:return: <int> 0
	"""
	with tools.ExcelContext(EXCEL_TAG) as ec:

		for paper_dict in paper_dict_generator(PAPER_DICT_KEYS):

			if len(paper_dict) == 1:
				continue

			paper_id = paper_dict['paper_id']
			paper_head = paper_dict.get('head', constant.ENDURE_ERROR)
			paper_intro = paper_dict.get('intro', constant.ENDURE_ERROR)
			paper_judges_info = paper_dict.get('judges_info', constant.ENDURE_ERROR)

			# court_info = get_court_info(paper_head)
			# tag_simple_procedure = get_tag_simple_procedure(paper_intro)
			# tag_designate = get_tag_designate(paper_intro)
			# tag_delay = get_tag_delay(paper_intro)
			# tag_investi_plus = get_tag_investi_plus(paper_intro)
			# judges_info_dict = get_judges_info(paper_judges_info)
			# gongsu_infos = get_gongsu_infos(paper_intro)

			# 输出至excel
			if ec.excel_tag:
				output_to_excel(
					ec.active_sheet,
					paper_id,
					# court_name=court_info.get('court_name', constant.ENDURE_ERROR),
					# court_grade=court_info.get('court_grade', constant.ENDURE_ERROR),
					# court_location=court_info.get('court_location', constant.ENDURE_ERROR),
					# court_location_label=court_info.get('court_location_label', constant.ENDURE_ERROR),
					# tag_simple_procedure=tag_simple_procedure,
					# tag_designate=tag_designate,
					# tag_delay=tag_delay,
					# tag_investi_plus=tag_investi_plus,
					# chief_judge_name=judges_info_dict.get('chief_judge_name', constant.ENDURE_ERROR),
					# judge_names=judges_info_dict.get('judge_names', constant.ENDURE_ERROR),
					# judge_time=judges_info_dict.get('judge_time', constant.ENDURE_ERROR),
					# tag_juror=judges_info_dict.get('tag_juror', constant.ENDURE_ERROR),
					# procuratorate_name=gongsu_infos.get('procuratorate_name', constant.ENDURE_ERROR),
					# prosecute_time=gongsu_infos.get('prosecute_time', constant.ENDURE_ERROR),
					# crime_p=gongsu_infos.get('crime_p', constant.ENDURE_ERROR),
					# tag_change_sue=gongsu_infos.get('tag_change_sue', constant.ENDURE_ERROR),
				)

	return 0


if __name__ == '__main__':
	pass
	# intro_info_main()

