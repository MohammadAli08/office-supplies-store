function setPriceRange(){
    var sliderRange = $("#slider-range");
    var startPrice = sliderRange.attr("startPrice");
    var endPrice = sliderRange.attr("endPrice");
    sliderRange.slider({
        range: true,
        min: 0,
        max: sliderRange.attr("maxPrice"),
        values: [startPrice, endPrice],
        slide: function (event, ui) {
            $("#amount").val("$" + ui.values[0] + " - $" + ui.values[1]);
        },
        change: function (event, ui) {
            var startPrice = sliderRange.slider("values", 0)
            var endPrice = sliderRange.slider("values", 1)
            setProductsFilter({"start_price": startPrice, "end_price": endPrice})
            $.getScript("/static/js/priceRange.js");
            $.getScript("/static/js/jquery-ui.min.js");
        },
    });
    $("#amount").val("$" + $("#slider-range").slider("values", 0) + " - $" + $("#slider-range").slider("values", 1));
}
