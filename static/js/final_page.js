function showLoaderOnClick(url) {
    showLoader();
    window.location = url;
}

function showLoader() {
    $('body').append('<div style="" id="loadingDiv"><div class="loader">Loading...</div></div>');
}