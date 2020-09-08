# import urllib.request, urllib.error, urllib.parse

url = 'http://cftic2.pun.seagate.com:5002/'

# response = urllib.request.urlopen(url)
# webContent = response.read()

# # print(webContent[0:300])

# f = open('obo-t17800628-33.html', 'wb')
# f.write(webContent)
# f.close

# import pdfkit 
# pdfkit.from_url(url,'report.pdf') 
import weasyprint
pdf = weasyprint.HTML(url).write_pdf()
open('report.pdf', 'wb').write(pdf)