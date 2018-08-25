# -*- coding:utf-8 -*-

# 被告人信息部分

import extract_bribe_infos.tools as tools
import extract_bribe_infos.constant as constant
import extract_bribe_infos.info_format as info_format
from extract_bribe_infos.parser.pre_extract import paper_dict_generator
from extract_bribe_infos.excel_output import output_to_excel


EXCEL_TAG = False
PAPER_DICT_KEYS = ['paper_id', 'intro', 'fact', 'argu']


def get_d_sentence(intro):
	"""
	get d_sentence from paper_intro
	:param intro: <str> paper_intro
	:return: <str> d_sentence
	"""
	intro_sentences = tools.cut_into_sentences(intro)
	target_s_id = 0
	for s_id in range(0, len(intro_sentences)):
		if '被告人' in intro_sentences[s_id]:
			target_s_id = s_id
			break
	d_sentence = intro_sentences[target_s_id] + intro_sentences[target_s_id + 1]  # 补充后面一句话

	return d_sentence


def get_d_name_and_d_family_name(d_sentence):
	"""
	get d_name, d_family_name from d_sentence
	:param d_sentence: <str> d_sentence
	:return: <str> d_name <str> d_family_name
	"""
	# 获取被告人姓名
	d_name = ''
	d_name_match = constant.d_name_pattern.search(d_sentence)
	if d_name_match:
		d_name = d_name_match.group(1).replace('：', '')
	# 获取被告人姓氏
	d_family_name = d_name[:1]

	return d_name, d_family_name


def get_d_sex(d_sentence):
	"""
	get d_sex from d_sentence
	:param d_sentence: <str> d_sentence
	:return: <int> -1 for unknown, 0 for female, 1 for male
	"""
	d_sex = -1
	if '男' in d_sentence:
		d_sex = 1
	if '女' in d_sentence:
		d_sex = 0

	return d_sex


def get_d_volk(d_sentence):
	"""
	get d_volk from d_sentence
	:param d_sentence: <str> d_sentence
	:return: <int> 1-58
	"""
	d_volk = 1
	d_volk_match = constant.d_volk_pattern.search(d_sentence)
	if d_volk_match:
		d_volk = constant.VOLK_DICT[d_volk_match.group(1)]

	return d_volk


def get_d_birthday(d_sentence):
	"""
	get d_birthday from d_sentence
	:param d_sentence: <str> d_sentence
	:return: <str> YYYY-MM-DD
	"""
	d_birthday = ''
	if '生' in d_sentence:
		d_birthday_after_match = constant.d_birthday_after_pattern.search(d_sentence)
		d_birthday_before_match = constant.d_birthday_before_pattern.search(d_sentence)

		if d_birthday_after_match:
			year, month, day = d_birthday_after_match.group(1), d_birthday_after_match.group(2), d_birthday_after_match.group(3)
			d_birthday = info_format.birth_time_format(year, month, day)

		elif d_birthday_before_match:
			year, month, day = d_birthday_before_match.group(1), d_birthday_before_match.group(2), d_birthday_before_match.group(3)
			d_birthday = info_format.birth_time_format(year, month, day)

	return d_birthday


def get_d_place_registered_ren(d_sentence):
	"""
	get d_place_registered_ren(...人) from d_sentence
	:param d_sentence: <str> d_sentence
	:return: <str> d_place_registered_ren
	"""
	d_place_registered_ren = ''
	d_sentence_parts = d_sentence.split('，')
	for part in d_sentence_parts:
		if '人' in part:
			if not constant.d_place_registered_not_ren_before.search(part):
				if not constant.d_place_registered_not_ren_after.search(part):
					d_place_registered_ren = part.replace('人', '')
					break

	return d_place_registered_ren


def get_d_place_registered(d_sentence):
	"""
	get d_place_registered from d_sentence
	:param d_sentence: <str> d_sentence
	:return: <str> d_place_registered
	"""
	a_match = constant.d_place_registered_a.search(d_sentence)
	b_match = constant.d_place_registered_b.search(d_sentence)

	if a_match:
		d_place_registered = a_match.group(1)
	elif b_match:
		d_place_registered = b_match.group(1)
	else:
		d_place_registered = get_d_place_registered_ren(d_sentence)

	return info_format.d_place_format(d_place_registered)


def get_d_place_current(d_sentence):
	"""
	get d_place_current from d_sentence
	:param d_sentence: <str> d_sentence
	:return: <str> d_place_current
	"""
	d_place_current = ''
	if '住' in d_sentence:
		not_zhu_matchs = list(constant.d_place_current_not_zhu.finditer(d_sentence))
		if len(not_zhu_matchs) > 0:
			d_sentence = d_sentence[not_zhu_matchs[-1].end(0):]
		if '监视居住' in d_sentence:
			d_sentence = d_sentence[:d_sentence.index('监视居住')]

		d_place_current_match = constant.d_place_current.search(d_sentence)
		if d_place_current_match:
			d_place_current = d_place_current_match.group(1)

	return info_format.d_place_format(d_place_current)


