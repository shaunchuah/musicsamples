$(document).ready(function () {
  $('[data-toggle="tooltip"]').tooltip();
  $("#mainTable").tablesorter({
    sortReset: true,
    dateFormat: "ddmmyyyy",
    headers: {
      8: {
        sorter: "shortDate",
      },
      15: {
        sorter: false,
      },
      16: {
        sorter: false,
      },
      17: {
        sorter: false,
      }
    },
  });

  $("#deleteConfirmModal").on("show.bs.modal", function (e) {
    var url = $(e.relatedTarget).data("href");
    $("#confirmDeleteBtn").attr("href", url);
  });
});
