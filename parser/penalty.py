# -*- coding:utf-8 -*-

# 量刑情节和判决结果部分

import extract_bribe_infos.tools as tools
import extract_bribe_infos.constant as constant
import extract_bribe_infos.info_format as info_format
from extract_bribe_infos.parser.pre_extract import paper_dict_generator
from extract_bribe_infos.excel_output import output_to_excel


EXCEL_TAG = False  # 提取之后是否直接输出
PAPER_DICT_KEYS = ['paper_id', 'opinion', 'judge']


def get_crime_c(judge):
	"""
	get crime_c from paper_judge
	:param judge: <str> paper_judge
	:return: <str> crime_c(385); 999 for crime not in CRIME_DICT.keys()
	"""
	crime_c_str = ''
	crime_c_list = constant.crime_c_pattern.findall(judge)
	for crime_c in crime_c_list:
		if '犯罪' in crime_c:
			continue
		crime_c_str += '{0}+'.format(constant.CRIME_DICT.get(crime_c[1:], 999))

	return crime_c_str[:-1]


def get_mianyu(shouhui_sentence):
	"""
	get mianyu from shouhui_sentence
	:param shouhui_sentence: <str> shouhui_sentence
	:return: <int> 0 for no, 1 for yes
	"""
	mianyu = 0
	if '免于' in shouhui_sentence:
		mianyu = 1

	return mianyu


def get_juyi(shouhui_sentence):
	"""
	get juyi from shouhui_sentence
	:param shouhui_sentence: <str> shouhui_sentence
	:return: <int> 0 for no, 15-365 for days
	"""
	juyi = 0
	juyi_match = constant.juyi_pattern.search(shouhui_sentence)
	if juyi_match:
		juyi = tools.convert_chinese_digits_to_arabic(juyi_match.group(1)) * 30

	return juyi


def get_tag_guanzhi(shouhui_sentence):
	"""
	get tag_guanzhi from shouhui_sentence
	:param shouhui_sentence: <str> shouhui_sentence
	:return: <int> 0 for no, 1 for yes
	"""
	tag_guanzhi = 0
	if '管制' in shouhui_sentence:
		tag_guanzhi = 1

	return tag_guanzhi


def get_tuxing(shouhui_sentence):
	"""
	get tuxing from shouhui_sentence
	:param shouhui_sentence: <str> shouhui_sentence
	:return: <int> 0 for no, >0 for months
	"""
	tuxing = 0
	if '无期徒刑' in shouhui_sentence:
		tuxing = 15 * 12
	else:
		tuxing_match = constant.tuxing_pattern.search(shouhui_sentence)
		if tuxing_match:
			tuxing_str = tuxing_match.group(1)
			tuxing = info_format.tuxing_format(tuxing_str)

	return tuxing


def get_sixing(shouhui_sentence):
	"""
	get sixing from shouhui_sentence
	:param shouhui_sentence: <str> shouhui_sentence
	:return: <int> 0 for no, 2 for sihuan, 3 for sihuan + xianjian, 9 for silizhi
	"""
	sixing = 0
	if '死刑' in shouhui_sentence:
		if '缓' in shouhui_sentence:
			if '限制' in shouhui_sentence:
				sixing = 3
			else:
				sixing = 2
		else:
			sixing = 9

	return sixing


def get_fajin(shouhui_sentence):
	"""
	get fajin from shouhui_sentence
	:param shouhui_sentence: <str> shouhui_sentence
	:return: <float> fajin
	"""
	fajin = 0.00
	if '罚金' in shouhui_sentence:
		fajin_match = constant.fajin_pattern.search(shouhui_sentence)
		if fajin_match:
			fajin_sum_str = tools.reserve_only_in(
				fajin_match.group(1),
				constant.SUM_CHARS
			)
			fajin_sum = tools.convert_to_arabic(fajin_sum_str)
			fajin = float(fajin_sum) / 10000.00

	return fajin


