odoo.define('appointment_scheduling_management.appointment_scheduling_management', function (require) {

    var odoo = require('web.ajax');

    $(document).ready(function(){

        function search_issues(stage_id, stage_name , span){
            odoo.jsonRpc('/search_issues', 'call', {'stage_id': stage_id, 'stage_name': stage_name}).then(function (data) {
                $('.issues').fadeOut("fast", function() {
                    $(this).html(data['html_data']).fadeIn("fast");
                    $(span).html(data['record_len']);
                });
            })
        }

        search_issues($('#sidebar-wrapper .list-group a').first().data('stage_id'), $('#sidebar-wrapper .list-group a').first().data('stage_name'), $('#sidebar-wrapper .list-group a').first().find('span'))

        function fun(){
            setTimeout(function(){
                odoo.jsonRpc('/notification-data', 'call', {}).then(function (data) {
                    $('.notifications-wrapper').html(data['html_data'])
                    if (data['flag']){
                        $('#dLabel').css('color', 'red');
                    }else{
                        $('#dLabel').css('color', 'white');
                    }
                })
                fun()
            },10000)
        }

        fun()

        $(document).on('click', '#reply-button', function(){
            $('#sidebar-wrapper .list-group a.active').removeClass('active');
            odoo.jsonRpc('/compose_new_mail', 'call', {'issue_id': $(this).data('issue_id')}).then(function (data) {
                $('.issues').fadeOut("fast", function() {
                    $(this).html(data).fadeIn("fast");
                });
            })
        })
        
        $('#compose_new_mail').click(function(){
            $('#sidebar-wrapper .list-group a.active').removeClass('active');
            odoo.jsonRpc('/compose_new_mail', 'call', {}).then(function (data) {
                $('.issues').fadeOut("fast", function() {
                    $(this).html(data).fadeIn("fast");
                });
            })
        })
        
        $('#sidebar-wrapper .list-group a').first().addClass('active');

        $('#sidebar-wrapper .list-group a').click(function(){
            $('#sidebar-wrapper .list-group a.active').removeClass('active');
            $(this).addClass('active');
            search_issues($(this).data('stage_id'), $(this).data('stage_name'), $(this).find('span'));
        });

        $(document).on('click', '.issue-form-view', function(){
            odoo.jsonRpc('/issue-form-view', 'call', {'issue_id': $(this).data('issue_id')}).then(function (data) {
                $('.issues').fadeOut("fast", function() {
                    $(this).html(data['html_data']).fadeIn("fast");
                });
                if (data['update']){
                    var new_span = $('#sidebar-wrapper .list-group a.new span')
                    var assign_span = $('#sidebar-wrapper .list-group a.open span')
                    new_span.html(parseInt(new_span.html()) - 1);
                    assign_span.html(parseInt(assign_span.html()) + 1);
                }
            })
        })

        $(document).on('click', '.navbar-employee-toggle', function () {
            if($('.sidebar-employee-data').hasClass('sidebar-open')){
                odoo.jsonRpc('/employee-data', 'call', {}).then(function (data) {
                    $('.sidebar-employee-data').html(data)
                })
            }
        })

    })

})