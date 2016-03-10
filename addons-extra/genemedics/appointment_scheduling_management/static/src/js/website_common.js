odoo.define('appointment_scheduling_management.appointment_scheduling_management', function (require) {
var odoo = require('web.ajax');

    $(document).ready(function() {
        
        
        $('#email').change(function(){
            var self = this;
            odoo.jsonRpc('/check_patient', 'call', {'email': $(this).val()}).then(function (data) {
                if (data){
                    $(self).val('');
                    swal({
                        title: "Oops! User Already Exist.",
                        type: "error",
                        confirmButtonClass: 'btn-danger',
                        confirmButtonText: 'Cancel'
                    });
                }
            })
        })
        
        var employee = false;
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

        $(document).on('change', '#id_start_date,select[name="meeting_type"]', function(){
            var view = {
                'adate': $('#id_start_date').val(),
                'meeting_type': $('select[name="meeting_type"]').val(),
                'location_id': $('select[name="location_id"]').val()
            }
            if(view['adate'] && view['meeting_type'] && view['location_id']){
                odoo.jsonRpc('/search_slot', 'call', view).then(function (data) {
                    $('.time-slots').fadeOut("slow", function() {
                        $(this).html(data).fadeIn("medium");
                        $('#slot_select').val('')
                        employee = false;
                    });
                });
            }
        });

        $(document).on('change', 'select[name="location_id"]', function() {
            var select = $('select[name="meeting_type"]');
            if ($(this).val()){
                odoo.jsonRpc('/meeting_type', 'call', {'state_id': $(this).val()}).then(function (data) {
                  $('option', select).remove();
//                  $(option).attr("disabled", "disabled");
//                  $(option).attr("selected", "selected");
//                  select.append($(option));
                  $.each(data, function(key,value) {
                      option = new Option(value[1],value[0]);
                      $(option).attr( "data-location", value[2] );
                      select.append($(option));
                  });
              }).then(function(){
                  select.change();
              })
            }
        });

//        $(document).on('change', 'select[name="meeting_type"]', function() {
//            if($('select[name="meeting_type"] option:selected').data('location') == 'physical_loc'){
//                $('#city-label').text($('select[name="location_id"] option:selected').data('city'));
//            }else{
//                $('#city-label').text('');
//            }
//        })

        $(document).on('click', '.time button', function() {
            if ($(this).hasClass('btn btn-success')){
                $('#slot_select').val($(this).text())
                employee = $(this).data('employee')
            }
        });

        $('#submit_button').click(function(){
            if (employee){
                odoo.jsonRpc('/create_appointment', 'call', {
                    'meeting_type': $('select[name="meeting_type"]').val(),
                    'location_id': $('select[name="location_id"]').val(),
                    'employee_id': employee,
                    'patient_id': $(this).data('patient_id'),
                    'date': $('#id_start_date').val(),
                    'time_slot': $('#slot_select').val()
                    }).then(function (data) {
                        swal({
                            title: "Success!",
                            text: "Appointment has been successfully scheduled.",
                            type: "success",
                            confirmButtonClass: 'btn-success',
                            confirmButtonText: 'Okay!'
                          },function(isConfirm){
                              if (isConfirm){
                                  document.location.reload(true);
                              }
                          });
                })
            }else{
                swal({
                    title: "Oops! You have not selected anything.",
                    type: "error",
                    confirmButtonClass: 'btn-danger',
                    confirmButtonText: 'Cancel'
                  });
            }
        })

//        $(document).on('change', 'select[name="meeting_type"]', function() {
//            odoo.jsonRpc('/meeting_type_onchange', 'call', {'meeting_type': $(this).val()}).then(function (data) {
//                $('select[name="location_id"]').val(data['location_id']);
//                
//                var select = $('#employee_id');
//                $('option', select).remove();
//                var option = new Option('Select a Consultant','');
//                $(option).attr("disabled", "disabled");
//                $(option).attr("selected", "selected");
//                select.append($(option));
//                $.each(data['employee_ids'], function(key,value) {
//                    option = new Option(value[1],value[0]);
//                    select.append($(option));
//                });
//            })
//        });

    });

});