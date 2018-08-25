# -*- coding:utf-8 -*-

# 小工具集

import os
import codecs
import time
import datetime
import shutil
import extract_bribe_infos.constant as constant
import extract_bribe_infos.excel_output as excel_output


SUBSTR_BACKUP_BASE_PATH = ""  # 替换字符时的原数据备份路径


def get_now_time():
	"""
	get now time
	:return: <str> year-month-day-hour-minute-second
	"""
	return time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())


def open_paper(paper_path):
	"""
	open paper file and get paper string
	:param paper_path: <str> paper_path
	:return: <str> paper
	"""
	with codecs.open(paper_path, 'r', encoding='utf-8') as f:
		paper = f.read()

	return paper


def write_into_txt(file_content, file_path, open_mode):
	"""
	write content into txt
	:param file_content: <str> file_content
	:param file_path: <str> file_path
	:param open_mode: <str> 'w' or 'a'
	:return: <int> 0
	"""
	if open_mode == 'w' and os.path.exists(file_path):
		raise FileExistsError('{0} already exist'.format(file_path))
	with codecs.open(file_path, open_mode, encoding='utf-8') as f:
		f.write(file_content)

	return 0


def paper_iterator():
	"""
	yield tuple (paper_id, paper_path, paper)
	"""
	for paper_id in range(0, constant.PAPER_NUMS):
		paper_path = os.path.join(constant.DATA_PATH, str(paper_id) + '.txt')
		paper = open_paper(paper_path)
		yield (paper_id, paper_path, paper)


def get_error_info(func, args, kwargs):
	"""
	get error_info when execute endure_error()
	:param func: <func> function that is decorated
	:param args: <tuple> args in function
	:param kwargs: <dict> kwargs in function
	:return: <str> error_info
	"""
	str_args_kwargs = []
	if len(args) > 0:
		str_args_kwargs.extend([str(arg)[:30] for arg in args])
	if len(kwargs) > 0:
		str_args_kwargs.extend([str(kwarg)[:30] for kwarg in kwargs.values()])
	error_info = 'Error excute: {0} & Args or Kwargs: {1} & Time: {2}'.format(
		func.__name__,
		'--'.join(str_args_kwargs),
		time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
	)

	return error_info


def write_endure_error(error_info):
	"""
	write error_info into constant.ENDURE_ERROR_PATH
	:param error_info: <str> error_info
	:return: <int> 0
	"""
	with codecs.open(constant.ENDURE_ERROR_PATH, 'a', encoding='utf-8') as f:
		f.write(error_info)
		f.write("\n")

	return 0


def endure_error(func):
	"""
	decorator, use try except to pass error and record error
	:param func: <func> not paper_divider()
	:return: <func> decorated function
	"""
	def wrapper(*args, **kwargs):

		# 检查接收参数中是否含有endure_error
		if constant.ENDURE_ERROR in args or constant.ENDURE_ERROR in kwargs.values():
			return constant.ENDURE_ERROR

		try:
			result = func(*args, **kwargs)
		except:
			error_info = get_error_info(func, args, kwargs)
			if constant.ENDURE_ERROR_WRITE:
				write_endure_error(error_info)
			if constant.ENDURE_ERROR_PRINT:
				print(error_info)
			# 出错时返回endure_error字符串
			result = constant.ENDURE_ERROR

		return result

	return wrapper


def endure_error_for_paper_divider(func):
	"""
	decorator especially for paper_divider(), use try except to pass error and record error
	:param func: <func> paper_divider
	:return: <func> decorated function
	"""
	def wrapper(*args, **kwargs):

		try:
			result = func(*args, **kwargs)
		except:
			error_info = get_error_info(func, args, kwargs)
			write_endure_error(error_info)
			if constant.ENDURE_ERROR_PRINT:
				print(error_info)
			# 出错时返回只含paper_id的字典
			result = {'paper_id': args[0]}

		return result

	return wrapper


class ExcelContext:
	"""
	Excel context
	"""
	def __init__(self, excel_tag):
		self.excel_tag = excel_tag

	def __enter__(self):
		if self.excel_tag:
			self.xlsx_app, self.workbook, self.active_sheet = excel_output.open_sheet()

		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		if self.excel_tag:
			excel_output.close_app_wb(self.xlsx_app, self.workbook)


