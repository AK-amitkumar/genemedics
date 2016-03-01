odoo.define('appointment_scheduling_management.appointment_scheduling_management', function (require) {
var odoo = require('web.ajax');

    $(document).ready(function() {

        if (window.location.pathname == '/appointment'){
            odoo.jsonRpc('/check_user_group', 'call', {}).then(function (data) {
                if(data){
                    $('header,footer,#oe_main_menu_navbar').hide();
                }
            })
        }

        $('#id_start_date').datepicker({
            changeMonth : true,
            changeYear : true,
            showButtonPanel : true,
            format : "dd/mm/yy",
            dateFormat : 'dd/mm/yy',
        });

        $(document).on('change', '#id_start_date,#employee_id,select[name="meeting_type"],select[name="location_id"]', function(){
            var view = {
                'adate': $('#id_start_date').val(),
                'employee_id': $('#employee_id').val(),
                'meeting_type': $('select[name="meeting_type"]').val(),
                'location_id': $('select[name="location_id"]').val()
            }
            if(view['adate'] && view['employee_id'] && view['meeting_type'] && view['location_id']){
                odoo.jsonRpc('/search_slot', 'call', view).then(function (data) {
                	$('.time-slots').fadeOut("slow", function() {
                	    $(this).html(data).fadeIn("medium");
                    });
                });
            }
        });

        $(document).on('click', '.time button', function() {
            if ($(this).hasClass('btn btn-success')){
                $('#slot_select').val($(this).text())
            }
        });

        $('#submit_botton').click(function(){
            odoo.jsonRpc('/create_appointment', 'call', {
                'meeting_type': $('select[name="meeting_type"]').val(),
                'location_id': $('select[name="location_id"]').val(),
                'employee_id': $('#employee_id').val(),
                'date': $('#id_start_date').val(),
                'time_slot': $('#slot_select').val()
                }).then(function (data) {
                    alert('Appointment has been successfully scheduled.');
                    location.reload();
            })
        })

        $(document).on('change', 'select[name="meeting_type"]', function() {
            odoo.jsonRpc('/meeting_type_onchange', 'call', {'meeting_type': $(this).val()}).then(function (data) {
                $('select[name="location_id"]').val(data['location_id']);
                
                var select = $('#employee_id');
                $('option', select).remove();
                var option = new Option('Select a Consultant','');
                $(option).attr("disabled", "disabled");
                $(option).attr("selected", "selected");
                select.append($(option));
                $.each(data['employee_ids'], function(key,value) {
                    option = new Option(value[1],value[0]);
                    select.append($(option));
                });
            })
        });

    });

});