def get_defendant_infos(d_sentence):
	"""
	get defendant_infos from d_sentence
	:param d_sentence: <str> d_sentence
	:return: <dict> defendant_infos {
		d_name: '', d_family_name: '', d_sex: -1, d_volk: 1, d_birthday: '',
		d_place_registered: '', d_place_current: ''
	}
	"""
	# d_name, d_family_name
	d_name, d_family_name = get_d_name_and_d_family_name(d_sentence)
	# 组合defendant_infos字典
	defendant_infos = {
		'd_name': d_name,
		'd_family_name': d_family_name,
		'd_sex': get_d_sex(d_sentence),
		'd_volk': get_d_volk(d_sentence),
		'd_birthday': get_d_birthday(d_sentence),
		'd_place_registered': get_d_place_registered(d_sentence),
		'd_place_current': get_d_place_current(d_sentence),
	}

	return defendant_infos


def search_job_name_matchs(job_name_matchs):
	"""
	search job_name_matchs, return job_names
	:param job_name_matchs: <generator> pattern.finditer() return
	:return: <list> job_names
	"""
	job_names = []
	for match in job_name_matchs:
		if not constant.not_job_name_pattern.search(match.group(0)):
			job_name = info_format.job_name_single_format(match.group(1))
			# 如果不符合要求，job_name_single_format返回空
			if len(job_name) > 0 and job_name not in job_names:
				job_names.append(job_name)

	return job_names


def get_job_names(intro, argu_and_fact):
	"""
	get job_names from paper_intro, paper_argu + paper_fact
	:param intro: <str> paper_intro
	:param argu_and_fact: <str> paper_argu + paper_fact
	:return: <list> job_names
	"""
	# 在intro中寻找
	job_name_matchs_of_intro = constant.job_name_pattern_for_intro.finditer(intro)
	job_names = search_job_name_matchs(job_name_matchs_of_intro)
	# 如未找到，在argu+fact中继续寻找
	if len(job_names) == 0:
		job_name_matchs_of_af = constant.job_name_pattern_for_af.finditer(argu_and_fact)
		job_names = search_job_name_matchs(job_name_matchs_of_af)

	return job_names


def get_job_domain_single(job_name):
	"""
	get job_domain for single job_name
	:param job_name: <str> job_name
	:return: <int> job_domain
	"""
	job_domain = 8
	# 第一层判断(根据所在单位)
	for job_pos in constant.JOB_DOMAIN_POS_RANKED:
		if job_pos in job_name:
			job_domain = constant.JOB_DOMAIN_POS_DICT[job_pos]
			break
	# 如未找到，开启第二层判断(根据担任职务)
	if job_domain == 8:
		for job_title in constant.JOB_DOMAIN_TITLE_DICT.keys():
			if job_title in job_name:
				job_domain = constant.JOB_DOMAIN_TITLE_DICT[job_title]

	return job_domain


def get_job_domain(job_names):
	"""
	get job_domain from job_names
	:param job_names: <list> job_names
	:return: <int> job_domain
	"""
	if len(job_names) == 0:
		return 8

	job_domain = 8
	# 从右侧遍历job_names，取最先得到的job_domain
	for job_id in range(len(job_names)-1, -1, -1):
		job_domain_temp = get_job_domain_single(job_names[job_id])
		if job_domain_temp != 8:
			job_domain = job_domain_temp
			break

	return job_domain


def revise_job_grade(job_grade, job_name):
	"""
	if job_grade > 2(厅局级及以上), revise it
	:param job_grade: <int> job_grade
	:param job_name: <str> job_name
	:return: <int> revised_job_grade
	"""
	# 碰撞减少
	revise_value = 0
	for revise_key in constant.JOB_GRADE_REVISE.keys():
		if revise_key in job_name:
			revise_value_temp = constant.JOB_GRADE_REVISE[revise_key]
			if revise_value_temp < revise_value:
				revise_value = revise_value_temp

	revised_job_grade = job_grade + revise_value if job_grade + revise_value > -1 else 0

	return revised_job_grade


def get_job_grade_single(job_name, job_domain):
	"""
	get job_grade from job_name
	:param job_name: <str> job_name
	:param job_domain: <int> get_job_domain_single() return
	:return: <int> job_grade
	"""
	job_grade = 6
	# 第一层：根据job_title直接判断
	for job_title in constant.JOB_GRADE_TITLE_DICT.keys():
		if job_title in job_name:
			job_grade = constant.JOB_GRADE_TITLE_DICT[job_title]
	# 第二层：根据job_domain分类处理
	if job_grade == 6:
		# 直接确定: 1群众自治组织
		if job_domain == 1:
			job_grade = 0
		# 单独处理： 0军队
		elif job_domain == 0:
			pass
		# 向前搜索: 2公检法司3人大政协4国企5事业单位和人民团体6行政机关7党的部门
		else:
			region_grade = tools.get_region_grade(job_name)
			if region_grade != 6:
				job_grade = region_grade
				# revise(3厅局级及以上)
				if job_grade > 2:
					job_grade = revise_job_grade(job_grade, job_name)

	return job_grade


