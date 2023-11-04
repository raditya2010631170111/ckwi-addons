odoo.define('fik_equipment_maintenance.MyCustomAction',  function (require) {
"use strict";
var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var rpc = require('web.rpc');
//var ActionManager = require('web.ActionManager');
var view_registry = require('web.view_registry');
var Widget = require('web.Widget');
var ajax = require('web.ajax');
var session = require('web.session');
var web_client = require('web.web_client');
var _t = core._t;
var QWeb = core.qweb;

var MyCustomAction = AbstractAction.extend({
    template: 'MaintenanceDashboardView',

    jsLibs: [
        '/fik_equipment_maintenance/static/src/js/Chart.js',
       
    ],
    events: {
	    'click .action-scrap': 'action_scrap',
        'click .action-in-progress':'action_in_progress',
        'click .action-in-repaired': 'action_repaired',
        'click .action-new-request': 'action_new_request',
        'click .action-in-checklist': 'action_in_checklist',
        'click .action-in-equipment': 'action_in_equipment',
        'click .action-team': 'action_in_team',

    },


    init: function(parent, context) {
        this._super(parent, context);
        var self = this;
    },

    start: function() {
        var self = this;
        self.render_dashboards();
        self.render_graphs();
        return this._super();
    },

    reload: function () {
            window.location.href = this.href;
    },

    render_dashboards: function(value) {
        var self = this;
        var maintenance_dashboard = QWeb.render('MaintenanceDashboardView', {
            widget: self,
        });

        rpc.query({
                model: 'maintenance.request',
                method: 'get_count_list',
                args: []
            })
            .then(function (result){
                    self.$el.find('.stage-new-request').text(result['calculate_stage'])
                    self.$el.find('.stage-in-progress').text(result['calculate_in_progress'])
                    self.$el.find('.stage-in-repaired').text(result['calculate_in_repaired'])
                    self.$el.find('.stage-in-scrap').text(result['calculate_in_scrap'])
            });

        return maintenance_dashboard
    },

     action_scrap:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Maintenance Request"),
            type: 'ir.actions.act_window',
            res_model: 'maintenance.request',
            view_mode: 'tree,form',
            view_type: 'list',
            views: [[false, 'list'],[false, 'form']],
            views: [[false, 'list'],[false, 'form']],
            domain: [['stage_id.status','=','Scrap']],
            target: 'current'
        },)
    },

    action_in_progress:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Maintenance Request"),
            type: 'ir.actions.act_window',
            res_model: 'maintenance.request',
            view_mode: 'tree,form',
            view_type: 'list',
            views: [[false, 'list'],[false, 'form']],
            views: [[false, 'list'],[false, 'form']],
            domain: [['stage_id.status','=','In Progress']],
            target: 'current'
        },)


    },

    action_in_checklist:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Maintenance CheckList"),
            type: 'ir.actions.act_window',
            res_model: 'maintenance.checklist',
            view_mode: 'tree,form',
            view_type: 'list',
            views: [[false, 'list'],[false, 'form']],
            views: [[false, 'list'],[false, 'form']],
            target: 'current'
        },)
    },

    action_in_team:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Maintenance Team"),
            type: 'ir.actions.act_window',
            res_model: 'maintenance.team',
            view_mode: 'tree,form',
            view_type: 'list',
            views: [[false, 'list'],[false, 'form']],
            views: [[false, 'list'],[false, 'form']],
            target: 'current'
        },)
    },

    action_in_equipment:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Maintenance Equipment"),
            type: 'ir.actions.act_window',
            res_model: 'maintenance.equipment',
            view_mode: 'tree,form',
            view_type: 'list',
            views: [[false, 'list'],[false, 'form']],
            views: [[false, 'list'],[false, 'form']],
            target: 'current'
        },)


    },



    action_repaired:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();

        this.do_action({
            name: _t("Maintenance Request"),
            type: 'ir.actions.act_window',
            res_model: 'maintenance.request',
            view_mode: 'tree,form',
            view_type: 'list',
            views: [[false, 'list'],[false, 'form']],
            views: [[false, 'list'],[false, 'form']],
            domain: [['stage_id.status','=','Repaired']],
            target: 'current'
        },)
    },

     action_new_request:function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        this.do_action({
            name: _t("Maintenance Request"),
            type: 'ir.actions.act_window',
            res_model: 'maintenance.request',
            view_mode: 'tree,form',
            view_type: 'list',
            views: [[false, 'list'],[false, 'form']],
            views: [[false, 'list'],[false, 'form']],
            domain: [['stage_id.status','=','New Request']],
            target: 'current'
        },)
    },


    getRandomColor: function () {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++ ) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    },
    render_graphs: function(){
        var self = this;
        self.graph_requisition_data();
        self.graph_monthly_maintainance_requision_data()
    },

     graph_requisition_data: function() {
        var self = this;
        var ctx = this.$el.find('#highprice')
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        rpc.query({
                model: 'purchase.requisition',
                method: 'get_requisition_week_data',
            })
            .then(function (result) {
                var data = result.data;
                var day = ["Monday", "Tuesday", "Wednesday", "Thursday",
                         "Friday", "Saturday", "Sunday"]
                var week_data = [];
                if (data){
                    for(var i = 0; i < day.length; i++){
                        day[i] == data[day[i]]
                        var day_data = day[i];
                        var day_count = data[day[i]];
                        if(!day_count){
                                day_count = 0;
                        }
                        week_data[i] = day_count

                    }
                }

                var myChart = new Chart(ctx, {
                type: 'bar',
                data: {

                    labels: day ,
                    datasets: [{
                        label: 'Equipment Purchase Requisition',
                        data: week_data,
                        backgroundColor: bg_color_list,
                        borderColor: bg_color_list,
                        borderWidth: 1,
                        pointBorderColor: 'white',
                        pointBackgroundColor: 'red',
                        pointRadius: 5,
                        pointHoverRadius: 10,
                        pointHitRadius: 30,
                        pointBorderWidth: 2,
                        pointStyle: 'rectRounded'
                    }]
                },
                options: {
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0,
                                max: Math.max.apply(null,week_data),
                              }
                        }]
                    },
                    responsive: true,
                    maintainAspectRatio: true,
                    leged: {
                        display: true,
                        labels: {
                            fontColor: 'black'
                        }
                },
            },
        });
            });
    },

     graph_monthly_maintainance_requision_data: function() {
        var self = this;
        var ctx = this.$el.find('#monthlymaintenance')
        Chart.plugins.register({
          beforeDraw: function(chartInstance) {
            var ctx = chartInstance.chart.ctx;
            ctx.fillStyle = "white";
            ctx.fillRect(0, 0, chartInstance.chart.width, chartInstance.chart.height);
          }
        });
        var bg_color_list = []
        for (var i=0;i<=12;i++){
            bg_color_list.push(self.getRandomColor())
        }
        rpc.query({
                model: 'maintenance.request',
                method: 'get_purchase_requision_data',
            })
            .then(function (result) {
                var data = result.data
                var months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                                'August', 'September', 'October', 'November', 'December']
                var month_data = [];

                if (data){
                    for(var i = 0; i < months.length; i++){
                        months[i] == data[months[i]]
                        var day_data = months[i];
                        var month_count = data[months[i]];
                        if(!month_count){
                                month_count = 0;
                        }
                        month_data[i] = month_count

                    }
                }
                var myChart = new Chart(ctx, {
                type: 'bar',
                data: {

                    labels: months,
                    datasets: [{
                        label: ' Maintenance Requests',
                        data: month_data,
                        backgroundColor: bg_color_list,
                        borderColor: bg_color_list,
                        borderWidth: 1,
                        pointBorderColor: 'white',
                        pointBackgroundColor: 'red',
                        pointRadius: 1,
                        pointHoverRadius: 10,
                        pointHitRadius: 30,
                        pointBorderWidth: 1,
                        pointStyle: 'rectRounded'
                    }]
                },
                options: {
                    scales: {
                        yAxes: [{
                            ticks: {
                                min: 0,
                                max: Math.max.apply(null,month_data),
                              }
                        }]
                    },
                    responsive: true,
                    maintainAspectRatio: true,
                    leged: {
                        display: true,
                        labels: {
                            fontColor: 'black'
                        }
                },
            },
        });

            });


    },

           
});


core.action_registry.add("maintenance_dashboard", MyCustomAction);
return MyCustomAction
});
