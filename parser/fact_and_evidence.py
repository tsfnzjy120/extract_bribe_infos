# -*- coding:utf-8 -*-

# 事实与证据部分

import extract_bribe_infos.tools as tools
import extract_bribe_infos.constant as constant
import extract_bribe_infos.info_format as info_format
from extract_bribe_infos.parser.pre_extract import paper_dict_generator
from extract_bribe_infos.excel_output import output_to_excel


EXCEL_TAG = False  # 提取之后是否直接输出
PAPER_DICT_KEYS = ['paper_id', 'argu', 'fact', 'opinion']


def get_sum_list(paper_part):
	"""
	get sum_list_p from paper_argu, or get sum_list_c from paper_opinion + paper_fact
	:return: <list> sum_list_p or sum_list_c
	"""
	sum_list = []
	sum_list_gongji, sum_list_not_gongji = [], []
	sum_matchs = constant.sum_pattern.finditer(paper_part)
	for match in sum_matchs:
		# 转化为浮点数
		sum_float = tools.convert_to_arabic(
			tools.reserve_only_in(match.group(1), constant.SUM_CHARS)
		)
		# 向前看10字符
		look_ahead_context = paper_part[match.start(1) - 10:match.start(1)]
		# 寻找'共计'
		if constant.sum_total_pattern.search(look_ahead_context):
			# 总结句中的'共计'
			if tools.look_ahead_back(
				paper_part,
				match.span(0),
				ahead_dict={'num': 20, 'char': '收受', 'request_have': True},
				back_dict={'num': 50, 'char': '受贿罪', 'request_have': True}
			):
				sum_list.append(sum_float)
				return sum_list  # 退出函数
			# 非总结句中的'共计'
			else:
				if sum_float not in sum_list_gongji and sum_float < 1000000000:  # 大于10亿直接排除
					sum_list_gongji.append(sum_float)
		# 非'共计'
		else:
			if sum_float not in sum_list_not_gongji and sum_float < 1000000000:  # 大于10亿直接排除
				sum_list_not_gongji.append(sum_float)
	# 取总和较小、非空的list
	if len(sum_list_gongji) > 0 and len(sum_list_not_gongji) > 0:
			sum_list = sum_list_gongji if sum(sum_list_gongji) < sum(sum_list_not_gongji) else sum_list_not_gongji
	else:
		sum_list = sum_list_gongji if len(sum_list_gongji) > 0 else sum_list_not_gongji

	return sum_list


def get_facts_num(sum_list, paper_part):
	"""
	get facts_num_p from, paper_arguor fact_num_c from
	:param sum_list: <list> get_sum_list return, use for initial
	:param paper_part: <str> paper_argu or paper_opinion + paper_fact, use for search '多次'
	:return: <int> facts_num_p or facts_num_c:
				-1 for duoci, 0 for unknown, 1 for single, >1 for exact times
	"""
	# 初始化，并寻找确切次数
	facts_num = len(sum_list) if len(sum_list) > 1 else 0
	# 找不到确切次数的，根据'多次'估计是否多次
	if facts_num == 0:
		if constant.duoci_pattern.search(paper_part):
			facts_num = -1
		else:
			facts_num = 1

	return facts_num


def get_sum_facts_dict(argu, opi_fact):
	"""
	get sum_facts_dict from paper_argu, paper_opinion + paper_fact
	:param argu: <str> paper_argu
	:param opi_fact: <str> paper_opinion + paper_fact
	:return: <dict> {
		'sum_total_p': '', 'sum_total_c': '', 'tag_sum_same': 1,
		'facts_num_p': 0, 'facts_num_c': 0, 'tag_facts_same': 1,
	}
	"""
	# 获取金额信息
	sum_list_p, sum_list_c = get_sum_list(argu), get_sum_list(opi_fact)
	# revise
	# 确保认定额不大于起诉额
	if sum(sum_list_c) > sum(sum_list_p) and len(sum_list_p) != 0:
		sum_list_c = sum_list_p
	# 一方为空，适用另一方
	if len(sum_list_p) == 0 and len(sum_list_c) != 0:
		sum_list_p = sum_list_c
	if len(sum_list_p) != 0 and len(sum_list_c) == 0:
		sum_list_c = sum_list_p

	tag_sum_same = 0 if sum(sum_list_p) != sum(sum_list_c) else 1
	sum_total_p = info_format.sum_total_format(sum_list_p)
	sum_total_c = info_format.sum_total_format(sum_list_c)

	# 获取次数信息
	facts_num_p = get_facts_num(sum_list_p, argu)
	facts_num_c = get_facts_num(sum_list_c, opi_fact)
	# revise
	# 对于双方确切次数，确保认定次数不大于起诉次数
	if facts_num_p > 1 and facts_num_c > 1:
		if facts_num_c > facts_num_p:
			facts_num_c = facts_num_p
	# 有一方是多次的，另一方也是多次
	if facts_num_p > 1 or facts_num_p == -1:
		if facts_num_c > 1 or facts_num_c == -1:
			pass
		else:
			facts_num_c = facts_num_p
	else:
		if facts_num_c > 1 or facts_num_c == -1:
			facts_num_p = facts_num_c
		else:
			pass

	# 判断tag_facts_same(仅针对确切次数)
	if facts_num_p > 1 and facts_num_c > 1 and facts_num_p != facts_num_c:
		tag_facts_same = 0
	else:
		tag_facts_same = 1

	# 组合sum_facts_dict
	sum_facts_dict = {
		'sum_total_p': sum_total_p, 'sum_total_c': sum_total_c, 'tag_sum_same': tag_sum_same,
		'facts_num_p': facts_num_p, 'facts_num_c': facts_num_c, 'tag_facts_same': tag_facts_same,
	}

	return sum_facts_dict


def fact_evi_main():
	"""
	test every def in fact_and_evidence.py
	:return: <int> 0
	"""
	with tools.ExcelContext(EXCEL_TAG) as ec:

		for paper_dict in paper_dict_generator(PAPER_DICT_KEYS):

			if len(paper_dict) == 1:
				continue

			paper_id = paper_dict['paper_id']
			paper_argu = paper_dict.get('argu', constant.ENDURE_ERROR)
			paper_fact = paper_dict.get('fact', constant.ENDURE_ERROR)
			paper_opinion = paper_dict.get('opinion', constant.ENDURE_ERROR)

			# sum_facts_dict = get_sum_facts_dict(paper_argu, paper_opinion + paper_fact)

			# 输出至excel
			if ec.excel_tag:
				output_to_excel(
					ec.active_sheet,
					paper_id,
					# sum_total_p=sum_facts_dict.get('sum_total_p', constant.ENDURE_ERROR),
					# sum_total_c=sum_facts_dict.get('sum_total_c', constant.ENDURE_ERROR),
					# tag_sum_same=sum_facts_dict.get('tag_sum_same', constant.ENDURE_ERROR),
					# facts_num_p=sum_facts_dict.get('facts_num_p', constant.ENDURE_ERROR),
					# facts_num_c=sum_facts_dict.get('facts_num_c', constant.ENDURE_ERROR),
					# tag_facts_same=sum_facts_dict.get('tag_facts_same', constant.ENDURE_ERROR),
				)

	return 0


if __name__ == '__main__':
	pass
	# fact_evi_main()