def substr_write_backup(paper_id, paper_path, substr_backup_path, paper_new):
	"""
	write new paper into file, and backup old paper into substr_backup_path
	:param paper_id: <int> paper_id
	:param paper_path: <str> paper_path(old) -- file
	:param substr_backup_path: <str> substr_backup_path -- directory
	:param paper_new: <str> new paper
	:return: <int> 0
	"""
	# 移动旧文件(备份)
	shutil.move(paper_path, os.path.join(substr_backup_path, str(paper_id) + '.txt'))
	# 写入新文件
	with codecs.open(paper_path, 'w', encoding='utf-8') as f:
		f.write(paper_new)
	print('at paper_id {0}: substr and backup has done'.format(paper_id))

	return 0


def substr(string, new_string):
	"""
	substitute new_string for string in all papers
	:param string: <str> original string
	:param new_string: <str> new string
	:return: <int> 0
	"""
	total = 0
	substr_backup_path = os.path.join(SUBSTR_BACKUP_BASE_PATH, str(int(time.time())))
	os.makedirs(substr_backup_path)

	for paper_id, paper_path, paper in paper_iterator():
		if string in paper:
			total += 1
			paper_new = paper.replace(string, new_string)
			substr_write_backup(paper_id, paper_path, substr_backup_path, paper_new)
	print('substitute {0} for {1} has done. Total: {2}'.format(string, new_string, total))
	print('substr backup is in {0}'.format(substr_backup_path))

	return 0


def remove_punctuation(text):
	"""
	remove ordinary punctuation
	:param text: <str> text
	:return: <str> text without punctuations
	"""
	punctuations = ['，', '。', '!', '！', '（', '）', '：', '“', '”', '‘', '’']
	for punc in punctuations:
		text = text.replace(punc, '')

	return text


def reserve_only_in(text, char_iter):
	"""
	reserve char only in char_iter(remove char not in char_iter)
	:param text: <str> text
	:param char_iter: <iterable> char in char_iter would be reserved
	:return: <str> reserved_text
	"""
	reserved_text = ''
	for c in text:
		if c in char_iter:
			reserved_text += c

	return reserved_text


def convert_chinese_digits_to_arabic(chinese_digits):
	"""
	convert chinese_digits to arabic(int)
	:param chinese_digits: <str> chinese_digits, like 一万三千 (until 元, not include 角、分)
	:return: <int>
	"""
	result, tmp, hnd_mln = 0, 0, 0
	for curr_char in chinese_digits:
		curr_digit = constant.CHINESE_ARABIC_MAP[curr_char]
		# 处理亿
		if curr_digit == 10 ** 8:
			result = result + tmp
			result = result * curr_digit
			hnd_mln = hnd_mln * 10 ** 8 + result
			result = 0
			tmp = 0
		# 处理万
		elif curr_digit == 10 ** 4:
			result = result + tmp
			result = result * curr_digit
			tmp = 0
		# 处理千、百、十
		elif curr_digit >= 10:
			tmp = 1 if tmp == 0 else tmp
			result = result + curr_digit * tmp
			tmp = 0
		# 处理单独数字
		else:
			tmp = tmp * 10 + curr_digit
	result = result + tmp
	result = result + hnd_mln

	return result


def convert_point_chinese_digits_to_arabic(point_chinese_digits):
	"""
	convert chinese_digits to arabic(int)
	:param point_chinese_digits: <str> chinese_digits, like 1.3万 or 13000.00(only have num and 万)
	:return: <int>
	"""
	# 参数检查(只含数字、小数点和万字)
	for check_char in point_chinese_digits:
		if check_char not in constant.NUM_CHARS:
			if check_char not in ('万', '.'):
				raise ValueError('char {0} of point_chinese_digits {1} is illegal'.format(check_char, point_chinese_digits))

	if '万' in point_chinese_digits:
		float_part = float(point_chinese_digits.replace('万', ''))
		result = int(float_part * 10000)
	else:
		point_pos = point_chinese_digits.find('.')
		int_part = point_chinese_digits[:point_pos]
		result = int(int_part)

	return result


