# -*- coding:utf-8 -*-

# EXCEL输出接口

import xlwings
import shutil
import os
import time
import extract_bribe_infos.constant as constant


INIT_TAG = False
XLSX_PATH = ""  # 保存Excel文件路径
LABEL_DICT = {
	# 在此设置把要素名输出到哪一列
	# 比如，'paper_mark': 'B'把paper_mark输出到B列
}


def open_sheet():
	"""
	open a xlsx app and get workbook, active_sheet
	:return: <xlwings.app> <xlwings.app.books> <xlwings.app.books.sheets>
	"""
	xlsx_app = xlwings.App(visible=False, add_book=False)
	xlsx_app.display_alerts = False
	xlsx_app.screen_updating = False

	workbook = xlsx_app.books.open(XLSX_PATH)
	active_sheet = workbook.sheets['Sheet1']

	if INIT_TAG:
		for paper_id in range(0, constant.PAPER_NUMS):
			range_id = 'A{0}'.format(paper_id + 2)
			active_sheet.range(range_id).value = str(paper_id)
			print('initial column {0}'.format(range_id))

	return xlsx_app, workbook, active_sheet


def output_to_excel(active_sheet, paper_id, **kwargs):
	"""
	output to excel
	:param active_sheet: <xlwings.app.books.sheets>
	:param paper_id: <int> paper_id
	:param kwargs
	:return: <int> 0
	"""
	if len(kwargs) == 0:
		raise ValueError('please set kwargs when output_to_excel')
	labels = []
	for label, value in kwargs.items():
		labels.append(label)
		value = str(value)
		if value == constant.ENDURE_ERROR:
			continue
		if len(value) > 0:
			range_id = LABEL_DICT[label] + str(paper_id + 2)
			active_sheet.range(range_id).value = value
	print('paper_id {0} has inserted into xlsx({1})'.format(paper_id, ','.join(labels)))

	return 0


def close_app_wb(xlsx_app, workbook):
	"""
	save, close workbook and quit app
	:param xlsx_app: <xlwings.app>
	:param workbook: <xlwings.app.books>
	:return: <int> 0
	"""
	workbook.save()
	workbook.close()
	xlsx_app.quit()
	# 保存xlsx文件副本
	shutil.copyfile(
		XLSX_PATH,
		os.path.join(os.path.split(XLSX_PATH)[0], 'shouhui_all_infos_{0}.xlsx'.format(int(time.time())))
	)

	return 0
