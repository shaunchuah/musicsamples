$(document).ready(function () {
  $('[data-toggle="tooltip"]').tooltip();
  $("#mainTable").tablesorter({
    sortReset: true,
    dateFormat: "ddmmyyyy",
    headers: {
      6: {
        sorter: "shortDate",
      },
      13: {
        sorter: false,
      },
      9: {
        sorter: false,
      },
      10: {
        sorter: false,
      },
      11: {
        sorter: false,
      },
      12: {
        sorter: false,
      },
    },
  });

  $("#deleteConfirmModal").on("show.bs.modal", function (e) {
    var url = $(e.relatedTarget).data("href");
    $("#confirmDeleteBtn").attr("href", url);
  });
});
