// Initialises autocompletion for both add sample pages and barcode adding page

const base_url = window.location.origin;
const autocomplete_locations = base_url + "/autocomplete/locations/";
const autocomplete_sublocations = base_url + "/autocomplete/sublocations/";
const autocomplete_patients = base_url + "/autocomplete/patients/";

$(document).ready(function () {
  $("input#id_sample_location").autocomplete({
    source: autocomplete_locations,
  });
  $("input#id_sample_sublocation").autocomplete({
    source: autocomplete_sublocations,
  });
  $("input#id_study_id").autocomplete({
    source: autocomplete_patients,
  });
});
