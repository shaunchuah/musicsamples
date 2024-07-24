$(document).ready(function () {
  // At initialisation hide all non-relevant fields
  $("label[for=id_biopsy_location], #id_biopsy_location").hide();
  $("label[for=id_biopsy_inflamed_status], #id_biopsy_inflamed_status").hide();
  $("label[for=id_haemolysis_reference], #id_haemolysis_reference").hide();
  $("label[for=id_qubit_cfdna_ng_ul], #id_qubit_cfdna_ng_ul").hide();
  $("label[for=id_music_timepoint], #id_music_timepoint").hide();

  // Show fields based on pre-existing form data

  // If biopsies show location and inflamed status field
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

  // If EDTA or Paxgene aliquots or extracted cfDNA, show haemolysis reference
  if (
    $("#id_sample_type").val() == "EDTA plasma child aliquot" ||
    $("#id_sample_type").val() == "PaxGene ccfDNA plasma child aliquot" ||
    $("#id_sample_type").val() == "PaxGene ccfDNA extracted cfDNA"
  ) {
    $("label[for=id_haemolysis_reference], #id_haemolysis_reference").show();
  }

  if ($("#id_sample_type").val() == "PaxGene ccfDNA extracted cfDNA") {
    $("label[for=id_qubit_cfdna_ng_ul], #id_qubit_cfdna_ng_ul").show();
  }

  // Begin listening for form changes

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
  $("#id_sample_type").change(function () {
    if ($("#id_sample_type").val() == "PaxGene ccfDNA extracted cfDNA") {
      $("label[for=id_qubit_cfdna_ng_ul], #id_qubit_cfdna_ng_ul").show("slow");
    } else {
      $("label[for=id_qubit_cfdna_ng_ul], #id_qubit_cfdna_ng_ul").hide();
    }
  });
  $("#id_study_name").change(function () {
    if (
      $("#id_study_name").val() == "music" ||
      $("#id_study_name").val() == "mini_music"
    ) {
      $("label[for=id_music_timepoint], #id_music_timepoint").show("slow");
    } else {
      $("label[for=id_music_timepoint], #id_music_timepoint").hide();
    }
  });
});