def get_moshou(shouhui_sentence):
	"""
	get moshou from shouhui_sentence
	:param shouhui_sentence: <str> shouhui_sentence
	:return: <float> 0.00 for no, -1.00 for totally, others for moshou sum
	"""
	moshou = 0.00
	if '没收' in shouhui_sentence:
		if '全部' in shouhui_sentence:
			moshou = -1.00
		else:
			moshou_match = constant.moshou_pattern.search(shouhui_sentence)
			if moshou_match:
				moshou_sum_str = tools.reserve_only_in(
					moshou_match.group(1),
					constant.SUM_CHARS,
				)
				moshou_sum = tools.convert_to_arabic(moshou_sum_str)
				moshou = float(moshou_sum) / 10000.00

	return moshou


def get_boduo(shouhui_sentence):
	"""
	get boduo from shouhui_sentence
	:param shouhui_sentence: <str> shouhui_sentence
	:return: <int> 0 for no, >0 for years, 10 for lifelong
	"""
	boduo = 0
	if '剥夺' in shouhui_sentence:
		if '终身' in shouhui_sentence:
			boduo = 10
		else:
			boduo_match = constant.boduo_pattern.search(shouhui_sentence)
			if boduo_match:
				boduo_str = boduo_match.group(1)
				boduo = tools.convert_chinese_digits_to_arabic(boduo_str)

	return boduo


def get_huanxing(shouhui_sentence):
	"""
	get huanxing from shouhui_sentence
	:param shouhui_sentence: <str> shouhui_sentence
	:return: <int> 0 for no, >0 for months
	"""
	huanxing = 0
	if '缓' in shouhui_sentence:
		huanxing_match = constant.huanxing_pattern.search(shouhui_sentence)
		if huanxing_match:
			huanxing_str = huanxing_match.group(1)
			huanxing = info_format.tuxing_format(huanxing_str)

	return huanxing


def get_punish_infos(judge):
	"""
	get punish_infos from judge
	:param judge: <str> paper_judge
	:return: <dict> {
		crime_c: '', tag_crimes: 0, mianyu: 0, juyi: 0, tag_guanzhi: 0,
		tuxing: 0, sixing: 0, fajin: 0.0, moshou: 0, boduo: 0, huanxing: 0
	}
	"""
	# 获得罪名
	crime_c = get_crime_c(judge)
	# 定位受贿罪处罚语句
	shouhui_sentence = ''
	judge_sentences = tools.cut_into_sentences(judge)
	for sentence in judge_sentences:
		if '犯受贿罪' in sentence:
			shouhui_sentence = sentence
			break

	punish_infos = {
		'crime_c': crime_c,
		'tag_crimes': len(crime_c.split('+')),
		'mianyu': get_mianyu(shouhui_sentence),
		'juyi': get_juyi(shouhui_sentence),
		'tag_guanzhi': get_tag_guanzhi(shouhui_sentence),
		'tuxing': get_tuxing(shouhui_sentence),
		'sixing': get_sixing(shouhui_sentence),
		'fajin': get_fajin(shouhui_sentence),
		'moshou': get_moshou(shouhui_sentence),
		'boduo': get_boduo(shouhui_sentence),
		'huanxing': get_huanxing(shouhui_sentence)
	}

	return punish_infos


def get_tag_zishou(opinion):
	"""
	get tag_zishou from paper_opinion
	:param opinion: <str> paper_opinion
	:return: <int> 0 for no, 1 for yes
	"""
	tag_zishou = 0
	zishou_match = constant.zishou_pattern.search(opinion)
	if zishou_match:
		if tools.look_ahead_back(
			opinion,
			zishou_match.span(0),
			ahead_dict={'num': 10, 'char': '不', 'request_have': False},
			back_dict={'num': 25, 'char': '不', 'request_have': False}
		) and tools.look_back(
			opinion,
			zishou_match.span(0)[1],
			back_dict={'num': 25, 'char': '误', 'request_have': False}
		):
			tag_zishou = 1

	return tag_zishou


def get_tag_ligong(opinion):
	"""
	get tag_ligong from paper_opinion
	:param opinion: <str> paper_opinion
	:return: <int> 0 for no, 1 for yes
	"""
	tag_ligong = 0
	ligong_match = constant.ligong_pattern.search(opinion)
	if ligong_match:
		if tools.look_ahead_back(
			opinion,
			ligong_match.span(0),
			ahead_dict={'num': 10, 'char': '不', 'request_have': False},
			back_dict={'num': 25, 'char': '不', 'request_have': False}
		) and tools.look_back(
			opinion,
			ligong_match.span(0)[1],
			back_dict={'num': 25, 'char': '误', 'request_have': False}
		):
			tag_ligong = 1

	return tag_ligong


