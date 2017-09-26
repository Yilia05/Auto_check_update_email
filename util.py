# -*- coding=utf-8 -*-
def blocks(context):
    blocks = []
    block = []
    for line in context:
        if line.strip():
            block.append(line)
            print block
        else:
            blocks.append(block)
            block = []
    return blocks


def to_html(context):
    # file = 'test.txt'
    body = '<html><head><title>send html test page</title></head><body><table border="1">'
    for block in blocks(context):
        if len(block):
            body += '<tr>'
            body += ('<td><b>' + block[0] + '</td><td>')
            # print '<td>' + block[1:] + '</td>'
            for i in range(1, block.__len__()):
                body += (block[i]+'<br />')
            body += '</td></tr>'
    body += '</table></body></html>'
    return body

