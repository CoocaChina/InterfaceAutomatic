#?/bin/usr/python
#-*- coding: utf-8 -*-
import os,sys
import xlrd
import xlwt
import logging
import logging.config
import xlwings as xw
from xlutils.copy import copy
class openExcel():
	def openExcel(self, fname,sheetname):     #fname文件路径，sheetname：测试用例sheet页名称
		bk = xlrd.open_workbook(fname)
		shxrange = range(bk.nsheets)
		try:
			sh = bk.sheet_by_name(sheetname)
		except:
			print ("no sheet in %s named mobilerecharge" % fname)
		#获取行数
		nrows = sh.nrows
		#获取列数
		ncols = sh.ncols
		return sh

	def ExcelParam(self, fname, sheetname):  # fname文件路径，sheetname：测试用例sheet页名称
		fname = fname
		bk = xlrd.open_workbook(fname)
		shxrange = range(bk.nsheets)
		try:
			sh = bk.sheet_by_name(sheetname)
		except:
			print ("no sheet in %s named mobilerecharge" % fname)
		# 获取行数
		nrows = sh.nrows
		# 获取列数
		ncols = sh.ncols
		exlParam = {}
		exllist = []
		for rownum in range(0, ncols):
			if rownum < ncols-1:
				exlData = sh.cell_value(0,rownum+1)
				exlValue = sh.cell_value(1,rownum+1)
				exllist.append (exlData)
				exlParam[exlData] = exlValue
		return exlParam
	def getParamByCaseID(self, fname, sheetname,caseID):  # fname文件路径，sheetname：测试用例sheet页名称,caseID 获取某个caseid的参数
		fname = fname
		caseID = caseID
		bk = xlrd.open_workbook(fname)
		shxrange = range(bk.nsheets)
		try:
			sh = bk.sheet_by_name(sheetname)
		except:
			print ("no sheet in %s named mobilerecharge" % fname)
		# 获取行数
		nrows = sh.nrows
		# 获取列数
		ncols = sh.ncols
		caseParam = {}
		caselist = []
		for rownum in range(1,nrows):
			if rownum <nrows:
				if int(sh.cell_value(rownum,0))== int(caseID):
					for colNum in range(2, ncols):
						if colNum < ncols:
							exlData = sh.cell_value(0, colNum)
							exlValue = sh.cell_value(rownum, colNum)
							caselist.append(exlData)
							caseParam[exlData] = exlValue
							#caseParam = eval(str(caseParam).replace('u',''))
							#exec('caseParam=',eval(str(caseParam).replace('u','')))
							#print caseParam
					return caseParam
			else:
				print ("There have no this case!")

	def getParamByRowID(self, fname, sheetname, rowID):  # fname文件路径，sheetname：测试用例sheet页名称,caseID 获取某个caseid的参数
		fname = fname
		rownum = rowID
		bk = xlrd.open_workbook(fname, formatting_info=True)
		shxrange = range(bk.nsheets)
		try:
			sh = bk.sheet_by_name(sheetname)
		except:
			print ("no sheet in %s named mobilerecharge" % fname)
		# 获取行数
		nrows = sh.nrows
		if rownum > nrows + 1:
			print ('该表格中没有这一列！')
			return {}
		# 获取列数
		ncols = sh.ncols
		print (ncols)
		caseParam = {}
		caselist = []
		for colNum in range(1, ncols):
			if colNum < ncols:
				exlData = sh.cell_value(0, colNum)
				exlValue = sh.cell_value(rownum, colNum)
				caselist.append(exlData)
				caseParam[exlData] = exlValue
		return caseParam
	def openTxtFile(self,txtPath):
		f = open(txtPath)
		#print type(f)
		line = f.readline()
		return line
		f.close()

	def readxtFile(self, txtPath):
		f = open(txtPath)
		# print type(f)
		line = f.readline()
		txt = f.readlines()
		return txt
		f.close()
	def whriteExcel(self,fname, sheetname,caseID,colName,colValue):
		fname = fname
		caseRowNum=0
		caseColNum=0
		colValue=colValue
		#rowNum = 0
		#colNum=0
		fname = fname
		caseID = caseID
		bk = xlrd.open_workbook(fname,formatting_info=True)
		count = len(bk.sheets())
		# print count
		shxrange = range(bk.nsheets)
		try:
			sh = bk.sheet_by_name(sheetname)
			#sh = bk.sheet_by_name("userRegister")
			count = sh.number
			# print(count)
		except:
			print("no sheet in %s named mobilerecharge" % fname)
		# 获取行数
		nrows = sh.nrows
		# print nrows
		# 获取列数
		ncols = sh.ncols
		# print(nrows)
		# print(ncols)
		for rowNum in range(1,nrows):
			if rowNum <nrows and (str(sh.cell_value(rowNum, 0)) == str(caseID)):
				caseRowNum = rowNum
		for colNum in range(0, ncols):
			if colNum < ncols and (str(sh.cell_value(0, colNum)) == str(colName)):
				caseColNum = colNum
		# print (caseColNum)
		# print (caseRowNum)
		if caseColNum!=0 and caseRowNum!=0:
			w = copy(bk)
			w.get_sheet(count).write(int(caseRowNum), int(caseColNum), colValue)
			w.save(fname)
	def whriteXLWexcel(self,fname,sheetname,cellsite,cellvalue):
		app = xw.App(visible=False, add_book=False)
		wb = app.books.open(fname)
		# wb就是新建的工作簿(workbook)，下面则对wb的sheet1的A1单元格赋值
		wb.sheets[sheetname].range(cellsite).value = cellvalue
		wb.save()
		wb.close()
		app.quit()
if __name__ == '__main__':
	test1 = openExcel()
	#print test1.ExcelParam('../data/TestData.xlsx','mobilerecharge')
	#print test1.getParamByCaseID('../data/TestData_Wujy.xls','getAuthCode','1')
	#test1.whriteExcel('../data/TestData_Wujy.xls','getAuthCode','1','result','pass')
	fname = ("../data/TestData_shijf.xls")
	sheetname = ("train_ticket_case")
	cellsite = 'B2'
	cellvalue = '测试111111'
	test1.whriteXLWexcel(fname,sheetname,cellsite,cellvalue)



