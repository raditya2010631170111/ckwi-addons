odoo.define("jidoka_dynamic_accounts_report.trial", function (require) {
  "use strict";
  var TrialBalance = require("dynamic_cash_flow_statements.trial");
  var AbstractAction = require("web.AbstractAction");
  var core = require("web.core");
  var field_utils = require("web.field_utils");
  var rpc = require("web.rpc");
  var session = require("web.session");
  var utils = require("web.utils");
  var QWeb = core.qweb;
  var _t = core._t;

  window.click_num = 0;
  var TrialBalanceCustom = TrialBalance.include({
    load_data: function (initial_render = true) {
      var self = this;
      // console.log("Kepanggil TB");
      self.$(".categ").empty();
      try {
        var self = this;
        self
          ._rpc({
            model: "account.trial.balance",
            method: "view_report",
            args: [[this.wizard_id]],
          })
          .then(function (datas) {
            _.each(datas["report_lines"], function (rep_lines) {
              rep_lines.debit = self.format_currency(
                datas["currency"],
                rep_lines.debit
              );
              rep_lines.credit = self.format_currency(
                datas["currency"],
                rep_lines.credit
              );
              rep_lines.balance = self.format_currency(
                datas["currency"],
                rep_lines.balance
              );
              if (rep_lines.End_balance) {
                rep_lines.End_balance["debit"] = self.format_currency(
                  datas["currency"],
                  rep_lines.End_balance["debit"]
                );
                rep_lines.End_balance["credit"] = self.format_currency(
                  datas["currency"],
                  rep_lines.End_balance["credit"]
                );
                rep_lines.End_balance["balance"] = self.format_currency(
                  datas["currency"],
                  rep_lines.End_balance["balance"]
                );
                console.log(
                  self.format_currency(
                    datas["currency"],
                    rep_lines.End_balance["debit"]
                  )
                );
              }
              if (rep_lines.Init_balance) {
                rep_lines.Init_balance["debit"] = self.format_currency(
                  datas["currency"],
                  rep_lines.Init_balance["debit"]
                );
                rep_lines.Init_balance["credit"] = self.format_currency(
                  datas["currency"],
                  rep_lines.Init_balance["credit"]
                );
                rep_lines.Init_balance["balance"] = self.format_currency(
                  datas["currency"],
                  rep_lines.Init_balance["balance"]
                );
                console.log(
                  self.format_currency(
                    datas["currency"],
                    rep_lines.Init_balance["debit"]
                  )
                );
              }
            });
            if (initial_render) {
              self.$(".filter_view_tb").html(
                QWeb.render("TrialFilterView", {
                  filter_data: datas["filters"],
                })
              );
              self.$el.find(".journals").select2({
                placeholder: "Select Journals...",
              });
              self.$el.find(".target_move").select2({
                placeholder: "Target Move...",
              });
            }
            var child = [];

            self.$(".table_view_tb").html(
              QWeb.render("TrialTable", {
                report_lines: datas["report_lines"],
                filter: datas["filters"],
                currency: datas["currency"],
                credit_total: self.format_currency(
                  datas["currency"],
                  datas["debit_total"]
                ),
                debit_total: self.format_currency(
                  datas["currency"],
                  datas["debit_total"]
                ),
                Init_credit_total: self.format_currency(
                  datas["currency"],
                  datas["Init_debit_total"]
                ),
                Init_debit_total: self.format_currency(
                  datas["currency"],
                  datas["Init_debit_total"]
                ),
                End_credit_total: self.format_currency(
                  datas["currency"],
                  datas["End_debit_total"]
                ),
                End_debit_total: self.format_currency(
                  datas["currency"],
                  datas["End_debit_total"]
                ),
              })
            );
          });
      } catch (el) {
        window.location.href;
      }
    },
    print_pdf: function (e) {
      e.preventDefault();
      var self = this;
      self
        ._rpc({
          model: "account.trial.balance",
          method: "view_report",
          args: [[self.wizard_id]],
        })
        .then(function (data) {
          var action = {
            type: "ir.actions.report",
            report_type: "qweb-pdf",
            report_name: "jidoka_dynamic_accounts_report.trial_balance",
            report_file: "jidoka_dynamic_accounts_report.trial_balance",
            data: {
              report_data: data,
            },
            context: {
              active_model: "account.trial.balance",
              landscape: 1,
              trial_pdf_report: true,
            },
            display_name: "Trial Balance",
          };
          return self.do_action(action);
        });
    },

    format_currency: function(currency, amount) {
      if (typeof(amount) != 'number') {
          amount = parseFloat(amount);
      }
      var formatted_value = amount.toLocaleString(currency[2],{
          minimumFractionDigits: 2
      })
      return formatted_value
    },
  });

  return TrialBalanceCustom;
});
