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


// ------------common------------

function separate(number) {
    return (number).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function errorCheck(data, func) {
    if (data["error"]) {
        showAlert(data["error"], "error");
    } else {
        return func()
    }
}


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


// -----------products-----------

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
}

function setProductColor(price, discount, colorName, colorId, stockCount) {
    var priceText = `
        <span class="item_price" dir="rtl">
            ${separate(price - discount)} تومان
        </span>
    `
    if (discount) {
        priceText = `<del>${separate(price)}</del>` + priceText
    };
    $("#price").html(priceText);
    $("#colors-title").text(`رنگ ها : (${colorName})`)
    var colors = $("#colors")[0].getElementsByTagName('li');
    for (var i = 0; i < colors.length; i++) {
        var color = colors[i].getElementsByTagName("a")[0].getElementsByTagName("span")[0]
        color.style.borderColor = "gainsboro"
    };
    $("#color-" + colorId).css("border-color", "blue");
    setInStockStatus(stockCount);
}

function setInStockStatus(stockCount) {
    var htmlMessage;
    if (stockCount > 5) {
        htmlMessage = '<h4 class="available">موجود در انبار</h4>';
    } else if (stockCount > 0) {
        htmlMessage = `<h4 class="few-in-stock">تنها ${stockCount} عدد در انبار موجود است</h4>`
    } else {
        htmlMessage = '<h4 class="unavailable">ناموجود</h4>';
    }
    $("#in-stock-status").html("<i><h4>وضعیت</h4></i>" + htmlMessage);
}

function likeOrDislikeProduct(productId) {
    $.get(`/products/${productId}/like-or-dislike-ajax/`).then(res => {
        errorCheck(res, function () {
            if (res["is_liked"]) {
                $("#like-product").html('<span class="glyphicon glyphicon-heart"></span>')
            } else {
                $("#like-product").html('<span class="glyphicon glyphicon-heart-empty"></span>')
            }
            showAlert(res["success"], "success");
        })
    })
}


// --------------comments------------------

function showMoreComments(productId, pageNum) {
    $.get(`/products/${productId}/get-comments-ajax/${pageNum}`).then(res => {
        errorCheck(res, function () {
            $("#show-more-comments").remove();
            $("#reviews-area").html(function (i, origHtml) {
                return origHtml + res["comments"]
            });
        });
    });
};

function replyComment(commentId, userName) {
    $("#parent-id-input").val(commentId);
    document.getElementById("add-review").scrollIntoView({ behavior: "smooth" })
    $("#form-title").html(
        "ثبت پاسخ برای نظرِ " + userName + `
        <button class="btn btn-primary" onclick='unReplyComment()'>
            <i class='fa fa-xmark'>
                ثبت نظر معمولی
            </i>
        </button>`)
    $("#rating-input").html("");
    $("#message-input").focus();
}

function unReplyComment() {
    $("#parent-id-input").val("");
    $("#rating-input").html(`
        <div class="rating1" id="rating-input">
            <span class="starRating">
                <input id="rating5" type="radio" name="rate" value="5" checked>
                <label for="rating5">5</label>
                <input id="rating4" type="radio" name="rate" value="4">
                <label for="rating4">4</label>
                <input id="rating3" type="radio" name="rate" value="3">
                <label for="rating3">3</label>
                <input id="rating2" type="radio" name="rate" value="2">
                <label for="rating2">2</label>
                <input id="rating1" type="radio" name="rate" value="1">
                <label for="rating1">1</label>
            </span>
            : نمره
        </div>
    `);
    $("#form-title").html("اضافه کردن نظر");
}
