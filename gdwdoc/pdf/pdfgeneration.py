# -*- coding: utf-8 -*-

import os
import shutil
import tempfile
from DateTime import DateTime
from zope.app.component.interfaces import ISite
from zope.app.component.hooks import getSite
from Products.CMFCore.utils import getToolByName

from aws.pdfbook import logger

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


def saveImagesRecodeParser(self, context):
    """Save images from ZODB to temp directory
    """
    portal = getSite()
    portal_url = portal.absolute_url()
    if not portal_url.endswith('/'):
        portal_url += '/'
    portal_path = '/'.join(portal.getPhysicalPath())
    context_path = '/'.join(context.getPhysicalPath())

    reference_tool = getToolByName(portal, 'reference_catalog')
    for filename, image in self.images:

        # Traverse methods mess with unicode
        if type(image) is unicode:
            image = str(image)
        path = image.replace(portal_url, '')
        #filename = os.path.basename(path)

        item = None
        # using uid
        if image.find('resolveuid') != -1:
            uuid = image.split('/')[-1]
            item = reference_tool.lookupObject(uuid)
            logger.debug("Get image from uid %s", uuid)

        if not item:
            # relative url
            try:
                item = context.restrictedTraverse(image)
                logger.debug("Get image from context")
            except:
                logger.debug("Failed to get image from context path %s",
                             image)
        if not item:
            # absolute url
            image_path = '/'.join((portal_path, path))
            try:
                item = portal.restrictedTraverse(image_path)
                logger.debug("Get image from portal")
            except:
                logger.debug("Failed to get image from portal path %s",
                             image_path)
                continue

        # Eek, we should put an adapter for various image providers (overkill ?).
        data = ''
        if item.meta_type in ('Portal Image', 'Image', 'ATBlob'):
            data = item.data
        elif item.meta_type == 'ATImage':
            data = item.getImage()
            data = getattr(item, 'data', data)
        elif item.meta_type == 'Filesystem Image':
            imagePath = item.filename
            shutil.copy(imagePath, os.path.join(self.fsinfo.tmp_dir, filename))

        if data:
            image_file = open(os.path.join(self.fsinfo.tmp_dir, filename), 'wb')
            image_file.write(str(data))
            image_file.close()
    return