def get_tag_tanbai(opinion):
	"""
	get tag_tanbai from paper_opinion
	:param opinion: <str> paper_opinion
	:return: <int> 0 for no, 1 for yes
	"""
	tag_tanbai = 0
	tanbai_match = constant.tanbai_pattern.search(opinion)
	if tanbai_match:
		tag_tanbai = 1

	return tag_tanbai


def decide_congfan(opinion):
	"""
	decide congfan
	:param opinion: <str> paper_opinion
	:return: <bool> True or False
	"""
	decide_congfan_tag = False
	congfan_match = constant.congfan_pattern.search(opinion)
	if congfan_match:
		if tools.look_ahead_back(
			opinion,
			congfan_match.span(0),
			ahead_dict={'num': 10, 'char': '不', 'request_have': False},
			back_dict={'num': 10, 'char': '意见', 'request_have': False}
		):
			decide_congfan_tag = True

	return decide_congfan_tag


def decide_zhufan(opinion):
	"""
	decide zhufan
	:param opinion: <str> paper_opinion
	:return: <bool> True or False
	"""
	decide_zhufan_tag = False
	zhufan_match = constant.zhufan_pattern.search(opinion)
	if zhufan_match:
		if tools.look_ahead_back(
			opinion,
			zhufan_match.span(0),
			ahead_dict={'num': 10, 'char': '不', 'request_have': False},
			back_dict={'num': 10, 'char': '意见', 'request_have': False}
		):
			decide_zhufan_tag = True

	return decide_zhufan_tag


def decide_zhucong(opinion):
	"""
	decide zhucong(no division)
	:param opinion: <str> paper_opinion
	:return: <bool> True or False
	"""
	decide_zhucong_tag = False
	zhucong_match = constant.zhucong_pattern.search(opinion)
	if zhucong_match:
		decide_zhucong_tag = True

	return decide_zhucong_tag


def get_gongfan(opinion):
	"""
	get gongfan from paper_opinion
	:param opinion: <str> paper_opinion
	:return: <int> 0 for no, 1 for zhucong(no division), 2 for zhufan, 3 for congfan
	"""
	gongfan = 0
	if decide_congfan(opinion):
		gongfan = 3
	elif decide_zhufan(opinion):
		gongfan = 2
	elif decide_zhucong(opinion):
		gongfan = 1

	return gongfan


def get_tag_suohui(opinion):
	"""
	get tag_suohui from paper_opinion
	:param opinion: <str> paper_opinion
	:return: <int> 0 for no, 1 for yes
	"""
	tag_suohui = 0
	suohui_match = constant.suohui_pattern.search(opinion)
	if suohui_match:
		if tools.look_ahead(
				opinion,
				suohui_match.span(0)[0],
				ahead_dict={'num': 10, 'char': '不', 'request_have': False}
		) and tools.look_ahead(
			opinion,
			suohui_match.span(0)[0],
			ahead_dict={'num': 10, 'char': '非', 'request_have': False}
		):
			tag_suohui = 1

	return tag_suohui


def get_tag_tuizang(opinion):
	"""
	get tag_tuizang from paper_opinion
	:param opinion: <str> paper_opinion
	:return: <int> 0 for no, 1 for yes
	"""
	tag_tuizang = 0
	# 退赃
	tuizang_match = constant.tuizang_pattern.search(opinion)
	if tuizang_match:
		if tools.look_back(
			opinion,
			tuizang_match.span(0)[1],
			back_dict={'num': 25, 'char': '不', 'request_have': False}
		):
			tag_tuizang = 1
	# 配合追缴
	if tag_tuizang != 1:
		peihe_match = constant.peihe_pattern.search(opinion)
		if peihe_match:
			if tools.look_back(
					opinion,
					peihe_match.span(0)[1],
					back_dict={'num': 10, 'char': '追缴', 'request_have': True}
			):
				tag_tuizang = 1

	return tag_tuizang


