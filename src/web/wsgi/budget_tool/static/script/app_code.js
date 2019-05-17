// Generated by CoffeeScript 2.3.2
(function() {
  window.Subcategory = class Subcategory {
    constructor(dict) {
      this.name = ko.observable(dict.name);
      this.remaining = ko.observable(dict.remaining);
      this.spent = ko.observable(dict.spent);
      this.allocated = ko.observable(dict.allocated);
      this.edit = ko.observable(false);
      this.toggle_edit = () => {
        return this.edit(!this.edit());
      };
      this.name_changed = () => {
        return this.toggle_edit();
      };
    }

  };

  window.CategoryDisplay = class CategoryDisplay {
    constructor(name, value) {
      var i, len, ref, subcat, underlyingArray;
      this.category = ko.observable(name);
      this.allocated = ko.observable(value.allocated);
      this.spent = ko.observable(value.spent);
      this.remaining = ko.observable(value.remaining);
      underlyingArray = [];
      ref = value.subcategories;
      for (i = 0, len = ref.length; i < len; i++) {
        subcat = ref[i];
        underlyingArray.push(new window.Subcategory(subcat));
      }
      this.subcategories = ko.observableArray(underlyingArray);
    }

  };

  window.ViewModel = class ViewModel {
    constructor() {
      this.error_message = ko.observable("");
      this.total_income = ko.observable("");
      this.total_budgeted = ko.observable("");
      this.unaccounted = ko.observable("");
      this.categories = ko.observableArray([]);
      this.budget = {};
      this.selected_add_category = ko.observable("");
      this.selected_add_subcategory = ko.observable("");
      this.add_expense_amount = ko.observable("");
      this.add_expense_notes = ko.observable("");
      this.something_changed = (idx1, idx2, d) => {
        var cat, i, item, len, ref, subcat_idx;
        cat = this.categories()[idx1].category();
        subcat_idx = -1;
        ref = this.budget;
        for (i = 0, len = ref.length; i < len; i++) {
          item = ref[i];
          if (item.Category === cat) {
            subcat_idx += 1;
          }
          if (subcat_idx === idx2) {
            item['Subcategory'] = d.name();
            item['Allocated'] = d.allocated();
            break;
          }
        }
        return d.toggle_edit();
      };
      this.show_error = (error_message) => {
        var modal;
        modal = $('#ErrorModal');
        modal.foundation('open');
        return this.error_message(error_message);
      };
      this.handle_budget_upload = () => {
        return document.getElementById("budget_input_elem").click();
      };
      this.dollars = function(amount) {
        return '$' + amount.toFixed(2);
      };
      this.get_budget_params = () => {
        return $.post('ajax/', {
          request: "ajax_get_budget_parameters",
          budget: JSON.stringify(this.budget)
        }, (data) => {
          var item, result, underlyingArray;
          result = JSON.parse(data);
          if (result.Error) {
            this.show_error(result.Message);
            return;
          }
          this.total_income(this.dollars(result.income));
          this.total_budgeted(this.dollars(result.budgeted));
          this.unaccounted(this.dollars(result.unaccounted));
          underlyingArray = [];
          for (item in result.bins) {
            underlyingArray.push(new window.CategoryDisplay(item, result.bins[item]));
          }
          return this.categories(underlyingArray);
        });
      };
      this.get_budget_csv = () => {
        var file, reader;
        file = document.getElementById("budget_input_elem").files[0];
        reader = new FileReader();
        reader.onloadend = (event) => {
          return $.post('ajax/', {
            request: "ajax_upload_budget",
            csv: event.target.result
          }, (data) => {
            var result;
            result = JSON.parse(data);
            if (result.Error) {
              this.show_error(result.Message);
              return;
            }
            this.budget = result;
            return this.get_budget_params();
          });
        };
        return reader.readAsBinaryString(file);
      };
      this.add_expense = () => {
        this.budget.push({
          'Type': 'Transaction',
          'Category': this.selected_add_category().category(),
          'Subcategory': this.selected_add_subcategory().name(),
          'Amount': parseFloat(this.add_expense_amount()),
          'Notes': this.add_expense_notes()
        });
        return this.get_budget_params();
      };
      this.download_budget_csv = () => {
        return this.show_error("Download functionality not yet implemented.");
      };
      this.event_startup = () => {
        return console.log("STARTUP");
      };
    }

  };

  // ******************************************************************************
  // Setup Knockout.js ViewModel
  // ******************************************************************************
  window.viewmodel = new window.ViewModel();

  $(function() {
    ko.applyBindings(window.viewmodel, $('#app_body')[0]);
    ko.applyBindings(window.viewmodel, $('#ErrorModal')[0]);
    return window.viewmodel.event_startup();
  });

}).call(this);

//# sourceMappingURL=app_code.js.map
