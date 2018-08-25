# -*- coding:utf-8 -*-

# 要素值格式化

import re
import extract_bribe_infos.tools as tools
import extract_bribe_infos.constant as constant


def paper_mark_format(paper_mark):
	"""
	:param <str> paper_mark
	:return: <str> paper_mark_formatted
	"""
	if '年' in paper_mark:

		def repl_year(year_match):
			"""
			convert year to (year)
			:param <match> year_match
			:return: <str> (year)
			"""
			return '(' + year_match.group(0) + ')'

		paper_mark = paper_mark.replace('年', '')
		paper_mark_formatted = re.sub(r'20\d{2}', repl_year, paper_mark, 1)
	else:
		paper_mark_formatted = paper_mark.replace('（', '(').replace('）', ')')

	return paper_mark_formatted


def court_name_format(court_in_head):
	"""
	:param court_name: <str> court_in_head
	:return: <str> court_name
	"""
	court_name = constant.brackets_pattern.sub('', court_in_head).replace('\ufeff', '')

	return court_name


def judge_time_format(year, month, day):
	"""
	format time as YYYY-MM-DD
	:param year: <str> XXXX(chinese)年
	:param month: <str> XX(chinese)月
	:param day: <str> XXX(chinese)日
	:return: <str> time
	"""
	# 参数规范
	year = tools.reserve_only_in(year, constant.TIME_KEYWORD)
	month = tools.reserve_only_in(month, constant.TIME_KEYWORD)
	day = tools.reserve_only_in(day, constant.TIME_KEYWORD)
	# 组合YYYY-MM-DD
	try:
		time = '-'.join([
			constant.TIME_YEAR_DICT[year],
			constant.TIME_MONTH_DICT[month],
			constant.TIME_DAY_DICT[day]
		])
	except:
		time = constant.ENDURE_ERROR

	return time


def birth_time_format(year, month, day):
	"""
	format time as YYYY-MM-DD
	:param year: <str> XXXX(arabic)年
	:param month: <str> XX(arabic)月
	:param day: <str> XXX(arabic)日
	:return: <str> time
	"""
	# 参数规范
	year = tools.reserve_only_in(year, constant.NUM_CHARS)
	month = tools.reserve_only_in(month, constant.NUM_CHARS)
	day = tools.reserve_only_in(day, constant.NUM_CHARS)
	# 组合YYYY-MM-DD
	time = '-'.join([year, month, day])

	return time


def tuxing_format(tuxing_str):
	"""
	format tuxing_str as tuxing(months)
	:param tuxing_str: <str> tuxing_str
	:return: <int> tuxing(months)
	"""
	year, month = 0, 0
	if '年' in tuxing_str:
		year_str = constant.tuxing_year_pattern.search(tuxing_str).group(1)
		year = tools.convert_chinese_digits_to_arabic(year_str)
	if '月' in tuxing_str:
		month_str = constant.tuxing_month_pattern.search(tuxing_str).group(1)
		month = tools.convert_chinese_digits_to_arabic(month_str)

	return year * 12 + month


def d_place_format(d_place):
	"""
	format d_place_registered or d_place_current
	:param d_place: <str> d_place_registered or d_place_current
	:return: <str> d_place_formatted
	"""
	# 处理含有'（：及 因'的情况
	if '（' in d_place:
		d_place = d_place[:d_place.index('（')]  # 除去括号和其中的内容
	elif '：' in d_place:
		d_place = d_place[d_place.index('：') + 1:]
	elif '及' in d_place:
		d_place = d_place[d_place.index('及') + 4:]
	elif '因' in d_place:
		d_place = d_place[:d_place.index('因')]
	# 除去'址'
	d_place = d_place.replace('址', '')
	# 除去。），；
	d_place_formatted = d_place.replace('。', '').replace('）', '').replace('，', '').replace('；', '')

	# revise
	if '年' in d_place_formatted:
		d_place_formatted = ''
	if '罪' in d_place_formatted:
		d_place_formatted = ''

	return d_place_formatted


def job_name_single_format(job_name):
	"""
	format single job_name
	:param job_name: <str> job_name
	:return: <str> job_name_formatted
	"""
	# 直接抛弃
	# 长度过短(人名、职位简称等)
	if len(job_name) < 8:
		return ''
	if constant.number_pattern.search(job_name):
		return ''
	# 其他情况
	not_job_name_match = constant.format_job_name_pattern.search(job_name)
	if not_job_name_match:
		return ''

	# 格式化
	# 除去括号和其中的内容
	if '（' in job_name:
		job_name_formatted = job_name[:job_name.find('（')]
	else:
		job_name_formatted = job_name
	# 省略第一个顿号及之后的内容
	if '、' in job_name_formatted:
		job_name_formatted = job_name_formatted[:job_name_formatted.find('、')]
	# 除去标点符号
	job_name_formatted = tools.remove_punctuation(job_name_formatted)

	# 再次抛弃长度过短
	if len(job_name_formatted) < 8:
		return ''

	return job_name_formatted


def job_name_output_format(job_names):
	"""
	format job_name for output
	:param job_names: <list> job_names
	:return: <str> job_name_formatted
	"""
	job_name_formatted = '+'.join(job_names[::-1])

	return job_name_formatted


def sum_total_format(sum_list):
	"""
	format sum_list to sum_total
	:param sum_list: <list> get_sum_list() return
	:return: <str> sum_total(like 11.11), unit: ten thousand
	"""
	if len(sum_list) == 0:
		return ''

	sum_total_float = sum(sum_list)
	sum_total = '{0:.2f}'.format(sum_total_float / 10000.00)

	return sum_total


def p_name_format(p_name):
	"""
	format procuratorate_name
	:param p_name: <str> procuratorate_name
	:return: <str> p_name_formatted
	"""
	# 除去括号和其中的内容
	p_name = constant.brackets_pattern.sub('', p_name)
	# 处理含逗号和于的情况
	start_id = p_name.index('，') + 1 if '，' in p_name else 0
	end_id = p_name.index('于') if '于' in p_name else len(p_name)

	p_name_formatted = p_name[start_id:end_id]
	# 舍弃过长
	if len(p_name_formatted) > 30:
		p_name_formatted = ''

	return p_name_formatted
