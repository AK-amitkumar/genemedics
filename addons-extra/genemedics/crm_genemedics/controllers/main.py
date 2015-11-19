import json
import openerp
import openerp.http as http
from openerp.http import request
import openerp.addons.web.controllers.main as webmain
import json


class meeting_invitation_npg(openerp.addons.calendar.controllers.main.meeting_invitation):

    @http.route('/calendar/meeting/accept', type='http', auth="calendar")
    def accept(self, db, token, action, id, **kwargs):
        registry = openerp.modules.registry.RegistryManager.get(db)
        attendee_pool = registry.get('calendar.attendee')
        with registry.cursor() as cr:
            attendee_id = attendee_pool.search(cr, openerp.SUPERUSER_ID, [('access_token', '=', token), ('state', '!=', 'accepted')])
            if attendee_id:
                attendee_pool.do_accept(cr, openerp.SUPERUSER_ID, attendee_id)
                        
        SIMPLE_TEMPLATE = """
<html>
<head>
 <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
 <meta http-equiv="content-type" content="text/html; charset=utf-8" />
 <title>Meeting accepted</title>
</head>
<body>
<b>Meeting accepted</b>
</body>
</html>
"""
        return SIMPLE_TEMPLATE

    @http.route('/calendar/meeting/decline', type='http', auth="calendar")
    def declined(self, db, token, action, id):
        registry = openerp.modules.registry.RegistryManager.get(db)
        attendee_pool = registry.get('calendar.attendee')
        with registry.cursor() as cr:
            attendee_id = attendee_pool.search(cr, openerp.SUPERUSER_ID, [('access_token', '=', token), ('state', '!=', 'declined')])
            if attendee_id:
                attendee_pool.do_decline(cr, openerp.SUPERUSER_ID, attendee_id)
#         return self.view(db, token, action, id, view='form')

        SIMPLE_TEMPLATE = """
<html>
<head>
 <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
 <meta http-equiv="content-type" content="text/html; charset=utf-8" />
 <title>Meeting Declined</title>
</head>
<body>
<b>Meeting Declined</b>
</body>
</html>
"""
        return SIMPLE_TEMPLATE

    @http.route('/calendar/meeting/view', type='http', auth="calendar")
    def view(self, db, token, action, id, view='calendar'):
        registry = openerp.modules.registry.RegistryManager.get(db)
        meeting_pool = registry.get('calendar.event')
        attendee_pool = registry.get('calendar.attendee')
        partner_pool = registry.get('res.partner')
        with registry.cursor() as cr:
            attendee = attendee_pool.search_read(cr, openerp.SUPERUSER_ID, [('access_token', '=', token)], [])

            if attendee and attendee[0] and attendee[0].get('partner_id'):
                partner_id = int(attendee[0].get('partner_id')[0])
                tz = partner_pool.read(cr, openerp.SUPERUSER_ID, partner_id, ['tz'])['tz']
            else:
                tz = False

            attendee_data = meeting_pool.get_attendee(cr, openerp.SUPERUSER_ID, id, dict(tz=tz))
            print"attendee_data...........................................................",attendee_data

        if attendee:
            attendee_data['current_attendee'] = attendee[0]
            
        
        SIMPLE_TEMPLATE = """
<html>
<head>
 <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
 <meta http-equiv="content-type" content="text/html; charset=utf-8" />
 <title>Event Details</title>
</head>
<body>
<b>Event Details</b>
<div>
<p>%s</p>
</div>
</body>
</html>
""" %  json.dumps(attendee_data)
        return SIMPLE_TEMPLATE