def get_job_grade(job_names):
	"""
	get job_grade from job_names
	:param job_names: <list> job_names
	:return: <int> job_grade
	"""
	if len(job_names) == 0:
		return 6

	job_grade = 6
	# 从右侧开始判断，取第一个得到的级别
	for job_id in range(len(job_names)-1, -1, -1):
		job_name = job_names[job_id]
		job_domain = get_job_domain_single(job_name)
		# 无法获得job_domain，则无法获得job_grade
		if job_domain == 8:
			continue
		# 保证级别递减
		job_grade_temp = get_job_grade_single(job_name, job_domain)
		if job_grade_temp < job_grade:
			job_grade = job_grade_temp
		# 取到第一个值后，退出循环
		if job_grade != 6:
			break

	return job_grade


def get_job_infos(intro, argu_and_fact):
	"""
	get job_infos from paper_intro, paper_argu + paper_fact
	:param intro: <str> paper_intro
	:param argu_and_fact: <str> paper_argu + paper_fact
	:return: <dict> job_infos {
		job_name: '', job_domain: 8, job_grade: 6
	}
	"""
	# 获得单位名称
	job_names = get_job_names(intro, argu_and_fact)
	# 组合workplace_infos字典
	job_infos = {
		'job_name': info_format.job_name_output_format(job_names),
		'job_domain': get_job_domain(job_names),
		'job_grade': get_job_grade(job_names)
	}

	return job_infos


# 算法改进中，暂不可用
def get_lawyer_name(intro):
	"""
	get lawyer_name from paper_intro
	:param intro: <str> paper_intro
	:return: <str> lawyer_name, break by '+'
	"""
	pass

	return ''


# 算法改进中，暂不可用
def get_law_firm_name(intro):
	"""
	get law_firm_name from paper_intro
	:param intro: <str> paper_intro
	:return: <str> law_firm_name, break by '+'
	"""
	pass

	return ''


# 算法改进中，暂不可用
def get_lawyer_infos(intro):
	"""
	get lawyer_infos from paper_intro
	:param intro: <str> paper_intro
	:return: <dict> lawyer_infos {
		lawyer_name: '', law_firm_name: '', law_firm_location: ''
	}
	"""
	# 获得律师姓名
	lawyer_name = get_lawyer_name(intro)
	# 获得律所名称
	law_firm_name = get_law_firm_name(intro)
	# 组合lawyer_infos字典
	lawyer_infos = {
		'lawyer_name': lawyer_name,
		'law_firm_name': law_firm_name,
	}

	return lawyer_infos


def defendant_info_main():
	"""
	test every def in defendant_info.py
	:return: <int> 0
	"""
	with tools.ExcelContext(EXCEL_TAG) as ec:

		for paper_dict in paper_dict_generator(PAPER_DICT_KEYS):

			if len(paper_dict) == 1:
				continue

			paper_id = paper_dict['paper_id']
			paper_intro = paper_dict.get('intro', constant.ENDURE_ERROR)
			paper_argu = paper_dict.get('argu', constant.ENDURE_ERROR)
			paper_fact = paper_dict.get('fact', constant.ENDURE_ERROR)
			d_sentence = get_d_sentence(paper_intro)
			argu_and_fact = paper_argu + paper_fact

			# defendant_infos = get_defendant_infos(d_sentence)
			# job_infos = get_job_infos(paper_intro, argu_and_fact)
			# lawyer_infos = get_lawyer_infos(paper_intro)

			# 输出至excel
			if ec.excel_tag:
				output_to_excel(
					ec.active_sheet,
					paper_id,
					# defendant_name=defendant_infos.get('d_name', constant.ENDURE_ERROR),
					# defendant_family_name=defendant_infos.get('d_family_name', constant.ENDURE_ERROR),
					# defendant_sex=defendant_infos.get('d_sex', constant.ENDURE_ERROR),
					# defendant_volk=defendant_infos.get('d_volk', constant.ENDURE_ERROR),
					# defendant_birthday=defendant_infos.get('d_birthday', constant.ENDURE_ERROR),
					# defendant_place_registered=defendant_infos.get('d_place_registered', constant.ENDURE_ERROR),
					# defendant_place_current=defendant_infos.get('d_place_current', constant.ENDURE_ERROR),
					# job_name=job_infos.get('job_name', constant.ENDURE_ERROR),
					# job_domain=job_infos.get('job_domain', constant.ENDURE_ERROR),
					# job_grade=job_infos.get('job_grade', constant.ENDURE_ERROR),
					# lawyer_name=lawyer_infos.get('lawyer_name', constant.ENDURE_ERROR),
					# law_firm_name=lawyer_infos.get('law_firm_name', constant.ENDURE_ERROR),
				)

	return 0


if __name__ == '__main__':
	pass
	# defendant_info_main()

