# -*- coding: utf-8 -*-

import os
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from Products.Five.browser import BrowserView
from aws.pdfbook.conversions import makePDF
from aws.pdfbook.config import DOWNLOAD_BUFFER_SIZE


class PdfDownload(BrowserView):

    def handlePDF(self):
        """
        Making and downloading PDF
        """
        html = self._makeHTML()
        context = aq_inner(self.context)
        info = makePDF(html, context, self.request)

        pdf_filepath = info.pdf_filepath
        pdf_filename = os.path.basename(pdf_filepath)
        response = self.request.RESPONSE
        setHeader = response.setHeader
        setHeader('Content-type', 'application/pdf')
        setHeader('Content-length', str(os.stat(pdf_filepath)[6]))
        mode = 'attachment'
        setHeader('Content-disposition',
                  '%s; filename=%s' % (mode, pdf_filename))

        fp = open(pdf_filepath, 'rb')
        while True:
            data = fp.read(DOWNLOAD_BUFFER_SIZE)
            if data:
                response.write(data)
            else:
                break
        fp.close()
        return

    def _makeHTML(self):
        """
        Making HTML
        """
        html_engine = getMultiAdapter((self.context, self.request), name=u'printlayout')
        return html_engine(context=self.context, request=self.request)
