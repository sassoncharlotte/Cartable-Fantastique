// we remove the double click event which highlights the text
document.body.addEventListener('mousedown', function(event) {
    if (event.detail > 1) {
        event.preventDefault();
    }
});

var selected = false;
var content_selected = "";
var class_selected = "";

var disableChangePage = function (bool) {
	var prev = document.getElementById("previous_page");
	var next = document.getElementById("next_page")
	if (!bool) {
		prev.disabled = false;
		next.disabled = false;
		return;
	}
	prev.disabled = true;
	next.disabled = true;
}

function myFunction(elem){
  var class_swap = elem.getAttribute("framed_entities");
  elem.style.backgroundColor = "lightyellow";
  if (!selected) {
		content_selected = elem.innerHTML;
		class_selected = class_swap;
    selected = true;
    disableChangePage(true);
  }
  else{
		if (class_swap === class_selected){
			var swap_labels = document.getElementsByClassName(class_swap);
	    var index_to_swap = -1;
	    for(var index=0;index < swap_labels.length;index++){
	        if ((swap_labels[index].style.backgroundColor === "lightyellow") & (swap_labels[index].innerHTML ===content_selected)) index_to_swap = index;
				}
       var other_elem = swap_labels[index_to_swap];
       var temp = other_elem.innerHTML;
       other_elem.innerHTML = elem.innerHTML;
       elem.innerHTML = temp;
			 other_elem.style.backgroundColor = "transparent";
	     }
			else{
				var swap_labels = document.getElementsByClassName(class_selected);
		    for(var index=0;index < swap_labels.length;index++){
		        swap_labels[index].style.backgroundColor = "transparent";
					}
				}
		content_selected = "";
		class_selected = ""
		elem.style.backgroundColor = "transparent";
    selected = false;
    disableChangePage(false);
  }
}
