const gidamps_participants_by_center_data = JSON.parse(
  document.getElementById("gidamps_participants_by_center").textContent
);

const gidamps_participants_by_study_group_data = JSON.parse(
  document.getElementById("gidamps_participants_by_study_group").textContent
);

const gidamps_participants_by_recruitment_setting_data = JSON.parse(
  document.getElementById("gidamps_participants_by_recruitment_setting").textContent
);

const gidamps_participants_by_new_diagnosis_of_ibd_data = JSON.parse(
  document.getElementById("gidamps_participants_by_new_diagnosis_of_ibd").textContent
);

$(document).ready(function () {

  // Participants by study center
  const gidamps_participants_by_center_chart_area = document
    .getElementById("gidamps_participants_by_center_chart_area")
    .getContext("2d");
  const gidamps_participants_by_center_chart = new Chart(
    gidamps_participants_by_center_chart_area,
    {
      type: "bar",
      data: {
        datasets: [
          {
            label: "study_center",
            backgroundColor: COLORS,
            data: gidamps_participants_by_center_data.map((item) => item.count),
          },
        ],
        labels: gidamps_participants_by_center_data.map((item) => item.center),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          position: "bottom",
        },
      },
    }
  );
  // End of Participants by study center

  // Participants by study group
  const gidamps_participants_by_study_group_chart_area = document
    .getElementById("gidamps_participants_by_study_group_chart_area")
    .getContext("2d");
  const gidamps_participants_by_study_group_chart = new Chart(
    gidamps_participants_by_study_group_chart_area,
    {
      type: "bar",
      data: {
        datasets: [
          {
            label: "study_group",
            backgroundColor: COLORS,
            data: gidamps_participants_by_study_group_data.map((item) => item.count),
          },
        ],
        labels: gidamps_participants_by_study_group_data.map((item) => item.study_group),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          position: "bottom",
        },
      },
    }
  );
  // End of Participants by study group

  // Participants by recruitment setting
  const gidamps_participants_by_recruitment_setting_chart_area = document
    .getElementById("gidamps_participants_by_recruitment_setting_chart_area")
    .getContext("2d");
  const gidamps_participants_by_recruitment_setting_chart = new Chart(
    gidamps_participants_by_recruitment_setting_chart_area,
    {
      type: "bar",
      data: {
        datasets: [
          {
            label: "baseline_recruitment_type",
            backgroundColor: COLORS,
            data: gidamps_participants_by_recruitment_setting_data.map((item) => item.count),
          },
        ],
        labels: gidamps_participants_by_recruitment_setting_data.map((item) => item.baseline_recruitment_type),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          position: "bottom",
        },
      },
    }
  );
  // End of Participants by recruitment setting

  // Participants by new diagnosis of ibd
  const gidamps_participants_by_new_diagnosis_of_ibd_chart_area = document
    .getElementById("gidamps_participants_by_new_diagnosis_of_ibd_chart_area")
    .getContext("2d");
  const gidamps_participants_by_new_diagnosis_of_ibd_chart = new Chart(
    gidamps_participants_by_new_diagnosis_of_ibd_chart_area,
    {
      type: "bar",
      data: {
        datasets: [
          {
            label: "new_diagnosis_of_ibd",
            backgroundColor: COLORS,
            data: gidamps_participants_by_new_diagnosis_of_ibd_data.map((item) => item.count),
          },
        ],
        labels: gidamps_participants_by_new_diagnosis_of_ibd_data.map((item) => item.new_diagnosis_of_ibd),
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        legend: {
          position: "bottom",
        },
      },
    }
  );
  
});
