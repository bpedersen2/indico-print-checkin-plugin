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

from wtforms.fields.simple import StringField
from wtforms.fields.html5 import URLField
from wtforms.validators import DataRequired, URL

from indico.web.forms.base import FormDefaults, IndicoForm


WEBHOOK_DESC = """Provide an URL to be called as a webhook with the badge pdf
as argument"""

class EventSettingsForm(IndicoForm):
    #event_specific_fields = ['webhookurl']
    webhookurl = URLField(_('webhook-url'), [DataRequired(), URL()], description=WEBHOOK_DESC)
