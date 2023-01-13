
var show = function (elem) {
	elem.style.display = 'block';
};

var hide = function (elem) {
	elem.style.display = 'none';
};

window.onresize = hideChoices;

function hideChoices(){
	var mc_menus = document.getElementsByClassName("mc_menu");
	for(var index=0;index < mc_menus.length;index++) hide(mc_menus[index]);
};

function myFunction(button) {
	hideChoices();
  var id_mc_menu = button.getAttribute("id_mc_menu");
  var content = document.getElementById(id_mc_menu);

  if (!content) return;

	show(content);
	var button_pos = button.getBoundingClientRect();
	var content_pos = content.getBoundingClientRect();
	content.style.top = (button_pos.top + button_pos.height) + "px";
	content.style.left = (button_pos.left - content_pos.width/2) + "px";
	if (content.style.left<"10px") content.style.left = "0px"
};

function setChoiceValue(button) {
  var id_mc_button = button.getAttribute("id_mc_button");
  var id_mc_menu = button.getAttribute("id_mc_menu");
  var content = document.getElementById(id_mc_button);
  var mc_menu = document.getElementById(id_mc_menu);
  if (button.innerHTML!==content.innerHTML) content.innerHTML = button.innerHTML;
  hide(mc_menu);
};

// we remove the double click event which highlights the text
var el = document.body;
if(el){
  el.addEventListener('mousedown', function(event) {
    if (event.detail > 1) {
        event.preventDefault();
	}
});
}