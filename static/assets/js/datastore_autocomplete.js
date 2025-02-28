const base_url = window.location.origin;
const autocomplete_patients = base_url + "/autocomplete/patients/";

$(document).ready(function () {
  $("input#id_study_id").autocomplete({
    source: autocomplete_patients,
    minLength: 2,
    select: function (event, ui) {
      // Update Alpine.js data store
      this.dispatchEvent(
        new CustomEvent("autocomplete", {
          detail: { value: ui.item.value },
        })
      );
      // Set the input value
      $(this).val(ui.item.value);
      return false;
    },
  });
});
