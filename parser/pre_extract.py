# -*- coding:utf-8 -*-

# 文本分区

import extract_bribe_infos.info_format as info_format
import extract_bribe_infos.constant as constant
import extract_bribe_infos.tools as tools
from extract_bribe_infos.excel_output import output_to_excel


EXCEL_TAG = False  # 提取之后是否直接输出


@tools.endure_error
def get_paper_mark(paper):
	"""
	get paper_mark
	:param paper: <str> paper
	:return: <str> paper_mark
	"""
	paper_mark = constant.paper_mark_pattern.search(paper, 0, 100).group(0).replace('书', '')
	paper_mark = info_format.paper_mark_format(paper_mark)

	return paper_mark


def paper_divider_head(paper):
	"""
	get paper_dict['head']
	:param paper: <str> raw paper
	:return: <str> paper_head <str> paper_not_head
	"""
	mark_index = constant.paper_mark_pattern.search(paper, 0, 100).end(0)
	paper_head = paper[:mark_index]
	paper_not_head = paper[mark_index:]

	return paper_head, paper_not_head


def paper_divider_intro(paper_not_head):
	"""
	get paper_dict['intro']
	:param paper_not_head: <str> paper_not_head
	:return: <str> paper_intro <str> paper_not_intro
	"""
	slzj_index = constant.slzj_pattern.search(paper_not_head).end(0)
	paper_intro = paper_not_head[:slzj_index]
	paper_not_intro = paper_not_head[slzj_index:]

	return paper_intro, paper_not_intro


def paper_divider_argu(paper_not_intro):
	"""
	get paper_dict['argu'] (is_null, 1.no argu 2.argu is fact)
	:param paper_not_intro: <str> paper_not_intro
	:return: <str> paper_argu (can be '') <str> paper_not_argu
	"""
	slcm_match = constant.slcm_pattern.search(paper_not_intro)
	if slcm_match:
		argu_index = slcm_match.start(0)
		paper_argu = paper_not_intro[:argu_index]
		paper_not_argu = paper_not_intro[argu_index:]
	else:
		paper_argu = ''
		paper_not_argu = paper_not_intro

	return paper_argu, paper_not_argu


def paper_divider_fact(paper_not_argu):
	"""
	get paper_dict['fact']
	:param paper_not_argu: <str> paper_not_argu
	:return: <str> paper_fact <str> paper_not_fact
	"""
	byrw_match = constant.byrw_pattern.search(paper_not_argu)
	fact_index = byrw_match.start(0)
	paper_fact = paper_not_argu[:fact_index]
	paper_not_fact = paper_not_argu[fact_index:]

	return paper_fact, paper_not_fact


def paper_divider_opinion(paper_not_fact):
	"""
	get paper_dict['opinion']
	:param paper_not_fact: <str> paper_not_fact
	:return: <str> paper_opinion <str> paper_not_opinion
	"""
	pjrx_match = constant.pjrx_pattern.search(paper_not_fact)
	opinion_index = pjrx_match.end(0)
	paper_opinion = paper_not_fact[:opinion_index]
	paper_not_opinion = paper_not_fact[opinion_index:]

	return paper_opinion, paper_not_opinion


def paper_divider_judge_judges_info(paper_not_opinion):
	"""
	get paper_dict['judge'] and paper_dict['judges_info']
	:param paper_not_opinion: <str> paper_not_opinion
	:return: <str> paper_judge <str> paper_judges_info
	"""
	spz_index = constant.spz_pattern.search(paper_not_opinion).start(0)
	paper_judge = paper_not_opinion[:spz_index]
	paper_judges_info = paper_not_opinion[spz_index:]

	return paper_judge, paper_judges_info


@tools.endure_error_for_paper_divider
def paper_divider(paper_id, paper):
	"""
	divide paper into 7 parts
	:param paper_id: <int> paper_id
	:param paper: <str> raw paper
	:return: <dict> head, intro, argu, fact, opinion, judge, judges_info
	distribution:
		head <mark> intro <slzj> argu(is_null, 1.no argu 2.argu is fact) <slcm>
		fact <byrw> opinion <pjrx> judge <spz> judges_info
	"""
	paper_dict = {
		'paper_id': paper_id,  # paper_id
	}
	# head
	paper_dict['head'], paper_not_head = paper_divider_head(paper)
	# intro
	paper_dict['intro'], paper_not_intro = paper_divider_intro(paper_not_head)
	# argu
	paper_dict['argu'], paper_not_argu = paper_divider_argu(paper_not_intro)
	# fact
	paper_dict['fact'], paper_not_fact = paper_divider_fact(paper_not_argu)
	# opinion
	paper_dict['opinion'], paper_not_opinion = paper_divider_opinion(paper_not_fact)
	# judge and judges_info
	paper_dict['judge'], paper_dict['judges_info'] = paper_divider_judge_judges_info(paper_not_opinion)

	return paper_dict


def paper_dict_generator(paper_dict_keys):
	"""
	generate paper_dict partly or totally(always have paper_id)
	:param paper_dict_keys: <list> keys of dict, which will be generated
	:return: yield dict { paper_id: paper_id, dict_key: dict_value, ... }
	"""
	if 'paper_id' not in paper_dict_keys:
		paper_dict_keys.append('paper_id')
	for paper_id, paper_path, paper in tools.paper_iterator():
		paper_dict_all = paper_divider(paper_id, paper)

		if len(paper_dict_all) == 1:
			yield paper_dict_all
		else:
			paper_dict = {}
			for dict_key in paper_dict_keys:
				paper_dict[dict_key] = paper_dict_all[dict_key]
			yield paper_dict


@tools.endure_error
def get_trial_level(paper_mark, intro):
	"""
	get trial_level
	:param paper_mark: <str> paper_mark
	:param intro: <str>paper_dict['intro'] -- for revising
	:return: <int> trial_level
	"""
	trial_level = 0
	if '再' in paper_mark or '抗' in paper_mark or '重' in paper_mark:
		trial_level = 3
	elif '初' in paper_mark:
		trial_level = 1
	elif '终' in paper_mark:
		trial_level = 2

	# revise
	if trial_level != 3:
		if '发回' in intro or '重审' in intro:
			trial_level = 3

	return trial_level


def pre_extract_main():
	"""
	test every def in pre_extract.py
	:return: <int> 0
	"""
	with tools.ExcelContext(EXCEL_TAG) as ec:
		for paper_id, paper_path, paper in tools.paper_iterator():
			# paper_mark = get_paper_mark(paper)
			# paper_dict = paper_divider(paper_id, paper)
			# trial_level = get_trial_level(paper_mark, paper_dict.get('intro', constant.ENDURE_ERROR))
			pass

			# 输出至excel
			if ec.excel_tag:
				output_to_excel(
					ec.active_sheet,
					paper_id,
					# paper_mark=paper_mark,
					# trial_level=trial_level
				)

	return 0


if __name__ == '__main__':
	pass
	# pre_extract_main()
