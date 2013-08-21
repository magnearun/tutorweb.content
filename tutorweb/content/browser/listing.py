from collections import defaultdict
import urllib

from AccessControl import getSecurityManager
from zc.relation.interfaces import ICatalog
from zope.component import getMultiAdapter, getUtility
from zope.app.intid.interfaces import IIntIds

from plone.memoize import view

from Products.CMFCore import permissions
from Products.Five.browser import BrowserView

from tutorweb.content.schema import IQuestion, ICourse


class ListingView(BrowserView):
    """Class for all views that just list sub-content"""
    def questionListing(self):
        """Listing of all question items"""
        listing = self.context.restrictedTraverse('@@folderListing')(
            object_provides=IQuestion.__identifier__,
            sort_on="id",
        )
        out = []
        for o in (l.getObject() for l in listing):
            out.append(dict(
                url=o.absolute_url(),
                id=o.id,
                title=o.Title(),
                timesanswered=o.timesanswered,
                timescorrect=o.timescorrect,
            ))
        return out

    def slideListing(self):
        """Listing of all slide items"""
        listing = self.context.restrictedTraverse('@@folderListing')(
            portal_type="Slide",
            sort_on="id",
        )
        return listing

    @view.memoize
    def lectureListing(self):
        """Listing of all lecture items"""
        listing = self.context.restrictedTraverse('@@folderListing')(
            Type="Lecture",
            sort_on="id",
        )
        out = []
        for o in (l.getObject() for l in listing):
            contentCount = self.contentCount(o)
            out.append(dict(
                url=o.absolute_url(),
                id=o.id,
                title=o.Title(),
                slides=contentCount['Slides'],
                questions=contentCount['Question'],
                pdf=None,  #TODO:
            ))
        return out

    def tutorialListing(self):
        """Listing of all tutorial items"""
        listing = self.context.restrictedTraverse('@@folderListing')(
            Type="Tutorial",
            sort_on="id",
        )
        out = []
        for o in (l.getObject() for l in listing):
            contentCount = self.contentCount(o)
            out.append(dict(
                url=o.absolute_url(),
                id=o.id,
                title=o.Title(),
                language=o.language,
                courses=contentCount['Courses'],
                pdf=None,  #TODO:
                files=contentCount['File'],
                lectures=contentCount['Lecture'],
                author=o.author,
                credits=o.credits,
            ))
        return out

    def fileListing(self):
        """Listing of all file items"""
        listing = self.context.restrictedTraverse('@@folderListing')(
            Type="File",
            sort_on="id",
        )
        out = []
        for l in listing:
            out.append(dict(
                url=l.getURL(),
                title=l.Title(),
            ))
        return out

    def courseListing(self):
        """Listing of all course items"""
        listing = self.context.restrictedTraverse('@@folderListing')(
            Type="Course",
        )
        out = []
        for o in (l.getObject() for l in listing):
            contentCount = self.contentCount(o)
            out.append(dict(
                url=o.absolute_url(),
                id=o.id,
                title=o.Title(),
                tutorials=len(o.tutorials),
                files=contentCount['File'],
            ))
        return out

    def relatedCourses(self):
        """All courses that have this tutorial as part of them"""
        values = getUtility(ICatalog).findRelations(dict(
            to_id=getUtility(IIntIds).getId(self.context),
            from_interfaces_flattened=ICourse,
        ))
        out = []
        for v in values:
            out.append(dict(
                url=v.from_object.absolute_url(),
                title=v.from_object.Title(),
            ))
        return sorted(out, key=lambda k: k['title'])

    def contentCount(self, target):
        """Return counts of child content grouped by portal_type"""
        listing = target.restrictedTraverse('@@folderListing')()
        out = defaultdict(int)
        for l in listing:
            if l.PortalType() in ['tw_latexquestion']:
                #TODO: Should really be checking for IQuestion
                out['Question'] += 1
            else:
                out[l.Type()] += 1
        return out

    def quizUrl(self):
        """Return URL to the quiz for this lecture"""
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state',
        )
        out = portal_state.portal_url()
        out += "/++resource++tutorweb.quiz/load.html?"
        if self.context.portal_type == 'tw_lecture':
            out += urllib.urlencode(dict(
                tutUri=self.context.aq_parent.absolute_url() + '/quizdb-sync',
                lecUri=self.context.absolute_url() + '/quizdb-sync',
            ))
        elif self.context.portal_type == 'tw_tutorial':
            # Start a quiz based on the first lecture
            if len(self.lectureListing()) == 0:
                # No lectures, so it's not going to be a very interesting drill
                return '#'
            out += urllib.urlencode(dict(
                tutUri=self.context.absolute_url() + '/quizdb-sync',
                lecUri=self.lectureListing()[0]['url'] + '/quizdb-sync',
            ))
        else:
            raise NotImplemented
        return out

    def canEdit(self):
        """Return true iff user can edit context"""
        return getSecurityManager() \
            .checkPermission(permissions.ModifyPortalContent, self)
