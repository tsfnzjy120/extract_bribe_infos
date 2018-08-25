# -*- coding:utf-8 -*-

# 样本预处理、更新样本数量

import os
import codecs
import shutil
import itertools
import re
from win32com import client as w32c
import docx as pydocx
import extract_bribe_infos.tools as tools
import extract_bribe_infos.constant as constant
from extract_bribe_infos.parser.pre_extract import get_paper_mark


MOVE_LIST = []  # paper_id 要删除的文本ID
WORD_PATH = ''  # Word文件所在路径
TXT_PATH = ''  # TXT文件所在路径
ADD_PAPER_PATH = ''  # 要新增的文件所在路径


def get_file_num(data_path):
	"""
	get file_num in data path
	:param data_path: <str> data_path
	:return: <int> file_num
	"""
	if not os.path.isdir(data_path):
		raise Exception('{0} does not exist or is not a directory'.format(data_path))
	file_num = -1
	for root, dirs, files in os.walk(data_path):
		file_num = len(files)

	return file_num


def move_paper(move_list):
	"""
	:param move_list: <list> papers to move to trash_paper
	:return: <int> 0
	"""
	for paper_id in move_list:
		file_name = str(paper_id) + '.txt'
		file_path = os.path.join(constant.DATA_PATH, file_name)
		move_to_path = os.path.join(constant.TRASH_PATH, file_name)
		shutil.move(file_path, move_to_path)
		print('move {0} to trash_paper'.format(file_name))

	return 0


def rename_paper(data_path):
	"""
	rename all paper file
	:param data_path: <str> data_path
	:return: <int> paper_nums
	"""
	if not os.path.isdir(data_path):
		raise Exception('{0} does not exist or is not a directory'.format(data_path))
	print('renaming papers...')
	# 第一次改名: P0, P1, P2...(避免文件名冲突)
	counter = 0
	for root, dirs, files in os.walk(data_path):
		for file in files:
			file_path = os.path.join(data_path, file)
			re_file_path = os.path.join(data_path, 'P' + str(counter) + '.txt')
			os.rename(file_path, re_file_path)
			print('first rename done at P{0}'.format(counter))
			counter += 1
	# 第二次改名: 0, 1, 2...(去掉P)
	for p_id in range(0, counter):
		file_path = os.path.join(data_path, 'P' + str(p_id) + '.txt')
		re_file_path = os.path.join(data_path, str(p_id) + '.txt')
		os.rename(file_path, re_file_path)
		print('second rename done at {0}'.format(p_id))
	print('rename papers done. total: {0}'.format(counter))

	return counter


def re_arrange_paper(move_list):
	"""
	rearrange paper files
	:param move_list: <list> for move_paper use
	:return: <int> 0
	"""
	move_paper(move_list)
	rename_paper(constant.DATA_PATH)
	print('please alter constant PAPER_NUMS in constant.py')

	return 0


def read_docx(docx_path):
	"""
	read .docx
	:param docx_path: <str> docx_path
	:return: <str> docx_content
	"""
	if not os.path.exists(docx_path):
		raise FileNotFoundError('{0} does not exist'.format(docx_path))
	docx = pydocx.Document(docx_path)
	paras = docx.paragraphs
	full_text = [p.text for p in paras]

	return ''.join(full_text)


def docx_to_txt(word_path, txt_path, word_id=0):
	"""
	write .txt paper in txt_path, using .docx in word_path
	:param word_path: <str> .docx or .doc directory
	:param txt_path: <str> .txt directory
	:param word_id: <int> word_id
	:return: <int> word_id
	"""
	if not os.path.isdir(word_path):
		raise Exception('{0} is not a directory or does not exist!'.format(word_path))
	if not os.path.isdir(txt_path):
		raise Exception('{0} is not a directory or does not exist!'.format(txt_path))
	for root, dirs, files in os.walk(word_path):
		for file in files:
			ext = os.path.splitext(file)[1]
			if ext == '.docx':
				docx_path = os.path.join(root, file)
				if os.path.exists(docx_path):
					docx_content = read_docx(docx_path)
					tools.write_into_txt(docx_content, os.path.join(txt_path, str(word_id) + '.txt'), 'w')
					print('{0} has turned to {1}'.format(file, str(word_id) + '.txt'))
					word_id += 1

	return word_id


def read_doc(word_app, doc_path):
	"""
	read .doc
	:param word_app: <w32c.Dispatch()> word_app
	:param doc_path: <str> doc_path file
	:return: <int> 0
	"""
	if not os.path.exists(doc_path):
		raise FileNotFoundError('{0} not found'.format(doc_path))
	doc = word_app.Documents.Open(doc_path)
	temp_txt_path = os.path.join(os.path.split(doc_path)[0], 'temp.txt')
	doc.SaveAs(temp_txt_path, 4)  # 另存为temp.txt
	doc.Close()
	with codecs.open(temp_txt_path, 'r', encoding='gbk') as f:
		doc_content = f.read()
	os.remove(temp_txt_path)

	return doc_content


