from collections import defaultdict
import urllib

from AccessControl import getSecurityManager
from zope.component import getMultiAdapter

from Products.CMFCore import permissions
from Products.Five.browser import BrowserView

from tutorweb.content.schema import IQuestion


class ListingView(BrowserView):
    """Class for all views that just list sub-content"""
    def questionListing(self):
        """Listing of all question items"""
        listing = self.context.restrictedTraverse('@@folderListing')(
            object_provides=IQuestion.__identifier__,
        )
        return listing

    def slideListing(self):
        """Listing of all slide items"""
        listing = self.context.restrictedTraverse('@@folderListing')(
            portal_type="Slide",
        )
        return listing

    def lectureListing(self):
        """Listing of all lecture items"""
        listing = self.context.restrictedTraverse('@@folderListing')(
            portal_type="tw_lecture",
        )
        return listing

    def tutorialListing(self):
        """Listing of all tutorial items"""
        listing = self.context.restrictedTraverse('@@folderListing')(
            portal_type="tw_tutorial",
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
                code=o.code,
                pdf=None,  #TODO:
                files=contentCount['File'],
                lectures=contentCount['Lecture'],
                author=o.author,
                credits=o.credits,
            ))
        return out

    def contentCount(self, target):
        """Return counts of child content grouped by portal_type"""
        listing = target.restrictedTraverse('@@folderListing')()
        out = defaultdict(int)
        for l in listing:
            out[l.Type()] += 1
        return out

    def courseListing(self):
        """Listing of all course items"""
        listing = self.context.restrictedTraverse('@@folderListing')(
            portal_type="Course",
        )
        return listing

    def quizUrl(self):
        """Return URL to the quiz for this lecture"""
        portal_state = getMultiAdapter(
            (self.context, self.request),
            name=u'plone_portal_state',
        )
        out = portal_state.portal_url()
        out += "/++resource++tutorweb.quiz/load.html?"
        out += urllib.urlencode(dict(
            tutUri=self.context.aq_parent.absolute_url() + '/quizdb-sync',
            lecUri=self.context.absolute_url() + '/quizdb-sync',
        ))
        return out

    def canEdit(self):
        """Return true iff user can edit context"""
        return getSecurityManager() \
            .checkPermission(permissions.ModifyPortalContent, self)
