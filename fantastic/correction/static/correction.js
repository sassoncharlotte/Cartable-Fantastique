var successor= document.getElementById("script_correction").getAttribute("successor");
var predecessor=document.getElementById("script_correction").getAttribute("predecessor");
var current=document.getElementById("script_correction").getAttribute("current");

document.addEventListener("keydown", function(event){
    var char = event.which || event.keyCode;
    console.log(char);
    switch(char){
        case 39: //right arrow key
            window.location.href = window.location.protocol + "//" + window.location.host + "/correction/" + successor;
            break;
        case 37: // left arrow key
            window.location.href = window.location.protocol + "//" + window.location.host + "/correction/" + predecessor;
            break;
        case 38: // up arrow key
            document.getElementById("nice_conversion_button").click();
            break;
        case 40: // down arrow key
            document.getElementById("wrong_conversion_button").click();
            break;
        case 77: // M
            document.getElementById("wrong_extraction_button").click();
            break;
        case 13: // Enter key
            document.getElementById("new_tag_button").click();
            break;
        case 80: // P 
            document.getElementById("show_prediction_button").click();
            break;
        case 67: //C
            document.getElementById("show_xml_html_button").click();
            break;
    }
});

function DisplayWaitMessage(){
    var third_part = document.getElementById("third_part");
    third_part.innerHTML = "Veuillez patienter ..."
}

function SubmitCorresponding(div){
    var id = div.id;
    var submit_id = id.substring(0, id.length-4) + "_button";
    console.log(submit_id);
    document.getElementById(submit_id).click();
}
