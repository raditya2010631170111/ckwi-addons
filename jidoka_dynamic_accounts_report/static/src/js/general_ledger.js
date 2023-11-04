odoo.define(
  "jidoka_dynamic_accounts_report.general_ledger",
  function (require) {
    "use strict";
    var GeneralLedger = require("dynamic_cash_flow_statements.general_ledger");
    var AbstractAction = require("web.AbstractAction");
    var core = require("web.core");
    var field_utils = require("web.field_utils");
    var rpc = require("web.rpc");
    var session = require("web.session");
    var utils = require("web.utils");
    var QWeb = core.qweb;
    var _t = core._t;

    window.click_num = 0;
    var GeneralLedgerCustom = GeneralLedger.include({
      events: {
        "click .parent-line": "journal_line_click",
        "click .child_col1": "journal_line_click",
        "click #apply_filter": "apply_filter",
        "click #pdf": "print_pdf",
        "click #xlsx": "print_xlsx",
        "click .gl-line": "show_drop_down",
        "click .view-account-move": "view_acc_move",
        "click #btn_expand_all": "expand_all",
      },
      start: async function() {
              
          await this._super(...arguments);
          var self = this;
          self.initial_render = true;
          if (this.searchModel.config.domain.length != 0) {
              var filter_data_selected = {};
              var searchModeDomain = this.searchModel.config.domain;
              

              // CEK DOMAIN
              if (searchModeDomain[0][2] !== ''){
                  filter_data_selected.account_ids = [searchModeDomain[0][2]] 
              }
              if (searchModeDomain[1][2] !== '') {
                  var dateString = searchModeDomain[1][2];
                  filter_data_selected.date_from = dateString + "-01";
              }
              if (searchModeDomain[2][2] !== '') {
                  var str_date = searchModeDomain[2][2].split("-")
                  var str_date_to = new Date(str_date[0], str_date[1], 0).getDate();
                  var str_month_to = new Date(str_date[0], str_date[1], 0).getMonth()+1;
                  var dateString = str_date[0] +"-"+ str_month_to +"-"+ str_date_to;
                  filter_data_selected.date_to = dateString;

              }
            //   console.warn('LOG FILTER DATA SELECTED',filter_data_selected)
              rpc.query({
                  model: 'account.general.ledger',
                  method: 'create',
                  args: [filter_data_selected]
              }).then(function(t_res) {
                  self.wizard_id = t_res;
                  self.load_data(self.initial_render);
              })
          }else{
              rpc.query({
                  model: 'account.general.ledger',
                  method: 'create',
                  args: [{

                  }]
              }).then(function(t_res) {
                  self.wizard_id = t_res;
                  self.load_data(self.initial_render);
              })
          }
      },
      expand_all: function () {
        // console.log("Kepanggil");
        var gl_line = $(".gl-line");
        for (var i = 0; i < gl_line.length; i++) {
          gl_line[i].click();
        }
      },
      show_drop_down: function(event) {
          event.preventDefault();
          var self = this;
          var account_id = $(event.currentTarget).data('account-id');
          var offset = 0;
          var td = $(event.currentTarget).next('tr').find('td');
          if (td.length == 1) {
                  var action_title = self._title
                  self._rpc({
                      model: 'account.general.ledger',
                      method: 'view_report',
                      args: [
                          [self.wizard_id], action_title
                      ],
                  }).then(function(data) {
                  _.each(data['report_lines'], function(rep_lines) {
                          _.each(rep_lines['move_lines'], function(move_line) {
                              var rate = 0
                              if (move_line.amount_currency !== 0){
                                  if (move_line.debit !== 0){
                                      rate = move_line.debit / (move_line.amount_currency)
                                  }else if (move_line.credit !== 0){
                                      rate = move_line.credit / (move_line.amount_currency * -1)
                                  }
                              }
                          move_line.debit = self.format_currency(data['currency'],move_line.debit);
                          move_line.credit = self.format_currency(data['currency'],move_line.credit);
                          move_line.balance = self.format_currency(data['currency'],move_line.balance);
                          move_line.rate = self.format_currency(data['currency'],rate);
                          


                          });
                          });

                  for (var i = 0; i < data['report_lines'].length; i++) {
                  console.log(data['report_lines']);
                  if (account_id == data['report_lines'][i]['id'] ){

                  $(event.currentTarget).next('tr').find('td .gl-table-div').remove();
                  $(event.currentTarget).next('tr').find('td ul').after(
                      QWeb.render('SubSection', {
                          account_data: data['report_lines'][i]['move_lines'],
                          currency_symbol : data.currency[0],
                          currency_position : data.currency[1],

                      }))
                  $(event.currentTarget).next('tr').find('td ul li:first a').css({
                      'background-color': '#00ede8',
                      'font-weight': 'bold',
                  });
                  }
                  }

                  });
          }
      },
      format_currency: function(currency, amount) {
        if (typeof(amount) != 'number') {
            amount = parseFloat(amount);
        }
        let formatted_value = amount.toLocaleString(currency[2],{
            minimumFractionDigits: 2
        })
        return formatted_value
      },
    });

    return GeneralLedgerCustom;
  }
);
