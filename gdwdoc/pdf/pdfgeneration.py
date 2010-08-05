# -*- coding: utf-8 -*-

import os
import tempfile
from DateTime import DateTime
from zope.app.component.interfaces import ISite

PDF_PREFIX = "Gites-de-Wallonie"


def initFileSystemInfo(self, context):
    self.tmp_dir = tempfile.mkdtemp()
    self.html_filename = os.path.join(self.tmp_dir, context.getId() + '.html')
    filename_path = ""

    # parent id is not used if document is at root level
    if ISite.providedBy(context.aq_parent):
        filename_path = context.getId()
    else:
        filename_path = "%s-%s" % (context.aq_parent.getId(), context.getId())

    self.pdf_filename = '%s-%s-%s.pdf' % (PDF_PREFIX,
                                          filename_path,
                                          DateTime().strftime('%d-%m-%Y'))
    self.pdf_filepath = os.path.join(self.tmp_dir, self.pdf_filename)
    return
