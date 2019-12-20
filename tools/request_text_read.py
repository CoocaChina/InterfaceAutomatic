# ?/bin/usr/python
# -*- coding: utf-8 -*-
# import sysconfig


def request_text_read(txtpath):
    with open(txtpath) as read_file:
        content = read_file.read()
        print(read_file)
        for line in read_file:
            print(line.rstrip())
        # print(content)
    # for line in rate1:
    #     line = line.strip().split(':')
    #     dic[line[0]] = line[1].replace(' ', '')
    # return dic
    # print(dic)


def open_txt(textpath):
    f = open(textpath)
    lines = f.readlines()
    print(lines)
    f.close()


if __name__ == '__main__':
    open_txt("D:\\soft\\request\\0_Request.txt")
