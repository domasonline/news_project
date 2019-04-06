function call_counter(url, pk) {
    window.open(url);
    $.get('home/'+pk+'/', function (data) {
        alert("counter updated!");
    });
}