def get_tag_bad_effects(opinion):
	"""
	get tag_bad_effects from paper_opinion
	:param opinion: <str> paper_opinion
	:return: <int> 0 for no, 1 for yes
	"""
	tag_bad_effects = 0
	shyx_match = constant.shyx_pattern.search(opinion)
	if shyx_match:
		if tools.look_ahead(
			opinion,
			shyx_match.span(0)[0],
			ahead_dict={'num': 10, 'char': '恶劣', 'request_have': True}
		) or tools.look_back(
			opinion,
			shyx_match.span(0)[1],
			back_dict={'num': 10, 'char': '恶劣', 'request_have': True}
		) or tools.look_back(
			opinion,
			shyx_match.span(0)[1],
			back_dict={'num': 10, 'char': '坏', 'request_have': True}
		) or tools.look_ahead(
			opinion,
			shyx_match.span(0)[0],
			ahead_dict={'num': 10, 'char': '坏', 'request_have': True}
		):
			tag_bad_effects = 1

	return tag_bad_effects


def get_punish_factors(opinion):
	"""
	get punish_infos from opinion
	:param opinion: <str> paper_opinion
	:return: <dict> {
		tag_zishou: 0, tag_ligong: 0, tag_tanbai: 0, gongfan: 0,
		tag_suohui: 0, tag_tuizang: 0, tag_bad_effects: 0
	}
	"""
	punish_factors = {
		'tag_zishou': get_tag_zishou(opinion),
		'tag_ligong': get_tag_ligong(opinion),
		'tag_tanbai': get_tag_tanbai(opinion),
		'gongfan': get_gongfan(opinion),
		'tag_suohui': get_tag_suohui(opinion),
		'tag_tuizang': get_tag_tuizang(opinion),
		'tag_bad_effects': get_tag_bad_effects(opinion)
	}

	return punish_factors


def penalty_main():
	"""
	test every def in penalty.py
	:return: <int> 0
	"""
	with tools.ExcelContext(EXCEL_TAG) as ec:

		for paper_dict in paper_dict_generator(PAPER_DICT_KEYS):

			if len(paper_dict) == 1:
				continue

			paper_id = paper_dict['paper_id']
			# paper_opinion = paper_dict.get('opinion', constant.ENDURE_ERROR)
			# paper_judge = paper_dict.get('judge', constant.ENDURE_ERROR)
			#
			# punish_infos = get_punish_infos(paper_judge)
			# punish_factors = get_punish_factors(paper_opinion)

			# 输出至excel
			if ec.excel_tag:
				output_to_excel(
					ec.active_sheet,
					paper_id,
					# crime_c=punish_infos.get('crime_c', constant.ENDURE_ERROR),
					# tag_crimes=punish_infos.get('tag_crimes', constant.ENDURE_ERROR),
					# mianyu=punish_infos.get('mianyu', constant.ENDURE_ERROR),
					# juyi=punish_infos.get('juyi', constant.ENDURE_ERROR),
					# tag_guanzhi=punish_infos.get('tag_guanzhi', constant.ENDURE_ERROR),
					# tuxing=punish_infos.get('tuxing', constant.ENDURE_ERROR),
					# sixing=punish_infos.get('sixing', constant.ENDURE_ERROR),
					# fajin=punish_infos.get('fajin', constant.ENDURE_ERROR),
					# moshou=punish_infos.get('moshou', constant.ENDURE_ERROR),
					# boduo=punish_infos.get('boduo', constant.ENDURE_ERROR),
					# huanxing=punish_infos.get('huanxing', constant.ENDURE_ERROR),
					# tag_zishou=punish_factors.get('tag_zishou', constant.ENDURE_ERROR),
					# tag_ligong=punish_factors.get('tag_ligong', constant.ENDURE_ERROR),
					# tag_tanbai=punish_factors.get('tag_tanbai', constant.ENDURE_ERROR),
					# gongfan=punish_factors.get('gongfan', constant.ENDURE_ERROR),
					# tag_suohui=punish_factors.get('tag_suohui', constant.ENDURE_ERROR),
					# tag_tuizang=punish_factors.get('tag_tuizang', constant.ENDURE_ERROR),
					# tag_bad_effects=punish_factors.get('tag_bad_effects', constant.ENDURE_ERROR),
				)

	return 0


if __name__ == '__main__':
	pass
	# penalty_main()