def convert_to_arabic(str_digits):
	"""
	convert str_digits to arabic(int)
	:param str_digits: <str> str_digits, include two kinds: 一万三千(kind_tag=0) or 1.3万(kind_tag=1)
	:return: <int> arabic
	"""
	# 参数检查
	if not isinstance(str_digits, str):
		raise ValueError('{0} is not a string of digits'.format(str_digits))
	kind_tag = 0
	for check_char in str_digits:
		if check_char not in constant.CHINESE_ARABIC_MAP.keys():
			if check_char == '.':
				kind_tag = 1
			else:
				raise ValueError('char {0} of str_digits {1} is illegal'.format(check_char, str_digits))
	# 分类处理
	if kind_tag == 0:
		result = convert_chinese_digits_to_arabic(str_digits)
	else:
		result = convert_point_chinese_digits_to_arabic(str_digits)

	return result


def xnor(a, b):
	"""
	xnor operate
	:param a: <bool> True or False
	:param b: <bool> True or False
	:return: <bool> True or False
	"""
	return (a and b) or (not a and not b)


def look_ahead(context, start, ahead_dict):
	"""
	look ahead for located substr
	:param context: <str> paper context
	:param start: <int> span[0], start index of substr
	:param ahead_dict: <dict> {'num': int, 'char': str, 'request_have': bool}
	:return: <bool> True or False
	"""
	ahead_start = start - ahead_dict['num'] if start - ahead_dict['num'] > -1 else 0
	look_ahead_str = context[ahead_start:start]
	actual_have = ahead_dict['char'] in look_ahead_str

	return xnor(ahead_dict['request_have'], actual_have)


def look_back(context, end, back_dict):
	"""
	look back for located substr
	:param context: <str> paper context
	:param end: <int> span[1], end index of substr
	:param back_dict: <dict> {'num': int, 'char': str, 'request_have': bool}
	:return: <bool> True or False
	"""
	look_back_str = context[end:end + back_dict['num']]
	actual_have = back_dict['char'] in look_back_str

	return xnor(back_dict['request_have'], actual_have)


def look_ahead_back(context, span, ahead_dict, back_dict):
	"""
	look ahead and look back for located substr
	:param context: <str> paper context
	:param span: <tuple> location of substr
	:param ahead_dict: <dict> {'ahead_num': int, 'ahead_char': str, 'ahead_have': bool}
	:param back_dict: <dict> {'back_num': int, 'back_char': str, 'back_have': bool}
	:return: <bool> True or False
	"""
	look_ahead_tag = look_ahead(context, span[0], ahead_dict)
	look_back_tag = look_back(context, span[1], back_dict)

	return look_ahead_tag and look_back_tag


def get_region_grade(region):
	"""
	get region grade
	:param region: <str> string that have region info in it
	:return: <int> 6-未知 5-国家 4-省级 3-地区级 2-县级 1-乡级 0-村级
	"""
	region_grade = 6
	for grade in constant.REGION_GRADE_RANKED:
		search_grade_index = region.find(grade)
		if search_grade_index != -1:
			# 中央特别处理-直接返回
			if grade in ('中国', '全国', '中央', '国家'):
				region_grade = 5
				break
			# 市的特殊处理-降级
			elif grade == '市' and region_grade == 3:
				region_grade = 2
			# 区的特殊处理-升级
			elif grade == '区' and region_grade == 4:
				region_grade = 3
			else:
				# 保证region_grade值递减
				grade_num = constant.REGION_GRADE_DICT[grade]
				if grade_num < region_grade:
					region_grade = grade_num

			region = region[search_grade_index + len(grade):]  # 截取字符串

	return region_grade


def get_time_diff(start_time, end_time):
	"""
	get time difference(days) between start_time and end_time
	:param start_time: <str> start_time
	:param end_time: <str> end_time
	:return: <int> time_diff(days)
	"""
	start_time = datetime.datetime.strptime(start_time, '%Y-%m-%d')
	end_time = datetime.datetime.strptime(end_time, '%Y-%m-%d')
	time_delta = end_time - start_time
	time_diff = time_delta.days if time_delta.days > 0 else -time_delta.days

	return time_diff


def cut_into_sentences(text):

	sentences = constant.split_sentences.split(text)

	return sentences


if __name__ == '__main__':
	pass


