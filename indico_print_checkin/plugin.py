# This file is part of Indico.
# Copyright (C) 2017 Bjoern Pedersen.
#
# Indico is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# Indico is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Indico; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals

import requests
from flask import json, session
from sqlalchemy.orm import joinedload

from indico.core import signals

from indico.core.logger import Logger
from indico.core.plugins import IndicoPlugin, url_for_plugin
from indico.web.menu import SideMenuItem
from indico.modules.events.features.util import is_feature_enabled
from indico.modules.events.registration.badges import RegistrantsListToBadgesPDF, RegistrantsListToBadgesPDFFoldable
from indico.modules.events.registration.util import build_registration_api_data, get_event_section_data
from indico.util.string import slugify



from indico_print_checkin import _, print_checkin_event_settings
from indico_print_checkin.blueprint import blueprint

logger = Logger.get('print_checkin')

class PrintCheckinPlugin(IndicoPlugin):
    """Print on Checkin Plugin

    Triggers a webhook with an registration badge.
    """
    configurable = True

    def init(self):
        super(PrintCheckinPlugin, self).init()
        self.connect(signals.menu.items, self.extend_event_management_menu,
                     sender='event-management-sidemenu')

        self.connect(signals.event.registration.registration_checkin_updated,
                     self._handle_checkin)

    def _mode(self, registration):
        if print_checkin_event_settings.get(registration.event, 'send_json'):
            return 'json'
        return 'pdf'

    def _wh_url(self, registration):
        return print_checkin_event_settings.get(registration.event, 'webhookurl')

    def _send_json(self, registration):
        try:
            event=registration.event
            fullreg = (event.registrations
                       .filter_by(id=registration.id,
                                  is_deleted=False)
                       .options(joinedload('data').joinedload('field_data'))
                       .first_or_404())
            data = self.build_registration_data(fullreg)
            requests.post(self._wh_url(registration), data = json.dumps(data),
                          headers= {'Content-Type': 'application/json'})
        except Exception as e:
            logger.warn(_('Could not send data (%s)'), e)

    def build_registration_data(self, reg):
        data = build_registration_api_data(reg)
        data['data_by_id'] = {}
        data['data_by_name'] = {}
        for field_id, item in reg.data_by_field.iteritems():
            data['data_by_id'][field_id] = item.friendly_data
        for item in reg.data:
            fieldname = slugify(item.field_data.field.title)
            fieldparent = slugify(item.field_data.field.parent.title)
            data['data_by_name']['{}_{}'.format(fieldparent, fieldname)] = item.friendly_data
        return data

    def send_pdf(self, registration):
        try:

            fname = 'print-' + str(registration.id) + '.pdf'
            files = {'file': (fname, pdf, 'application/pdf', {'Expires': '0'})}
            pdf = generate_ticket(registration)
            requests.post(self._wh_url(registration), files=files)
        except Exception as e:
            logger.warn(_('Could not print the checkin badge (%s)'), e)

    def _handle_checkin(self, registration, **kwargs):
        if is_feature_enabled(registration.event, 'print_checkin') and registration.checked_in:
            mode = self._mode(registration)
            if self._mode(registration) == 'json':
                self._send_json(registration)
            elif mode == 'pdf':
                self._send_pdf(registration)

    @property
    def logo_url(self):
        return url_for_plugin(self.name + '.static', filename='images/logo.png')

    def get_blueprints(self):
        return blueprint

    def extend_event_management_menu(self, sender, event, **kwargs):
        if event.can_manage(session.user):
            return SideMenuItem('BadgeOnCheckin', _('Bagde On Checkin Printing'),
                                url_for_plugin('print_checkin.configure', event),
                                section='services')

    def get_event_management_url(self, event, **kwargs):
        if event.can_manage(session.user):
            return url_for_plugin('print_checkin.configure', event)


def generate_ticket(registration):
    """Mostly copied from indico.module.events.registration.utils, but different ticket
       template resolution
    """

    from indico.modules.designer.util import get_default_template_on_category
    from indico.modules.events.registration.controllers.management.tickets import DEFAULT_TICKET_PRINTING_SETTINGS
    # default is A4


    template = print_checkin_event_settings.get(registration.event, 'ticket_template')
    if not template:
        template = (registration.registration_form.ticket_template or
                    get_default_template_on_category(registration.event.category))

    signals.event.designer.print_badge_template.send(template, regform=registration.registration_form)
    pdf_class = RegistrantsListToBadgesPDFFoldable if template.backside_template else RegistrantsListToBadgesPDF
    pdf = pdf_class(template, DEFAULT_TICKET_PRINTING_SETTINGS, registration.event, [registration.id])
    return pdf.get_pdf()
