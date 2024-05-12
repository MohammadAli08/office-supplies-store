// ------------url------------
var inputUrl = new URL(window.location.href);
var inputParams = new URLSearchParams(inputUrl.search);

function updateInputUrlAndInputParams() {
    inputUrl = new URL(window.location.href);
    inputParams = new URLSearchParams(inputUrl.search);
};

function setParameterWithOutReload(name, value) {
    updateInputUrlAndInputParams()
    inputParams.set(name, value)
    var url = inputUrl.href.split("?")[0] + "?" + inputParams
    window.history.pushState("", "", url);
};

function deleteParameterWithOutReload(name) {
    updateInputUrlAndInputParams()
    inputParams.delete(name)
    var url = inputUrl.href.split("?")[0] + "?" + inputParams
    window.history.pushState("", "", url);
};


// --------sweet-alerts--------

function showAlert(title, icon, onload) {
    const Toast = Swal.mixin({
        toast: true,
        position: "top-end",
        showConfirmButton: false,
        timer: 3000,
        timerProgressBar: true,
        didOpen: (toast) => {
            toast.onmouseenter = Swal.stopTimer;
            toast.onmouseleave = Swal.resumeTimer;
        }
    });
    if (onload) {
        window.onload = Toast.fire({
            icon: icon,
            title: title
        })
    } else {
        Toast.fire({
            icon: icon,
            title: title
        });
    }
}


// -----------ajax-----------


function setProductsFilter(data) {
    for (let key in data) {
        setParameterWithOutReload(key, data[key])
    };
    var paramData = {};
    updateInputUrlAndInputParams();

    for (let [key, value] of inputParams) {
        paramData[key] = value;
    };

    if ("paginate_change" in paramData) {
        deleteParameterWithOutReload("page")
    }

    deleteParameterWithOutReload("category_changed");

    $.get("/products/filter-ajax", paramData).then((res) => {
        if (res["categories"]) {
            $("#categories-area").html(res["categories"]);
        };
        $("#products-area").html(res["products"]);
        $("#pagination-area").html(res["pagination"]);
        $("#price-filter-area").html(res["price_filter"]);
        setPriceRange();
    });
};