def doc_to_txt(word_path, txt_path, word_id=0):
	"""
	convert .doc into txt, from word_path to txt_path
	:param word_path: <str> .docx or .doc directory
	:param txt_path: <str> .txt directory
	:param word_id: <int> word_id
	:return: <int> word_id
	"""
	# 目录存在性检查
	if not os.path.isdir(word_path):
		raise Exception('{0} is not a directory or does not exist!'.format(word_path))
	if not os.path.isdir(txt_path):
		raise Exception('{0} is not a directory or does not exist!'.format(txt_path))
	# 初始化word_app
	word_app = w32c.Dispatch('Word.Application')
	word_app.Visible = False
	word_app.DisplayAlerts = False
	word_app.ScreenUpdating = False
	# 搜索doc并处理
	for root, dirs, files in os.walk(word_path):
		for file in files:
			ext = os.path.splitext(file)[1]
			if ext == '.doc':
				doc_path = os.path.join(root, file)
				doc_content = read_doc(word_app, doc_path)
				tools.write_into_txt(doc_content, os.path.join(txt_path, str(word_id) + '.txt'), 'w')
				print('{0} has turned to {1}'.format(file, str(word_id) + '.txt'))
				word_id += 1
	word_app.Quit()

	return word_id


def rename_word_in_path(word_path):
	"""
	rename .doc and .docx in word_path
	:param word_path: <str> .doc or .docx directory
	:return: <int> 0
	"""
	print('wait for renaming word files in {0}...'.format(word_path))
	file_name_tpl = 'rename_word_'
	cnt = 0
	for root, dirs, files in os.walk(word_path):
		for file in files:
			file_path = os.path.join(root, file)
			file_ext = os.path.splitext(file_path)[1]
			new_file_path = os.path.join(root, file_name_tpl + str(cnt) + file_ext)
			os.rename(file_path, new_file_path)
			cnt += 1
	print('rename word files in {0} done. Total: {1}'.format(word_path, cnt))

	return 0


def word_to_txt(word_path, txt_path):
	"""
	write .txt paper at txt_path, using all .docx or .doc in word_path
	:param word_path: <str> .docx or .doc directory
	:param txt_path: .txt directory
	:return: <int> 0
	"""
	if not os.path.isdir(word_path):
		raise Exception('{0} is not a directory or does not exist!'.format(word_path))
	if not os.path.isdir(txt_path):
		raise Exception('{0} is not a directory or does not exist!'.format(txt_path))

	# 文件重命名(避免文件名的编码、空格等问题)
	rename_word_in_path(word_path)

	# docx先处理
	word_id = docx_to_txt(word_path, txt_path)
	docx_num = word_id

	# doc后处理
	word_id = doc_to_txt(word_path, txt_path, word_id)
	doc_num = word_id - docx_num

	print('word to txt done. docx: {0}  doc: {1}'.format(docx_num, doc_num))

	return 0


def paper_washer_single(raw_paper):
	"""
	wash paper
	:param raw_paper: <str> raw paper
	:return: <str> paper
	"""
	# 去除空格
	raw_paper = raw_paper.replace(' ', '')
	raw_paper = raw_paper.replace('　', '')
	# 去除BOM头
	if raw_paper[:3] == codecs.BOM_UTF8:
		raw_paper = raw_paper[3:]
	# 去除不可见字符
	for i in range(0, 33):
		raw_paper = raw_paper.replace(chr(i), '')
	# 格式化英文引号
	chinese_quotations = itertools.cycle(['“', '”'])
	# 英文双引号转中文双引号
	raw_paper = re.sub(r'"', lambda q1: chinese_quotations.__next__(), raw_paper)
	# 英文单引号转中文双引号
	raw_paper = re.sub(r"'", lambda q2: chinese_quotations.__next__(), raw_paper)
	# 英文逗号转中文逗号 + 英文冒号转中文冒号 + 英文括号转中文括号
	raw_paper = raw_paper.replace(',', '，').replace(':', '：').replace('(', '（').replace(')', '）')

	return raw_paper


def paper_washer_in_path(raw_paper_path, dest_path):
	"""
	wash all papers in raw_paper_path
	:param raw_paper_path: <str> raw_paper_path
	:param dest_path: <str> dest_path(store new paper)
	:return: <int> 0
	"""
	if not os.path.isdir(raw_paper_path):
		raise Exception('{0} does not exist or is not a directory'.format(raw_paper_path))
	if not os.path.isdir(dest_path):
		raise Exception('{0} does not exist or is not a directory'.format(dest_path))
	for root, dirs, files in os.walk(raw_paper_path):
		for file in files:
			file_path = os.path.join(root, file)
			paper = tools.open_paper(file_path)
			paper = paper_washer_single(paper)
			tools.write_into_txt(paper, os.path.join(dest_path, file), 'w')
			print('wash paper for {0}'.format(file_path))

	return 0


