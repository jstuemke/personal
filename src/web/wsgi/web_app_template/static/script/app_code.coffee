class window.ViewModel
  constructor: () ->
    @error_message = ko.observable("")
    @sample_user_input = ko.observable("")

    @show_error = (error_message) =>
      modal = $('#ErrorModal')
      modal.foundation('open')
      @error_message(error_message)

    @sample_ajax_call = =>
      console.log("AJAX")

      $.post 'ajax/',
        request: "ajax_callback"
        user: @sample_user_input
        (data) =>
          result = JSON.parse(data)
          if result.Error
            @show_error(result.Message)
            return

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

