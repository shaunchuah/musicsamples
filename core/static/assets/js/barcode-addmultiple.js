const url_string = "/api/multiple_samples/";
const token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
console.log(token);

function submitScan() {
  $.ajax({
    headers: {
      "X-CSRFToken": token,
    },
    url: url_string,
    method: "post",
    data: {
      sample_id: $("#sample_id").val(),
      sample_location: $("#id_sample_location").val(),
      sample_sublocation: $("#id_sample_sublocation").val(),
      study_name: $("#id_study_name").val(),
      music_timepoint: $("#id_music_timepoint").val(),
      patient_id: $("#id_patient_id").val(),
      sample_type: $("#id_sample_type").val(),
      haemolysis_reference: $("#id_haemolysis_reference").val(),
      biopsy_location: $("#id_biopsy_location").val(),
      biopsy_inflamed_status: $("#id_biopsy_inflamed_status").val(),
      sample_datetime: $("#id_sample_datetime").val(),
      processing_datetime: $("#id_processing_datetime").val(),
      sample_comments: $("#id_sample_comments").val(),
      sample_volume: $("#id_sample_volume").val(),
      sample_volume_units: $("#id_sample_volume_units").val(),
      freeze_thaw_count: $("#id_freeze_thaw_count").val(),
      frozen_datetime: $("#id_frozen_datetime").val(),
    },
    success: function (result) {
      $(".alert-success").show();
      $(".alert-success").fadeOut(1000);
      $("#tbody tr:first").before(
        `<tr><td>${$("#sample_id").val()}</td><td>Success</td><td>Sample ${$(
          "#sample_id"
        ).val()} captured.</td></tr>`
      );
      $("#sample_id").val("");
      $("#sample_id").focus();
      console.log(result);
    },
    error: function (error) {
      // for bootstrap, add was-validated to the form;
      document
        .getElementById("add_multiple_form")
        .classList.add("was-validated");
      const error_json = JSON.parse(error.responseText);

      for (let [key, value] of Object.entries(error_json)) {
        if (key == "non_field_errors") {
          document.getElementById("non_field_errors").classList.add('mb-3');
          document.getElementById("non_field_errors").textContent =
            value.join(" ");
        } else {
          // style the input to is-invalid
          let id_string = "id_" + key;
          document.getElementById(id_string).classList.add("is-invalid");

          // add error messages to appropriate divs;
          let id_error_string = "id_" + key + "_error";
          let error_message_array = value;
          let error_message_list = error_message_array.join(" ");
          document.getElementById(id_error_string).textContent =
            error_message_list;
        }
      }

      $("#error_message").text(
        error.statusText + "(Scanned ID: " + $("#sample_id").val() + ")"
      );
      $(".alert-danger").show();
      $(".alert-danger").fadeOut(3000);
      $("#tbody tr:first").before(
        `<tr><td>${$("#sample_id").val()}</td><td>Error</td><td>${
          error.statusText
        }</td></tr>`
      );
      $("#sample_id").val("");
      $("#sample_id").focus();
    },
  });
}

function adjust(v) {
  if (v > 9) {
    return v.toString();
  } else {
    return "0" + v.toString();
  }
}

$(document).ready(function () {
  // Javascript method's body can be found in assets/js/demos.js
  $(".alert").hide();

  var today = new Date();
  var date =
    today.getFullYear() +
    "-" +
    adjust(today.getMonth() + 1) +
    "-" +
    adjust(today.getDate());
  var time = adjust(today.getHours()) + ":" + adjust(today.getMinutes());
  var dateTime = date + "T" + time;
  $("#id_processing_datetime").val(dateTime);

  $("#sample_id").keydown(function (e) {
    if (e.keyCode == 13 || e.keyCode == 9) {
      e.preventDefault();
      submitScan();
    }
  });

  $("input#id_sample_id").focus();
  $("input#id_sample_location").autocomplete({
    source: "/autocomplete/locations/",
  });
  $("input#id_patient_id").autocomplete({
    source: "/autocomplete/patients/",
  });

  $("label[for=id_biopsy_location], #id_biopsy_location").hide();
  $("label[for=id_biopsy_inflamed_status], #id_biopsy_inflamed_status").hide();
  $("label[for=id_haemolysis_reference], #id_haemolysis_reference").hide();
  $("label[for=id_music_timepoint], #id_music_timepoint").hide();

  // Show/Hide form fields depending on input sample type
  if (
    $("#id_sample_type").val() == "Formalin biopsy" ||
    $("#id_sample_type").val() == "RNAlater biopsy" ||
    $("#id_sample_type").val() == "Paraffin tissue block"
  ) {
    $("label[for=id_biopsy_location], #id_biopsy_location").show();
    $(
      "label[for=id_biopsy_inflamed_status], #id_biopsy_inflamed_status"
    ).show();
  }

  if (
    $("#id_sample_type").val() == "EDTA plasma child aliquot" ||
    $("#id_sample_type").val() == "PaxGene ccfDNA plasma child aliquot" ||
    $("#id_sample_type").val() == "PaxGene ccfDNA extracted cfDNA"
  ) {
    $("label[for=id_haemolysis_reference], #id_haemolysis_reference").show();
  }

  $("#id_sample_type").change(function () {
    if (
      $("#id_sample_type").val() == "Formalin biopsy" ||
      $("#id_sample_type").val() == "RNAlater biopsy" ||
      $("#id_sample_type").val() == "Paraffin tissue block"
    ) {
      $("label[for=id_biopsy_location], #id_biopsy_location").show("slow");
      $(
        "label[for=id_biopsy_inflamed_status], #id_biopsy_inflamed_status"
      ).show("slow");
    } else {
      $("label[for=id_biopsy_location], #id_biopsy_location").hide();
      $(
        "label[for=id_biopsy_inflamed_status], #id_biopsy_inflamed_status"
      ).hide();
    }
  });

  $("#id_sample_type").change(function () {
    if (
      $("#id_sample_type").val() == "EDTA plasma child aliquot" ||
      $("#id_sample_type").val() == "PaxGene ccfDNA plasma child aliquot" ||
      $("#id_sample_type").val() == "PaxGene ccfDNA extracted cfDNA"
    ) {
      $("label[for=id_haemolysis_reference], #id_haemolysis_reference").show(
        "slow"
      );
    } else {
      $("label[for=id_haemolysis_reference], #id_haemolysis_reference").hide();
    }
  });
  $("#id_study_name").change(function () {
    if (
      $("#id_study_name").val() == "music" ||
      $("#id_study_name").val() == "mini_music"
    ) {
      $("label[for=id_music_timepoint], #id_music_timepoint").show();
    } else {
      $("label[for=id_music_timepoint], #id_music_timepoint").hide();
    }
  });
});
