$(document).ready(function () {
  // At initialisation hide all non-relevant fields
  $("label[for=id_biopsy_location], #id_biopsy_location").hide();
  $("label[for=id_biopsy_inflamed_status], #id_biopsy_inflamed_status").hide();
  $("label[for=id_haemolysis_reference], #id_haemolysis_reference").hide();
  $("label[for=id_qubit_cfdna_ng_ul], #id_qubit_cfdna_ng_ul").hide();
  $("label[for=id_paraffin_block_key], #id_paraffin_block_key").hide();
  $("label[for=id_music_timepoint], #id_music_timepoint").hide();
  $("label[for=id_marvel_timepoint], #id_marvel_timepoint").hide();

  // Show fields based on pre-existing form data

  // If music or minimusic show timepoint
  if (
    $("#id_study_name").val() == "music" ||
    $("#id_study_name").val() == "mini_music"
  ) {
    $("label[for=id_music_timepoint], #id_music_timepoint").show();
  }

  if (
    $("#id_study_name").val() == "marvel"
  ) {
    $("label[for=id_music_timepoint], #id_marvel_timepoint").show();
  }

  // If biopsies show location and inflamed status field
  if (
    $("#id_sample_type").val() == "biopsy_formalin" ||
    $("#id_sample_type").val() == "biopsy_rnalater" ||
    $("#id_sample_type").val() == "paraffin_block"
  ) {
    $("label[for=id_biopsy_location], #id_biopsy_location").show();
    $(
      "label[for=id_biopsy_inflamed_status], #id_biopsy_inflamed_status"
    ).show();
  }

  if ($("#id_sample_type").val() == "paraffin_block") {
    $("label[for=id_paraffin_block_key], #id_paraffin_block_key").show();
  }

  // If EDTA or Paxgene aliquots or extracted cfDNA, show haemolysis reference
  if (
    $("#id_sample_type").val() == "edta_plasma" ||
    $("#id_sample_type").val() == "cfdna_plasma" ||
    $("#id_sample_type").val() == "cfdna_extracted"
  ) {
    $("label[for=id_haemolysis_reference], #id_haemolysis_reference").show();
  }

  if ($("#id_sample_type").val() == "cfdna_extracted") {
    $("label[for=id_qubit_cfdna_ng_ul], #id_qubit_cfdna_ng_ul").show();
  }

  // Begin listening for form changes

  $("#id_sample_type").change(function () {
    if (
      $("#id_sample_type").val() == "biopsy_formalin" ||
      $("#id_sample_type").val() == "biopsy_rnalater" ||
      $("#id_sample_type").val() == "paraffin_block"
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
    if ($("#id_sample_type").val() == "paraffin_block") {
      $("label[for=id_paraffin_block_key], #id_paraffin_block_key").show(
        "slow"
      );
    } else {
      $("label[for=id_paraffin_block_key], #id_paraffin_block_key").hide();
    }
  });

  $("#id_sample_type").change(function () {
    if (
      $("#id_sample_type").val() == "edta_plasma" ||
      $("#id_sample_type").val() == "cfdna_plasma" ||
      $("#id_sample_type").val() == "cfdna_extracted"
    ) {
      $("label[for=id_haemolysis_reference], #id_haemolysis_reference").show(
        "slow"
      );
    } else {
      $("label[for=id_haemolysis_reference], #id_haemolysis_reference").hide();
    }
  });
  $("#id_sample_type").change(function () {
    if ($("#id_sample_type").val() == "cfdna_extracted") {
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

    if (
      $("#id_study_name").val() == "marvel"
    ) {
      $("label[for=id_marvel_timepoint], #id_marvel_timepoint").show("slow");
    } else {
      $("label[for=id_marvel_timepoint], #id_marvel_timepoint").hide();
    }
  });
});
