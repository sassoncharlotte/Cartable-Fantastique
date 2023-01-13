// we update the line's vertical position list
// if the position changes by a bit, it's not another line
// the "bit" is defined by a threshold
var threshold = 15;
var nb_lines_per_page = document.getElementById("script_front").getAttribute("lines_per_page");

// we add events to handle

// when you load the page, you color the lines
window.addEventListener('load', style);
// we handle changes of pages
document.getElementById('previous_page').addEventListener('click', previous_page);
document.getElementById('next_page').addEventListener('click', next_page);
// when you resize the window, lines move and we need to update their colors
window.addEventListener('resize', color_lines);
// we update color when stuff is typed in editable content
var editable_content = document.querySelectorAll("[contenteditable=true]");
for (let j = 0; j < editable_content.length; j++) {
    editable_content[j].addEventListener('input', color_lines);
}

function style() {
    /* apply all the style, to use only when loading the page !!
       we do not resplit lines when the window is resized for instance, it would not work because of invisible words
    */
       
    split_lines_into_pages();
    show_page(0);
    color_lines();
}

function color_lines () {
    /* look at every word, and according to its position color it with the right color
    */

    // we only look at the words of the page, other invisble words from other pages could change the colors
    var page = document.getElementById('page'.concat(get_page().toString()));
    var words = page.querySelectorAll('[id^="word"]');

    // we create the list of vertical position from every line
    // we do not use the function for that to not go twice through each word
    var lines_y_pos = [];
    for (let k = 0; k < words.length; k++) {
        var word = words[k];
        var y_pos = word.getBoundingClientRect().top; // vertical position of the word

        // we update the line's vertical position list
        // if the position changes by a bit, it's not another line
        // the "bit" is defined by a threshold
        var cond = (elt) => Math.abs(elt - y_pos) < threshold;
        if (!(lines_y_pos.some(cond))) {
            lines_y_pos.push(y_pos);
        }

        var distance_to_lines = lines_y_pos.map(x => Math.abs(x-y_pos));
        var line_number = distance_to_lines.indexOf(Math.min.apply(Math, distance_to_lines));
        color_word(word, line_number);
    }

}

function get_lines_y_pos() {
    /* we create the list of vertical position of the lines
    */

    // counting number of words: elts with id starting by word
    var words_count = document.querySelectorAll('[id^="word"]').length;
    
    // we go through each word
    var lines_y_pos = [];
    for (let id = 0; id < (words_count); id++) {
        var word = document.getElementById('word'.concat(id.toString()));
        var y_pos = word.getBoundingClientRect().top; // vertical position of the word

        // we update the line's vertical position list
        // if the position changes by a bit, it's not another line
        // the "bit" is defined by a threshold
        var cond = (elt) => Math.abs(elt - y_pos) < threshold;
        if (!(lines_y_pos.some(cond))) {
            lines_y_pos.push(y_pos);
        }
    }

    return lines_y_pos
}

function color_word(word, line_number) {
    // order of colors that are displayed
    var color_name = {
        0: 'blue',
        1: 'red',
        2: 'green'
    };

    // we remove every class of color for a word
    for (let k = 0; k < 3; k++) { 
        word.classList.remove(color_name[k]);
    }
    word.classList.add(color_name[line_number%3]);
}

function split_lines_into_pages() {
    /* we split blocks into different pages, to verify:
    - blocks are insecable parts of text thus one block cannot be on multiple pages
    - no more than 3 lines per page (except if that breaks the first rule)
    */

    var blocks = document.querySelectorAll('[id^="block"]');
    var lines_y_pos = get_lines_y_pos();
    var total_lines_nb = lines_y_pos.length;
    // the page where each block should be
    var block_page = {};
    var lines_per_block = {};

    // we go through each block to get where each block should be
    for (let id = 0; id < blocks.length; id++) {
        var block = blocks[id];
        var words_of_block = block.childNodes;

        // we'll look at how many lines are per block and per page
        var first_word = words_of_block[0];
        var last_word = words_of_block[words_of_block.length-1];
        var first_y_pos = first_word.getBoundingClientRect().top;
        var last_y_pos = last_word.getBoundingClientRect().top;
        var first_distance_to_lines = lines_y_pos.map(x => Math.abs(x-first_y_pos));
        var last_distance_to_lines = lines_y_pos.map(x => Math.abs(x-last_y_pos));
        var first_line_number = first_distance_to_lines.indexOf(Math.min.apply(Math, first_distance_to_lines));
        var last_line_number = last_distance_to_lines.indexOf(Math.min.apply(Math, last_distance_to_lines));

        lines_per_block[id] = last_line_number - first_line_number + 1;

        // the first pages should be filled at max 3 lines per page
        // then we'll look at if we add 1, 2 or 3 lines for the last pages
        if (nb_lines_per_page == 1) {
            block_page[id] = (id == 0) ? 0 : block_page[id-1] + 1;
        }
        else {
            if (id == 0) {
                block_page[id] = 0;
            }
            else {
                // we look at what blocks are on last page to know how many lines are on last page
                var blocks_on_last_page = [];
                for (let j=0; j<id; j++) {
                    if (block_page[j] == block_page[id-1]) {
                        blocks_on_last_page.push(j);
                    }
                }

                var lines_on_last_page = 0;
                for (let k=0; k<blocks_on_last_page.length; k++) {
                    lines_on_last_page += lines_per_block[blocks_on_last_page[k]];
                }

                if (lines_on_last_page + lines_per_block[id] <= nb_lines_per_page) {
                    block_page[id] = block_page[id-1]
                }
                else {
                    block_page[id] = block_page[id-1] + 1
                }
            }                
        }
    }

    // then we go through each block to position it on the right page
    for (let id = 0; id < blocks.length; id++) {
        var block = blocks[id];
        var words_of_block = block.childNodes;

        // if the block is on the wrong page
        if (block.parentNode.id.slice(4) != block_page[id]) {
            // if the page where the block should be on exists
            if (document.getElementById('page'.concat(block_page[id].toString()))) {
                var page = document.getElementById('page'.concat(block_page[id].toString()));
                page.appendChild(block);
            }
            else { // we create that page
                var exercise_text = document.getElementById('exercise_text');
                var new_page = document.createElement("p");
                new_page.id = 'page'.concat(block_page[id].toString());
                new_page.appendChild(block);
                exercise_text.appendChild(new_page);
            }

        }
    }
}

function show_page(page_id) {
    /* displays the page and updates button, we should not have a next page button if there is no next page
    */
    var back_button = document.getElementById('previous_page');
    var next_button = document.getElementById('next_page');

    // if the previous page does not exist
    back_button.style.display = (page_id == 0) ? 'none' : 'block';
    // if the next page exists
    next_button.style.display = (document.getElementById("page".concat((page_id+1).toString()))) ? 'inline' : 'none';

    // we update the hash
    window.location.hash = '#page'.concat(page_id.toString()); 

    // we show the right page and hide others
    var page = document.getElementById('page'.concat(page_id.toString()));
    var pages = document.querySelectorAll('[id^="page"]');

    for (let id = 0; id < pages.length; id++) {
        pages[id].style.display = 'none';
    }
    page.style.display = 'block';

}

function get_page() {
    // the page on where we are is indicated by the hash
    return (window.location.hash) ? parseInt(window.location.hash.slice(5),10) : 0;
}

function previous_page() {
    show_page(get_page()-1);
    // we need to update the color of the lines as the lines change
    color_lines();
}

function next_page() {
    show_page(get_page()+1);
    // we need to update the color of the lines as the lines change
    color_lines();
}
