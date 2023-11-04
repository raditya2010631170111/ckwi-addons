odoo.define(
  "jidoka_dynamic_accounts_report.cash_flow_custom",
  function (require) {
    "use strict";
    var AbstractAction = require("web.AbstractAction");
    var core = require("web.core");
    var field_utils = require("web.field_utils");
    var rpc = require("web.rpc");
    var session = require("web.session");
    var utils = require("web.utils");
    var QWeb = core.qweb;
    var _t = core._t;
    var today = new Date();
    var default_periode =
      today.getFullYear() + "-" + ("0" + (today.getMonth() + 1)).slice(-2);

    window.click_num = 0;
    var CashFlowCustom = AbstractAction.extend({
      template: "CashFlowCustomTemp",
      events: {
        "click #xlsx": "print_xlsx",
        "click #apply_filter": "apply_filter",
      },

      init: function (parent, action) {
        this._super(parent, action);
        this.currency = action.currency;
        this.report_lines = action.report_lines;
        this.wizard_id = action.context.wizard | null;
      },

      start: function () {
        var self = this;
        self.initial_render = true;
        rpc
          .query({
            model: "cash.flow.custom",
            method: "create",
            args: [{}],
          })
          .then(function (t_res) {
            self.wizard_id = t_res;
            self.load_data(self.initial_render);
          });
      },

      load_data: function (initial_render = true) {
        var self = this;
        // console.log("Title : ", self._title);
        // self.$(".categ").empty();
        try {
          var self = this;
          self
            ._rpc({
              model: "cash.flow.custom",
              method: "view_report",
              args: [[this.wizard_id], self._title],
            })
            .then(function (datas) {
              // console.log('--- datas ---');
              // console.log(datas);
              if (initial_render) {
                self.$(".filter_view_cash_flow_custom").html(
                  QWeb.render("CashFlowCustomFilterView", {
                    title: self._title,
                  })
                );
                var periode_res = document.getElementById("periode_res");
                periode_res.value = default_periode;
                periode_res.innerHTML = periode_res.value;
              }
              var child = [];
              // console.log("Kepannggil");
              self.$(".table_view_cash_flow_custom").html(
                QWeb.render("CashFlowCustomTable", {
                  // header_table: datas["header_table"],
                  report_lines: datas["report_lines"],
                  title: datas["tag"],
                  filters: datas["filters"],
                  // total: datas["total"],
                })
              );
            });
        } catch (el) {
          console.log(' # catch ', el);
          window.location.href;
        }
      },

      format_currency: function (currency, amount) {
        if (typeof amount != "number") {
          amount = parseFloat(amount);
        }
        var formatted_value = amount.toLocaleString(currency[2], {
          minimumFractionDigits: 2,
        });
        return formatted_value;
      },

      print_xlsx: function () {
        var self = this;
        self
          ._rpc({
            model: "cash.flow.custom",
            method: "view_report",
            args: [[self.wizard_id], self._title],
          })
          .then(function (data) {
            var action = {
              type: "ir_actions_dynamic_xlsx_download",
              data: {
                model: "cash.flow.custom",
                options: JSON.stringify(data["filters"]),
                output_format: "xlsx",
                report_data: JSON.stringify(data["report_lines"]),
                report_name: self._title,
                dfr_data: JSON.stringify(data),
              },
            };
            return self.do_action(action);
          });
      },

      apply_filter: function (event) {
        event.preventDefault();
        var self = this;
        self.initial_render = false;

        var filter_data_selected = {};
        console.log("Periode", $("#periode").val());
        var periode_res = document.getElementById("periode_res");
        if ($("#periode").val()) {
          var periode = $("#periode").val();
          filter_data_selected.periode = periode;
          periode_res.value = periode;
        } else {
          filter_data_selected.periode = "";
          periode_res.value = default_periode;
        }
        periode_res.innerHTML = periode_res.value;
        rpc
          .query({
            model: "cash.flow.custom",
            method: "write",
            args: [self.wizard_id, filter_data_selected],
          })
          .then(function (res) {
            self.initial_render = false;
            self.load_data(self.initial_render);
          });
      },
    });
    core.action_registry.add("cf_custom", CashFlowCustom);
    return CashFlowCustom;
  }
);
