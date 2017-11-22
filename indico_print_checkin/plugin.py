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

from __future__ import unicode_literals, print_function

from wtforms.fields.simple import TextField
from wtforms.validators import DataRequired

from indico.core import signals
from indico.core.logger import Logger
from indico.core.plugins import IndicoPlugin, IndicoPluginBlueprint, url_for_plugin
from indico.web.forms.base import FormDefaults, IndicoForm

from indico_print_checkin import _

WEBHOOK_DESC = """Provide an URL to be called as a webhook with the badge pdf
as argument"""

class EventSettingsForm(IndicoForm):
    webhookurl = TextField(_('webhook-url'), [DataRequired()])

    def __init__(self, *args, **kwargs):
        super(EventSettingsForm, self).__init__(*args, **kwargs)
        self.webhookurl.description = WEBHOOK_DESC + '\n'

class PrintCheckinPlugin(IndicoPlugin):
    """Print on Checkin Plugin

    Triggers a webhook with an registration badge.
    """
    configurable = True
    event_settings_form = EventSettingsForm
    default_event_settings = { 'webhookurl' : '' }

    def init(self):
        super(PrintCheckinPlugin, self).init()
        self.connect(signals.event.registration.registration_checkin_updated,
                     self._handle_checkin)

    def _handle_checkin(self, registration, **kwargs):
        print('%r' % registration)


    @property
    def logo_url(self):
        return url_for_plugin(self.name + '.static', filename='images/logo.png')

    def get_blueprints(self):
        return IndicoPluginBlueprint('print_checkin', __name__)

