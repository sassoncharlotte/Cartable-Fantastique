// we remove the double click event which highlights the text
document.body.addEventListener('mousedown', function(event) {
    if (event.detail > 1) {
        event.preventDefault();
    }
});

let entities = document.getElementsByClassName("framed_entities");


let number_of_colors = document.getElementById("script").getAttribute("number_of_colors");
if (typeof number_of_colors === "undefined" ) {
    number_of_colors = 1;
}

let displayed_colors_json = document.getElementById("script").getAttribute("displayed_colors_json");
if (typeof displayed_colors_json === "undefined" ) {
    displayed_colors_json = JSON.stringify({});
}

for (let entity of entities) {
    entity.onclick = function() {change_color(entity.getAttribute('id'), parseInt(entity.getAttribute('color_number')), number_of_colors, displayed_colors_json)};
    
    entity.addEventListener('mouseenter', e => {
        entity.style.cursor = 'pointer';
    });
};


function translate_color(colors_french) {
    let colors_dict = {'bleu':'blue_background', 'rouge':'red_background', 'vert':'green_background', 'noir':'grey_background', 'jaune':'yellow_background', 'rose':'pink_background'};
    let colors_english = [];
    for (var i = 0; i < colors_french.length; i++) {
        color = colors_french[i];
        colors_english.push(colors_dict[color]);
    }

    return colors_english
}


function change_color(id, color_number, number_of_colors, displayed_colors_json) {
    let colors_obj = JSON.parse(displayed_colors_json);
    let colors = [];
    element = document.getElementById(id);

    if (Object.keys(colors_obj).length>=number_of_colors) {
        let colors_french = Object.values(colors_obj);
        colors = translate_color(colors_french);

    } else {
        colors = ['yellow', 'pink', 'blue', 'green'];
    }

    for (let k = 0; k < 3; k++) { 
        element.classList.remove(colors[k]);
    }
    element.classList.remove('white');

    if (color_number<number_of_colors) {
        element.classList.add(colors[color_number]);
        color_number+=1;
        element.setAttribute('color_number', color_number.toString());

    } else {
        element.classList.add('white');
        element.setAttribute('color_number', '0');
    }
};
