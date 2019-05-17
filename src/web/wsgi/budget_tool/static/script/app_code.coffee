class window.Subcategory
  constructor: (dict) ->

    @name = ko.observable(dict.name)
    @remaining = ko.observable(dict.remaining)
    @spent = ko.observable(dict.spent)
    @allocated = ko.observable(dict.allocated)

    @edit = ko.observable(false)

    @toggle_edit = =>
      @edit(not @edit())

    @name_changed = =>
      @toggle_edit()


class window.CategoryDisplay
  constructor: (name, value) ->
    @category = ko.observable(name)
    @allocated = ko.observable(value.allocated)
    @spent = ko.observable(value.spent)
    @remaining = ko.observable(value.remaining)

    underlyingArray = []
    for subcat in value.subcategories
      underlyingArray.push(new window.Subcategory(subcat))

    @subcategories = ko.observableArray(underlyingArray)



class window.ViewModel
  constructor: () ->
    @error_message = ko.observable("")
    @total_income = ko.observable("")
    @total_budgeted = ko.observable("")
    @unaccounted = ko.observable("")
    @categories = ko.observableArray([])
    
    @budget = {}

    @selected_add_category = ko.observable("")
    @selected_add_subcategory = ko.observable("")
    @add_expense_amount = ko.observable("")
    @add_expense_notes = ko.observable("")

    @something_changed = (idx1, idx2, d) =>

      cat = @categories()[idx1].category()
      subcat_idx = -1


      for item in @budget

        if item.Category == cat
          subcat_idx += 1

        if subcat_idx == idx2
          item['Subcategory'] = d.name()
          item['Allocated'] = d.allocated()
          break

      d.toggle_edit()



    @show_error = (error_message) =>
      modal = $('#ErrorModal')
      modal.foundation('open')
      @error_message(error_message)

    @handle_budget_upload = =>
      document.getElementById("budget_input_elem").click()
    @dollars = (amount) ->
      return '$' + amount.toFixed(2)

    @get_budget_params = =>

      $.post 'ajax/',
        request: "ajax_get_budget_parameters"
        budget: JSON.stringify(@budget)
        (data) =>

          result = JSON.parse(data)
          if result.Error
            @show_error(result.Message)
            return

          @total_income(@dollars(result.income))
          @total_budgeted(@dollars(result.budgeted))
          @unaccounted(@dollars(result.unaccounted))

          underlyingArray = []
          for item of result.bins
            underlyingArray.push(new window.CategoryDisplay(item, result.bins[item]))

          @categories(underlyingArray)

    @get_budget_csv = =>

      file = document.getElementById("budget_input_elem").files[0]
      reader = new FileReader()
      reader.onloadend = (event) =>
        $.post 'ajax/',
          request: "ajax_upload_budget"
          csv: event.target.result
          (data) =>

            result = JSON.parse(data)
            if result.Error
              @show_error(result.Message)
              return

            @budget = result
            @get_budget_params()

      reader.readAsBinaryString(file)

    @add_expense = =>

      @budget.push({
        'Type': 'Transaction',
        'Category': @selected_add_category().category(),
        'Subcategory': @selected_add_subcategory().name(),
        'Amount': parseFloat(@add_expense_amount()),
        'Notes': @add_expense_notes()
      })

      @get_budget_params()

    @download_budget_csv = =>

      @show_error("Download functionality not yet implemented.")

    @event_startup = =>
      console.log("STARTUP")


# ******************************************************************************
# Setup Knockout.js ViewModel
# ******************************************************************************
window.viewmodel = new window.ViewModel()
$ ->

  ko.applyBindings(window.viewmodel, $('#app_body')[0])
  ko.applyBindings(window.viewmodel, $('#ErrorModal')[0])

  window.viewmodel.event_startup()