def add_paper(data_path, add_paper_path):
	"""
	add paper(in add_paper_path) into data_path
	:param data_path: <str> data_path
	:param add_paper_path: <str> add_paper_path
	:return: <int> 0
	"""
	if not os.path.isdir(data_path):
		raise Exception('{0} does not exist or is not a directory'.format(data_path))
	if not os.path.isdir(data_path):
		raise Exception('{0} does not exist or is not a directory'.format(add_paper_path))
	add_paper_id = get_file_num(data_path)
	for root, dirs, files in os.walk(add_paper_path):
		for file in files:
			file_path = os.path.join(root, file)
			file_content = tools.open_paper(file_path)
			added_file_path = os.path.join(data_path, str(add_paper_id) + '.txt')
			tools.write_into_txt(file_content, added_file_path, 'w')
			print('add paper from {0} to {1}'.format(file_path, added_file_path))
			add_paper_id += 1
	print('add paper done. Total: {0}'.format(add_paper_id))
	print('please revise PAPER_NUMS in constant.py')

	return 0


def get_repeat_papers(paper_path):
	"""
	get repeat paper_ids (use paper_mark)
	:param paper_path: <str> paper_path
	:return: <list> paper_repeat_ids
	"""
	if not os.path.isdir(paper_path):
		raise Exception('{0} does not exist or is not a directory'.format(paper_path))
	print('get paper_repeat_ids starts. This may take a little long time...')
	paper_repeat_ids = []
	paper_marks = []
	for root, dirs, files in os.walk(paper_path):
		for file in files:
			file_path = os.path.join(root, file)
			file_content = tools.open_paper(file_path)
			paper_mark = get_paper_mark(file_content)

			if paper_mark in paper_marks:
				paper_id = int(os.path.splitext(file)[0])
				print('get repeat paper id {0}'.format(paper_id))
				paper_repeat_ids.append(paper_id)
			else:
				paper_marks.append(paper_mark)

	paper_repeat_num = len(paper_repeat_ids)
	print('get paper_repeat_ids done. Total: {0}'.format(paper_repeat_num))
	print(paper_repeat_ids)

	return paper_repeat_ids


def remove_repeat_papers(paper_path):
	"""
	remove repeat paper and rename
	:param paper_path: <str> paper_path (must use constant.DATA_PATH because of re_arrange_paper() )
	:return: <int> 0
	"""
	paper_repeat_ids = get_repeat_papers(paper_path)
	print('removing repeat papers...')
	re_arrange_paper(paper_repeat_ids)
	print('remove repeat papers done. Total: {0}'.format(len(paper_repeat_ids)))

	return 0


def judge_not_shouhui(paper_id, paper):
	"""
	judge paper is shouhui or not
	排除五种情况：(0)不是判决书(1)不构成受贿罪(2)构成非国家工作人员受贿罪(3)构成单位受贿罪(4)二审、再审
	:param paper_id: <int> paper_id
	:param paper: <str> file_content
	:return: <int> not_shouhui_tag(0 for shouhui, 1 for not shouhui)
	"""
	not_shouhui_tag = 0
	if '判决书' not in paper:
		not_shouhui_tag = 1
		print('paper_id {0} is not shouhui: {1}'.format(paper_id, '不是判决书'))
	elif '犯受贿罪' not in paper:
		not_shouhui_tag = 1
		print('paper_id {0} is not shouhui: {1}'.format(paper_id, '不构成受贿罪'))
	elif '犯非国家工作人员受贿罪' in paper:
		not_shouhui_tag = 1
		print('paper_id {0} is not shouhui: {1}'.format(paper_id, '构成非国家工作人员受贿罪'))
	elif '单位受贿罪' in paper:
		not_shouhui_tag = 1
		print('paper_id {0} is not shouhui: {1}'.format(paper_id, '构成单位受贿罪'))
	elif '上诉人' in paper or '原审' in paper:
		not_shouhui_tag = 1
		print('paper_id {0} is not shouhui: {1}'.format(paper_id, '二审、再审'))

	return not_shouhui_tag


def remove_not_shouhui(paper_path):
	"""
	remove not official shouhui
	:param paper_path: <str> paper_path (must use constant.DATA_PATH because of re_arrange_paper() )
	:return: <int> 0
	"""
	print('get paper_not_shouhui_ids...')
	paper_not_shouhui_ids = []
	for root, dirs, files in os.walk(paper_path):
		for file in files:
			paper_id = int(os.path.splitext(file)[0])
			file_path = os.path.join(root, file)
			file_content = tools.open_paper(file_path)
			if judge_not_shouhui(paper_id, file_content) == 1:
				paper_not_shouhui_ids.append(paper_id)
	print('removing not_shouhui papers...')
	re_arrange_paper(paper_not_shouhui_ids)
	print('remove not_shouhui papers done. Total: {0}'.format(len(paper_not_shouhui_ids)))


if __name__ == '__main__':
	pass
	# re_arrange_paper(MOVE_LIST)
	# word_to_txt(WORD_PATH, TXT_PATH)
	# paper_washer_in_path(TXT_PATH, ADD_PAPER_PATH)
	# add_paper(constant.DATA_PATH, ADD_PAPER_PATH)
	# remove_repeat_papers(constant.DATA_PATH)
	# remove_not_shouhui(constant.DATA_PATH)

